# -*- coding: utf-8 -*-
"""Tesla Model Y 오너 매뉴얼 RAG 챗봇 (Streamlit)."""

from __future__ import annotations

import pickle
import re
import time
from pathlib import Path
from typing import Any, Iterator

import numpy as np
import streamlit as st
from openai import OpenAI

BASE_DIR = Path(__file__).resolve().parent
VEC_PATH = BASE_DIR / "data" / "vec" / "vectors_manual.p"
EMBED_MODEL_NAME = "dragonkue/BGE-m3-ko"
PAGE_TITLE_PATTERN = re.compile(r"page_(\d+)", re.IGNORECASE)

st.set_page_config(
    page_title="Model Y Manual",
    page_icon="🚗",
    layout="wide",
)


# API 키 설정 (secrets에서 가져오거나 기본값 사용)
try:
    API_KEY = st.secrets.get("openai_api_key", "")
except:
    API_KEY = ""


@st.cache_resource
def get_bge_m3_ko_model():
    try:
        import torch
        from sentence_transformers import SentenceTransformer
    except ImportError as e:
        raise ImportError(
            "RAG 임베딩을 위해 패키지가 필요합니다. 다음을 설치하세요:\n"
            "pip install -U sentence-transformers torch"
        ) from e

    device = "cuda" if torch.cuda.is_available() else "cpu"
    return SentenceTransformer(EMBED_MODEL_NAME, trust_remote_code=True, device=device)


@st.cache_resource
def load_manual_vectors() -> list[dict[str, Any]]:
    if not VEC_PATH.is_file():
        raise FileNotFoundError(
            f"벡터 DB 파일을 찾을 수 없습니다: {VEC_PATH}\n"
            "먼저 `py -3 data_processing.py all` 을 실행하세요."
        )

    with VEC_PATH.open("rb") as file:
        data = pickle.load(file)

    if not isinstance(data, list):
        raise ValueError("vectors_manual.p 형식이 예상(list[dict])과 다릅니다.")
    return data


@st.cache_resource
def get_manual_embeddings_matrix() -> tuple[list[dict[str, Any]], np.ndarray]:
    items = load_manual_vectors()
    valid_items: list[dict[str, Any]] = []
    embeddings: list[list[float]] = []

    for item in items:
        vector = item.get("embedd")
        if vector is not None:
            valid_items.append(item)
            embeddings.append(vector)

    if not embeddings:
        return [], np.array([], dtype="float32")

    matrix = np.asarray(embeddings, dtype="float32")
    matrix = matrix / (np.linalg.norm(matrix, axis=1, keepdims=True) + 1e-12)
    return valid_items, matrix


def embed_query(query: str) -> np.ndarray:
    model = get_bge_m3_ko_model()
    vector = model.encode(
        [query],
        normalize_embeddings=True,
        show_progress_bar=False,
    )
    return np.asarray(vector[0], dtype="float32")


def format_page_label(title: str | None, filename: str | None = None) -> str:
    source = title or filename or "알 수 없는 페이지"
    match = PAGE_TITLE_PATTERN.search(source)
    if match:
        return f"매뉴얼 {match.group(1)}페이지 ({source})"
    return source


def search_similar_pages(query: str, top_k: int = 5) -> list[dict[str, Any]]:
    items, matrix = get_manual_embeddings_matrix()
    if not items or matrix.size == 0:
        return []

    query_vector = embed_query(query)
    query_vector = query_vector / (np.linalg.norm(query_vector) + 1e-12)
    scores = matrix @ query_vector

    top_k = min(top_k, len(scores))
    top_indices = np.argsort(-scores)[:top_k]

    results: list[dict[str, Any]] = []
    for index in top_indices:
        item = items[int(index)]
        results.append(
            {
                "score": float(scores[index]),
                "filename": item.get("filename"),
                "title": item.get("title"),
                "text": item.get("text"),
                "item": item,
            }
        )
    return results


def build_rag_system_prompt(rag_results: list[dict[str, Any]]) -> str:
    if not rag_results:
        return (
            "당신은 Tesla Model Y 오너 매뉴얼 전문 도우미입니다. "
            "현재 질문과 관련된 매뉴얼 페이지를 찾지 못했습니다. "
            "매뉴얼에 없는 내용은 추측하지 말고, 정보가 없음을 안내하세요."
        )

    context_blocks: list[str] = []
    for rank, result in enumerate(rag_results, start=1):
        label = format_page_label(result.get("title"), result.get("filename"))
        score = float(result.get("score", 0.0))
        text = (result.get("text") or "").strip() or "(내용 없음)"
        context_blocks.append(
            f"### 참고 {rank}: {label}\n"
            f"유사도: {score:.4f}\n"
            f"---\n{text}"
        )

    context = "\n\n".join(context_blocks)
    return f"""당신은 Tesla Model Y 오너 매뉴얼 전문 도우미입니다.
아래 [매뉴얼 참고 자료]만을 바탕으로 사용자 질문에 정확하고 친절하게 답변하세요.

[답변 규칙]
- 참고 자료에 없는 내용은 추측하지 말고, 매뉴얼에 해당 정보가 없다고 안내하세요.
- 답변에 관련 매뉴얼 페이지 번호를 함께 알려주세요.
- 안전·경고 관련 내용은 주의사항을 빠짐없이 전달하세요.
- 한국어로 답변하세요.

[매뉴얼 참고 자료]
{context}
"""


