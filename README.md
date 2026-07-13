# BOQ Price Finder 🔍

ค้นราคาวัสดุจาก 4 แหล่ง → เลือกเก็บเข้า Price Library → Export Excel / เติมราคาเข้าไฟล์ BOQ

แหล่งข้อมูล: sirichaielectric.com, ranfaifa.com, ราคากลาง สพฐ.2568 (yotathai), apelectricstore.com + เพิ่ม URL เองได้

## วิธีใช้ (ครั้งแรก)

ต้องมี **Python 3** ในเครื่อง ([ดาวน์โหลด](https://www.python.org/downloads/) — ตอนติดตั้งบน Windows ติ๊ก "Add Python to PATH")

- **Mac**: ดับเบิลคลิก `run.command` (ครั้งแรกถ้าเปิดไม่ได้ ให้คลิกขวา → Open)
- **Windows**: ดับเบิลคลิก `run.bat`

หรือรันเองใน terminal:

```
pip3 install -r requirements.txt
python3 server.py
```

แล้วเปิด http://127.0.0.1:5544

หน้า Flask นี้จะดึงเว็บสดตอนกดค้นหา:

- `http://127.0.0.1:5544/` = หน้าเต็ม ใช้ Flask API สด + Library/BOQ
- `http://127.0.0.1:5544/single` = หน้าไฟล์เดียว แต่ถ้าเปิดผ่าน Flask จะเรียก `/api/search` เพื่อดึงเว็บสด

ถ้าต้องการใช้ Streamlit แบบดึงเว็บสดด้วย Python โดยตรง:

```
streamlit run streamlit_app.py
```

แล้วกด **Live Search** ในหน้า Streamlit

## ขั้นตอนการใช้งาน

1. **ค้นหาราคา** — พิมพ์ชื่อสินค้า (เช่น สายไฟ THW, ท่อ EMT, โคมไฟฉุกเฉิน) ระบบแสดงชื่อ/ราคา/หน่วย/แหล่ง/URL/วันที่ดึง ตั้ง markup % ได้ → กด **Save**
2. **Price Library** — รายการราคาที่เลือกใช้จริง แก้ markup/ลบได้ → **Export เป็น Excel**
3. **เติมราคาเข้า BOQ** — วางไฟล์ BOQ (.xlsx ที่มีชีท "Detail") ไว้ในโฟลเดอร์นี้ → เลือกราคาจาก Library ให้แต่ละรายการ (มีปุ่มจับคู่อัตโนมัติ) → ระบบเติมค่าวัสดุ (คอลัมน์ E) และค่าแรง (คอลัมน์ G) แล้วบันทึกเป็นไฟล์ใหม่ "(filled วันที่).xlsx" — ไฟล์เดิมไม่ถูกแก้

## แชร์ให้เครื่องอื่นใน Wi-Fi วงเดียวกัน (ไม่บังคับ)

```
HOST=0.0.0.0 python3 server.py        # Mac
set HOST=0.0.0.0 && python server.py  # Windows
```

แล้วให้อีกเครื่องเปิด `http://<IP เครื่องคุณ>:5544`

## หมายเหตุ

- `data/obec2568.json` = ราคากลาง สพฐ. ปีงบ 2568 (2,061 รายการ) แปลงจาก PDF ไว้แล้ว ถ้าปีใหม่ออกให้รัน `extract_obec.py <ไฟล์.pdf>` ใหม่ (ต้อง `pip3 install pdfplumber`)
- ราคาที่ดึงมาเป็นราคาหน้าเว็บ ณ วันที่ค้น ควรตรวจสอบก่อนใช้เสนอราคาจริง
