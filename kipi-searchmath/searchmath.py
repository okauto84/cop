# -*- coding: utf-8 -*-

import streamlit as st
from openai import OpenAI
import time
import pandas as pd
import re
from datetime import datetime

# 페이지 설정
st.set_page_config(
    page_title="Stock",
    page_icon="🔍",
    layout="wide"
)

# API 키 설정 (secrets에서 가져오거나 기본값 사용)
try:
    API_KEY = st.secrets.get("openai_api_key", "")
except:
    API_KEY = ""

# 사이드바 설정
with st.sidebar:
    st.markdown("### 설정")
    
    with st.expander("📍 출력방법", expanded=False):
        output_method = st.selectbox(
            "출력 방식 선택",
            ["실시간 출력", "일괄 출력"],
            index=0
        )
    
    with st.expander("💭 모델", expanded=False):
        model_name = st.selectbox(
            "모델 선택",
            ["gpt-5-mini"],
            index=0
        )

# 메인 화면
st.markdown("# Stock")


def normalize_for_editor(df: pd.DataFrame) -> pd.DataFrame:
    """data_editor 타입 호환을 위해 컬럼 타입 정규화"""
    df = df.copy()
    for col in df.columns:
        if col == "선택":
            if df[col].dtype == object or str(df[col].dtype) == "object":
                df[col] = df[col].astype(str).str.upper().isin(("TRUE", "1", "YES")).fillna(False)
            df[col] = df[col].astype(bool)
        elif col == "날짜":
            df[col] = pd.to_datetime(df[col], errors="coerce")
        elif col in ("수량", "체결 단가", "수수료", "정산금액"):
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
            df[col] = df[col].astype(int if col == "수량" else float)
        else:
            df[col] = df[col].astype(str).replace("nan", "").replace("<NA>", "")
    return df


def _sheet_url_to_export_csv(url: str, gid: str = "0") -> str:
    """공개 스프레드시트 URL을 CSV 내보내기 URL로 변환"""
    url = (url or "").strip()
    if not url:
        return ""
    # /d/SPREADSHEET_ID/ 형태 추출
    m = re.search(r"/d/([a-zA-Z0-9_-]+)", url)
    if not m:
        return ""
    sid = m.group(1)
    # 기존 URL에 #gid= 숫자가 있으면 사용
    gid_m = re.search(r"[#?]gid=(\d+)", url)
    if gid_m:
        gid = gid_m.group(1)
    return f"https://docs.google.com/spreadsheets/d/{sid}/export?format=csv&gid={gid}"


def _read_gsheet(url: str = None) -> pd.DataFrame:
    """공개 Google Sheet URL로 시트 읽기 (URL은 secrets 또는 인자로 전달)"""
    u = (url or st.secrets.get("google_sheet_url", "") or "").strip()
    if not u:
        return pd.DataFrame()
    export_url = _sheet_url_to_export_csv(u)
    if not export_url:
        return pd.DataFrame()
    try:
        df = pd.read_csv(export_url)
        if df is not None and len(df.columns) > 0:
            df.columns = df.columns.astype(str).str.strip()
            return df
    except Exception:
        pass
    return pd.DataFrame()


def _get_gspread_credentials():
    """Secrets의 gcp_service_account로 쓰기용 credentials 반환. 없으면 None."""
    try:
        sa = st.secrets.get("gcp_service_account", None)
        if not sa:
            return None
        from google.oauth2.service_account import Credentials
        info = dict(sa)
        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        return Credentials.from_service_account_info(info, scopes=scopes)
    except Exception:
        return None


def _write_gsheet(url: str, df: pd.DataFrame) -> tuple:
    """표 데이터를 Google Sheet에 덮어쓰기. (성공 여부, 메시지)"""
    url = (url or "").strip()
    if not url:
        return False, "google_sheet_url이 없습니다."
    creds = _get_gspread_credentials()
    if creds is None:
        return False, "secrets에 gcp_service_account를 설정하세요. 서비스 계정 JSON을 넣고, 시트를 해당 이메일과 편집 권한으로 공유하세요."
    try:
        import gspread
        gc = gspread.authorize(creds)
        sh = gc.open_by_url(url)
        ws = sh.sheet1
        save_df = df.drop(columns=["선택"], errors="ignore").copy()
        if "날짜" in save_df.columns:
            save_df["날짜"] = pd.to_datetime(save_df["날짜"], errors="coerce").dt.strftime("%Y-%m-%d")
        data = [save_df.columns.tolist()] + save_df.fillna("").astype(str).values.tolist()
        ws.clear()
        ws.update(data, "A1", value_input_option="USER_ENTERED")
        return True, "Google Sheet에 저장되었습니다."
    except Exception as e:
        return False, str(e)


# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

# 테이블 데이터: secrets의 google_sheet_url로 읽어서 표시, 이후 세션에 유지
if "table_data" not in st.session_state:
    df = _read_gsheet(st.secrets.get("google_sheet_url", ""))
    if df is not None and len(df.columns) > 0:
        if "선택" not in df.columns:
            df.insert(0, "선택", False)
        st.session_state.table_data = df
    else:
        default_cols = ["선택", "날짜", "종목명", "구분", "수량", "체결 단가", "수수료", "정산금액", "메모"]
        st.session_state.table_data = pd.DataFrame(columns=default_cols)

# ---------- 테이블 섹션: CSV와 동일한 header/셀 내용, 왼쪽 체크박스 + 행삭제 ----------
st.markdown("#### 📊 일지")

table_df = normalize_for_editor(st.session_state.table_data)
column_config = {}
for col in table_df.columns:
    if col == "선택":
        column_config[col] = st.column_config.CheckboxColumn("선택", width="small", help="삭제할 행을 선택하세요.")
    elif col == "날짜":
        column_config[col] = st.column_config.DateColumn(col, format="YYYY-MM-DD", step=1)
    elif col == "구분":
        column_config[col] = st.column_config.SelectboxColumn(col, options=["", "매수", "매도"], width="small")
    elif col == "수량":
        column_config[col] = st.column_config.NumberColumn(col, min_value=0, step=1, format="%d")
    elif col in ("체결 단가", "수수료", "정산금액"):
        column_config[col] = st.column_config.NumberColumn(col, min_value=0, format="%d")
    else:
        column_config[col] = st.column_config.TextColumn(col, width="medium")

# 사용자가 셀·행을 직접 수정 가능, 편집 내용은 세션에 유지(메모리 상태로 되돌아가지 않음)
display_df = st.data_editor(
    table_df,
    use_container_width=True,
    num_rows="dynamic",
    column_config=column_config,
    hide_index=True,
)
# 편집 결과를 항상 세션에 반영하여 다음 rerun에서도 수정 상태 유지
st.session_state.table_data = display_df

# 표 아래 버튼: 행 추가, 행 삭제, 저장, google sheet 불러오기 (간격 좁게, 작은 크기)
col_btn4, col_btn1, col_btn2, col_btn3 = st.columns([1.0, 0.6, 0.6, 0.5])

with col_btn1:
    if st.button("행 추가"):
        df = st.session_state.table_data
        row = {}
        for c in df.columns:
            if c == "선택":
                row[c] = False
            elif c == "날짜":
                row[c] = datetime.now().strftime("%Y-%m-%d")
            elif c == "구분":
                row[c] = ""
            elif c in ("수량", "체결 단가", "수수료", "정산금액"):
                row[c] = 0
            else:
                row[c] = ""
        new_row = pd.DataFrame([row])
        st.session_state.table_data = pd.concat([df, new_row], ignore_index=True)
        st.rerun()

with col_btn2:
    if st.button("행 삭제"):
        df = st.session_state.table_data
        if "선택" in df.columns:
            remaining = df[df["선택"] != True].drop(columns=["선택"], errors="ignore")
            st.session_state.table_data = remaining.copy()
            st.session_state.table_data.insert(0, "선택", False)
            st.success("선택한 행이 삭제되었습니다.")
        st.rerun()

with col_btn3:
    if st.button("저장"):
        url = st.secrets.get("google_sheet_url", "")
        if not url or not str(url).strip():
            st.error("Streamlit secrets에 google_sheet_url을 설정하세요.")
        else:
            ok, msg = _write_gsheet(url, st.session_state.table_data)
            if ok:
                st.success(msg)
            else:
                st.error(f"저장 실패: {msg}")

