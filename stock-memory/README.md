## Stock 메모리 뷰어

이 프로그램은 **Streamlit** 과 **OpenAI API** 를 활용하여, 공개된 **Google Sheet** 의 내용을 불러와 주식 관련 정보를 카드(객체) 형태로 보여주고, 해당 데이터를 기반으로 **질의응답(챗봇)** 을 할 수 있게 해 주는 웹 앱입니다.

---

### 주요 기능

- **Google Sheet 불러오기**
  - `st.secrets["google_sheet_url"]` 에 설정된 공개 Google Sheet URL 을 불러옵니다.
  - 첫 번째 시트(첫 탭)를 CSV 로 변환해 `pandas.DataFrame` 으로 읽어들입니다.
  - A열은 `key`, B열은 `value` 로 사용하며, **빈 행 3줄**을 기준으로 하나의 블록(객체)으로 구분합니다.

- **객체(Objects) 카드 뷰**
  - 각 블록을 하나의 객체(JSON) 로 변환하여, **`Objects` 섹션의 expander 카드**로 표시합니다.
  - `이평 배열`, `이평 분류`, `거래량 배열`, `거래량 분류`, `종합 분류` 등 중요한 key 는 **굵게 표시**합니다.
  - `평균단가`, `현재가`, `수익률` 항목은 값에 따라 **색상(빨강/파랑)** 으로 수익/손실 여부를 직관적으로 보여줍니다.
  - 상단의 `모두 접기`, `모두 펼치기` 버튼으로 전체 카드를 한 번에 열고 닫을 수 있습니다.

- **데이터 기반 챗봇**
  - 불러온 객체 리스트(`sheet_objects_json`) 를 하나의 JSON 데이터로 시스템 프롬프트에 포함합니다.
  - 사용자가 입력한 질문에 대해, **마크 미너비니/윌리엄 오닐 스타일의 추세 추종 돌파 매매 전문가** 관점에서 답변하도록 안내합니다.
  - 채팅 입력창(`st.chat_input`) 을 통해 질의하고, 이전 대화는 `st.session_state.messages` 에 누적 저장됩니다.

- **OpenAI API 연동**
  - `st.secrets["openai_api_key"]` 또는 코드 상의 `API_KEY` 값을 사용해 OpenAI Chat Completions API 를 호출합니다.
  - `output_method = "실시간 출력"` 인 경우, 모델이 생성한 답변을 **한 글자씩 타이핑되는 효과**로 보여줍니다.
  - 인증 오류, 쿼터 초과 등 주요 에러 상황을 한국어 메시지로 안내합니다.

- **UI/스타일**
  - `layout="wide"` 로 넓은 화면을 활용합니다.
  - 표 하단 버튼, 채팅 말풍선, 입력창 라운딩 등은 CSS 로 간단히 커스터마이징 되어 있습니다.

---

### 요구 사항

- Python 3.9 이상 권장
- 필수 패키지(예시):
  - `streamlit`
  - `pandas`
  - `openai`

예시 `requirements.txt`:

```txt
streamlit
pandas
openai
```

---

### 환경 설정

#### 1. Streamlit secrets 설정

프로젝트 루트(또는 이 앱이 실행되는 디렉터리)에 `.streamlit/secrets.toml` 파일을 생성하고 다음과 같이 설정합니다.

```toml
openai_api_key = "YOUR_OPENAI_API_KEY"
google_sheet_url = "https://docs.google.com/spreadsheets/d/스프레드시트ID/edit"
```

- `google_sheet_url` 은 **링크로 누구나 열람 가능(보기 권한)** 으로 공개된 시트여야 합니다.
- 첫 번째 시트(탭)의 내용이 이 앱에서 사용됩니다.

#### 2. 직접 코드에서 API 키 지정 (선택)

만약 `secrets` 를 사용하지 않는다면, `stock.py` 상단의 `API_KEY` 값을 직접 채워 넣을 수도 있습니다.

```python
API_KEY = "YOUR_OPENAI_API_KEY"
```

---

### 실행 방법

터미널(또는 PowerShell)에서 이 디렉터리로 이동한 뒤 아래 명령을 실행합니다.

```bash
streamlit run stock.py
```

브라우저가 자동으로 열리며, 화면 상단의 **`google sheet 불러오기` 버튼**을 누르면 시트 데이터가 로딩되고, 이후 객체 리스트와 챗봇 기능을 사용할 수 있습니다.

---

### 동작 흐름 요약

1. 앱 실행 → `google sheet 불러오기` 클릭
2. `google_sheet_url` 기반으로 CSV URL 생성 후 `pandas.read_csv` 로 로드
3. A/B 열을 기준으로 **빈 행 3줄 단위로 객체 분할**
4. 각 객체를 카드(expander) 로 렌더링 (중요 항목 볼드/색상 표시)
5. 사용자가 질문 입력 → OpenAI API 호출
6. 불러온 객체 JSON 을 참고하여 투자 조언/분석 답변 생성

