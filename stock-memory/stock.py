# -*- coding: utf-8 -*-

import streamlit as st
from openai import OpenAI
import time
import pandas as pd
import os
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

# 데이터 디렉토리 생성
data_dir = "./data"
if not os.path.exists(data_dir):
    os.makedirs(data_dir)

# 엑셀 파일 경로
excel_path = os.path.join(data_dir, "stockmemory.xlsx")

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

# 주식 거래 내역 데이터 초기화
if "stock_data" not in st.session_state:
    # 기존 파일이 있으면 로드
    if os.path.exists(excel_path):
        try:
            st.session_state.stock_data = pd.read_excel(excel_path, engine="openpyxl")
        except Exception as e:
            st.error(f"파일 로드 오류: {e}")
            st.session_state.stock_data = pd.DataFrame(columns=[
                "날짜", "종목명", "구분", "수량", "체결 단가", "수수료", "정산금액", "메모"
            ])
    else:
        # 새 데이터프레임 생성
        st.session_state.stock_data = pd.DataFrame(columns=[
            "날짜", "종목명", "구분", "수량", "체결 단가", "수수료", "정산금액", "메모"
        ])

# 주식 거래 내역 관리 섹션
st.markdown("## 📊 주식 거래 내역")

# 파일 첨부 영역
uploaded_file = st.file_uploader(
    "📎 엑셀 파일 첨부 (.xlsx)",
    type=["xlsx"],
    help="엑셀 파일을 업로드하면 기존 데이터에 추가됩니다."
)

# 파일이 업로드된 경우 처리
if uploaded_file is not None:
    try:
        # 업로드된 엑셀 파일 읽기
        uploaded_df = pd.read_excel(uploaded_file, engine="openpyxl")
        
        # 컬럼명 정리 (공백 제거)
        uploaded_df.columns = uploaded_df.columns.astype(str).str.strip()
        
        # 필요한 컬럼이 있는지 확인하고, 없으면 기본 컬럼으로 매핑
        required_columns = ["날짜", "종목명", "구분", "수량", "체결 단가", "수수료", "정산금액", "메모"]
        
        # 컬럼 매핑 (업로드된 파일의 컬럼명이 다를 수 있음)
        column_mapping = {}
        for col in uploaded_df.columns:
            col_clean = col.strip()
            # 유사한 컬럼명 찾기
            for req_col in required_columns:
                if req_col in col_clean or col_clean in req_col:
                    column_mapping[col] = req_col
                    break
        
        # 컬럼명 표준화
        if column_mapping:
            uploaded_df = uploaded_df.rename(columns=column_mapping)
        
        # 필요한 컬럼이 모두 있는지 확인
        missing_cols = [col for col in required_columns if col not in uploaded_df.columns]
        
        if missing_cols:
            # 없는 컬럼은 빈 값으로 추가
            for col in missing_cols:
                uploaded_df[col] = None
        
        # 필요한 컬럼만 선택
        uploaded_df = uploaded_df[required_columns]
        
        # 날짜 컬럼 처리
        if "날짜" in uploaded_df.columns:
            uploaded_df["날짜"] = pd.to_datetime(uploaded_df["날짜"], errors="coerce")
        
        # 수량, 체결 단가, 수수료, 정산금액을 숫자로 변환
        numeric_columns = ["수량", "체결 단가", "수수료", "정산금액"]
        for col in numeric_columns:
            if col in uploaded_df.columns:
                uploaded_df[col] = pd.to_numeric(uploaded_df[col], errors="coerce").fillna(0)
        
        # 기존 데이터와 병합
        if len(st.session_state.stock_data) > 0:
            # 기존 데이터와 병합
            st.session_state.stock_data = pd.concat(
                [st.session_state.stock_data, uploaded_df],
                ignore_index=True
            )
        else:
            # 기존 데이터가 없으면 업로드된 데이터로 설정
            st.session_state.stock_data = uploaded_df
        
        st.success(f"✅ 엑셀 파일을 읽어 {len(uploaded_df)}건의 데이터를 추가했습니다. (총 {len(st.session_state.stock_data)}건)")
        
    except Exception as e:
        st.error(f"엑셀 파일 읽기 오류: {e}")

# 행 추가/삭제 컨트롤
col1, col2, col3 = st.columns([1, 1, 2])

with col1:
    if st.button("➕ 행 추가"):
        new_row = pd.DataFrame([{
            "날짜": datetime.now().strftime("%Y-%m-%d"),
            "종목명": "",
            "구분": "매수",
            "수량": 0,
            "체결 단가": 0,
            "수수료": 0,
            "정산금액": 0,
            "메모": ""
        }])
        st.session_state.stock_data = pd.concat([st.session_state.stock_data, new_row], ignore_index=True)
        st.rerun()

with col2:
    if st.button("💾 저장"):
        try:
            st.session_state.stock_data.to_excel(excel_path, index=False, engine="openpyxl")
            st.success(f"✅ 저장 완료: {excel_path}")
        except Exception as e:
            st.error(f"저장 오류: {e}")

# 삭제할 행 선택
if len(st.session_state.stock_data) > 0:
    with col3:
        delete_indices = st.multiselect(
            "삭제할 행 선택",
            options=range(len(st.session_state.stock_data)),
            format_func=lambda x: f"행 {x+1}: {st.session_state.stock_data.iloc[x].get('종목명', '')} ({st.session_state.stock_data.iloc[x].get('날짜', '')})"
        )
        if delete_indices and st.button("🗑️ 선택한 행 삭제"):
            st.session_state.stock_data = st.session_state.stock_data.drop(
                st.session_state.stock_data.index[delete_indices]
            ).reset_index(drop=True)
            st.rerun()

# 데이터 편집기
if len(st.session_state.stock_data) > 0:
    edited_df = st.data_editor(
        st.session_state.stock_data,
        use_container_width=True,
        num_rows="dynamic",
        column_config={
            "날짜": st.column_config.DateColumn(
                "날짜",
                format="YYYY-MM-DD",
                step=1,
            ),
            "종목명": st.column_config.TextColumn(
                "종목명",
                width="medium",
            ),
            "구분": st.column_config.SelectboxColumn(
                "구분",
                options=["매수", "매도"],
                width="small",
            ),
            "수량": st.column_config.NumberColumn(
                "수량",
                min_value=0,
                step=1,
                format="%d",
            ),
            "체결 단가": st.column_config.NumberColumn(
                "체결 단가",
                min_value=0,
                format="%d",
            ),
            "수수료": st.column_config.NumberColumn(
                "수수료",
                min_value=0,
                format="%d",
            ),
            "정산금액": st.column_config.NumberColumn(
                "정산금액",
                format="%d",
            ),
            "메모": st.column_config.TextColumn(
                "메모",
                width="large",
            ),
        },
        hide_index=True,
    )
    st.session_state.stock_data = edited_df
else:
    st.info("📝 '행 추가' 버튼을 클릭하여 거래 내역을 추가하세요.")

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