def format_api_error(error: Exception) -> str:
    message = str(error)
    if "authentication" in message.lower() or "api_key" in message.lower():
        return f"🔑 API 키 오류: API 키를 확인해주세요.\n\n에러: {message}"
    if "quota" in message.lower() or "limit" in message.lower() or "rate" in message.lower():
        return f"📊 사용량 한도 초과: API 사용량을 확인해주세요.\n\n에러: {message}"
    return f"❌ API 호출 오류: {message}"


def stream_rag_answer(
    api_key: str,
    model: str,
    system_prompt: str,
    history: list[dict[str, str]],
    temperature: float,
    collect: list[str],
) -> Iterator[str]:
    collect.clear()
    if not api_key:
        message = (
            "⚠️ OpenAI API 키가 설정되지 않았습니다. "
            "`.streamlit/secrets.toml`에 `openai_api_key`를 설정해주세요."
        )
        collect.append(message)
        yield message
        return

    messages: list[dict[str, str]] = [{"role": "system", "content": system_prompt}]
    for item in history:
        role = item.get("role")
        content = item.get("content", "")
        if role in ("user", "assistant") and content:
            messages.append({"role": role, "content": content})

    try:
        client = OpenAI(api_key=api_key)
        stream = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            stream=True,
        )
        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                text = chunk.choices[0].delta.content
                collect.append(text)
                yield text
    except Exception as error:
        message = format_api_error(error)
        collect.append(message)
        yield message


with st.sidebar:
    st.markdown("### 설정")
    model_name = st.selectbox(
        "모델 선택",
        ["gpt-4o-mini", "gpt-4o", "gpt-5.4"],
        index=0,
    )
    top_k = st.slider("검색 페이지 수 (Top-K)", min_value=1, max_value=8, value=4)
    temperature = st.slider("Temperature", min_value=0.0, max_value=1.5, value=0.2, step=0.1)
    show_stats = st.checkbox("통계 표시", value=False)
    st.markdown("---")
    if st.button("대화 초기화"):
        st.session_state.messages = []
        st.session_state.rag_results = []
        st.rerun()

    st.caption(f"벡터 DB: `{VEC_PATH.relative_to(BASE_DIR)}`")


try:
    with st.spinner("임베딩 모델 및 벡터 DB 준비 중..."):
        _ = get_bge_m3_ko_model()
        _ = get_manual_embeddings_matrix()
except Exception as error:
    st.error(str(error))
    st.stop()


st.markdown("# Model Y Manual")
st.markdown("*Tesla Model Y 오너 매뉴얼 RAG 챗봇*")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "rag_results" not in st.session_state:
    st.session_state.rag_results = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Model Y 매뉴얼에 대해 질문해보세요"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        rag_results = search_similar_pages(prompt, top_k=top_k)
    except Exception as error:
        rag_results = []
        st.warning(f"RAG 검색 중 오류가 발생했습니다: {error}")

    st.session_state.rag_results = rag_results
    system_prompt = build_rag_system_prompt(rag_results)

    with st.chat_message("assistant"):
        collected: list[str] = []
        st.write_stream(
            stream_rag_answer(
                API_KEY,
                model_name,
                system_prompt,
                st.session_state.messages,
                temperature,
                collected,
            )
        )
        response_text = "".join(collected)
        st.session_state.messages.append({"role": "assistant", "content": response_text})

if show_stats and st.session_state.messages:
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("대화 턴", len(st.session_state.messages) // 2)
    with col2:
        st.metric("모델", model_name)
    with col3:
        st.metric("Top-K", top_k)

st.markdown("---")
st.markdown("### 참고 매뉴얼 페이지")
rag_results_display = st.session_state.get("rag_results", [])
if rag_results_display:
    for rank, result in enumerate(rag_results_display, start=1):
        label = format_page_label(result.get("title"), result.get("filename"))
        score = float(result.get("score", 0.0))
        text = (result.get("text") or "_텍스트 없음_").strip()
        with st.expander(f"{rank}. {label} (유사도: {score:.4f})", expanded=(rank == 1)):
            st.markdown(text.replace("\n", "  \n"))
else:
    st.caption("질문을 입력하면 관련 매뉴얼 페이지가 여기에 표시됩니다.")

st.markdown("---")
col1, col2 = st.columns(2)
with col1:
    st.info("구체적인 기능명·상황을 함께 질문하면 더 정확한 답변을 받을 수 있습니다.")
with col2:
    if st.button("대화 내용 다운로드", key="download_chat"):
        if st.session_state.messages:
            history_text = ""
            for message in st.session_state.messages:
                role = "사용자" if message["role"] == "user" else "AI"
                history_text += f"**{role}**: {message['content']}\n\n"
            st.download_button(
                label="TXT 저장",
                data=history_text,
                file_name=f"modelyl_chat_{time.strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
            )
        else:
            st.warning("저장할 대화가 없습니다.")

if not API_KEY:
    st.warning(
        "⚠️ OpenAI API 키가 설정되지 않았습니다. "
        "`.streamlit/secrets.toml`에 `openai_api_key`를 설정해주세요."
    )

st.markdown(
    """
<style>
    .stChatMessage {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .main > div {
        padding-top: 1.5rem;
    }
</style>
""",
    unsafe_allow_html=True,
)
