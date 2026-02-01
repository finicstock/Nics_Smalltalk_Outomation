import requests
import os
from datetime import datetime, timedelta
import re

# 한국 시간 설정
now_kst = datetime.utcnow() + timedelta(hours=9)
today_str = now_kst.strftime('%Y-%m-%d %H:%M')

TOKEN = os.environ['TELEGRAM_TOKEN']
CHAT_ID = os.environ['CHAT_ID']

def get_dram_spot_with_change():
    url = "https://www.dramexchange.com/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        content = response.text
        
        msg = f"💾 {today_str} DRAM 실시간 현물가\n"
        
        # 타겟 품목
        targets = ["DDR4 16Gb", "DDR4 8Gb", "DDR4 4Gb", "DDR3 4Gb"]
        found = False

        for target in targets:
            # 패턴: 품목명 ... 가격 ... 변동률(또는 변동값) 순서로 추출
            # HTML 구조상 가격 뒤에 오는 첫 번째 숫자(변동값)를 타겟팅합니다.
            pattern = re.compile(rf"{target}.*?(\d+\.\00-\d+).*?([+-]?\d+\.\d+)", re.IGNORECASE | re.DOTALL)
            # 좀 더 유연한 패턴: 가격을 먼저 찾고 그 뒤의 등락 표시(+/-)를 찾음
            pattern = re.compile(rf"{target}.*?(\d+\.\d+).*?(\+|\-)(\d+\.\d+)", re.IGNORECASE | re.DOTALL)
            
            match = pattern.search(content)
            if match:
                price = match.group(1)
                sign = match.group(2)
                change = match.group(3)
                
                emoji = "🔺" if sign == "+" else "⬇️"
                msg += f"\n🔸 {target}: ${price} ({emoji}{change}%)"
                found = True
            else:
                # 변동률 패턴이 안 잡힐 경우 가격만이라도 표시
                simple_pattern = re.compile(rf"{target}.*?(\d+\.\d+)", re.IGNORECASE | re.DOTALL)
                simple_match = simple_pattern.search(content)
                if simple_match:
                    msg += f"\n🔸 {target}: ${simple_match.group(1)} (변동 확인불가)"
                    found = True

        # DXI 지수 추출
        dxi_pattern = re.compile(r"DXI.*?(\d+[\d,.]*).*?(\+|\-)(\d+\.\d+)", re.IGNORECASE | re.DOTALL)
        dxi_match = dxi_pattern.search(content)
        if dxi_match:
            dxi_val = dxi_match.group(1)
            dxi_sign = dxi_match.group(2)
            dxi_change = dxi_match.group(3)
            dxi_emoji = "🔺" if dxi_sign == "+" else "⬇️"
            msg += f"\n\n📈 DXI Index: {dxi_val} ({dxi_emoji}{dxi_change}%)"
            found = True

        if not found:
            return "⚠️ 데이터 매칭 실패 (구조 확인 필요)"
            
        msg += "\n\n#DRAM #현물가 #반도체공부"
        return msg

    except Exception as e:
        return f"❌ 연결 오류: {str(e)}"

def send_to_channel(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": text})

if __name__ == "__main__":
    result = get_dram_spot_with_change()
    send_to_channel(result)
