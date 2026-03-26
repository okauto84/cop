# -*- coding: utf-8 -*-

import io
import re
from pathlib import Path

import streamlit as st
from openai import OpenAI
from pypdf import PdfReader

# 최초 로딩 시 사용할 기본 PDF (프로젝트 루트 기준 ./data/)
BASE_DIR = Path(__file__).resolve().parent
DEFAULT_PDF_PATH = BASE_DIR / "data" / "1020200026921A.pdf"

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
def parse_pdf(file_source) -> str:
    """PDF 바이트 또는 업로드 파일 객체에서 텍스트 추출"""
    try:
        if isinstance(file_source, bytes):
            data = file_source
        else:
            data = file_source.read()
        reader = PdfReader(io.BytesIO(data))
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
        system_prompt = """당신은 특허청에 소속되어 있는 베테랑 특허 심사관입니다. 주어진 LLM 분석 결과(발명의 효과 및 청구항 중심 핵심 기술 내용)를 바탕으로, 서로 다른 검색 방향을 가진 **유사 특허 검색용 검색식**을 작성하세요.

[검색식 작성 시 참고]:
1. 핵심 기술 키워드의 동의어·유의어를 당신이 알고 있는 지식으로 되도록 많이 반영합니다.
2. 기술 분야별 용어를 다양하게 조합합니다.
3. 한글·영문·숫자를 사용할 수 있으며, 구문검색 및 논리연산(AND *, OR +, NOT !, NEAR ^, 절단자 등)으로 구체화할 수 있습니다.
4. 검색식은 명확하고 실행 가능한 한 줄 문자열로 작성합니다.
5. 단어 구분을 위해 단어 앞뒤에 싱글/쌍따옴표를 넣지 않습니다.

[특허 검색식 작성 기준 요약]:
- 단어 검색, 구문 검색(인접 나열), AND(*), OR(+), NOT(!, AND와 함께), NEAR(^, 1~3단어 거리) 등을 활용할 수 있습니다.

[출력 형식 — 반드시 준수]:
1. **검색식 항목 개수는 반드시 7개 미만**입니다. (1개 이상 7개 이하. 중복·유사한 방향은 하나로 묶지 말고, 서로 다른 검색 관점으로 나눕니다.)
2. 각 항목은 **정확히 두 줄**로만 씁니다.
   - **첫째 줄**: **그 검색식이 다루는 관점에 대한 간략한 설명**을 한 줄로 씁니다. 필요하면 괄호로 보조 설명을 붙입니다.
   - **둘째 줄**: 위 설명에 대응하는 **특허 검색식**을 한 줄로 씁니다. (줄바꿈 없음)
3. 항목과 항목 사이에는 **빈 줄 하나**를 넣습니다.
4. 위 형식 외의 머리말·요약·번호 목록·마크다운 제목 등은 넣지 않습니다.
5. 가장 중요하다고 판단하는 순위부터 보여줍니다.

[출력 예시]
● 층간 도전성 범프 크기 구배(범프 크기 변화로 적층 연결)
ABF+Ajinomoto*Build-up*Film*인터포저*(TSV+Through-Silicon*Via)*수직*신호라인*연결*스택*패키지*패드*피치

● 인터포저를 통한 ASIC과 HBM 전기적 결합 (인터포저 내부라인/TSV 활용)
HBM+High*Bandwidth*Memory*ASIC*(Application*Specific*Integrated*Circuit)*인터포저*내부*연결*전기적*결합*(TSV+Through-Silicon*Via)*(내부라인+routing+interconnect)

● 상부 패드 피치와 인터포저 피치 일치
P1=P3*패드*피치*인터포저*상부*하부*스택*패키지

"""
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"다음 LLM 분석 결과를 바탕으로, 지정한 출력 형식(● 설명 한 줄 + 검색식 한 줄, 항목 10개 미만)으로 특허 검색식을 생성해 주세요.\n\n{analysis_result}"}
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

