# -*- coding: utf-8 -*-

import streamlit as st
from openai import OpenAI
from pypdf import PdfReader
import io

# 페이지 설정
st.set_page_config(
    page_title="SearchMath",
    page_icon="🔍",
    layout="wide"
)

# API 키 설정 (secrets에서 가져오거나 기본값 사용)
try:
    API_KEY = st.secrets.get("openai_api_key", "")
except Exception:
    API_KEY = ""

# 사이드바: 모델 선택만 유지
with st.sidebar:
    st.markdown("### 설정")
    model_name = st.selectbox(
        "모델 선택",
        ["gpt-5-mini"],
        index=0
    )

st.markdown("# SearchMath")

# PDF 파싱 함수
def parse_pdf(uploaded_file) -> str:
    """업로드된 PDF 파일에서 텍스트 추출"""
    try:
        reader = PdfReader(io.BytesIO(uploaded_file.read()))
        text_parts = []
        for page in reader.pages:
            t = page.extract_text()
            if t:
                text_parts.append(t)
        return "\n\n".join(text_parts) if text_parts else ""
    except Exception as e:
        return ""

# OpenAI API 호출 함수
def call_openai_for_patent(api_key: str, model: str, document_text: str) -> str:
    """문서 텍스트를 바탕으로 발명의 효과·청구항 중심 핵심 기술 내용 생성"""
    if not api_key or api_key == "":
        return "⚠️ API 키가 설정되지 않았습니다. Streamlit secrets의 openai_api_key를 설정해주세요."
    try:
        client = OpenAI(api_key=api_key)
        system_prompt = """당신은 특허청에 소속되어 있는 베테랑 특허 심사관입니다. 주어진 문서 텍스트에서 아래 두 가지를 명확히 추출·정리하여 답변하세요.

1. **발명의 효과**: 해당 발명이 달성하는 핵심적인 기술적 효과를 글자 수 200자 수준으로 서술하세요.
2. **청구항 중심으로 핵심 기술 내용**: 독립 청구항 및 필요 시 종속 청구항을 중심으로, 핵심 기술 구성과 요지를 글자 수 200자 수준으로 정리하세요.

출력은 반드시 다음 형식으로 작성하세요:
---
## 발명의 효과
(내용)

## 청구항 중심 핵심 기술 내용
(내용)
---"""
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"다음 문서 내용을 분석해 주세요.\n\n{document_text}"}
            ],
        )
        return response.choices[0].message.content
    except Exception as e:
        err = str(e)
        if "API_KEY" in err or "authentication" in err.lower() or "invalid" in err.lower():
            return f"🔑 API 키 오류: API 키를 확인해주세요.\n\n에러: {err}"
        if "quota" in err.lower() or "limit" in err.lower() or "rate" in err.lower():
            return f"📊 사용량 한도 초과: API 사용량을 확인해주세요.\n\n에러: {err}"
        return f"❌ API 호출 오류: {err}"

# 특허검색식 생성을 위한 OpenAI API 호출 함수
def call_openai_for_search_query(api_key: str, model: str, analysis_result: str) -> str:
    """LLM 분석 결과를 바탕으로 특허검색식 생성"""
    if not api_key or api_key == "":
        return "⚠️ API 키가 설정되지 않았습니다. Streamlit secrets의 openai_api_key를 설정해주세요."
    try:
        client = OpenAI(api_key=api_key)
        system_prompt = """당신은 특허청에 소속되어 있는 베테랑 특허 심사관입니다. 특허 검색을 위해 [검색식 설명]과 [검색식 작성 기준]에 따라서 주어진 LLM 분석 결과(발명의 효과 및 청구항 중심 핵심 기술 내용)를 바탕으로 유사 특허 검색을 위한 효과적인 특허 검색식을 생성하세요.

[특허 검색식에 대한 설명입니다.]:
1. 핵심 기술 키워드와 동의어/유의어를 포함합니다.
2. 기술 분야별 주요 용어 조합합니다.
3. 한글, 영문, 숫자를 이용할 수 있으며 구문검색("") 및 논리연산자(AND, OR, NOT, NEAR, 절단자)를 사용하면 더 구체적인 검색이 가능합니다.
4. 검색식은 명확하고 실행 가능한 형태로 작성합니다.

[특허 검색식 작성 기준에 대한 설명입니다.]:
1. 단어 검색
  - 상세내용 : 단어 검색	특정 단어가 포함된 검색
  - 예시 : 디스크
2. 구문 검색
  - 상세내용 : 검색어가 순서대로 인접하여 나열되도록 검색 (공백, 복합명사, 조사, 특수문자가 포함된 경우도 검색 가능)	
  - 예시 : 데이터 신호
3. 논리연산 AND : *
  - 상세내용 : 입력된 키워드가 모두 포함되도록 검색	
  - 예시 : 휴대폰*케이스
4. 논리연산 OR : +
  - 상세내용 : 입력된 키워드 중 하나라도 포함된 검색	
5. 논리연산 NOT : !
  - 상세내용 : 입력된 키워드 중 NOT(!) 연산자 뒤의 키워드는 포함하지 않는 검색 (단독 사용 불가, AND(*)와 함께 사용 가능)	
  - 예시 : 자동차*!엔진
6. 논리연산 NEAR : ^
  - 상세내용 : 첫 번째 검색어와 두 번째 검색어 사이의 거리(단어 수)를 지정하여 검색 (1~3단어 거리까지 지원, 단어 순서 고려)	
  - 예시 : 자동차^2각도
7. 단어를 구분하려는 용도로 단어 앞뒤에 싱글 따옴표('), 쌍따옴표(")를 넣지 않습니다.

[출력 형태]:
(검색식)

"""
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"다음 LLM 분석 결과를 바탕으로 특허 검색식을 생성해 주세요.\n\n{analysis_result}"}
            ],
        )
        return response.choices[0].message.content
    except Exception as e:
        err = str(e)
        if "API_KEY" in err or "authentication" in err.lower() or "invalid" in err.lower():
            return f"🔑 API 키 오류: API 키를 확인해주세요.\n\n에러: {err}"
        if "quota" in err.lower() or "limit" in err.lower() or "rate" in err.lower():
            return f"📊 사용량 한도 초과: API 사용량을 확인해주세요.\n\n에러: {err}"
        return f"❌ API 호출 오류: {err}"

