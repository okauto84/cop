# -*- coding: utf-8 -*-

import io
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
        # ["gpt-5-mini"],
        ["gpt-5.4"],
        index=0
    )
    st.markdown("---")
    if st.button("검색식 Q&A 대화 초기화", help="챗봇 대화 기록만 지웁니다. 검색식 목록은 유지됩니다."):
        st.session_state.chat_messages = []
        st.rerun()

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

1. **발명의 효과**: 해당 발명이 달성하는 핵심적인 기술적 효과를 글자 수 400자 수준으로 서술하세요.
2. **청구항 중심으로 핵심 기술 내용**: 독립 청구항 및 필요 시 종속 청구항을 중심으로, 핵심 기술 구성과 요지를 글자 수 400자 수준으로 정리하세요.

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
1. **검색식 항목 개수는 반드시 6개 미만**입니다. (1개 이상 6개 미만. 중복·유사한 방향은 하나로 묶지 말고, 서로 다른 검색 관점으로 나눕니다.)
2. **첫째 줄**: **그 검색식이 다루는 관점에 대한 간략한 설명**을 한 줄로 씁니다. 필요하면 괄호로 보조 설명을 붙입니다.
3. **둘째 줄**: 위 설명에 대응하는 **특허 검색식**을 한 줄로 씁니다. (줄바꿈 없음)
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

# 챗봇·컨텍스트용: 특허 검색식 작성 기준 요약 (생성 프롬프트와 일치)
SEARCH_QUERY_CRITERIA_CONTEXT = """[검색식 작성 참고]
[검색식 작성 시 참고]:
1. 핵심 기술 키워드의 동의어·유의어를 당신이 알고 있는 지식으로 되도록 많이 반영합니다.
2. 기술 분야별 용어를 다양하게 조합합니다.
3. 한글·영문·숫자를 사용할 수 있으며, 구문검색 및 논리연산(AND *, OR +, NOT !, NEAR ^, 절단자 등)으로 구체화할 수 있습니다.
4. 검색식은 명확하고 실행 가능한 한 줄 문자열로 작성합니다.
5. 단어 구분을 위해 단어 앞뒤에 싱글/쌍따옴표를 넣지 않습니다.

[특허 검색식 작성 기준 요약]:
- 단어 검색, 구문 검색(인접 나열), AND(*), OR(+), NOT(!, AND와 함께), NEAR(^, 1~3단어 거리) 등을 활용할 수 있습니다.

[출력 형식(목록 생성 시)]
- 항목마다 첫 줄: 간략한 설명, 둘째 줄: 검색식 한 줄. 항목은 여러 개일 수 있으며 우선순위 순으로 나열한다."""

