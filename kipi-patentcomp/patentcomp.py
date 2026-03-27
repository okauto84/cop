# -*- coding: utf-8 -*-

import io
from pathlib import Path

import streamlit as st
from openai import OpenAI
from pypdf import PdfReader

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_PDF_PATH = BASE_DIR / "data" / "1020200026921A.pdf"

st.set_page_config(
    page_title="PatentComp",
    page_icon="📄",
    layout="wide"
)

try:
    API_KEY = st.secrets.get("openai_api_key", "")
except Exception:
    API_KEY = ""

with st.sidebar:
    st.markdown("### 설정")
    model_name = st.selectbox(
        "모델 선택",
        ["gpt-5-mini"],
        index=0
    )
    st.markdown("---")
    if st.button("대화 초기화", help="챗봇 대화 기록을 지웁니다."):
        st.session_state.chat_messages = []
        st.rerun()

st.markdown("# PatentComp")


def parse_pdf(file_source) -> str:
    """PDF 바이트 또는 업로드 파일 객체에서 텍스트 추출"""
    try:
        data = file_source if isinstance(file_source, bytes) else file_source.read()
        reader = PdfReader(io.BytesIO(data))
        parts = [t for page in reader.pages if (t := page.extract_text())]
        return "\n\n".join(parts)
    except Exception:
        return ""


def call_chat(api_key: str, model: str, pdf_text: str, history: list[dict]) -> str:
    """PDF 텍스트를 컨텍스트로 하여 대화 응답"""
    if not api_key:
        return "⚠️ API 키가 설정되지 않았습니다. Streamlit secrets의 openai_api_key를 설정해주세요."
    try:
        client = OpenAI(api_key=api_key)
        _ctx = (pdf_text or "").strip() or "(첨부된 문서 없음)"
        system_prompt = f"""당신은 특허청 소속 특허 심사·분석 경험이 있는 도우미입니다.
아래 [첨부 문서]를 근거로 사용자의 질문에 성실히 답하세요.
문서에 없는 내용을 사실처럼 만들지 말고, 근거를 알 수 없으면 그 사실을 밝히세요.

[첨부 문서]
{_ctx}
"""
        messages: list[dict] = [{"role": "system", "content": system_prompt}]
        for m in history:
            if m.get("role") in ("user", "assistant") and m.get("content"):
                messages.append({"role": m["role"], "content": m["content"]})
        resp = client.chat.completions.create(model=model, messages=messages)
        return resp.choices[0].message.content or ""
    except Exception as e:
        err = str(e)
        if "API_KEY" in err or "authentication" in err.lower() or "invalid" in err.lower():
            return f"🔑 API 키 오류: {err}"
        if "quota" in err.lower() or "limit" in err.lower() or "rate" in err.lower():
            return f"📊 사용량 한도 초과: {err}"
        return f"❌ API 호출 오류: {err}"


# ── PDF 첨부 ──────────────────────────────────────────────────
st.markdown("#### PDF 첨부")
uploaded_file = st.file_uploader(
    "특허/출원 문서 PDF를 선택하세요",
    type=["pdf"],
    help="선택하지 않으면 ./data/1020200026921A.pdf 가 자동으로 사용됩니다.",
)

pdf_source = None
if uploaded_file is not None:
    pdf_source = uploaded_file
elif DEFAULT_PDF_PATH.is_file():
    pdf_source = DEFAULT_PDF_PATH.read_bytes()

if pdf_source is not None:
    if uploaded_file is None:
        st.caption(f"기본 PDF 사용: `data/{DEFAULT_PDF_PATH.name}`")

    current_file_id = (
        f"{uploaded_file.name}_{uploaded_file.size}"
        if uploaded_file is not None
        else f"default_{DEFAULT_PDF_PATH.name}_{len(pdf_source)}"
    )
    if "last_file_id" not in st.session_state or st.session_state.last_file_id != current_file_id:
        st.session_state.last_file_id = current_file_id
        st.session_state.pdf_text = ""
        st.session_state.chat_messages = []

    if not st.session_state.get("pdf_text"):
        with st.spinner("PDF를 파싱하고 있습니다..."):
            st.session_state.pdf_text = parse_pdf(pdf_source)

    extracted_text = st.session_state.pdf_text

    if not extracted_text.strip():
        st.error("PDF에서 텍스트를 추출할 수 없습니다. 스캔 이미지 PDF인 경우 OCR이 필요할 수 있습니다.")
    else:
        st.success(f"PDF 파싱 완료 (총 {len(extracted_text)}자 추출)")

        # ── 챗봇 ──────────────────────────────────────────────
        st.divider()
        st.markdown("##### Q&A")
        st.caption("첨부된 문서를 바탕으로 질문하면 답변합니다. 사이드바에서 대화를 초기화할 수 있습니다.")

        if "chat_messages" not in st.session_state:
            st.session_state.chat_messages = []

        for _msg in st.session_state.chat_messages:
            with st.chat_message(_msg["role"]):
                st.markdown(_msg["content"])

        _prompt = st.chat_input("문서에 대해 질문하세요")
        if _prompt:
            st.session_state.chat_messages.append({"role": "user", "content": _prompt})
            with st.spinner("답변 생성 중..."):
                _reply = call_chat(
                    API_KEY,
                    model_name,
                    extracted_text,
                    st.session_state.chat_messages,
                )
            st.session_state.chat_messages.append({"role": "assistant", "content": _reply})
            st.rerun()

if not API_KEY:
    st.warning("⚠️ OpenAI API 키가 설정되지 않았습니다. Streamlit secrets에 `openai_api_key`를 설정해주세요.")
