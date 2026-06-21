"""사이트별 파싱 함수.

각 사이트는 config.py의 SITE_SEARCH_URLS에 이미 카테고리/신품/가격/정렬
필터가 적용된 고정 URL을 그대로 요청해서 결과를 파싱한다.

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


def _title_match(title, words):
    """제목에 words의 모든 단어가 (대소문자 무시) 들어있는지."""
    t = title.lower()
    return all(w.lower() in t for w in words)


# ----------------------------------------------------------------------
# 1) 뮤직포스 (Cafe24) — Fender Custom Shop 전용 카테고리
# ----------------------------------------------------------------------
def search_musicforce(url, title_words=None):
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
        full_url = href if href.startswith("http") else "https://musicforce.co.kr" + href

        if title_words and title and not _title_match(title, title_words):
            continue
        results.append({"site": "musicforce", "id": pid, "title": title,
                        "price": price, "url": full_url})
    return results


# ----------------------------------------------------------------------
# 2) 버즈비 (고도몰 / NHN Commerce) — 일렉기타 카테고리 + 키워드
# ----------------------------------------------------------------------
def search_buzzbee(url, title_words=None):
    soup = _get_soup(url)
    results = []
    for box in soup.select(".item_cont"):
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

        nm_el = box.select_one("[data-goods-nm]")
        if nm_el and nm_el.get("data-goods-nm"):
            title = nm_el["data-goods-nm"].strip()
        else:
            img = box.select_one("img[alt]")
            title = img["alt"].strip() if img else ""

        price = ""
        pr_el = box.select_one("[data-goods-price]")
        if pr_el and pr_el.get("data-goods-price"):
            try:
                price = f"{int(float(pr_el['data-goods-price'])):,}원"
            except ValueError:
                price = pr_el["data-goods-price"]

        href = a["href"] if a else f"/goods/goods_view.php?goodsNo={gid}"
        href = href.replace("../", "/")
        full_url = href if href.startswith("http") else "https://www.buzzbee.co.kr" + href

        if title_words and title and not _title_match(title, title_words):
            continue
        results.append({"site": "buzzbee", "id": gid, "title": title,
                        "price": price, "url": full_url})
    return results


# ----------------------------------------------------------------------
# 3) 디지마트 (일본) — 일렉기타 카테고리 + 신품 + 가격 + 키워드
# ----------------------------------------------------------------------
def search_digimart(url, title_words=None, polite_delay=1.5):
    time.sleep(polite_delay)  # 예의 있게
    soup = _get_soup(url)
    results = []
    for block in soup.select(".itemSearchListItem"):
        dsid = block.get("data-instrument-cd")
        a = block.select_one("p.ttl a[href]")
        if not dsid:
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

        if title_words and title and not _title_match(title, title_words):
            continue
        results.append({"site": "digimart", "id": dsid, "title": title,
                        "price": price, "url": full_url})
    return results


SCRAPERS = {
    "musicforce": search_musicforce,
    "buzzbee": search_buzzbee,
    "digimart": search_digimart,
}
