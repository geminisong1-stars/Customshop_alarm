# 배포 가이드 (비개발자용)

이 문서대로만 따라 하면 서버 없이, 무료로, 30분마다 자동으로 악기 신상품을 텔레그램으로 받을 수 있습니다.

---

## 0. 준비물 체크리스트

- [ ] GitHub 계정 (이미 있음)
- [ ] 텔레그램 봇 토큰 (`TELEGRAM_BOT_TOKEN`)
- [ ] 텔레그램 chat_id (`TELEGRAM_CHAT_ID`)

봇 토큰/chat_id가 아직 없다면 아래 "참고: 텔레그램 봇 만들기"를 먼저 하세요.

---

## 1. GitHub 레포 만들기

1. https://github.com 로그인
2. 오른쪽 위 **+** 버튼 → **New repository** 클릭
3. Repository name: `guitar-watcher` (원하는 이름으로 해도 됨)
4. **Public**으로 두거나 **Private** 선택 — 둘 다 무방 (Private이어도 Actions 무료로 사용 가능)
5. 다른 옵션은 건드리지 말고 **Create repository** 클릭

---

## 2. 코드 업로드 (웹 화면에서, 터미널/git 명령어 없이)

방금 만든 레포 페이지에서:

1. **uploading an existing file** 링크 클릭 (또는 `Add file` → `Upload files`)
2. 아래 파일/폴더들을 전부 끌어다 놓기(드래그앤드롭):
   ```
   config.py
   scrapers.py
   core.py
   seen_store.py
   notifier.py
   main.py
   requirements.txt
   .env.example
   .gitignore
   .github/                  (폴더째로, 안에 workflows/watch.yml 포함)
   ```
   > `.env` 파일은 **올리면 안 됩니다** (내 진짜 비밀 토큰이 들어있음). `.gitignore`에 등록돼 있어서
   > 일반적인 git 명령으로는 안 올라가지만, 웹 업로드는 실수로 올릴 수 있으니 직접 빼고 올리세요.
   > `seen.json`도 올릴 필요 없습니다 — 첫 실행 때 자동으로 생성됩니다.
   > `test_step*.py`는 제가 개발 중 검증용으로 쓴 파일이라 안 올려도 됩니다 (올려도 무방, 동작에 영향 없음).
3. 맨 아래 **Commit changes** 클릭

> `.github` 폴더가 드래그앤드롭으로 잘 안 올라가면, GitHub 웹의 `Add file → Create new file`로
> 경로에 `.github/workflows/watch.yml`을 직접 입력하고 안의 내용을 붙여넣어도 됩니다.

---

## 3. GitHub Secrets 등록 (토큰을 안전하게 저장하는 곳)

코드에는 토큰을 절대 적지 않고, GitHub의 "Secrets" 라는 안전한 금고에 등록해서 Actions가 실행될 때만 꺼내 씁니다.

1. 레포 페이지 → **Settings** 탭
2. 왼쪽 메뉴 **Secrets and variables** → **Actions** 클릭
3. **New repository secret** 클릭, 아래 2개를 각각 등록:

   | Name | Secret 값 |
   |------|-----------|
   | `TELEGRAM_BOT_TOKEN` | BotFather에게 받은 토큰 |
   | `TELEGRAM_CHAT_ID` | getUpdates로 확인한 chat_id 숫자 |

4. 등록 완료되면 Settings → Secrets and variables → Actions 화면에 2개가 보임 (값은 가려져서 안 보임, 정상)

---

## 4. 잘 도는지 확인하기

1. 레포 페이지 → **Actions** 탭
2. 왼쪽에 **Guitar Watcher** 워크플로우 클릭
3. 오른쪽 **Run workflow** 버튼 → **Run workflow** 한 번 더 클릭 (수동 실행, 30분 기다릴 필요 없음)
4. 잠시 후(보통 30초~1분) 새로고침하면 실행 목록에 항목이 생김. 클릭해서 들어가면 로그를 볼 수 있음
5. 로그에 `[musicforce] 첫 실행 -> N건 조용히 기록` 같은 문구가 보이면 정상 (첫 실행은 알림이 안 옴, 의도된 동작)
6. 같은 화면에서 **Run workflow**를 한 번 더 눌러보면(=두 번째 실행), 이번에도 신규 0건일 가능성이 높음 (그 사이 진짜 신상품이 안 올라왔다면 정상)
7. 레포 파일 목록에 `seen.json`이 자동으로 생기고 커밋 기록이 쌓이면 정상 작동 중인 것
8. 이후로는 `cron`에 따라 **30분마다 자동 실행**됨 — 신상품이 올라오면 텔레그램으로 알림이 옴

### 만약 실패(빨간 X)했다면
- Actions 로그를 열어서 에러 메시지를 확인하고 저(Claude)에게 그대로 붙여넣어주세요.
- 가장 흔한 원인: Secrets 이름 오타, 토큰 값 앞뒤 공백 포함, Settings에서 Actions 권한이 막혀있는 경우
  (Settings → Actions → General → Workflow permissions 가 "Read and write permissions"인지 확인)

---

## 참고: 텔레그램 봇 만들기 (이미 하셨다면 생략)

1. 텔레그램에서 `@BotFather` 검색 → `/newbot` → 이름/아이디(끝은 꼭 `bot`) 입력
2. 발급된 토큰(`123456:AAExxxx...` 형태) 저장 → `TELEGRAM_BOT_TOKEN`
3. 만든 봇 채팅방을 열어 아무 메시지나 전송 (예: "hi")
4. 브라우저에서 `https://api.telegram.org/bot<토큰>/getUpdates` 접속
5. 응답에서 `"chat":{"id":숫자, ...}` 의 숫자 → `TELEGRAM_CHAT_ID`

---

## 운영 팁

- **키워드 변경**: `config.py`의 `KEYWORDS` 리스트를 GitHub 웹에서 직접 수정(연필 아이콘) 후 commit하면 다음 실행부터 적용됨.
- **실행 주기 변경**: `.github/workflows/watch.yml`의 `cron: '*/30 * * * *'` 부분 수정 (GitHub Actions cron은 UTC 기준).
- **잠깐 멈추고 싶을 때**: Actions 탭 → 워크플로우 선택 → 오른쪽 `···` 메뉴 → **Disable workflow**.
- 이 워크플로우는 매 실행마다 `seen.json`을 커밋하기 때문에, GitHub가 "60일간 활동 없는 레포의 예약 실행을 자동 정지"하는 정책에 걸리지 않습니다 (자동으로 계속 활동 기록이 생기는 셈).
