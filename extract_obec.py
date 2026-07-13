#!/usr/bin/env python3
"""Extract บัญชีราคาค่าวัสดุก่อสร้างและค่าแรงงาน ปีงบ 2568 (สพฐ.) PDF -> data/obec2568.json"""
import json
import os
import re
import sys

import pdfplumber

PDF = sys.argv[1] if len(sys.argv) > 1 else 'obec2568.pdf'
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'obec2568.json')

CID = re.compile(r'\(cid:\d+\)')


def clean_text(s):
    if not s:
        return ''
    s = CID.sub('', s)
    s = s.replace('\n', ' ')
    return re.sub(r'\s+', ' ', s).strip()


def clean_num(s):
    """'1 ,157' -> 1157.0 ; '1 04' -> 104.0 ; '-' -> None"""
    if not s:
        return None
    s = CID.sub('', s).replace(',', '').replace(' ', '').strip()
    if s in ('', '-', '.'):
        return None
    try:
        return float(s)
    except ValueError:
        return None


def main():
    items = []
    with pdfplumber.open(PDF) as pdf:
        for pageno, page in enumerate(pdf.pages, 1):
            tbl = page.extract_table()
            if not tbl:
                continue
            for row in tbl:
                if not row or len(row) < 5:
                    continue
                code = clean_text(row[0])
                name = clean_text(row[1])
                unit = clean_text(row[2])
                mat = clean_num(row[3])
                lab = clean_num(row[4])
                note = clean_text(row[5]) if len(row) > 5 else ''
                if not name or code in ('CODE',):
                    continue
                # keep only coded item rows or rows with a price
                if not re.match(r'^[A-Z]\d{3,}', code) and mat is None and lab is None:
                    continue
                items.append({
                    'code': code,
                    'name': name,
                    'unit': unit,
                    'material': mat,
                    'labor': lab,
                    'note': note,
                    'page': pageno,
                })
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump({'source': 'บัญชีราคาค่าวัสดุก่อสร้างและค่าแรงงาน ปีงบประมาณ 2568 (กองออกแบบ สพฐ.)',
                   'source_url': 'https://www.yotathai.com/yotanews/obec2568',
                   'items': items}, f, ensure_ascii=False)
    print('extracted', len(items), 'items ->', OUT)


if __name__ == '__main__':
    main()
