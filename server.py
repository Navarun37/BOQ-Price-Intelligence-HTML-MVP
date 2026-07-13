#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""BOQ Price Finder — ค้นราคาวัสดุจาก 4 แหล่ง + custom URL, เก็บเป็น Price Library,
export Excel และเติมราคากลับเข้าไฟล์ BOQ

รัน:  python3 server.py   แล้วเปิด http://127.0.0.1:5544
"""
import datetime
import json
import os
import re
import threading
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify, request, send_file, send_from_directory

BASE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE, 'data')
LIB_FILE = os.path.join(DATA_DIR, 'price_library.json')
OBEC_FILE = os.path.join(DATA_DIR, 'obec2568.json')
os.makedirs(DATA_DIR, exist_ok=True)

UA = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                    'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125 Safari/537.36'}
TIMEOUT = 15
app = Flask(__name__)
_lib_lock = threading.Lock()

THAI_MARKS = re.compile(u'[ัิ-ฺ็-๎\\s\\.\\-/]')


def norm(s):
    """normalize สำหรับค้นแบบทนตัวสะกด/วรรณยุกต์เพี้ยน (ข้อมูลจาก PDF)"""
    return THAI_MARKS.sub('', (s or '').lower())


def today():
    return datetime.date.today().isoformat()


def parse_price(text):
    m = re.search(r'([\d,]+(?:\.\d+)?)', text or '')
    if not m:
        return None
    try:
        return float(m.group(1).replace(',', ''))
    except ValueError:
        return None


# ---------------------------------------------------------------- sources
def search_sirichai(q):
    """sirichaielectric.com: ค้นหน้า search แล้วตามเข้าไปดึงราคาจากหน้าสินค้า (top 6)"""
    out = []
    r = requests.get('https://sirichaielectric.com/search_product.php',
                     params={'search': q}, headers=UA, timeout=TIMEOUT)
    r.encoding = 'utf-8'
    soup = BeautifulSoup(r.text, 'html.parser')
    links = []
    for a in soup.find_all('a', href=True):
        h = a['href']
        if h.endswith('-product') and h not in links:
            links.append(h)
    def fetch(href):
        url = 'https://sirichaielectric.com' + urllib.parse.quote(href)
        pr = requests.get(url, headers=UA, timeout=TIMEOUT)
        pr.encoding = 'utf-8'
        ps = BeautifulSoup(pr.text, 'html.parser')
        text = ps.get_text('\n', strip=True)
        name, price, unit = None, None, ''
        m = re.search(r'(.+?)\s*ราคา\s*([\d,]+(?:\.\d+)?)\s*บาท', text)
        if m:
            name, price = m.group(1).strip(), parse_price(m.group(2))
        m2 = re.search(r'[\d,]+(?:\.\d+)?\s*/\s*(\S+)', text)
        if m2:
            unit = m2.group(1)
        if not name:
            name = href.replace('-product', '').replace('-', ' ').strip('/')
        return {'name': name, 'price': price, 'unit': unit,
                'source': 'sirichaielectric.com', 'url': url}
    with ThreadPoolExecutor(max_workers=6) as ex:
        for f in as_completed([ex.submit(fetch, h) for h in links[:6]]):
            try:
                item = f.result()
                if item['price']:
                    out.append(item)
            except Exception:
                pass
    return out


def search_ranfaifa(q):
    """ranfaifa.com (LnwShop): AJAX POST /search/box"""
    h = dict(UA)
    h.update({'X-Requested-With': 'XMLHttpRequest', 'Referer': 'https://www.ranfaifa.com/'})
    r = requests.post('https://www.ranfaifa.com/search/box', data={'q': q},
                      headers=h, timeout=TIMEOUT)
    r.encoding = 'utf-8'
    soup = BeautifulSoup(r.text, 'html.parser')
    out = []
    for a in soup.select('a.productItem'):
        nm = a.select_one('.product_name')
        pz = a.select_one('.product_price')
        price = parse_price(pz.get_text()) if pz else None
        if nm and price:
            out.append({'name': nm.get_text(strip=True), 'price': price, 'unit': '',
                        'source': 'ranfaifa.com', 'url': a.get('href', '')})
    return out


def search_obec(q):
    """บัญชีราคาวัสดุ+ค่าแรง สพฐ. ปี 2568 (extract จาก PDF ไว้ล่วงหน้า)"""
    if not os.path.exists(OBEC_FILE):
        return []
    with open(OBEC_FILE, encoding='utf-8') as f:
        data = json.load(f)
    qn = norm(q)
    words = [norm(w) for w in q.split() if norm(w)]
    out = []
    for it in data['items']:
        nn = norm(it['name'])
        if qn in nn or (words and all(w in nn for w in words)):
            name = it['name'] + (' [%s]' % it['code'] if it['code'] else '')
            if it.get('note'):
                name += ' (%s)' % it['note']
            out.append({'name': name, 'price': it['material'], 'unit': it['unit'],
                        'labor': it['labor'],
                        'source': 'ราคากลาง สพฐ.2568 (yotathai.com)',
                        'url': data['source_url']})
        if len(out) >= 30:
            break
    return [o for o in out if o['price'] is not None or o.get('labor') is not None]


def search_apelectric(q):
    """apelectricstore.com: WooCommerce Store API (ราคา 0 = ต้องสอบถามร้าน -> ข้าม)"""
    r = requests.get('https://apelectricstore.com/wp-json/wc/store/v1/products',
                     params={'search': q, 'per_page': 15}, headers=UA, timeout=TIMEOUT)
    out = []
    for p in r.json():
        minor = p['prices'].get('currency_minor_unit', 2)
        price = float(p['prices']['price'] or 0) / (10 ** minor)
        if price > 0:
            name = BeautifulSoup(p['name'], 'html.parser').get_text()
            out.append({'name': name, 'price': price, 'unit': '',
                        'source': 'apelectricstore.com', 'url': p['permalink']})
    return out


def search_custom(q, url):
    """แหล่งที่ user เพิ่มเอง: ลอง WooCommerce API -> JSON-LD -> CSS selector ทั่วไป"""
    base = url.rstrip('/')
    out = []
    # 1) WooCommerce Store API
    try:
        r = requests.get(base + '/wp-json/wc/store/v1/products',
                         params={'search': q, 'per_page': 10}, headers=UA, timeout=TIMEOUT)
        if r.ok and 'json' in r.headers.get('content-type', ''):
            for p in r.json():
                minor = p['prices'].get('currency_minor_unit', 2)
                price = float(p['prices']['price'] or 0) / (10 ** minor)
                if price > 0:
                    out.append({'name': BeautifulSoup(p['name'], 'html.parser').get_text(),
                                'price': price, 'unit': '',
                                'source': urllib.parse.urlparse(base).netloc,
                                'url': p['permalink']})
            if out:
                return out
    except Exception:
        pass
    # 2) หน้า search ทั่วไป (?s= แบบ WordPress) + product cards
    try:
        r = requests.get(base + '/', params={'s': q}, headers=UA, timeout=TIMEOUT)
        r.encoding = r.apparent_encoding or 'utf-8'
        soup = BeautifulSoup(r.text, 'html.parser')
        host = urllib.parse.urlparse(base).netloc
        # JSON-LD Product
        for sc in soup.find_all('script', type='application/ld+json'):
            try:
                data = json.loads(sc.string or '')
            except Exception:
                continue
            objs = data if isinstance(data, list) else [data]
            for o in objs:
                graphs = o.get('@graph', [o]) if isinstance(o, dict) else []
                for g in graphs:
                    if isinstance(g, dict) and g.get('@type') == 'Product':
                        offer = g.get('offers') or {}
                        if isinstance(offer, list):
                            offer = offer[0] if offer else {}
                        price = parse_price(str(offer.get('price', '')))
                        if price:
                            out.append({'name': g.get('name', ''), 'price': price, 'unit': '',
                                        'source': host, 'url': g.get('url', base)})
        if out:
            return out
        for card in soup.select('li.product, div.product, .product-item, .product-card'):
            t = card.select_one('.woocommerce-loop-product__title, h2, h3, .title, .name')
            pz = card.select_one('.price, .amount, [class*=price]')
            a = card.select_one('a[href]')
            price = parse_price(pz.get_text()) if pz else None
            if t and price:
                out.append({'name': t.get_text(strip=True), 'price': price, 'unit': '',
                            'source': host, 'url': a['href'] if a else base})
    except Exception:
        pass
    return out


SOURCES = {
    'sirichai': search_sirichai,
    'ranfaifa': search_ranfaifa,
    'obec': search_obec,
    'apelectric': search_apelectric,
}


@app.route('/api/search')
def api_search():
    q = request.args.get('q', '').strip()
    if not q:
        return jsonify({'results': [], 'errors': []})
    wanted = request.args.get('sources', ','.join(SOURCES)).split(',')
    custom_urls = [u for u in request.args.get('custom', '').split('|') if u.strip()]
    results, errors = [], []
    with ThreadPoolExecutor(max_workers=6) as ex:
        futs = {}
        for key in wanted:
            if key in SOURCES:
                futs[ex.submit(SOURCES[key], q)] = key
        for cu in custom_urls:
            futs[ex.submit(search_custom, q, cu.strip())] = cu
        for f in as_completed(futs):
            try:
                results.extend(f.result())
            except Exception as e:
                errors.append('%s: %s' % (futs[f], e))
    for r in results:
        r['fetched_at'] = today()
    results.sort(key=lambda x: (x['price'] is None, x['price'] or 0))
    return jsonify({'results': results, 'errors': errors})


# ---------------------------------------------------------------- library
def load_lib():
    if os.path.exists(LIB_FILE):
        with open(LIB_FILE, encoding='utf-8') as f:
            return json.load(f)
    return []


def save_lib(lib):
    with open(LIB_FILE, 'w', encoding='utf-8') as f:
        json.dump(lib, f, ensure_ascii=False, indent=1)


@app.route('/api/library', methods=['GET', 'POST', 'DELETE'])
def api_library():
    with _lib_lock:
        lib = load_lib()
        if request.method == 'GET':
            return jsonify(lib)
        if request.method == 'POST':
            item = request.get_json(force=True)
            item['id'] = (max((i['id'] for i in lib), default=0) + 1)
            item['saved_at'] = today()
            lib.append(item)
            save_lib(lib)
            return jsonify(item)
        # DELETE ?id=
        did = int(request.args.get('id', -1))
        lib = [i for i in lib if i['id'] != did]
        save_lib(lib)
        return jsonify({'ok': True})


@app.route('/api/library/update', methods=['POST'])
def api_library_update():
    patch = request.get_json(force=True)
    with _lib_lock:
        lib = load_lib()
        for i in lib:
            if i['id'] == patch['id']:
                i.update(patch)
        save_lib(lib)
    return jsonify({'ok': True})


@app.route('/api/library/export')
def api_library_export():
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment
    lib = load_lib()
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'Price Library'
    heads = ['#', 'รายการ', 'ราคาฐาน (บาท)', 'Markup %', 'ราคาใช้จริง (บาท)',
             'หน่วย', 'ปริมาณ', 'รวมเงิน (บาท)', 'ค่าแรง (บาท)',
             'แหล่งที่มา', 'URL', 'วันที่ดึงข้อมูล', 'วันที่บันทึก']
    ws.append(heads)
    for c in ws[1]:
        c.font = Font(bold=True, color='FFFFFF')
        c.fill = PatternFill('solid', fgColor='305496')
        c.alignment = Alignment(horizontal='center')
    grand = 0.0
    for n, it in enumerate(lib, 1):
        qty = it.get('qty', 1) or 0
        fp = it.get('final_price')
        total = round(fp * qty, 2) if fp is not None else None
        grand += total or 0
        ws.append([n, it.get('name'), it.get('price'), it.get('markup_pct'),
                   fp, it.get('unit'), qty, total, it.get('labor'),
                   it.get('source'), it.get('url'), it.get('fetched_at'), it.get('saved_at')])
    ws.append([None, 'รวมทั้งหมด', None, None, None, None, None, round(grand, 2)])
    last = ws[ws.max_row]
    last[1].font = Font(bold=True)
    last[7].font = Font(bold=True)
    widths = [5, 55, 14, 10, 16, 10, 10, 15, 12, 28, 45, 14, 14]
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[openpyxl.utils.get_column_letter(i)].width = w
    out = os.path.join(DATA_DIR, 'price_library_%s.xlsx' % today())
    wb.save(out)
    return send_file(out, as_attachment=True,
                     download_name=os.path.basename(out))


# ---------------------------------------------------------------- BOQ
def list_boq_files():
    return [f for f in os.listdir(BASE)
            if f.lower().endswith('.xlsx') and not f.startswith('~$')
            and 'price_library' not in f]


@app.route('/api/boq/files')
def api_boq_files():
    return jsonify(list_boq_files())


@app.route('/api/boq/items')
def api_boq_items():
    import openpyxl
    fname = request.args.get('file') or (list_boq_files() or [None])[0]
    if not fname:
        return jsonify({'error': 'ไม่พบไฟล์ .xlsx ในโฟลเดอร์'}), 404
    path = os.path.join(BASE, fname)
    wb = openpyxl.load_workbook(path, data_only=True)
    sheet = None
    for name in wb.sheetnames:
        if name.strip().lower() in ('detail', 'details'):
            sheet = wb[name]
            break
    if sheet is None:
        sheet = wb[wb.sheetnames[-1]]
    items, section = [], ''
    for r in range(1, sheet.max_row + 1):
        a = sheet.cell(r, 1).value
        b = sheet.cell(r, 2).value
        c = sheet.cell(r, 3).value
        d = sheet.cell(r, 4).value
        e = sheet.cell(r, 5).value
        g = sheet.cell(r, 7).value
        if a is not None and b and not isinstance(b, (int, float)):
            section = '%s. %s' % (a, b)
        if b and isinstance(c, (int, float)) and d:
            if str(b).strip().upper().startswith('SUM'):
                continue
            items.append({'row': r, 'section': section, 'name': str(b).strip(),
                          'qty': c, 'unit': str(d).strip(),
                          'material': e, 'labor': g})
    return jsonify({'file': fname, 'sheet': sheet.title, 'items': items})


@app.route('/api/boq/fill', methods=['POST'])
def api_boq_fill():
    import openpyxl
    body = request.get_json(force=True)
    fname = body['file']
    assigns = body['assignments']  # [{row, material, labor}]
    path = os.path.join(BASE, fname)
    wb = openpyxl.load_workbook(path)  # เก็บสูตรเดิมไว้
    sheet = None
    for name in wb.sheetnames:
        if name.strip().lower() in ('detail', 'details'):
            sheet = wb[name]
            break
    if sheet is None:
        sheet = wb[wb.sheetnames[-1]]
    n = 0
    for a in assigns:
        r = int(a['row'])
        if a.get('material') is not None:
            sheet.cell(r, 5).value = float(a['material'])   # E ค่าวัสดุ/หน่วย
            n += 1
        if a.get('labor') is not None:
            sheet.cell(r, 7).value = float(a['labor'])       # G ค่าแรง/หน่วย
    stem = re.sub(r'\.xlsx$', '', fname, flags=re.I)
    outname = '%s (filled %s).xlsx' % (stem, datetime.datetime.now().strftime('%Y-%m-%d %H%M'))
    wb.save(os.path.join(BASE, outname))
    return jsonify({'ok': True, 'filled': n, 'output': outname})


@app.route('/api/boq/download')
def api_boq_download():
    fname = request.args.get('file', '')
    if fname not in os.listdir(BASE):
        return jsonify({'error': 'not found'}), 404
    return send_file(os.path.join(BASE, fname), as_attachment=True, download_name=fname)


@app.route('/')
def index():
    return send_from_directory(BASE, 'index.html')


if __name__ == '__main__':
    # HOST=0.0.0.0 python3 server.py  -> เปิดให้เครื่องอื่นใน Wi-Fi วงเดียวกันเข้าได้
    host = os.environ.get('HOST', '127.0.0.1')
    print('BOQ Price Finder -> http://%s:5544' % ('127.0.0.1' if host == '127.0.0.1' else host))
    app.run(host=host, port=5544, debug=False)
