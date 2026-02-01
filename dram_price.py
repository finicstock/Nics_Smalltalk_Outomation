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
        response = requests.get(url, headers=headers, timeout=20)
        content = response.text
        
        msg = f"🤖 {today_str} AI/서버 메모리 시황\n"
        found_data = False

        targets = [
            ("DDR5 16Gb", r"DDR5 16Gb.*?4800/5600"),
            ("DDR4 16Gb", r"DDR4 16Gb.*?3200"),
            ("DDR4 8Gb", r"DDR4 8Gb.*?3200")
        ]
        
        for name, keyword in targets:
            # 품목이 포함된 행(tr) 전체를 가져옴
            pattern = re.compile(rf"{keyword}.*?</tr>", re.IGNORECASE | re.DOTALL)
            match = pattern.search(content)
            
            if match:
                row_html = match.group(0)
                # 1. 숫자들만 모두 추출 (가격, 변동률 등)
                nums = re.findall(r"(\d+\.\d+)", row_html)
                # 2. 해당 행에서 변동률 바로 앞의 부호(+/-)를 정밀 조준
                # % 기호 바로 앞에 있는 부호를 찾습니다.
                sign_match = re.search(r"([+-])\s*\d+\.\d+\s*%", row_html)
                sign = sign_match.group(1) if sign_match else "+" # 부호 없으면 기본 +

                if len(nums) >= 5:
                    # 표 구조상 뒤에서 2번째가 Average($), 마지막이 Change(%)
                    price = nums[-2] 
                    change_raw = nums[-1]
                    
                    # 0.00일 때 보합 처리
                    if float(change_raw) == 0.0:
                        emoji, final_sign = "➖", ""
                    elif sign == "-":
                        emoji, final_sign = "⬇️", "-"
                    else:
                        emoji, final_sign = "🔺", "+"
                    
                    msg += f"\n🔸 {name}: ${price} ({emoji}{final_sign}{change_raw}%)"
                    found_data = True

        # DXI Index (별도 영역)
        dxi_pattern = re.compile(r"DXI.*?(\d{1,3}(?:,\d{3})*(?:\.\d+)?).*?([+-])?(\d+\.\d+)\s*%", re.IGNORECASE | re.DOTALL)
        dxi_match = dxi_pattern.search(content)
        if dxi_match:
            val, d_sign, d_change = dxi_match.groups()
            d_sign = d_sign if d_sign else "+"
            if float(d_change) == 0.0:
                d_emoji, d_final_sign = "➖", ""
            elif d_sign == "-":
                d_emoji, d_final_sign = "⬇️", "-"
            else:
                d_emoji, d_final_sign = "🔺", "+"
            msg += f"\n\n📈 DXI Index: {val} ({d_emoji}{d_final_sign}{d_change}%)"
            found_data = True

        msg += "\n\n#DRAM #HBM #반도체시황"
        return msg

    except Exception as e:
        return f"❌ 실행 에러: {str(e)}"

def send_to_channel(text):
    if not TOKEN or not CHAT_ID: return
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": text})

if __name__ == "__main__":
    result = get_ai_memory_data()
    send_to_channel(result)
