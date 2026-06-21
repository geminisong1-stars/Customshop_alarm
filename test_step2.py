"""2단계 검증:
  1) 첫 실행 -> 신규 알림 없이 조용히 seen.json 기록되는지 확인
  2) 같은 검색을 다시 실행 -> 진짜로 새 상품이 없으면 신규 0건인지 확인
  3) seen.json에서 임의로 ID 하나를 지워 '새 상품이 생긴 상황'을 시뮬레이션 ->
     다음 실행에서 그 ID가 정확히 신규로 잡히는지 확인
"""
import os
import json

from config import KEYWORDS, TITLE_FILTER, SEEN_FILE
from core import collect_site_items, detect_new_items
from seen_store import load_seen, save_seen

SITES = ["musicforce", "buzzbee", "digimart"]

# 깨끗한 상태에서 테스트하기 위해 기존 seen.json 제거
if os.path.exists(SEEN_FILE):
    os.remove(SEEN_FILE)

print("=" * 70)
print("[1차 실행] 첫 실행 -> 조용히 기록만 되어야 함 (신규 알림 0건)")
print("=" * 70)

seen = load_seen(SEEN_FILE)
all_items_round1 = {}
for site in SITES:
    items = collect_site_items(site, KEYWORDS, title_filter=TITLE_FILTER)
    all_items_round1[site] = items
    new_items, is_first = detect_new_items(site, items, seen)
    print(f"[{site}] 검색결과 {len(items)}건 | 첫실행={is_first} | 신규알림={len(new_items)}건 | seen기록={len(seen[site])}개")
    assert is_first is True
    assert len(new_items) == 0, "첫 실행인데 신규 알림이 발생함 (버그)"
save_seen(SEEN_FILE, seen)
print("-> seen.json 저장 완료\n")

print("=" * 70)
print("[2차 실행] 변동 없음 -> 신규 0건이어야 정상")
print("=" * 70)
seen = load_seen(SEEN_FILE)
for site in SITES:
    items = collect_site_items(site, KEYWORDS, title_filter=TITLE_FILTER)
    new_items, is_first = detect_new_items(site, items, seen)
    print(f"[{site}] 첫실행={is_first} | 신규알림={len(new_items)}건")
    assert is_first is False
save_seen(SEEN_FILE, seen)

print("\n" + "=" * 70)
print("[시뮬레이션] seen.json에서 사이트별 ID 1개씩 임의로 제거 -> '새 상품'으로 위장")
print("=" * 70)
seen = load_seen(SEEN_FILE)
removed = {}
for site in SITES:
    if seen[site]:
        removed_id = seen[site].pop(0)
        removed[site] = removed_id
        print(f"[{site}] seen에서 강제로 제거: {removed_id} (다음 실행에 '신규'로 떠야 정상)")
save_seen(SEEN_FILE, seen)

print("\n" + "=" * 70)
print("[3차 실행] 위에서 제거한 ID가 정확히 신규로 잡히는지 확인")
print("=" * 70)
seen = load_seen(SEEN_FILE)
ok = True
for site in SITES:
    items = collect_site_items(site, KEYWORDS, title_filter=TITLE_FILTER)
    new_items, is_first = detect_new_items(site, items, seen)
    new_ids = {it["id"] for it in new_items}
    expect = removed.get(site)
    print(f"[{site}] 신규알림={len(new_items)}건 | ids={sorted(new_ids)} | 기대값={expect}")
    for it in new_items:
        print(f"    -> {it['id']} | {it['price']:>12} | {it['title'][:50]}")
    if expect is not None:
        if expect not in new_ids:
            ok = False
            print(f"    !! FAIL: {expect} 가 신규로 잡히지 않음")
save_seen(SEEN_FILE, seen)

print("\n" + "=" * 70)
print("RESULT:", "PASS ✅" if ok else "FAIL ❌")
print("=" * 70)
