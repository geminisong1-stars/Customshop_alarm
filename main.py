"""검색 -> 신상품 감지 -> 텔레그램 알림 -> 상태(seen.json) 저장."""
import os

from config import SEEN_FILE
from core import collect_site_items, detect_new_items
from seen_store import load_seen, save_seen
from notifier import send_telegram, format_new_item_message

SITE_LABELS = {
    "musicforce": "뮤직포스",
    "musicforce_mbs": "뮤직포스 MBS",
    "buzzbee": "버즈비",
    "digimart": "디지마트",
    "themusiczoo": "더뮤직주",
    "wildwest": "와일드웨스트",
}
SITES = list(SITE_LABELS.keys())


def send_test_alert():
    """TEST_ALERT 환경변수가 켜진 경우: 실제 감시 대신 테스트 메시지 1건만 보낸다.

    텔레그램 봇 토큰/chat_id 연동이 정상인지 확인하는 용도.
    seen.json은 건드리지 않는다.
    """
    sample = {
        "title": "테스트 알림 — 이 메시지가 보이면 텔레그램 연동이 정상입니다 🎸",
        "price": "TEST",
        "url": "https://github.com/geminisong1-stars/Customshop_alarm",
    }
    msg = format_new_item_message("알림 테스트", sample)
    ok = send_telegram(msg)
    print("테스트 알림 전송 성공" if ok else "테스트 알림 전송 실패")
    return ok


def main():
    if os.environ.get("TEST_ALERT"):
        send_test_alert()
        return

    seen = load_seen(SEEN_FILE)
    total_new = 0

    for site in SITES:
        label = SITE_LABELS[site]
        try:
            items = collect_site_items(site)
        except Exception as e:
            print(f"[{site}] 검색 중 오류 발생, 이번 회차는 건너뜀: {e!r}")
            continue

        new_items, is_first_run = detect_new_items(site, items, seen)

        if is_first_run:
            print(f"[{site}] 첫 실행 -> {len(items)}건 조용히 기록 (알림 없음)")
            continue

        print(f"[{site}] 검색 {len(items)}건 / 신규 {len(new_items)}건")
        for item in new_items:
            msg = format_new_item_message(label, item)
            ok = send_telegram(msg)
            status = "전송 성공" if ok else "전송 실패"
            print(f"  -> id={item['id']} | {item['title'][:40]} | {status}")
            total_new += 1

    save_seen(SEEN_FILE, seen)
    print(f"\n완료. 총 신규 알림 {total_new}건. {SEEN_FILE} 저장됨.")


if __name__ == "__main__":
    main()
