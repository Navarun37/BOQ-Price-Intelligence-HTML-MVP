#!/bin/bash
# BOQ Price Finder — ดับเบิลคลิกเพื่อรัน (macOS)
cd "$(dirname "$0")"
python3 -m pip install -q -r requirements.txt
( sleep 2 && open http://127.0.0.1:5544 ) &
python3 server.py
