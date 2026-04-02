# -*- coding: utf-8 -*-

import io
from pathlib import Path

import streamlit as st
from openai import OpenAI
from pypdf import PdfReader
import time
import pandas as pd
import re
import json
import html
import plotly.express as px
import plotly.graph_objects as go

# ── 설정 ─────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent
DEFAULT_PDF_PATH = BASE_DIR / "data" / "1020200026921A.pdf"

st.set_page_config(
    page_title="PatentComp",
    page_icon="📄",
    layout="wide",
)

try:
    API_KEY = st.secrets.get("openai_api_key", "")
except Exception:
    API_KEY = ""

MODEL_NAME = "gpt-5.4"

# ── 유틸 함수 ────────────────────────────────────────────────────

def parse_pdf(file_source) -> str:
    """PDF 바이트 또는 업로드 파일 객체에서 텍스트 추출."""
    try:
        data = file_source if isinstance(file_source, bytes) else file_source.read()
        reader = PdfReader(io.BytesIO(data))
        parts = [t for page in reader.pages if (t := page.extract_text())]
        return "\n\n".join(parts)
    except Exception:
        return ""


def call_chat(api_key: str, model: str, pdf_text: str, history: list[dict]) -> str:
    """PDF 텍스트를 컨텍스트로 포함하여 OpenAI Chat API 호출."""
    if not api_key:
        return "⚠️ API 키가 설정되지 않았습니다. Streamlit secrets의 `openai_api_key`를 설정해주세요."
    try:
        client = OpenAI(api_key=api_key)
        ctx = (pdf_text or "").strip() or "(첨부된 문서 없음)"
        system_prompt = f"""당신은 특허청 소속 특허 심사·분석 경험이 있는 전문 도우미입니다.
아래 [첨부 문서]를 근거로 사용자의 질문에 성실하고 정확하게 답하세요.
문서에 없는 내용을 사실처럼 만들지 말고, 근거를 알 수 없으면 그 사실을 명시하세요.
답변은 한국어로 작성하세요.

[첨부 문서]
{ctx}
"""
        messages: list[dict] = [{"role": "system", "content": system_prompt}]
        for m in history:
            if m.get("role") in ("user", "assistant") and m.get("content"):
                messages.append({"role": m["role"], "content": m["content"]})

        resp = client.chat.completions.create(model=model, messages=messages)
        return resp.choices[0].message.content or ""
    except Exception as e:
        err = str(e)
        if "api_key" in err.lower() or "authentication" in err.lower() or "invalid" in err.lower():
            return f"🔑 API 키 오류: {err}"
        if "quota" in err.lower() or "limit" in err.lower() or "rate" in err.lower():
            return f"📊 사용량 한도 초과: {err}"
        return f"❌ API 호출 오류: {err}"


def stream_chat(api_key: str, model: str, pdf_text: str, history: list[dict]):
    """스트리밍 방식으로 OpenAI Chat API 호출 (제너레이터)."""
    if not api_key:
        yield "⚠️ API 키가 설정되지 않았습니다. Streamlit secrets의 `openai_api_key`를 설정해주세요."
        return
    try:
        client = OpenAI(api_key=api_key)
        ctx = (pdf_text or "").strip() or "(첨부된 문서 없음)"
        system_prompt = f"""당신은 특허청 소속 특허 심사·분석 경험이 있는 전문 도우미입니다.
아래 [첨부 문서]를 근거로 사용자의 질문에 성실하고 정확하게 답하세요.
문서에 없는 내용을 사실처럼 만들지 말고, 근거를 알 수 없으면 그 사실을 명시하세요.
답변은 한국어로 작성하세요.

[첨부 문서]
{ctx}
"""
        messages: list[dict] = [{"role": "system", "content": system_prompt}]
        for m in history:
            if m.get("role") in ("user", "assistant") and m.get("content"):
                messages.append({"role": m["role"], "content": m["content"]})

        with client.chat.completions.stream(model=model, messages=messages) as stream:
            for chunk in stream:
                delta = chunk.choices[0].delta.content if chunk.choices else None
                if delta:
                    yield delta
    except Exception as e:
        err = str(e)
        if "api_key" in err.lower() or "authentication" in err.lower() or "invalid" in err.lower():
            yield f"🔑 API 키 오류: {err}"
        elif "quota" in err.lower() or "limit" in err.lower() or "rate" in err.lower():
            yield f"📊 사용량 한도 초과: {err}"
        else:
            yield f"❌ API 호출 오류: {err}"


