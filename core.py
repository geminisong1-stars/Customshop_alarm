"""검색 결과 수집 + 신상품 감지 핵심 로직."""
from config import SITE_SEARCH_URLS, TITLE_FILTER_WORDS
from scrapers import SCRAPERS


def collect_site_items(site):
    """한 사이트의 고정 필터 URL을 조회해서 id 기준 중복 제거한 상품 목록을 반환."""
    fn = SCRAPERS[site]
    url = SITE_SEARCH_URLS[site]
    words = TITLE_FILTER_WORDS.get(site)

    by_id = {}
    for item in fn(url, title_words=words):
        by_id.setdefault(item["id"], item)
    return list(by_id.values())


def detect_new_items(site, items, seen):
    """
    site:  사이트 이름 (seen dict의 키)
    items: collect_site_items() 결과 (현재 검색된 전체 상품)
    seen:  load_seen() 으로 불러온 전체 상태 dict (이 함수가 in-place로 갱신함)

    반환: (new_items, is_first_run)
        - is_first_run=True 이면 이 사이트는 처음 감시하는 것이므로
          new_items는 항상 빈 리스트(알림 없이 조용히 기록만).
    """
    is_first_run = site not in seen
    seen_ids = set(seen.get(site, []))
    current_ids = {it["id"] for it in items}

    if is_first_run:
        new_items = []
    else:
        new_items = [it for it in items if it["id"] not in seen_ids]

    # seen 갱신: 기존에 본 것 + 이번에 본 것 합집합 (사라진 상품 ID도 유지 -> 나중에 재등록돼도 중복알림 방지)
    seen[site] = sorted(seen_ids | current_ids)

    return new_items, is_first_run
