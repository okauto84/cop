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
        ["gpt-5"],
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

# PDF 첨부 버튼 영역 (파일 업로더로 구현)
st.markdown("#### PDF 첨부")
uploaded_file = st.file_uploader(
    "특허/출원 문서 PDF를 선택하세요",
    type=["pdf"],
    help="PDF를 선택하면 자동으로 파싱 후 발명의 효과와 청구항 중심 핵심 기술 내용이 생성됩니다."
)

if uploaded_file is not None:
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

        st.markdown("---")

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