# PDF 첨부 버튼 영역 (파일 업로더로 구현)
st.markdown("#### PDF 첨부")
uploaded_file = st.file_uploader(
    "특허/출원 문서 PDF를 선택하세요",
    type=["pdf"],
    help="PDF를 선택하면 자동으로 파싱 후 발명의 효과와 청구항 중심 핵심 기술 내용을 분석하고, 이를 바탕으로 특허검색식을 생성합니다."
)

if uploaded_file is not None:
    # 파일이 변경되었는지 확인하여 세션 상태 초기화
    current_file_id = f"{uploaded_file.name}_{uploaded_file.size}"
    if "last_file_id" not in st.session_state or st.session_state.last_file_id != current_file_id:
        st.session_state.last_file_id = current_file_id
        if "search_query_result" in st.session_state:
            del st.session_state.search_query_result
    
    with st.spinner("PDF를 파싱하고 있습니다..."):
        extracted_text = parse_pdf(uploaded_file)

    if not extracted_text.strip():
        st.error("PDF에서 텍스트를 추출할 수 없습니다. 스캔 이미지 PDF인 경우 OCR이 필요할 수 있습니다.")
    else:
        st.success(f"PDF 파싱 완료 (총 {len(extracted_text)}자 추출)")
        with st.expander("추출된 원문 미리보기", expanded=False):
            st.text_area("원문", value=extracted_text[:5000] + ("..." if len(extracted_text) > 5000 else ""), height=200, disabled=True)

        with st.spinner("OpenAI API로 분석 중..."):
            result = call_openai_for_patent(API_KEY, model_name, extracted_text)
        
        with st.expander("LLM 분석 결과", expanded=True):
            st.text_area("결과", value=result, height=280, disabled=True, label_visibility="collapsed")

        # LLM 분석 결과를 바탕으로 특허검색식 생성
        if result and not result.startswith("⚠️") and not result.startswith("🔑") and not result.startswith("📊") and not result.startswith("❌"):
            # 세션 상태 초기화 또는 새로 생성
            if "search_query_result" not in st.session_state:
                with st.spinner("특허검색식 생성 중..."):
                    st.session_state.search_query_result = call_openai_for_search_query(API_KEY, model_name, result)
            
            with st.expander("특허검색식", expanded=True):
                # 검색식 수정 가능한 text_area
                edited_search_query = st.text_area(
                    "검색식", 
                    value=st.session_state.search_query_result, 
                    height=280, 
                    disabled=False, 
                    label_visibility="collapsed",
                    key="search_query_editor"
                )
                
                # 수정된 내용을 세션 상태에 저장
                if edited_search_query != st.session_state.search_query_result:
                    st.session_state.search_query_result = edited_search_query

        # st.markdown("---")

# 분석 결과·원문 미리보기: 글자 작게, 레이아웃 정리
st.markdown("""
<style>
    .stTextArea textarea {
        font-size: 0.8rem !important;
        line-height: 1.5 !important;
        font-family: inherit;
        background-color: #ffffff !important;
        color: #262730 !important;
        border: 1px solid #e0e0e0 !important;
    }
    .stExpander summary {
        font-size: 0.9rem !important;
    }
    /* 분석 결과 영역 배경 흰색 강제 */
    .stExpander .stTextArea textarea[disabled] {
        background-color: #ffffff !important;
        color: #262730 !important;
        -webkit-text-fill-color: #262730 !important;
    }
</style>
""", unsafe_allow_html=True)

# API 키 미설정 안내
if not API_KEY or API_KEY == "":
    st.warning("⚠️ OpenAI API 키가 설정되지 않았습니다. Streamlit secrets에 `openai_api_key`를 설정해주세요.")
