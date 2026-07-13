import concurrent.futures

import pandas as pd
import streamlit as st

from server import SOURCES, load_lib, make_source_status, save_lib, search_custom, today


st.set_page_config(
    page_title="BOQ Price Intelligence",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)


SOURCE_LABELS = {
    "sirichai": "sirichaielectric.com",
    "ranfaifa": "ranfaifa.com",
    "obec": "YOTATHAI OBEC 2568",
    "apelectric": "apelectricstore.com",
}


def fmt_price(value):
    if value is None or value == "":
        return "-"
    return f"{float(value):,.2f}"


def run_live_search(query, selected_sources, custom_sources):
    results, errors = [], []
    source_status = {
        "sirichai": make_source_status("no_result", 0, "ไม่ได้เลือกแหล่งนี้"),
        "ranfaifa": make_source_status("no_result", 0, "ไม่ได้เลือกแหล่งนี้"),
        "obec": make_source_status("no_result", 0, "ไม่ได้เลือกแหล่งนี้"),
        "apelectric": make_source_status("no_result", 0, "ไม่ได้เลือกแหล่งนี้"),
        "custom": make_source_status("no_result", 0, "ไม่ได้เพิ่ม Custom URL"),
    }

    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
        futures = {}
        for key in selected_sources:
            if key in SOURCES:
                futures[ex.submit(SOURCES[key], query)] = key
        for url in custom_sources:
            if url.strip():
                futures[ex.submit(search_custom, query, url.strip())] = "custom"

        for fut in concurrent.futures.as_completed(futures):
            source_key = futures[fut]
            try:
                found = fut.result()
                results.extend(found)
                if source_key == "custom":
                    old = source_status["custom"]
                    count = old["result_count"] + len(found)
                    msg = "" if count else "ไม่สามารถดึงราคาอัตโนมัติจากเว็บนี้ได้"
                    source_status["custom"] = make_source_status("success" if count else "no_result", count, msg)
                else:
                    source_status[source_key] = make_source_status(
                        "success" if found else "no_result",
                        len(found),
                        "" if found else "ไม่พบราคาที่ตรงกับคำค้น",
                    )
            except Exception as exc:
                errors.append(f"{source_key}: {exc}")
                source_status[source_key] = make_source_status("error", 0, str(exc))

    for item in results:
        item["fetched_at"] = today()
    results.sort(key=lambda x: (x.get("price") is None, x.get("price") or 0, x.get("name", "")))
    return results, errors, source_status


def next_library_id(items):
    return max((int(item.get("id", 0)) for item in items), default=0) + 1


def save_results(results, indexes, markup_pct):
    lib = load_lib()
    next_id = next_library_id(lib)
    for idx in indexes:
        item = results[idx]
        price = item.get("price")
        final_price = round(float(price) * (1 + markup_pct / 100), 2) if price is not None else None
        lib.append({
            "id": next_id,
            "name": item.get("name", ""),
            "price": price,
            "unit": item.get("unit", "") or "",
            "labor": item.get("labor"),
            "source": item.get("source", ""),
            "url": item.get("url", ""),
            "fetched_at": item.get("fetched_at", today()),
            "saved_at": today(),
            "markup_pct": markup_pct,
            "qty": 1,
            "final_price": final_price,
        })
        next_id += 1
    save_lib(lib)
    return len(indexes)


