import yfinance as yf
import requests
import os
from datetime import datetime

# 깃허브 Secrets에서 가져오기
TOKEN = os.environ['TELEGRAM_TOKEN']
CHAT_ID = os.environ['CHAT_ID']

def get_market_data():
    # 기호 설정: 미국10년금리, 달러지수, S&P500, 나스닥
    tickers = {
        "💵 달러지수": "DX-Y.NYB", 
        "📈 미 10년물 금리": "^TNX", 
        "🏛 S&P 500": "^GSPC", 
        "🚀 나스닥": "^IXIC"
    }
    
    today_str = datetime.now().strftime('%Y-%m-%d')
    results = f"📅 {today_str} 시장 브리핑\n"
    
    for name, sym in tickers.items():
        try:
            t = yf.Ticker(sym)
            # 최근 2일치 데이터를 가져와서 전일 대비 계산
            hist = t.history(period="2d")
            
            if len(hist) < 2:
                # 데이터가 부족할 경우 현재가만 표시
                price = t.fast_info.last_price
                results += f"\n{name}: {price:.2f}"
                continue

            current_price = hist['Close'].iloc[-1]
            prev_price = hist['Close'].iloc[-2]
            change = current_price - prev_price
            change_pct = (change / prev_price) * 100
            
            # 상승/하락 이모지 결정
            emoji = "🔺" if change > 0 else "🔻"
            
            results += f"\n{name}: {current_price:.2f} ({emoji} {abs(change_pct):.2f}%)"
        except Exception as e:
            results += f"\n{name}: 데이터 오류"
            
    results += "\n\n#미국증시 #자동업데이트"
    return results

def send_to_channel(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": text})

if __name__ == "__main__":
    market_info = get_market_data()
    send_to_channel(market_info)
