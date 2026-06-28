"""감시 설정.

사이트 화면에서 카테고리/신품여부/가격/정렬(최신순) 필터를 직접 건 뒤
주소창 URL을 그대로 복사해서 넣는다. 한 사이트당 URL 1개 = 감시 대상 1개.
(여러 키워드를 따로 돌리는 대신, 이미 필터링된 검색결과 1페이지를 그대로 본다.
 30분마다 도는 봇이라 신상품이 한 페이지 분량보다 많이 한 번에 올라올 일은
 사실상 없어서 페이지네이션은 필요 없다.)
"""

SITE_SEARCH_URLS = {
    # Fender Custom Shop 전용 카테고리라 키워드 불필요. sort_method=5 = 최신순.
    "musicforce": "https://musicforce.co.kr/product/list.html?cate_no=1240&sort_method=5",

    # cate_no=1246 = MBS(Masterbuilt) 전용 카테고리. sort_method=5 = 최신순.
    "musicforce_mbs": "https://musicforce.co.kr/product/list.html?cate_no=1246&sort_method=5",

    # cateCd=001001 = 일렉기타 카테고리, sort=date = 최신순.
    "buzzbee": (
        "https://www.buzzbee.co.kr/goods/goods_search.php?cateCd=001001"
        "&reSearchKeyword%5B%5D=fender+customshop&reSearchKey%5B%5D=all"
        "&sort=date&pageNum=30&key=goodsNm&keyword="
        "&goodsPrice%5B%5D=0&goodsPrice%5B%5D=20000000"
    ),

    # category12Id=101 = エレキギター(일렉기타) 전체, productTypes=NEW = 신품만,
    # priceFrom=500000 = 50만원 이상(의도적 필터), sortKey = 신착순.
    "digimart": (
        "https://www.digimart.net/search?category12Id=101"
        "&keywordAnd=fender+custom+shop&priceFrom=500000&productTypes=NEW"
        "&sortKey=INITIAL_PUBLIC_DATE_DESC&readCount=50"
    ),

    # Shopify JSON API — Fender Custom Shop 컬렉션, 최신순.
    "themusiczoo": (
        "https://www.themusiczoo.com/collections/fender-custom-shop/products.json"
        "?sort_by=created-descending&limit=50"
    ),
}

# 제목에 아래 단어가 전부 포함된 경우만 통과시키는 오검색 방지 필터.
# 카테고리/키워드만으로 이미 충분히 좁혀지는 사이트는 None으로 둔다.
TITLE_FILTER_WORDS = {
    "musicforce": None,
    "musicforce_mbs": None,
    "buzzbee": None,
    # 디지마트는 category12Id=101(일렉기타 전체)이라 Suhr 등 다른 브랜드가 섞여서 필요.
    "digimart": ["fender", "custom", "shop"],
    # The Music Zoo는 Fender Custom Shop 전용 컬렉션이라 필터 불필요.
    "themusiczoo": None,
}

SEEN_FILE = "seen.json"
DIGIMART_REQUEST_DELAY = 1.5
