"""사이트별 검색/파싱 함수.

각 함수는 키워드로 검색해서 상품 리스트(dict)를 반환한다.
반환 dict 형식:
    {
        "site":  "musicforce" | "buzzbee" | "digimart",
        "id":    "<사이트 내 고유 ID>",      # 새 상품 판별 기준 (제목 아님)
        "title": "<상품 제목>",
        "price": "<가격 문자열>",            # 못 구하면 ""
        "url":   "<상세페이지 절대 URL>",
    }
"""
import re
import time
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    ),
    "Accept-Language": "ko,en;q=0.9,ja;q=0.8",
}
TIMEOUT = 20


def _get_soup(url):
    r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
    r.raise_for_status()
    return BeautifulSoup(r.text, "html.parser")


def _title_match(title, keyword):
    """제목에 키워드의 모든 단어가 (대소문자 무시) 들어있는지."""
    t = title.lower()
    return all(w.lower() in t for w in keyword.split())


# ----------------------------------------------------------------------
# 1) 뮤직포스 (Cafe24)
# ----------------------------------------------------------------------
def search_musicforce(keyword, title_filter=False):
    url = f"https://www.musicforce.co.kr/product/search.html?keyword={requests.utils.quote(keyword)}"
    soup = _get_soup(url)
    results = []
    for li in soup.select("ul.prdList > li"):
        a = li.select_one("a[href*=product_no]")
        if not a:
            continue
        m = re.search(r"product_no=(\d+)", a["href"])
        if not m:
            continue
        pid = m.group(1)

        name_el = li.select_one(".name")
        title = name_el.get_text(" ", strip=True) if name_el else ""
        title = re.sub(r"^상품명\s*:\s*", "", title).strip()

        block_text = li.get_text(" ", strip=True)
        pm = re.search(r"판매가\s*:\s*([\d,]+원)", block_text)
        if pm:
            price = pm.group(1)
        else:
            price_el = li.select_one(".price")
            price = price_el.get_text(" ", strip=True) if price_el else ""

        href = a["href"]
        full_url = href if href.startswith("http") else "https://www.musicforce.co.kr" + href

        if title_filter and title and not _title_match(title, keyword):
            continue
        results.append({"site": "musicforce", "id": pid, "title": title,
                        "price": price, "url": full_url})
    return results


# ----------------------------------------------------------------------
# 2) 버즈비 (고도몰 / NHN Commerce)
# ----------------------------------------------------------------------
def search_buzzbee(keyword, title_filter=False):
    url = f"https://www.buzzbee.co.kr/goods/goods_search.php?keyword={requests.utils.quote(keyword)}"
    soup = _get_soup(url)
    results = []
    for box in soup.select(".item_cont"):
        # 고유번호: data-goods-no 가 붙은 버튼에서 추출
        no_el = box.select_one("[data-goods-no]")
        a = box.select_one("a[href*='goods_view.php']")
        gid = None
        if no_el and no_el.get("data-goods-no"):
            gid = no_el["data-goods-no"].strip()
        elif a:
            m = re.search(r"goodsNo=(\d+)", a["href"])
            gid = m.group(1) if m else None
        if not gid:
            continue

        # 제목: data-goods-nm > img alt 순으로
        nm_el = box.select_one("[data-goods-nm]")
        if nm_el and nm_el.get("data-goods-nm"):
            title = nm_el["data-goods-nm"].strip()
        else:
            img = box.select_one("img[alt]")
            title = img["alt"].strip() if img else ""

        # 가격: data-goods-price
        price = ""
        pr_el = box.select_one("[data-goods-price]")
        if pr_el and pr_el.get("data-goods-price"):
            try:
                price = f"{int(float(pr_el['data-goods-price'])):,}원"
            except ValueError:
                price = pr_el["data-goods-price"]

        # 링크 절대화 (../goods/goods_view.php -> 절대경로)
        href = a["href"] if a else f"/goods/goods_view.php?goodsNo={gid}"
        href = href.replace("../", "/")
        full_url = href if href.startswith("http") else "https://www.buzzbee.co.kr" + href

        if title_filter and title and not _title_match(title, keyword):
            continue
        results.append({"site": "buzzbee", "id": gid, "title": title,
                        "price": price, "url": full_url})
    return results


# ----------------------------------------------------------------------
# 3) 디지마트 (일본) — 신착순 정렬
# ----------------------------------------------------------------------
def search_digimart(keyword, title_filter=False, polite_delay=1.5):
    time.sleep(polite_delay)  # 예의 있게
    url = ("https://www.digimart.net/search?"
           f"keyword={requests.utils.quote(keyword)}"
           "&sortKey=INITIAL_PUBLIC_DATE_DESC")  # 新着順
    soup = _get_soup(url)
    results = []
    for block in soup.select(".itemSearchListItem"):
        dsid = block.get("data-instrument-cd")
        a = block.select_one("p.ttl a[href]")
        if not dsid:
            # fallback: href에서 DS번호
            if a:
                m = re.search(r"/DS(\d+)/", a["href"])
                dsid = "DS" + m.group(1) if m else None
        if not dsid:
            continue

        title = a.get_text(" ", strip=True) if a else ""
        price_el = block.select_one(".price")
        price = price_el.get_text(" ", strip=True) if price_el else ""

        href = a["href"] if a else ""
        full_url = href if href.startswith("http") else "https://www.digimart.net" + href

        if title_filter and title and not _title_match(title, keyword):
            continue
        results.append({"site": "digimart", "id": dsid, "title": title,
                        "price": price, "url": full_url})
    return results


SCRAPERS = {
    "musicforce": search_musicforce,
    "buzzbee": search_buzzbee,
    "digimart": search_digimart,
}
