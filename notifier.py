"""알림 발송 (텔레그램).

토큰/chat_id는 환경변수에서만 읽는다 (코드에 하드코딩 금지).
로컬 실행 시 .env 파일이 있으면 자동으로 불러온다 (GitHub Actions에서는
Secrets가 환경변수로 직접 주입되므로 .env가 없어도 동작함).
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")


def send_telegram(text):
    """텔레그램으로 메시지 전송. 설정이 없으면 조용히 스킵하고 False 반환."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("[notifier] TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID 가 설정되지 않아 전송을 건너뜁니다.")
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }
    r = requests.post(url, data=payload, timeout=15)
    if r.status_code != 200:
        print(f"[notifier] 텔레그램 전송 실패: {r.status_code} {r.text}")
        return False
    return True


def format_new_item_message(site_label, item):
    """새 상품 1건을 텔레그램 메시지 텍스트로 포맷."""
    price = f"\n💰 {item['price']}" if item.get("price") else ""
    return (
        f"🆕 <b>[{site_label}] 새 상품 발견</b>\n"
        f"📦 {item['title']}{price}\n"
        f"🔗 {item['url']}"
    )
