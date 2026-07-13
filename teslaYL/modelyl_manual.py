# -*- coding: utf-8 -*-
"""Tesla Model Y 오너 매뉴얼 RAG 챗봇 (Streamlit).

흐름:
1) 사용자 질문 → vectors_manual.p 유사 지문 검색
2) 검색된 지문을 컨텍스트로 OpenAI API 답변 생성
3) 지문과 동일한 파일명의 data/img 이미지를 화면에 출력
"""

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
DATA_DIR = BASE_DIR / "data"
VEC_PATH = DATA_DIR / "vec" / "vectors_manual.p"
IMG_DIR = DATA_DIR / "img"
EMBED_MODEL_NAME = "dragonkue/BGE-m3-ko"
MODEL_NAME = "gpt-5.4"
TOP_K = 3
TEMPERATURE = 0.2
PAGE_TITLE_PATTERN = re.compile(r"page_(\d+)", re.IGNORECASE)
IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".webp")

st.set_page_config(
    page_title="Model Y L Manual",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# API 키 설정 (secrets에서 가져오거나 기본값 사용)
try:
    API_KEY = st.secrets.get("openai_api_key", "")
except Exception:
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


def page_stem_from_item(title: str | None, filename: str | None = None) -> str | None:
    """page_003.txt / page_003 → page_003"""
    for source in (title, filename):
        if not source:
            continue
        stem = Path(str(source)).stem
        if PAGE_TITLE_PATTERN.search(stem):
            return stem
    return None


def format_page_label(title: str | None, filename: str | None = None) -> str:
    stem = page_stem_from_item(title, filename)
    if stem:
        match = PAGE_TITLE_PATTERN.search(stem)
        if match:
            return f"매뉴얼 {int(match.group(1))}페이지 ({stem})"
    return title or filename or "알 수 없는 페이지"


def resolve_page_image(title: str | None, filename: str | None = None) -> Path | None:
    """지문 파일명과 동일한 stem의 이미지를 data/img에서 찾습니다."""
    stem = page_stem_from_item(title, filename)
    if not stem:
        return None

    for ext in IMAGE_EXTENSIONS:
        image_path = IMG_DIR / f"{stem}{ext}"
        if image_path.is_file():
            return image_path
    return None


def search_similar_passages(query: str, top_k: int = 5) -> list[dict[str, Any]]:
    """vectors_manual.p에서 질문과 유사한 지문을 검색하고 대응 이미지 경로를 붙입니다."""
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
        title = item.get("title")
        filename = item.get("filename")
        image_path = resolve_page_image(title, filename)
        results.append(
            {
                "score": float(scores[index]),
                "filename": filename,
                "title": title,
                "text": item.get("text") or "",
                "image_path": str(image_path) if image_path else None,
                "item": item,
            }
        )
    return results


def build_rag_system_prompt(rag_results: list[dict[str, Any]]) -> str:
    if not rag_results:
        return (
            "당신은 Tesla Model Y L 오너 매뉴얼 전문 도우미입니다. "
            "현재 질문과 관련된 매뉴얼 지문을 찾지 못했습니다. "
            "매뉴얼에 없는 내용은 추측하지 말고, 정보가 없음을 안내하세요."
        )

    context_blocks: list[str] = []
    for rank, result in enumerate(rag_results, start=1):
        label = format_page_label(result.get("title"), result.get("filename"))
        score = float(result.get("score", 0.0))
        text = (result.get("text") or "").strip() or "(내용 없음)"
        context_blocks.append(
            f"### 참고 지문 {rank}: {label}\n"
            f"유사도: {score:.4f}\n"
            f"---\n{text}"
        )

    context = "\n\n".join(context_blocks)
    return f"""당신은 Tesla Model Y 오너 매뉴얼 전문 도우미입니다.
아래 [매뉴얼 참고 지문]만을 바탕으로 사용자 질문에 정확하고 친절하게 답변하세요.

[답변 규칙]
- 참고 지문에 없는 내용은 추측하지 말고, 매뉴얼에 해당 정보가 없다고 안내하세요.
- 답변에 관련 매뉴얼 페이지 번호를 함께 알려주세요.
- 안전·경고 관련 내용은 주의사항을 빠짐없이 전달하세요.
- 한국어로 답변하세요.

[매뉴얼 참고 지문]
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
            temperature=TEMPERATURE,
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


def render_passage_with_image(result: dict[str, Any], rank: int, *, expanded: bool = False) -> None:
    """검색된 지문 텍스트와 동일 페이지 이미지를 함께 표시합니다."""
    label = format_page_label(result.get("title"), result.get("filename"))
    score = float(result.get("score", 0.0))
    text = (result.get("text") or "_텍스트 없음_").strip()
    image_path = result.get("image_path")

    with st.expander(f"{rank}. {label} (유사도: {score:.4f})", expanded=expanded):
        col_text, col_img = st.columns([1.2, 1.0], gap="medium")
        with col_text:
            st.markdown("**참고 지문**")
            st.markdown(text.replace("\n", "  \n"))
        with col_img:
            st.markdown("**매뉴얼 이미지**")
            if image_path and Path(image_path).is_file():
                st.image(image_path, use_container_width=True, caption=Path(image_path).name)
            else:
                stem = page_stem_from_item(result.get("title"), result.get("filename")) or "?"
                st.caption(f"이미지 없음: `data/img/{stem}.png`")


try:
    with st.spinner("임베딩 모델 및 벡터 DB 준비 중..."):
        _ = get_bge_m3_ko_model()
        _ = get_manual_embeddings_matrix()
except Exception as error:
    st.error(str(error))
    st.stop()


st.markdown("# Model Y Manual")
st.markdown("*Tesla Model Y 오너 매뉴얼 RAG 챗봇*")
st.caption("질문 → 유사 지문 검색 → API 답변 → 동일 페이지 이미지 표시")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "rag_results" not in st.session_state:
    st.session_state.rag_results = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        # 이전 assistant 답변에 연결된 참고 이미지 다시 표시
        if message["role"] == "assistant" and message.get("rag_results"):
            st.markdown("#### 참고 매뉴얼 이미지")
            image_cols = st.columns(min(3, len(message["rag_results"])))
            for idx, result in enumerate(message["rag_results"]):
                image_path = result.get("image_path")
                with image_cols[idx % len(image_cols)]:
                    if image_path and Path(image_path).is_file():
                        st.image(
                            image_path,
                            use_container_width=True,
                            caption=format_page_label(result.get("title"), result.get("filename")),
                        )

if prompt := st.chat_input("Model Y 매뉴얼에 대해 질문해보세요"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 1) vectors_manual.p에서 정답 후보 지문 검색
    try:
        with st.spinner("관련 매뉴얼 지문 검색 중..."):
            rag_results = search_similar_passages(prompt, top_k=TOP_K)
    except Exception as error:
        rag_results = []
        st.warning(f"RAG 검색 중 오류가 발생했습니다: {error}")

    st.session_state.rag_results = rag_results
    system_prompt = build_rag_system_prompt(rag_results)

    # 2) 검색된 지문으로 API 답변 생성 + 3) 동일 img 출력
    with st.chat_message("assistant"):
        collected: list[str] = []
        st.write_stream(
            stream_rag_answer(
                API_KEY,
                MODEL_NAME,
                system_prompt,
                [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
                collected,
            )
        )
        response_text = "".join(collected)

        if rag_results:
            st.markdown("#### 참고 매뉴얼 이미지")
            image_cols = st.columns(min(3, len(rag_results)))
            for idx, result in enumerate(rag_results):
                image_path = result.get("image_path")
                with image_cols[idx % len(image_cols)]:
                    if image_path and Path(image_path).is_file():
                        st.image(
                            image_path,
                            use_container_width=True,
                            caption=format_page_label(result.get("title"), result.get("filename")),
                        )
                    else:
                        stem = page_stem_from_item(result.get("title"), result.get("filename")) or "?"
                        st.caption(f"이미지 없음: `{stem}`")

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": response_text,
                "rag_results": [
                    {
                        "title": r.get("title"),
                        "filename": r.get("filename"),
                        "score": r.get("score"),
                        "image_path": r.get("image_path"),
                        "text": r.get("text"),
                    }
                    for r in rag_results
                ],
            }
        )

st.markdown("---")
st.markdown("### 참고 후보 문서")
rag_results_display = st.session_state.get("rag_results", [])
if rag_results_display:
    for rank, result in enumerate(rag_results_display, start=1):
        render_passage_with_image(result, rank, expanded=False)
else:
    st.caption("질문을 입력하면 관련 지문과 이미지가 여기에 표시됩니다.")

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
    /* 사이드바 및 토글 버튼 완전 숨김 */
    [data-testid="stSidebar"],
    [data-testid="stSidebarCollapsedControl"],
    [data-testid="collapsedControl"],
    section[data-testid="stSidebar"] {
        display: none !important;
        width: 0 !important;
        min-width: 0 !important;
    }
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