def parse_search_query_blocks(text: str) -> list[tuple[str, str]]:
    """● 설명\\n검색식 형태의 LLM 출력을 (설명, 검색식) 목록으로 분리"""
    text = (text or "").strip()
    if not text:
        return []
    parts = re.split(r"(?m)^●\s*", text)
    pairs: list[tuple[str, str]] = []
    for part in parts:
        part = part.strip()
        if not part:
            continue
        lines = part.split("\n", 1)
        desc = lines[0].strip()
        query = lines[1].strip() if len(lines) > 1 else ""
        if desc or query:
            pairs.append((desc, query))
    return pairs

# PDF 첨부 버튼 영역 (파일 업로더로 구현; 미선택 시 기본 PDF 자동 로드)
st.markdown("#### PDF 첨부")
uploaded_file = st.file_uploader(
    "특허/출원 문서 PDF를 선택하세요",
    type=["pdf"],
    help="PDF를 선택하면 자동으로 파싱 후 발명의 효과와 청구항 중심 핵심 기술 내용을 분석하고, 이를 바탕으로 특허검색식을 생성합니다. "
         "선택하지 않으면 최초 로딩 시 ./data/1020200026921A.pdf 가 자동으로 사용됩니다."
)

pdf_source = None
if uploaded_file is not None:
    pdf_source = uploaded_file
elif DEFAULT_PDF_PATH.is_file():
    pdf_source = DEFAULT_PDF_PATH.read_bytes()

if pdf_source is not None:
    if uploaded_file is None:
        st.caption(f"기본 PDF 사용: `data/{DEFAULT_PDF_PATH.name}` (업로드 없음)")
    # 파일이 변경되었는지 확인하여 세션 상태 초기화
    if uploaded_file is not None:
        current_file_id = f"{uploaded_file.name}_{uploaded_file.size}"
    else:
        current_file_id = f"default_{DEFAULT_PDF_PATH.name}_{len(pdf_source)}"
    if "last_file_id" not in st.session_state or st.session_state.last_file_id != current_file_id:
        st.session_state.last_file_id = current_file_id
        if "search_query_result" in st.session_state:
            del st.session_state.search_query_result
        for _i in range(12):
            _qk = f"sq_query_{_i}"
            if _qk in st.session_state:
                del st.session_state[_qk]
        if "sq_query_fallback" in st.session_state:
            del st.session_state["sq_query_fallback"]
    
    with st.spinner("PDF를 파싱하고 있습니다..."):
        extracted_text = parse_pdf(pdf_source)

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

            st.markdown("##### 특허검색식")
            _pairs = parse_search_query_blocks(st.session_state.search_query_result)
            if not _pairs:
                st.caption("검색식 (● 형식으로 인식되지 않은 경우 전체)")
                _single = st.text_area(
                    "검색식",
                    value=st.session_state.search_query_result,
                    height=140,
                    key="sq_query_fallback",
                    label_visibility="collapsed",
                )
                if _single != st.session_state.search_query_result:
                    st.session_state.search_query_result = _single
            else:
                _edited_queries: list[str] = []
                for _i, (_desc, _q) in enumerate(_pairs):
                    with st.container():
                        st.caption(_desc if _desc.strip() else "—")
                        _qv = st.text_area(
                            "검색식",
                            value=_q,
                            height=72,
                            key=f"sq_query_{_i}",
                            label_visibility="collapsed",
                        )
                        _edited_queries.append(_qv)
                    if _i < len(_pairs) - 1:
                        st.markdown('<div style="height:0.75rem"></div>', unsafe_allow_html=True)

                _merged = "\n\n".join(
                    f"● {d}\n{qv}" for (d, _), qv in zip(_pairs, _edited_queries)
                )
                if _merged != st.session_state.search_query_result:
                    st.session_state.search_query_result = _merged

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
