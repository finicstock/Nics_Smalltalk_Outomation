import requests
import os
from datetime import datetime, timedelta
import re

now_kst = datetime.utcnow() + timedelta(hours=9)
today_str = now_kst.strftime('%Y-%m-%d %H:%M')

TOKEN = os.environ['TELEGRAM_TOKEN']
CHAT_ID = os.environ['CHAT_ID']

def get_ai_memory_data():
    url = "https://www.dramexchange.com/"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        content = response.text
        
        msg = f"🤖 {today_str} AI/서버 메모리 시황\n"
        
        # 1. AI 서버용 핵심: DDR5 가격 (패턴 추출)
        # DDR5는 현재 AI PC와 서버의 표준입니다.
        ddr5_targets = ["DDR5 16Gb", "DDR5 32Gb"]
        msg += "\n[Next-Gen DRAM]"
        for target in ddr5_targets:
            pattern = re.compile(rf"{target}.*?(\d+\.\d+).*?(\+|\-)(\d+\.\d+)", re.IGNORECASE | re.DOTALL)
            match = pattern.search(content)
            if match:
                msg += f"\n⚡ {target}: ${match.group(1)} ({ '🔺' if match.group(2)=='+' else '⬇️' }{match.group(3)}%)"

        # 2. 기존 주력 품목
        msg += "\n\n[Mainstream DRAM]"
        ddr4_targets = ["DDR4 16Gb", "DDR4 8Gb"]
        for target in ddr4_targets:
            pattern = re.compile(rf"{target}.*?(\d+\.\d+).*?(\+|\-)(\d+\.\d+)", re.IGNORECASE | re.DOTALL)
            match = pattern.search(content)
            if match:
                msg += f"\n🔸 {target}: ${match.group(1)} ({ '🔺' if match.group(2)=='+' else '⬇️' }{match.group(3)}%)"

        # 3. DXI 지수 (전체 업황)
        dxi_pattern = re.compile(r"DXI.*?(\d+[\d,.]
