"""감시 설정."""

# 감시할 키워드/브랜드 (검색어로 그대로 사용됨)
# 주의: 뮤직포스(Cafe24)는 띄어쓰기를 그대로 매칭하므로 "fender customshop"처럼
#       붙여 쓰면 0건이 나올 수 있다. 버즈비/디지마트는 띄어쓰기 유무 영향이 없으니
#       항상 띄어쓰기를 살린 형태("fender custom shop")로 적는 것을 권장.
KEYWORDS = [
    "fender custom shop",
]

# 제목에 키워드 단어가 모두 포함된 경우만 통과시킬지 여부 (오검색 방지용 추가 필터)
TITLE_FILTER = False

# 상태 저장 파일 경로
SEEN_FILE = "seen.json"

# 디지마트는 큰 사이트라 요청 사이에 텀을 둠 (초)
DIGIMART_REQUEST_DELAY = 1.5
