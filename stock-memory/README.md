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