with col_btn4:
    if st.button("google sheet 불러오기"):
        url = st.secrets.get("google_sheet_url", "")
        if not url or not str(url).strip():
            st.error("Streamlit secrets에 google_sheet_url을 설정하세요.")
        else:
            df = _read_gsheet(url)
            if df is not None and len(df.columns) > 0:
                if "선택" not in df.columns:
                    df.insert(0, "선택", False)
                st.session_state.table_data = df
                st.success("Google Sheet를 불러왔습니다.")
                st.rerun()
            else:
                st.error("시트를 불러올 수 없습니다. google_sheet_url과 시트 공개(링크로 볼 수 있음) 설정을 확인하세요.")

st.markdown("---")

# 챗봇 섹션
st.markdown("#### 💬 분석")

# OpenAI API 호출 함수
def call_openai_api(messages: list) -> str:
    """OpenAI API를 호출하는 함수"""
    try:
        if not API_KEY or API_KEY == "":
            return "⚠️ API 키가 설정되지 않았습니다. Streamlit secrets의 openai_api_key 또는 코드의 API_KEY 변수를 설정해주세요."

        client = OpenAI(api_key=API_KEY)
        
        response = client.chat.completions.create(
            model=model_name,
            messages=messages,
        )
        
        return response.choices[0].message.content

    except Exception as e:
        error_msg = str(e)
        if "API_KEY" in error_msg or "authentication" in error_msg.lower() or "invalid" in error_msg.lower():
            return f"🔑 API 키 오류: API 키를 확인해주세요.\n\n에러 상세: {error_msg}"
        elif "quota" in error_msg.lower() or "limit" in error_msg.lower() or "rate" in error_msg.lower():
            return f"📊 사용량 한도 초과: API 사용량을 확인해주세요.\n\n에러 상세: {error_msg}"
        else:
            return f"❌ API 호출 중 오류가 발생했습니다: {error_msg}"

# 이전 대화 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 사용자 입력 처리
if prompt := st.chat_input("질문해보세요!"):
    # 사용자 메시지 추가
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # OpenAI API 호출
    with st.chat_message("assistant"):
        # 대화 히스토리를 메시지 리스트로 변환
        messages_for_api = [
            {"role": msg["role"], "content": msg["content"]}
            for msg in st.session_state.messages
        ]
        
        if output_method == "실시간 출력":
            with st.spinner("OpenAI가 답변을 생성하고 있습니다..."):
                response = call_openai_api(messages_for_api)
            message_placeholder = st.empty()
            displayed_text = ""
            for char in response:
                displayed_text += char
                message_placeholder.markdown(displayed_text + "▌")
                time.sleep(0.01)
            message_placeholder.markdown(response)
        else:
            with st.spinner("OpenAI가 답변을 생성하고 있습니다..."):
                response = call_openai_api(messages_for_api)
            st.markdown(response)

    # AI 응답을 세션에 저장
    st.session_state.messages.append({"role": "assistant", "content": response})

# API 키 안내
if not API_KEY or API_KEY == "":
    st.warning("⚠️ OpenAI API 키가 설정되지 않았습니다. Streamlit secrets 또는 코드를 수정해주세요.")
    with st.expander("API 키 설정 방법"):
        st.markdown("""
        1. [OpenAI Platform](https://platform.openai.com/api-keys)에서 API 키를 발급받으세요.
        2. Streamlit secrets에 `openai_api_key`로 설정하거나
        3. 코드의 `API_KEY` 변수를 직접 수정하세요.

        ```python
        API_KEY = "your-actual-api-key-here"
        ```
        """)

# CSS 스타일 추가
st.markdown("""
<style>
    /* 표 아래 버튼 행: 간격 좁게, 글자·버튼 크기 작게 */
    .main [data-testid="stHorizontalBlock"] [data-testid="column"] .stButton > button {
        font-size: 0.75rem;
        padding: 0.15rem 0.35rem;
        min-height: 1.35rem;
    }
    .main [data-testid="stHorizontalBlock"] > div {
        padding-left: 0.15rem;
        padding-right: 0.15rem;
    }
    .stChatMessage {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .stTextInput > div > div > input {
        border-radius: 20px;
    }
    .main > div {
        padding-top: 2rem;
    }
    .stSidebar {
        background-color: #f0f2f6;
    }
</style>
""", unsafe_allow_html=True)