def render_css():
    st.markdown(
        """
        <style>
        :root{
          --bg:#f8f9ff; --card:#ffffff; --ink:#0b1c30; --muted:#545f73;
          --line:#e3e8f2; --primary:#065f46; --primary-deep:#004532;
          --mint:#a6f2d1; --mint-soft:#e9f8f1; --head-band:#eff4ff;
          --sidebar:#0b4a36; --sidebar-deep:#083a2b; --sidebar-ink:#d7ece2;
        }
        .stApp{background:var(--bg);color:var(--ink);font-family:"Inter","Sarabun",sans-serif;}
        header[data-testid="stHeader"]{display:none;}
        footer{display:none;}
        [data-testid="stSidebar"]{background:linear-gradient(180deg,var(--sidebar),var(--sidebar-deep));}
        [data-testid="stSidebar"] *{color:var(--sidebar-ink);}
        [data-testid="stSidebar"] h1,[data-testid="stSidebar"] h2,[data-testid="stSidebar"] h3{color:#fff;}
        [data-testid="stSidebar"] label,[data-testid="stSidebar"] p{font-size:14px;}
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] strong{color:#fff;}
        .block-container{padding-top:0.85rem;max-width:1280px;}
        .boq-topbar{background:#fff;border:1px solid var(--line);border-radius:0 0 10px 10px;
          padding:14px 18px;margin:0 0 24px;display:flex;justify-content:space-between;align-items:center;}
        .boq-appname{font-weight:800;color:var(--primary-deep);font-size:18px;}
        .boq-pill{display:inline-flex;gap:8px;align-items:center;background:var(--mint-soft);color:#0a5c3a;
          border:1px solid #cdebdc;border-radius:999px;padding:5px 14px;font-size:13px;font-weight:700;}
        .boq-dot{width:7px;height:7px;border-radius:999px;background:#12a06b;display:inline-block;}
        .boq-head h2{font-size:30px;font-weight:800;margin:0;color:var(--ink);}
        .boq-head p{color:var(--muted);margin:6px 0 20px;line-height:1.55;}
        .boq-card{background:#fff;border:1px solid var(--line);border-radius:16px;padding:22px;margin:0 0 20px;
          box-shadow:0 4px 20px rgba(0,0,0,.05);}
        .source-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:8px;margin-bottom:14px;}
        .source-card{border:1px solid var(--line);border-radius:8px;padding:9px 11px;background:#fff;}
        .source-card .name{font-size:11px;text-transform:uppercase;letter-spacing:.06em;color:var(--muted);font-weight:800;}
        .source-card .state{margin-top:4px;font-size:13px;font-weight:800;}
        .source-card .msg{font-size:11.5px;color:var(--muted);margin-top:3px;}
        .source-card.success{background:#f2fbf7;border-color:#cdebdc;}
        .source-card.success .state{color:#0a5c3a;}
        .source-card.no_result .state{color:#946200;}
        .source-card.error{background:#fff8f8;border-color:#f0c7c7;}
        .source-card.error .state{color:#ba1a1a;}
        div[data-testid="stDataFrame"], div[data-testid="stDataEditor"]{border:1px solid var(--line);border-radius:12px;overflow:hidden;}
        .stButton>button{background:var(--primary);color:white;border:1px solid var(--primary);border-radius:8px;
          font-weight:800;padding:0.52rem 1rem;}
        .stButton>button:hover{background:var(--primary-deep);color:white;border-color:var(--primary-deep);}
        .stTextInput input,.stNumberInput input,.stTextArea textarea{border-radius:8px;border:1px solid var(--line);}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_topbar():
    st.markdown(
        """
        <div class="boq-topbar">
          <span class="boq-appname">BOQ Price Intelligence</span>
          <span class="boq-pill"><span class="boq-dot"></span> System Online</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_page_head(title, desc):
    st.markdown(
        f"""
        <div class="boq-head">
          <h2>{title}</h2>
          <p>{desc}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_source_status(source_status):
    if not source_status:
        return
    cards = []
    for key, label in {**SOURCE_LABELS, "custom": "Custom URL"}.items():
        item = source_status.get(key)
        if not item:
            continue
        state = item.get("status", "no_result")
        count = item.get("result_count", 0)
        msg = item.get("message", "")
        cards.append(
            f"""
            <div class="source-card {state}">
              <div class="name">{label}</div>
              <div class="state">{state} · {count} item(s)</div>
              <div class="msg">{msg}</div>
            </div>
            """
        )
    st.markdown('<div class="source-grid">' + "".join(cards) + "</div>", unsafe_allow_html=True)


def results_dataframe(results, markup_pct):
    rows = []
    for i, item in enumerate(results):
        price = item.get("price")
        final_price = round(float(price) * (1 + markup_pct / 100), 2) if price is not None else None
        rows.append({
            "Save": False,
            "#": i + 1,
            "Item Name": item.get("name", ""),
            "Base Price (THB)": fmt_price(price),
            "Unit": item.get("unit", "") or "-",
            "Labor": fmt_price(item.get("labor")),
            "Source": item.get("source", ""),
            "Retrieved": item.get("fetched_at", today()),
            "Markup %": markup_pct,
            "Final Price": fmt_price(final_price),
        })
    return pd.DataFrame(rows)


def show_search_page(selected_sources, custom_sources, markup_pct):
    render_page_head(
        "Price Search",
        "ค้นราคาวัสดุจากเว็บร้านค้าที่เชื่อถือได้ ราคากลางภาครัฐ (สพฐ.2568) และแหล่งที่เพิ่มเอง เพื่อจัดทำ Bill of Quantities อย่างแม่นยำ",
    )

    st.markdown('<div class="boq-card">', unsafe_allow_html=True)
    query = st.text_input(
        "Search Query",
        placeholder="เช่น Smoke detector, สายไฟ THW, ท่อ EMT, กล้อง CCTV ...",
        key="search_query",
    )
    c1, c2, c3 = st.columns([1, 1, 5])
    with c1:
        search_clicked = st.button("Execute Search", disabled=not query.strip(), use_container_width=True)
    with c2:
        clear_clicked = st.button("Clear", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    if clear_clicked:
        st.session_state.live_results = []
        st.session_state.live_errors = []
        st.session_state.source_status = None

    if search_clicked:
        with st.spinner("กำลังดึงราคาเว็บสดผ่าน Python..."):
            st.session_state.live_results, st.session_state.live_errors, st.session_state.source_status = run_live_search(
                query.strip(), selected_sources, custom_sources
            )

    results = st.session_state.live_results
    st.markdown('<div class="boq-card">', unsafe_allow_html=True)
    left, right = st.columns([2, 3])
    with left:
        st.subheader(f"Search Results ({len(results)} items)")
    with right:
        if results:
            b1, b2, b3 = st.columns(3)
            save_all = b1.button("Save All", use_container_width=True)
            save_selected = b2.button("Save Selected", use_container_width=True)
            unsave_all = b3.button("Unsave All", use_container_width=True)
        else:
            save_all = save_selected = unsave_all = False

    render_source_status(st.session_state.source_status)

    if st.session_state.live_errors:
        st.warning("บางแหล่งดึงไม่สำเร็จ: " + "; ".join(st.session_state.live_errors))

    if not results:
        st.info("พิมพ์คำค้นแล้วกด Execute Search")
    else:
        df = results_dataframe(results, markup_pct)
        if unsave_all:
            df["Save"] = False
        edited = st.data_editor(
            df,
            hide_index=True,
            use_container_width=True,
            height=460,
            column_config={
                "Save": st.column_config.CheckboxColumn("Save"),
                "Item Name": st.column_config.TextColumn("Item Name", width="large"),
                "Final Price": st.column_config.TextColumn("Final Price", width="small"),
            },
            disabled=[col for col in df.columns if col != "Save"],
            key="result_editor",
        )

        selected_indexes = edited.index[edited["Save"]].tolist()
        if save_all:
            count = save_results(results, list(range(len(results))), float(markup_pct))
            st.success(f"Saved {count} item(s) to Price Library")
        if save_selected:
            if selected_indexes:
                count = save_results(results, selected_indexes, float(markup_pct))
                st.success(f"Saved {count} item(s) to Price Library")
            else:
                st.warning("เลือกรายการที่ต้องการบันทึกก่อน")
    st.markdown("</div>", unsafe_allow_html=True)


def show_library_page():
    render_page_head(
        "Price Library",
        "รายการราคาที่บันทึกไว้สำหรับใช้อ้างอิง เสนอราคา และเติมกลับเข้า BOQ",
    )
    st.markdown('<div class="boq-card">', unsafe_allow_html=True)
    lib = load_lib()
    st.subheader(f"{len(lib)} Items")
    if not lib:
        st.info("ยังไม่มีรายการใน Price Library")
    else:
        st.dataframe(lib, use_container_width=True, hide_index=True, height=520)
    st.markdown("</div>", unsafe_allow_html=True)


def show_boq_page():
    render_page_head(
        "Fill BOQ",
        "ฟีเจอร์เติม BOQ แบบเต็มยังอยู่ใน Flask HTML app ส่วนหน้า Streamlit นี้เน้นค้นราคาและบันทึก Library",
    )
    st.markdown('<div class="boq-card">', unsafe_allow_html=True)
    st.info("ถ้าต้องใช้ Fill BOQ เต็มรูปแบบ ให้รัน Flask: python3 server.py แล้วเปิด http://127.0.0.1:5544/")
    st.markdown("</div>", unsafe_allow_html=True)


def init_state():
    st.session_state.setdefault("live_results", [])
    st.session_state.setdefault("live_errors", [])
    st.session_state.setdefault("source_status", None)


init_state()
render_css()

with st.sidebar:
    st.markdown("## BOQ Intelligence")
    st.caption("PRICE FINDER MVP")
    page = st.radio("Navigation", ["Price Search", "Price Library", "Fill BOQ"], label_visibility="collapsed")
    st.divider()
    st.markdown("**Target Sources**")
    selected_sources = [
        key for key, label in SOURCE_LABELS.items()
        if st.checkbox(label, value=True, key=f"src_{key}")
    ]
    st.markdown("**Add Website Source**")
    custom_text = st.text_area(
        "Custom URLs",
        placeholder="https://www.example.com\nhttps://shop.example.com/search?q={q}",
        label_visibility="collapsed",
    )
    custom_sources = [line.strip() for line in custom_text.splitlines() if line.strip()]
    markup_pct = st.number_input("Global Markup (%)", min_value=0.0, value=10.0, step=0.5)
    st.caption("Sources: sirichaielectric • ranfaifa • OBEC 2568 • apelectric + custom URL")

render_topbar()

if page == "Price Search":
    show_search_page(selected_sources, custom_sources, markup_pct)
elif page == "Price Library":
    show_library_page()
else:
    show_boq_page()
