"""3단계 검증: 텔레그램 실제 발송 테스트."""
from notifier import send_telegram, format_new_item_message

# 1) 단순 텍스트 발송 테스트
ok1 = send_telegram("✅ 기타악기 알림봇 연결 테스트입니다. 이 메시지가 보이면 설정 성공!")
print("단순 메시지 발송 결과:", ok1)

# 2) 실제 알림 형식 미리보기 테스트 (가짜 상품 데이터)
fake_item = {
    "title": "Fender Custom Shop 1965 Stratocaster Relic (테스트용 가짜 데이터)",
    "price": "7,199,000원",
    "url": "https://example.com/test-product",
    "keyword": "fender custom shop",
}
msg = format_new_item_message("뮤직포스", fake_item)
ok2 = send_telegram(msg)
print("신규상품 알림형식 발송 결과:", ok2)
