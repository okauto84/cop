# -*- coding: utf-8 -*-

import streamlit as st
from openai import OpenAI
import time
import pandas as pd
import os

# 페이지 설정
st.set_page_config(
    page_title="stock",
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
            ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"],
            index=0
        )

# 메인 화면
st.markdown("# stock")

# 데이터 디렉토리 및 CSV 경로 (스크립트 파일 기준으로 경로 해석)
_script_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(_script_dir, "data")
csv_path = os.path.join(data_dir, "stockmemory.csv")
if not os.path.exists(data_dir):
    os.makedirs(data_dir)


def load_stock_csv(path: str) -> pd.DataFrame | None:
    """./data/stockmemory.csv 파일을 읽어 동일한 header와 셀 내용으로 DataFrame 반환"""
    if not os.path.exists(path):
        return None
    for encoding in ("utf-8-sig", "utf-8", "cp949", "euc-kr"):
        try:
            df = pd.read_csv(path, encoding=encoding, header=0)
            df.columns = df.columns.astype(str).str.strip()
            return df
        except (UnicodeDecodeError, Exception):
            continue
    return None


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


# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

# 테이블 데이터: 페이지 열 때 CSV 로드, 동일한 header/셀 내용 유지
if "table_data" not in st.session_state:
    df = load_stock_csv(csv_path)
    if df is not None and len(df.columns) > 0:
        if "선택" not in df.columns:
            df.insert(0, "선택", False)
        st.session_state.table_data = df
    else:
        default_cols = ["선택", "날짜", "종목명", "구분", "수량", "체결 단가", "수수료", "정산금액", "메모"]
        st.session_state.table_data = pd.DataFrame(columns=default_cols)
else:
    # 테이블이 비어 있는데 CSV에 데이터가 있으면 다시 로드 (경로/파일 이슈 해결 후 반영)
    if len(st.session_state.table_data) == 0:
        df = load_stock_csv(csv_path)
        if df is not None and len(df) > 0:
            if "선택" not in df.columns:
                df.insert(0, "선택", False)
            st.session_state.table_data = df

# ---------- 테이블 섹션: CSV와 동일한 header/셀 내용, 왼쪽 체크박스 + 행삭제 ----------
st.markdown("## 📊 내역")

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

display_df = st.data_editor(
    table_df,
    use_container_width=True,
    num_rows="fixed",
    column_config=column_config,
    hide_index=True,
)
st.session_state.table_data = display_df

# 행삭제: 체크된 행만 삭제 후 CSV 저장
if st.button("행삭제"):
    df = st.session_state.table_data
    if "선택" in df.columns:
        remaining = df[df["선택"] != True].drop(columns=["선택"], errors="ignore")
        st.session_state.table_data = remaining.copy()
        st.session_state.table_data.insert(0, "선택", False)
        try:
            remaining.to_csv(csv_path, index=False, encoding="utf-8-sig")
            st.success("선택한 행이 삭제되었습니다.")
        except Exception as e:
            st.error(f"저장 오류: {e}")
    st.rerun()

st.markdown("---")

# 챗봇 섹션
st.markdown("## 💬 챗봇")

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
