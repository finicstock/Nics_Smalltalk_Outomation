import requests
import os
from datetime import datetime, timedelta
import re

# 한국 시간 설정
now_kst = datetime.utcnow() + timedelta(hours=9)
today_str = now_kst.strftime('%Y-%m-%d %H:%M')

TOKEN = os.environ['TELEGRAM_TOKEN']
CHAT_ID = os.environ['CHAT_ID']

def get_dram_spot_real():
    # 데이터 소스: 여러 반도체 가격 공시 사이트 중 크롤링이 허용된 곳 활용
    url = "https://www.dramexchange.com/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        content = response.text
        
        # HTML 태그를 무시하고 텍스트에서 패턴 추출 (정규표현식 사용)
        # DDR4 8Gb (1G*8) 2666 Mbps 같은 패턴 뒤의 숫자를 찾습니다.
        msg = f"💾 {today_str} DRAM 실시간 현물가\n"
        
        # 주요 타겟 품목 리스트
        targets = ["DDR4 16Gb", "DDR4 8Gb", "DDR4 4Gb", "DDR3 4Gb"]
        found = False

        for target in targets:
            # 패턴: 품목명 뒤에 나오는 가격(숫자.숫자) 추출
            pattern = re.compile(rf"{target}.*?(\d+\.\d+)", re.IGNORECASE | re.DOTALL)
            match = pattern.search(content)
            if match:
                price = match.group(1)
                msg += f"\n🔸 {target}: ${price}"
                found = True

        # DXI 지수 추가 추출
        dxi_pattern = re.compile(r"DXI.*?(\d+[\d,.]*)", re.IGNORECASE | re.DOTALL)
        dxi_match = dxi_pattern.search(content)
        if dxi_match:
            msg += f"\n\n📈 DXI Index: {dxi_match.group(1)}"
            found = True

        if not found:
            return "⚠️ 현재 사이트 점검 중이거나 구조가 변경되었습니다. (데이터 매칭 실패)"
            
        return msg

    except Exception as e:
        return f"❌ 연결 오류: {str(e)}"

def send_to_channel(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": text})

if __name__ == "__main__":
    result = get_dram_spot_real()
    send_to_channel(result)