# ── 헤더 ─────────────────────────────────────────────────────────
st.markdown("# 📄 PatentComp")
st.caption("특허 문서를 첨부하고 AI와 대화하세요.")

if not API_KEY:
    st.warning(
        "⚠️ OpenAI API 키가 설정되지 않았습니다. "
        "Streamlit secrets에 `openai_api_key`를 설정해주세요."
    )

st.divider()

# ── PDF 첨부 ─────────────────────────────────────────────────────
st.markdown("### 📎 PDF 첨부")

col_upload, col_info = st.columns([3, 2])

with col_upload:
    uploaded_file = st.file_uploader(
        "특허/출원 문서 PDF를 선택하세요",
        type=["pdf"],
        help="선택하지 않으면 기본 샘플 PDF(data/1020200026921A.pdf)가 사용됩니다.",
    )

pdf_source = None
if uploaded_file is not None:
    pdf_source = uploaded_file
elif DEFAULT_PDF_PATH.is_file():
    pdf_source = DEFAULT_PDF_PATH.read_bytes()

if pdf_source is None:
    with col_info:
        st.info("PDF 파일을 업로드하거나, `data/` 폴더에 기본 PDF를 배치하세요.")
    st.stop()

# ── 파일 변경 감지 및 세션 초기화 ────────────────────────────────
current_file_id = (
    f"{uploaded_file.name}_{uploaded_file.size}"
    if uploaded_file is not None
    else f"default_{DEFAULT_PDF_PATH.name}_{len(pdf_source)}"
)

if st.session_state.get("last_file_id") != current_file_id:
    st.session_state.last_file_id = current_file_id
    st.session_state.pdf_text = ""
    st.session_state.chat_messages = []

# ── PDF 파싱 ──────────────────────────────────────────────────────
if not st.session_state.get("pdf_text"):
    with st.spinner("PDF를 파싱하고 있습니다..."):
        st.session_state.pdf_text = parse_pdf(pdf_source)

pdf_text: str = st.session_state.pdf_text

with col_info:
    if uploaded_file is None:
        st.caption(f"기본 PDF 사용: `data/{DEFAULT_PDF_PATH.name}`")
    if pdf_text.strip():
        st.success(f"✅ 파싱 완료 — 총 **{len(pdf_text):,}자** 추출")
    else:
        st.error("PDF에서 텍스트를 추출할 수 없습니다.")

if not pdf_text.strip():
    st.error(
        "PDF 텍스트 추출에 실패했습니다. "
        "스캔 이미지 PDF인 경우 OCR이 필요할 수 있습니다."
    )
    st.stop()

# ── PDF 미리보기 (접기/펼치기) ───────────────────────────────────
with st.expander("📄 PDF 텍스트 미리보기 (처음 1,000자)", expanded=False):
    st.text(pdf_text[:1000] + ("..." if len(pdf_text) > 1000 else ""))

st.divider()

# ── 챗봇 ─────────────────────────────────────────────────────────
col_title, col_model, col_btn = st.columns([4, 2, 1])

with col_title:
    st.markdown("### 💬 AI 챗봇")

with col_model:
    selected_model = st.selectbox(
        "모델",
        options=["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"],
        index=0,
        label_visibility="collapsed",
    )

with col_btn:
    if st.button("🗑️ 초기화", help="대화 기록을 초기화합니다."):
        st.session_state.chat_messages = []
        st.rerun()

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

# 대화 기록 표시
chat_container = st.container()
with chat_container:
    if not st.session_state.chat_messages:
        st.info("💡 첨부된 PDF 문서에 대해 자유롭게 질문해보세요.")
    else:
        for msg in st.session_state.chat_messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

# 입력창
prompt = st.chat_input("문서에 대해 질문하세요…")

if prompt:
    st.session_state.chat_messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""
        try:
            for chunk in stream_chat(
                API_KEY,
                selected_model,
                pdf_text,
                st.session_state.chat_messages[:-1],  # 방금 추가한 user 메시지 제외 (이미 history에 포함)
            ):
                full_response += chunk
                placeholder.markdown(full_response + "▌")
            placeholder.markdown(full_response)
        except Exception as e:
            full_response = f"❌ 오류: {e}"
            placeholder.markdown(full_response)

    st.session_state.chat_messages.append({"role": "assistant", "content": full_response})
