# -*- coding: utf-8 -*-

import streamlit as st
from openai import OpenAI
import time
import pandas as pd
from datetime import datetime

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

# 파일 첨부 영역
uploaded_file = st.file_uploader(
    "📎 엑셀 파일 첨부 (.xlsx)",
    type=["xlsx"],
    help="엑셀 파일을 업로드하면 JSON 데이터로 변환합니다."
)

attached_json = None

if uploaded_file is not None:
    try:
        df = pd.read_excel(uploaded_file, header=0, engine="openpyxl")
        df.columns = df.columns.astype(str).str.strip()
        key_order = ["발신일시", "제목", "발신인", "수신인", "참조", "내용"]
        col_map = {}
        for i, key in enumerate(key_order):
            if key in df.columns:
                col_map[key] = df.columns.get_loc(key)
            elif i < len(df.columns):
                col_map[key] = i
        rows = []
        for _, row in df.iterrows():
            item = {}
            for key in key_order:
                if key not in col_map:
                    continue
                idx = col_map[key]
                val = row.iloc[idx]
                if pd.isna(val):
                    val = None
                elif key == "발신일시" and val is not None:
                    if isinstance(val, datetime):
                        val = val.isoformat()
                    elif isinstance(val, pd.Timestamp):
                        val = val.isoformat()
                    else:
                        try:
                            val = pd.to_datetime(val).isoformat()
                        except Exception:
                            val = str(val)
                elif key == "수신인":
                    if pd.isna(val) or val is None or str(val).strip() == "":
                        val = []
                    else:
                        val = [s.strip() for s in str(val).split(",") if s.strip()]
                elif hasattr(val, "isoformat"):
                    val = val.isoformat() if hasattr(val, "isoformat") else str(val)
                else:
                    val = str(val) if val is not None else None
                item[key] = val
            rows.append(item)
        attached_json = rows
        if "attached_json" not in st.session_state:
            st.session_state.attached_json = None
        st.session_state.attached_json = attached_json
        st.success(f"✅ 엑셀을 읽어 {len(attached_json)}건의 JSON 데이터를 처리했습니다.")
    except Exception as e:
        st.error(f"엑셀 읽기 오류: {e}")
        attached_json = None
        st.session_state.attached_json = None
else:
    if "attached_json" in st.session_state:
        st.session_state.attached_json = None
    attached_json = None

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

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
