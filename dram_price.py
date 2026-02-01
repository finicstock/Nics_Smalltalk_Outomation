import requests
import os
from datetime import datetime, timedelta
import re

now_kst = datetime.utcnow() + timedelta(hours=9)
today_str = now_kst.strftime('%Y-%m-%d %H:%M')

TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')

def get_ai_memory_data():
    url = "https://www.dramexchange.com/"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        content = response.text
        
        msg = f"🤖 {today_str} AI/서버 메모리 시황\n"
        found_data = False

        # 1. 개별 품목 타겟팅 (정밀 매칭)
        targets = [
            ("DDR5 16Gb", "DDR5 16Gb.*?\d+/\d+"),
            ("DDR4 16Gb", "DDR4 16Gb.*?3200"),
            ("DDR4 8Gb", "DDR4 8Gb.*?3200")
        ]
        
        for name, keyword in targets:
            pattern = re.compile(rf"{keyword}.*?(\d+\.\d+).*?(\d+\.\d+).*?(\d+\.\d+).*?(\d+\.\d+).*?(\d+\.\d+).*?([+-]?\d+\.\d+)\s*%", re.IGNORECASE | re.DOTALL)
            match = pattern.search(content)
            
            if match:
                price = match.group(5)  # Session Average
                change = match.group(6) # Session Change
                emoji = "🔺" if float(change) > 0 else ("⬇️" if float(change) < 0 else "🔹")
                msg += f"\n🔸 {name}: ${price} ({emoji}{change}%)"
                found_data = True

        # 2. DXI 지수 추가 추출
        # DXI는 보통 숫자가 크고(예: 25,000점) 뒤에 등락률이 붙습니다.
        dxi_pattern = re.compile(r"DXI.*?(\d{1,3}(?:,\d{3})*(?:\.\d+)?).*?([+-]?\d+\.\d+)\s*%", re.IGNORECASE | re.DOTALL)
        dxi_match = dxi_pattern.search(content)
        
        if dxi_match:
            dxi_val = dxi_match.group(1)
            dxi_change = dxi_match.group(2)
            dxi_emoji = "🔺" if float(dxi_change) > 0 else ("⬇️" if float(dxi_change)
