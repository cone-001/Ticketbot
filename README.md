## Ticketbot

Discord 서버에서 **티켓 채널을 자동 생성·관리**하는 봇입니다.
사용자 문의 대응, 민원 처리, 고객지원 서버 구조에 적합합니다.

---

## 🚀 주요 기능

* 버튼 또는 명령어로 티켓 생성
* 사용자별 독립 티켓 채널 자동 생성
* 티켓 닫기 기능(버튼/명령어)
* 관리자·매니저 역할 기반 관리
* `.env` 환경 변수 설정 기반 동작

---

## 📦 요구사항

* Python 3.x
* Discord Bot Token
* Discord 서버에서 채널 생성 및 권한 관리 권한
* **Discord 개발자 모드 활성화 필요**

  * 이유: 역할 ID, 채널 ID, 카테고리 ID 복사에 필요
  * 경로: **사용자 설정 → 고급 → 개발자 모드 ON**

---

## 📥 설치

```bash
git clone https://github.com/cone-001/Ticketbot.git
cd Ticketbot

pip install -r requirements.txt
```

---

## ⚙️ 환경 변수 설정

프로젝트 루트에 `.env` 파일을 생성하고 다음을 입력합니다:

```env
BOT_TOKEN=your_token_here
ADMIN_ROLE_ID=your_admin_role_id
MANAGER_ROLE_ID=your_manager_role_id
CHANNEL_ID=your_channel_id
CATEGORY_ID=your_category_id
```

각 항목 설명:

* **BOT_TOKEN**: 디스코드 봇 토큰
* **ADMIN_ROLE_ID**: 관리자 역할 ID
* **MANAGER_ROLE_ID**: 매니저 역할 ID
* **CHANNEL_ID**: 티켓 생성 메시지가 올라갈 채널 ID
* **CATEGORY_ID**: 티켓이 생성될 카테고리 ID

---

## 📌 카테고리 ID 가져오는 방법

1. 서버에서 티켓을 모아둘 **카테고리를 직접 원하는 이름으로 생성**합니다.
2. 개발자 모드가 켜져 있는 상태에서

   * 카테고리 우클릭 → **“ID 복사”**
3. 복사한 값을 `.env`의 `CATEGORY_ID`에 넣으면 됩니다.

---

## ▶️ 실행

```bash
python Ticket.py
```

---

## 📁 프로젝트 구조

```
Ticketbot/
 ├── Ticket.py        # 메인 실행 스크립트
 ├── requirements.txt # 필요한 패키지 목록
 ├── .env             # 환경 변수 파일 (직접 생성)
```

---

## 🛠 권한 및 역할 설정 가이드

* 티켓 생성 버튼을 사용할 역할을 별도로 지정하는 것이 효율적입니다.
* 티켓이 생성될 카테고리를 미리 만들어 두면 관리가 깔끔합니다.
* 생성된 티켓 채널 접근 권한은

  * 티켓 요청자
  * 관리자 역할
  * 매니저 역할
    만 접근 가능하게 설정됩니다.

---
