# [CoP] Stock Trading Journal & AI Analyzer

`stock.py`는 **Streamlit**을 기반으로 구축된 지능형 주식 거래 일지 관리 도구입니다. 사용자는 매매 내역을 시각적으로 기록하고, 구글 시트(Google Sheets)와 실시간으로 데이터를 동기화하며, OpenAI의 최신 언어 모델을 통해 본인의 투자 성향과 전략을 분석할 수 있습니다.

---

## 🚀 핵심 기능 (Key Features)

* **📊 인터랙티브 데이터 에디터**: `st.data_editor`를 활용하여 엑셀과 유사한 환경에서 행 추가, 삭제 및 실시간 데이터 수정이 가능합니다.
* **☁️ Google Sheets 실시간 연동**:
    * **읽기**: 공개된 시트 URL에서 CSV 형태로 데이터를 즉시 불러옵니다.
    * **쓰기**: GCP 서비스 계정 인증을 통해 편집된 내용을 구글 시트에 즉시 덮어쓰기 저장합니다.
* **💬 AI 투자 분석가**: `gpt-5-mini` 모델과 연동된 챗봇이 내장되어 있어, 일지에 기록된 데이터를 바탕으로 투자 성과 분석 및 전략 피드백을 제공합니다.
* **🛠 맞춤형 설정**: 사이드바를 통해 응답 출력 방식(실시간/일괄) 및 모델 종류를 자유롭게 선택할 수 있습니다.

---



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