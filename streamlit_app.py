import concurrent.futures

import streamlit as st

from server import SOURCES, load_lib, save_lib, search_custom, today


st.set_page_config(page_title="BOQ Live Price Finder", layout="wide")


def fmt_price(value):
    if value is None or value == "":
        return "-"
    return f"{float(value):,.2f}"


def run_live_search(query, selected_sources, custom_sources):
    results, errors = [], []
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
        futures = {}
        for key in selected_sources:
            if key in SOURCES:
                futures[ex.submit(SOURCES[key], query)] = key
        for url in custom_sources:
            if url.strip():
                futures[ex.submit(search_custom, query, url.strip())] = url.strip()

        for fut in concurrent.futures.as_completed(futures):
            source = futures[fut]
            try:
                results.extend(fut.result())
            except Exception as exc:
                errors.append(f"{source}: {exc}")

    for item in results:
        item["fetched_at"] = today()
    results.sort(key=lambda x: (x.get("price") is None, x.get("price") or 0))
    return results, errors


def next_library_id(items):
    return max((int(item.get("id", 0)) for item in items), default=0) + 1


def save_selected_results(results, selected_indexes, markup_pct):
    lib = load_lib()
    next_id = next_library_id(lib)
    for idx in selected_indexes:
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
    return len(selected_indexes)


if "live_results" not in st.session_state:
    st.session_state.live_results = []
if "live_errors" not in st.session_state:
    st.session_state.live_errors = []

st.title("BOQ Live Price Finder")
st.caption("ค้นราคาแบบสดด้วย Python/Streamlit จากเว็บหลัก + เว็บที่เพิ่มเอง แล้ว Save เข้า Price Library เดียวกับ Flask app")

with st.sidebar:
    st.header("Search Sources")
    source_labels = {
        "sirichai": "sirichaielectric.com",
        "ranfaifa": "ranfaifa.com",
        "obec": "YOTATHAI OBEC 2568",
        "apelectric": "apelectricstore.com",
    }
    selected_sources = [
        key for key, label in source_labels.items()
        if st.checkbox(label, value=True, key=f"src_{key}")
    ]
    custom_text = st.text_area(
        "Add Website Sources",
        placeholder="https://www.example.com\nhttps://shop.example.com/search?q={q}",
        help="ใส่ได้หลายเว็บ แยกบรรทัด ถ้าเว็บมี pattern ค้นหาเองให้ใช้ {q}",
    )
    custom_sources = [line.strip() for line in custom_text.splitlines() if line.strip()]
    markup_pct = st.number_input("Markup %", min_value=0.0, value=10.0, step=0.5)

query = st.text_input("Search Query", placeholder="เช่น Smoke detector, สายไฟ THW, ท่อ EMT")

if st.button("Live Search", type="primary", disabled=not query.strip()):
    with st.spinner("กำลังดึงราคาเว็บสดผ่าน Python..."):
        st.session_state.live_results, st.session_state.live_errors = run_live_search(
            query.strip(), selected_sources, custom_sources
        )

if st.session_state.live_errors:
    st.warning("บางแหล่งดึงไม่สำเร็จ: " + "; ".join(st.session_state.live_errors))

results = st.session_state.live_results
st.subheader(f"Search Results ({len(results)} items)")

if results:
    rows = []
    for i, item in enumerate(results):
        price = item.get("price")
        final_price = round(float(price) * (1 + markup_pct / 100), 2) if price is not None else None
        rows.append({
            "#": i + 1,
            "Item Name": item.get("name", ""),
            "Base Price": fmt_price(price),
            "Final Price": fmt_price(final_price),
            "Unit": item.get("unit", "") or "-",
            "Labor": fmt_price(item.get("labor")),
            "Source": item.get("source", ""),
            "URL": item.get("url", ""),
        })
    st.dataframe(rows, use_container_width=True, hide_index=True)

    selected = st.multiselect(
        "Select rows to save",
        options=list(range(len(results))),
        format_func=lambda i: f"{i + 1}. {results[i].get('name', '')[:90]}",
    )
    if st.button("Save Selected To Library", disabled=not selected):
        saved_count = save_selected_results(results, selected, float(markup_pct))
        st.success(f"Saved {saved_count} item(s) to Price Library")
else:
    st.info("พิมพ์คำค้นแล้วกด Live Search")

with st.expander("Price Library Preview"):
    lib = load_lib()
    st.write(f"{len(lib)} saved item(s)")
    if lib:
        st.dataframe(lib, use_container_width=True, hide_index=True)