def call_openai_search_query_chat(
    api_key: str,
    model: str,
    llm_analysis_text: str,
    search_query_text: str,
    criteria_context: str,
    history: list[dict],
) -> str:
    """LLM 분석 결과·특허검색식·기준을 컨텍스트로 하여 대화 응답"""
    if not api_key or api_key == "":
        return "⚠️ API 키가 설정되지 않았습니다. Streamlit secrets의 openai_api_key를 설정해주세요."
    try:
        client = OpenAI(api_key=api_key)
        _analysis = (llm_analysis_text or "").strip() or "(분석 결과 없음)"
        _queries = (search_query_text or "").strip() or "(특허검색식 없음)"
        system_prompt = f"""당신은 특허청 소속 특허 심사·검색 경험이 있는 도우미입니다. 사용자의 질문에 답할 때 아래 **[LLM 분석 결과]**, **[특허검색식 결과]**, **[검색식 기준]**을 모두 참고하세요. 세 가지가 서로 보완 관계이므로, 분석에서 드러난 발명의 요지·효과·청구 방향과 실제 검색식 문자열·검색 연산 규칙을 일관되게 연결해 설명하세요.

- [LLM 분석 결과]는 출원 문서를 바탕으로 한 발명의 효과·청구항 중심 요약입니다. [특허검색식 결과]는 그 분석을 토대로 생성·편집된 검색식 목록(내부 저장 형식일 수 있음)입니다. 질문 유형에 따라 둘 중 어느 쪽을 더 강조할지 판단하세요.
- 검색식 목록에 없는 식을 사실처럼 만들지 마세요. 제안·수정 시 [검색식 기준]에 맞게 이유를 짧게 덧붙이세요.
- 분석 결과와 검색식이 어긋나 보이면, 그 차이를 짚고 기준에 맞게 조정 방향을 제안할 수 있습니다.
- 일부가 비어 있으면 그 한계를 밝히고, 주어진 정보만으로 답할 수 있는 범위에서 도우세요.

[LLM 분석 결과 — 발명의 효과·청구항 중심 핵심 기술 등]
{_analysis}

[특허검색식 결과 — 사용자가 화면에서 편집한 최종 문자열]
{_queries}

[검색식 기준]
{criteria_context}
"""
        messages: list[dict] = [{"role": "system", "content": system_prompt}]
        for m in history:
            role = m.get("role")
            content = m.get("content", "")
            if role in ("user", "assistant") and content:
                messages.append({"role": role, "content": content})
        response = client.chat.completions.create(model=model, messages=messages)
        return response.choices[0].message.content or ""
    except Exception as e:
        err = str(e)
        if "API_KEY" in err or "authentication" in err.lower() or "invalid" in err.lower():
            return f"🔑 API 키 오류: API 키를 확인해주세요.\n\n에러: {err}"
        if "quota" in err.lower() or "limit" in err.lower() or "rate" in err.lower():
            return f"📊 사용량 한도 초과: API 사용량을 확인해주세요.\n\n에러: {err}"
        return f"❌ API 호출 오류: {err}"

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
        if "patent_analysis_result" in st.session_state:
            del st.session_state.patent_analysis_result
        if "search_query_editor" in st.session_state:
            del st.session_state["search_query_editor"]
        if "chat_messages" in st.session_state:
            del st.session_state["chat_messages"]
    
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
            st.session_state.patent_analysis_result = result
            # 세션 상태 초기화 또는 새로 생성
            if "search_query_result" not in st.session_state:
                with st.spinner("특허검색식 생성 중..."):
                    st.session_state.search_query_result = call_openai_for_search_query(API_KEY, model_name, result)

            with st.expander("특허검색식", expanded=True):
                _sq_ed = st.text_area(
                    "결과",
                    value=st.session_state.search_query_result,
                    height=280,
                    key="search_query_editor",
                    label_visibility="collapsed",
                )
                if _sq_ed != st.session_state.search_query_result:
                    st.session_state.search_query_result = _sq_ed

            st.divider()
            st.markdown("##### 검색식 Q&A")
            st.caption(
                "현재 문서에 대한 LLM 분석 결과와 특허검색식·검색식 작성 기준을 함께 참고하여 질문할 수 있습니다. "
                "사이드바에서 대화만 초기화할 수 있습니다."
            )
            if "chat_messages" not in st.session_state:
                st.session_state.chat_messages = []

            for _msg in st.session_state.chat_messages:
                with st.chat_message(_msg["role"]):
                    st.markdown(_msg["content"])

            _chat_prompt = st.chat_input("검색식·검색 기준에 대해 질문하세요")
            if _chat_prompt:
                st.session_state.chat_messages.append({"role": "user", "content": _chat_prompt})
                with st.spinner("답변 생성 중..."):
                    _reply = call_openai_search_query_chat(
                        API_KEY,
                        model_name,
                        st.session_state.get("patent_analysis_result", ""),
                        st.session_state.search_query_result,
                        SEARCH_QUERY_CRITERIA_CONTEXT,
                        st.session_state.chat_messages,
                    )
                st.session_state.chat_messages.append({"role": "assistant", "content": _reply})
                st.rerun()

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