# [CoP] 지능형 주식 거래 일지 및 전략 분석 시스템 (RAG 기반 파일럿)
# (미완성) google sheet update를 위한 gcp에서 권한 설정 필요

---

## 1. 개요 (Overview)
개인 투자 데이터의 효율적인 관리와 분석을 위해, **Streamlit** 프레임워크와 **OpenAI**의 거대언어모델(LLM)을 결합한 지능형 주식 거래 일지 시스템을 구축합니다. 이 시스템은 단순 기록을 넘어 사용자의 매매 패턴을 AI가 학습하고 피드백을 제공하는 것을 목적으로 합니다.

---

## 2. 주요 관리 데이터 (Metadata)
정밀한 투자 분석을 위해 아래 5가지 핵심 필드를 중심으로 데이터를 구조화하고 Google Sheets와 동기화합니다.

| 필드명 | 상세 설명 |
| :--- | :--- |
| **날짜** | 주식 매매가 발생한 구체적인 시점 |
| **종목명** | 거래 대상 주식 또는 자산의 명칭 |
| **구분** | 매수, 매도 등 거래의 성격 정의 |
| **수량/단가** | 거래 규모 및 가격 정보 (수익률 계산의 기초) |
| **메모** | 매매 사유 및 당시 시장 상황 (AI 분석의 핵심 소스) |

---

## 3. 시스템 워크플로우 (Workflow)
사용자가 데이터를 기록하고 AI를 통해 인사이트를 도출하는 4단계 프로세스입니다.

1. **데이터 인터페이스 (Interface)**: `st.data_editor`를 통해 웹 환경에서 실시간으로 매매 내역 편집 및 행 관리
2. **저장 및 동기화 (Cloud Sync)**: Google Sheets API(GCP 서비스 계정)를 활용하여 클라우드에 데이터 영구 저장
3. **콘텍스트 추출 (Retrieval)**: 세션에 저장된 거래 기록을 OpenAI API로 전달하기 위한 데이터 전처리
4. **AI 전략 분석 (Generation)**: `gpt-5-mini` 모델이 사용자의 질문에 따라 투자 성과를 분석하고 맞춤형 답변 생성

---

## 4. 핵심 기술 요소
본 시스템의 안정적인 운영과 지능형 기능을 위해 다음 기술을 활용합니다.

> ### 💡 Streamlit & Google Sheets API
> 웹 인터페이스 구현과 클라우드 데이터베이스 역할을 동시에 수행합니다. 특히 Secrets 기능을 통해 API 키와 서비스 계정 정보를 안전하게 관리합니다.
> 
> ### 🔍 Semantic Analysis (의미 기반 분석)
> 사용자가 입력한 '메모'와 '거래 내역'을 바탕으로, AI가 단순 수치를 넘어 투자자의 심리나 전략적 오류를 찾아내는 의미론적 분석을 수행합니다.

---

## 5. 기대 효과
* **데이터 관리 효율화**: 수동 기록의 번거로움을 줄이고 구글 시트를 통한 기기 간 데이터 공유 가능
* **객관적 투자 복기**: AI와의 대화를 통해 감정적 매매를 배제하고 객관적인 관점에서 투자 전략 검토
* **확장성 확보**: 향후 벡터 DB 도입을 통한 과거 매매 사례 유사도 검색 기능으로의 고도화 기반 마련


---

## 🛠 설치 및 실행 (Installation)

본 프로젝트를 로컬 환경에서 실행하려면 아래의 라이브러리 설치가 필요합니다.

```bash
pip install streamlit openai pandas gspread google-auth
이후 다음 명령어로 앱을 실행합니다.

Bash
streamlit run stock.py
⚙️ 환경 설정 (Configuration)
앱의 모든 기능을 활용하려면 .streamlit/secrets.toml 파일에 아래 정보를 설정해야 합니다.

Ini, TOML
# OpenAI API 인증
openai_api_key = "your_openai_api_key"

# 구글 시트 연동 (시트는 '링크가 있는 모든 사용자'에게 읽기 권한이 있어야 함)
google_sheet_url = "[https://docs.google.com/spreadsheets/d/your_sheet_id](https://docs.google.com/spreadsheets/d/your_sheet_id)"

# 구글 서비스 계정 (쓰기 권한 필요 시 설정)
[gcp_service_account]
type = "service_account"
project_id = "..."
private_key_id = "..."
private_key = "..."
client_email = "..."
# (서비스 계정 JSON 파일의 나머지 항목들을 여기에 입력하세요)