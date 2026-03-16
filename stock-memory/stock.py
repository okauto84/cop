# -*- coding: utf-8 -*-

import streamlit as st
from openai import OpenAI
import time
import pandas as pd
import re
import json
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

# Google Sheet URL (secrets에서 가져오거나 기본값 사용)
try:
    google_sheet_url = st.secrets.get("google_sheet_url", "")
except:
    google_sheet_url = ""

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
st.markdown("# test")


def _sheet_url_to_export_csv(url: str) -> str:
    """공개 스프레드시트 URL을 CSV 내보내기 URL로 변환. gid 생략 시 첫 번째 시트가 내보내짐."""
    url = (url or "").strip()
    if not url:
        return ""
    # /d/SPREADSHEET_ID/ 형태 추출
    m = re.search(r"/d/([a-zA-Z0-9_-]+)", url)
    if not m:
        return ""
    sid = m.group(1)
    # gid 없이 export하면 첫 번째 시트가 기본. gid=0 은 시트 ID가 0이 아닐 때 400 Bad Request 발생.
    return f"https://docs.google.com/spreadsheets/d/{sid}/export?format=csv"


def _read_gsheet(url: str = None) -> tuple[pd.DataFrame, str]:
    """공개 Google Sheet URL로 첫 번째 시트(total sheet)만 읽기. (DataFrame, 에러메시지) 반환. 성공 시 에러메시지는 ''."""
    u = (url or "").strip()
    if not u:
        return pd.DataFrame(), "google_sheet_url이 비어 있습니다."
    export_url = _sheet_url_to_export_csv(u)
    if not export_url:
        return pd.DataFrame(), "URL 형식이 올바르지 않습니다. 예: https://docs.google.com/spreadsheets/d/스프레드시트ID/edit"
    try:
        df = pd.read_csv(export_url)
        if df is not None and len(df.columns) > 0:
            df.columns = df.columns.astype(str).str.strip()
            return df, ""
        return pd.DataFrame(), "시트에 컬럼이 없거나 비어 있습니다."
    except Exception as e:
        err = str(e).strip()
        if "403" in err or "Forbidden" in err or "Access" in err.lower():
            return pd.DataFrame(), "시트에 대한 접근이 거부되었습니다. 시트를 '링크가 있는 모든 사용자에게 공개'로 설정하세요."
        if "404" in err or "Not Found" in err:
            return pd.DataFrame(), "시트를 찾을 수 없습니다. URL과 시트 존재 여부를 확인하세요."
        return pd.DataFrame(), f"읽기 오류: {err}"


# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

# Google Sheet URL로 불러와 시트 영역을 테이블(DataFrame)로 변환하여 변수에 저장
def load_sheet_as_table(url: str) -> tuple[pd.DataFrame, str]:
    """Google Sheet URL을 받아 첫 번째 시트(total sheet)만 table 형태(DataFrame)로 변환. (DataFrame, 에러메시지) 반환."""
    return _read_gsheet(url)

# 세션에 저장된 테이블(내용) 초기화
if "sheet_table" not in st.session_state:
    st.session_state.sheet_table = pd.DataFrame()

if st.button("google sheet 불러오기"):
    url = (google_sheet_url or "").strip()
    if not url:
        st.error("Streamlit secrets에 google_sheet_url을 설정하세요.")
    else:
        # URL로 불러와 table 형태로 변환 후 변수에 저장
        sheet_table, err_msg = load_sheet_as_table(url)
        if err_msg:
            st.error(f"시트를 불러올 수 없습니다. {err_msg}")
        elif sheet_table is not None and len(sheet_table.columns) > 0:
            st.session_state.sheet_table = sheet_table
            st.success("Google Sheet를 불러왔습니다.")
            st.rerun()
        else:
            st.error("시트를 불러올 수 없습니다. google_sheet_url과 시트 공개(링크로 볼 수 있음) 설정을 확인하세요.")

# 저장된 테이블 변수 (시트 내용 = context)
context = st.session_state.sheet_table


def _parse_sheet_to_objects(df: pd.DataFrame, empty_rows: int = 3) -> list[dict]:
    """연속 empty_rows줄의 빈 행으로 구분된 블록을 별도 object로 파싱. A열=key, B열=value. JSON 형식 리스트 반환."""
    if df is None or len(df) == 0 or df.columns.size < 2:
        return []
    col_a, col_b = df.columns[0], df.columns[1]
    objects: list[dict] = []
    current: list[tuple[str, str]] = []
    empty_streak = 0

    for _, row in df.iterrows():
        a = row[col_a]
        b = row[col_b]
        a_str = "" if pd.isna(a) else str(a).strip()
        b_str = "" if pd.isna(b) else str(b).strip()
        if a_str == "" and b_str == "":
            empty_streak += 1
            if empty_streak >= empty_rows:
                if current:
                    objects.append(dict(current))
                current = []
        else:
            empty_streak = 0
            current.append((a_str, b_str))

    if current:
        objects.append(dict(current))
    return objects


# 내용(context)을 그대로 화면에 출력
st.markdown("#### Google Sheet 내용")
if context is not None and len(context) > 0:
    st.dataframe(context, use_container_width=True, hide_index=True)

    # 행 3줄 빈 곳으로 구분 → A열=key, B열=value 객체 리스트(JSON)로 변수 저장
    sheet_objects = _parse_sheet_to_objects(context, empty_rows=3)
    if "sheet_objects_json" not in st.session_state:
        st.session_state.sheet_objects_json = []
    st.session_state.sheet_objects_json = sheet_objects

    # 각 object별로 표 형식 출력
    if sheet_objects:
        st.markdown("#### 구분된 객체 (표)")
        for i, obj in enumerate(sheet_objects):
            st.markdown(f"**Object {i + 1}**")
            table_df = pd.DataFrame([{"key": k, "value": v} for k, v in obj.items()])
            st.table(table_df)
else:
    st.info("Google Sheet를 불러오면 여기에 내용이 표시됩니다.")

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
