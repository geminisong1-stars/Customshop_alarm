"""1단계 검증: 세 사이트 x 두 키워드 결과 출력."""
from scrapers import SCRAPERS

KEYWORDS = ["PRS", "Stratocaster"]

for kw in KEYWORDS:
    print("\n" + "#" * 72)
    print(f"#  키워드: {kw}")
    print("#" * 72)
    for site, fn in SCRAPERS.items():
        try:
            items = fn(kw)
            print(f"\n[{site}] {len(items)}개")
            for it in items[:3]:
                print(f"  - id={it['id']:>10} | {it['price']:>12} | {it['title'][:55]}")
                print(f"      {it['url']}")
            if len(items) > 3:
                print(f"  ... 외 {len(items)-3}개")
        except Exception as e:
            print(f"\n[{site}] ERROR: {e!r}")
