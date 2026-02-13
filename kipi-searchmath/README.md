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