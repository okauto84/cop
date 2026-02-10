# -*- coding: utf-8 -*-

import streamlit as st
from openai import OpenAI
import time
import pandas as pd
import json
from collections import Counter
from datetime import datetime

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False

# 페이지 설정
st.set_page_config(
    page_title="kipi-messenger",
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
    st.markdown("### 🔍 Rules")

    # 각종 설정 옵션들
    with st.expander("📁 개요", expanded=False):
        st.write("챗봇 인터페이스")

    with st.expander("📍 출력방법", expanded=False):
        output_method = st.selectbox(
            "출력 방식 선택",
            ["실시간 출력", "일괄 출력"],
            index=0
        )

    with st.expander("💭 알고리즘", expanded=False):
        model_name = st.selectbox(
            "모델 선택",
            ["gpt-5-mini"],
            index=0
        )

    with st.expander("📄 라이센스", expanded=False):
        st.write("MIT License")

    with st.expander("📊 표시설정", expanded=False):
        show_stats = st.checkbox("통계 표시", value=False)


# 메인 화면
st.markdown("# okauto")

# 파일 첨부 영역 (Powered by OpenAI 위치)
uploaded_file = st.file_uploader(
    "📎 엑셀 파일 첨부 (.xlsx)",
    type=["xlsx"],
    help="첫 행이 헤더인 엑셀 파일을 업로드하면 발신일시·제목·발신인·수신인·참조·내용으로 JSON을 생성합니다."
)
attached_json = None  # 첨부된 JSON 데이터 (변수에 저장)

if uploaded_file is not None:
    try:
        df = pd.read_excel(uploaded_file, header=0, engine="openpyxl")
        df.columns = df.columns.astype(str).str.strip()
        # 키 순서: 발신일시, 제목, 발신인, 수신인, 참조, 내용 (엑셀 컬럼명 매칭 또는 순서로 매핑)
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
                    # 수신인: 콤마(,) 기준으로 리스트로 저장
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

# 막대 그래프: 발신인 / 발신일시 (JSON 데이터가 있을 때만)
_chart_data = st.session_state.get("attached_json") or attached_json
if _chart_data and len(_chart_data) > 0:
    # 발신인 기준 횟수
    sender_counts = {}
    for item in _chart_data:
        v = item.get("발신인")
        if v is None or (isinstance(v, str) and not v.strip()):
            label = "(없음)"
        else:
            label = str(v).strip()
        sender_counts[label] = sender_counts.get(label, 0) + 1
    df_sender = pd.DataFrame(
        list(sender_counts.items()),
        columns=["발신인", "건수"]
    ).set_index("발신인").sort_values("건수", ascending=False)

    # 발신일시 기준 횟수 (날짜별)
    date_strs = []
    for item in _chart_data:
        v = item.get("발신일시")
        if v is None:
            date_strs.append("(없음)")
        else:
            s = str(v)
            date_strs.append(s[:10] if len(s) >= 10 else s)
    date_counts = Counter(date_strs)
    df_date = pd.DataFrame(
        list(date_counts.items()),
        columns=["발신일시", "건수"]
    ).set_index("발신일시")
    try:
        df_date.index = pd.to_datetime(df_date.index, errors="coerce")
        df_date = df_date[df_date.index.notna()].sort_index()
        df_date.index = df_date.index.strftime("%Y-%m-%d")
    except Exception:
        df_date = df_date.sort_index()

    col_left, col_right = st.columns(2)
    with col_left:
        st.subheader("발신인별 건수")
        st.bar_chart(df_sender)
    with col_right:
        st.subheader("발신일시별 건수")
        st.bar_chart(df_date)

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

if "total_tokens" not in st.session_state:
    st.session_state.total_tokens = 0


def extract_query_info(query: str) -> dict:
    """
    LLM API를 사용해 질문(query)에서 '발신인', '수신인', '발신일시', '내용' 정보를 추출.
    다양한 표현 방식을 이해하여 정보를 추출합니다.
    """
    if not API_KEY or API_KEY == "your-openai-api-key-here":
        return {"발신인": "", "수신인": "", "발신일시": "", "내용": query}
    try:
        client = OpenAI(api_key=API_KEY)
        prompt = f"""다음 질문에서 '발신인', '수신인', '발신일시', '내용' 정보를 추출해주세요.
다양한 표현 방식을 이해하여 정보를 추출하세요:
- 발신인: 보낸 사람, 작성자, 발신자 등 다양한 표현으로 언급된 사람 이름
- 수신인: 받는 사람, 수신자, 대상자 등 다양한 표현으로 언급된 사람 이름 (여러 명일 수 있음)
- 발신일시: 날짜·시간 관련 표현 (예: 2024년 1월, 1/15, 지난주, 월요일 등)
- 내용: 질문의 핵심 주제·키워드·찾고자 하는 내용. 없으면 전체 질문을 그대로 넣으세요.

정보가 명시되지 않은 필드는 빈 문자열("")로 반환하세요.
JSON 형식으로만 응답하세요. 다른 설명은 하지 마세요.

질문: {query}

응답 형식:
{{
  "발신인": "추출된 발신인 또는 빈 문자열",
  "수신인": "추출된 수신인 또는 빈 문자열",
  "발신일시": "추출된 발신일시 또는 빈 문자열",
  "내용": "추출된 내용 또는 전체 질문"
}}"""
        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
        )
        result_text = response.choices[0].message.content.strip()
        try:
            result = json.loads(result_text)
            return {
                "발신인": result.get("발신인", ""),
                "수신인": result.get("수신인", ""),
                "발신일시": result.get("발신일시", ""),
                "내용": result.get("내용", query),
            }
        except json.JSONDecodeError:
            return {"발신인": "", "수신인": "", "발신일시": "", "내용": query}
    except Exception:
        return {"발신인": "", "수신인": "", "발신일시": "", "내용": query}


def search_similar_content(extracted_info: dict, items: list, top_k: int = 2) -> list:
    """
    추출된 '발신인', '수신인', '발신일시', '내용'을 기준으로 JSON의 해당 필드들과 일치하는 정보로 TF-IDF 검색.
    다양한 표현 방식을 고려하여 유사한 정보를 찾습니다. Top2 반환.
    """
    if not HAS_SKLEARN or not items:
        return []
    
    # 검색 쿼리: 발신인 + 수신인 + 발신일시 + 내용 (추출된 정보 모두 결합)
    query_parts = []
    if extracted_info.get("발신인", "").strip():
        query_parts.append(f"발신인: {extracted_info['발신인'].strip()}")
    if extracted_info.get("수신인", "").strip():
        query_parts.append(f"수신인: {extracted_info['수신인'].strip()}")
    if extracted_info.get("발신일시", "").strip():
        query_parts.append(f"발신일시: {extracted_info['발신일시'].strip()}")
    if extracted_info.get("내용", "").strip():
        query_parts.append(extracted_info["내용"].strip())
    search_query = " ".join(query_parts) if query_parts else extracted_info.get("내용", "")
    
    if not search_query.strip():
        return []
    
    # 각 JSON 항목의 '발신인', '수신인', '발신일시', '내용'을 결합해 검색 대상 텍스트 생성
    doc_texts = []
    for item in items:
        parts = []
        sender = item.get("발신인")
        if sender:
            parts.append(f"발신인: {sender}")
        receiver = item.get("수신인")
        if isinstance(receiver, list):
            receiver = ", ".join(receiver) if receiver else ""
        if receiver:
            parts.append(f"수신인: {receiver}")
        sent_time = item.get("발신일시")
        if sent_time:
            parts.append(f"발신일시: {sent_time}")
        content = item.get("내용")
        if content:
            parts.append(str(content))
        doc_texts.append(" ".join(parts))
    
    if not doc_texts:
        return []
    
    # TF-IDF 벡터화 (다양한 표현 방식 고려를 위해 문자 단위 n-gram 사용)
    vectorizer = TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 4))
    try:
        X = vectorizer.fit_transform(doc_texts)
        q_vec = vectorizer.transform([search_query])
        sims = cosine_similarity(q_vec, X).ravel()
    except Exception:
        return []
    top_indices = sims.argsort()[-top_k:][::-1]
    result = []
    for i in top_indices:
        if sims[i] <= 0:
            continue
        result.append({"index": int(i), "score": float(sims[i]), "item": items[i]})
    return result


def build_context_prompt(query: str, similar_items: list) -> str:
    """검색 결과 Top2의 내용 범위에서 질의에 대한 답변을 생성하도록 프롬프트 생성."""
    if not similar_items:
        return query
    parts = [
        "아래 [참고 자료]의 내용 범위에서만 [질문]에 답변하세요.",
        "참고 자료에 없는 내용은 추측하거나 추가 정보를 제공하지 마세요.",
        "참고 자료의 내용만을 바탕으로 정확하고 간결하게 답변하세요.",
        "",
        "## 참고 자료 (Top 2)",
        "---",
    ]
    for i, rec in enumerate(similar_items, start=1):
        item = rec["item"]
        sender = item.get("발신인") or ""
        receiver = item.get("수신인")
        if isinstance(receiver, list):
            receiver = ", ".join(receiver) if receiver else ""
        receiver = receiver or ""
        sent_time = item.get("발신일시") or ""
        title = item.get("제목") or ""
        content = (item.get("내용") or "").strip() or "(내용 없음)"
        
        parts.append(f"[{i}] 발신인: {sender} | 수신인: {receiver} | 발신일시: {sent_time} | 제목: {title}")
        parts.append(content)
        parts.append("")
    parts.extend([
        "---",
        "## 질문",
        query.strip(),
        "",
        "위 참고 자료(Top 2)의 내용 범위에서만 질문에 답변하세요."
    ])
    return "\n".join(parts)


# OpenAI API 호출 함수
def call_openai_api(prompt: str) -> str:
    """
    OpenAI API를 호출하는 함수
    """
    try:
        if not API_KEY or API_KEY == "your-openai-api-key-here":
            return "⚠️ API 키가 설정되지 않았습니다. Streamlit secrets의 openai_api_key 또는 코드의 API_KEY 변수를 설정해주세요.\n\n" \
                   f"데모용 응답: '{prompt}'에 대한 답변입니다. 실제 환경에서는 OpenAI API가 연동되어 정확한 답변을 제공할 것입니다."

        # OpenAI 클라이언트 초기화
        client = OpenAI(api_key=API_KEY)

        # API 호출
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "user", "content": prompt}
            ],
        )

        # 응답 텍스트 추출
        response_text = response.choices[0].message.content

        # 토큰 사용량 업데이트
        if hasattr(response, 'usage'):
            tokens_used = response.usage.total_tokens if hasattr(response.usage, 'total_tokens') else 0
            st.session_state.total_tokens += tokens_used
        else:
            # 대략적인 토큰 수 계산 (단어 수 기반)
            st.session_state.total_tokens += len(prompt.split()) + len(response_text.split())

        return response_text

    except Exception as e:
        error_msg = str(e)
        if "API_KEY" in error_msg or "authentication" in error_msg.lower() or "invalid" in error_msg.lower():
            return f"🔑 API 키 오류: API 키를 확인해주세요.\n\n에러 상세: {error_msg}"
        elif "quota" in error_msg.lower() or "limit" in error_msg.lower() or "rate" in error_msg.lower():
            return f"📊 사용량 한도 초과: API 사용량을 확인해주세요.\n\n에러 상세: {error_msg}"
        else:
            return f"❌ API 호출 중 오류가 발생했습니다: {error_msg}\n\n" \
                   f"데모용 응답: '{prompt}'에 대한 답변을 드리겠습니다."

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

    # (1) API를 통해 query에서 정보 추출
    data_for_search = st.session_state.get("attached_json") or []
    extracted_info = {}
    similar_items = []
    
    with st.chat_message("assistant"):
        if data_for_search:
            with st.spinner("질문에서 정보를 추출하는 중..."):
                extracted_info = extract_query_info(prompt)
            
            # (2) 추출된 정보를 기반으로 TF-IDF 검색 (Top2)
            if HAS_SKLEARN:
                with st.spinner("유사한 데이터를 검색하는 중..."):
                    similar_items = search_similar_content(extracted_info, data_for_search, top_k=2)
            
            # Top2 검색 결과 화면 출력 (접고 펼 수 있게)
            if similar_items:
                st.markdown("#### 🔍 검색 결과 (Top 2)")
                
                # 추출된 정보 표시 (발신인, 수신인, 발신일시, 내용)
                with st.expander("📋 추출된 정보", expanded=False):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**발신인**: {extracted_info.get('발신인', '(없음)')}")
                        st.write(f"**수신인**: {extracted_info.get('수신인', '(없음)')}")
                    with col2:
                        st.write(f"**발신일시**: {extracted_info.get('발신일시', '(없음)')}")
                        content_preview = extracted_info.get('내용', '(없음)')
                        st.write(f"**내용**: {content_preview[:100] + '...' if len(content_preview) > 100 else content_preview}")
                
                # Top2 결과를 각각 expander로 표시
                for i, rec in enumerate(similar_items, start=1):
                    item = rec["item"]
                    score = rec["score"]
                    
                    # 제목 생성
                    title_part = item.get("제목") or "(제목 없음)"
                    expander_title = f"**[{i}] 유사도: {score:.4f}** | {title_part}"
                    
                    with st.expander(expander_title, expanded=(i == 1)):
                        # 발신인, 수신인, 발신일시, 내용을 구분해서 표시
                        col_info, col_content = st.columns([1, 2])
                        
                        with col_info:
                            st.markdown("**📌 기본 정보**")
                            st.markdown(f"- **발신인**: {item.get('발신인', '(없음)')}")
                            receiver = item.get("수신인")
                            if isinstance(receiver, list):
                                receiver = ", ".join(receiver) if receiver else "(없음)"
                            st.markdown(f"- **수신인**: {receiver if receiver else '(없음)'}")
                            st.markdown(f"- **발신일시**: {item.get('발신일시', '(없음)')}")
                            st.markdown(f"- **제목**: {item.get('제목', '(없음)')}")
                        
                        with col_content:
                            st.markdown("**📄 내용**")
                            content = (item.get("내용") or "").strip() or "(내용 없음)"
                            # 내용을 스타일이 적용된 div로 표시
                            content_html = f"""
                            <div style="
                                background-color: #f5f5f5;
                                color: #1a1a1a;
                                padding: 12px;
                                border-radius: 6px;
                                border: 1px solid #e0e0e0;
                                min-height: 150px;
                                font-size: 14px;
                                line-height: 1.6;
                                white-space: pre-wrap;
                                word-wrap: break-word;
                            ">
                            {content.replace('<', '&lt;').replace('>', '&gt;')}
                            </div>
                            """
                            st.markdown(content_html, unsafe_allow_html=True)
                        
                        st.markdown("---")
            else:
                if not HAS_SKLEARN:
                    st.caption("⚠️ 유사도 검색을 위해 `pip install scikit-learn`이 필요합니다.")
                else:
                    st.caption("검색 결과가 없습니다.")
        else:
            st.caption("💡 엑셀 파일을 첨부하면 질문에서 정보를 추출하고 유사한 데이터를 검색합니다.")

        # 참고 자료 기반 프롬프트로 OpenAI 답변 생성
        api_prompt = build_context_prompt(prompt, similar_items)

        if output_method == "실시간 출력":
            with st.spinner("OpenAI가 답변을 생성하고 있습니다..."):
                response = call_openai_api(api_prompt)
            message_placeholder = st.empty()
            displayed_text = ""
            for char in response:
                displayed_text += char
                message_placeholder.markdown(displayed_text + "▌")
                time.sleep(0.01)
            message_placeholder.markdown(response)
        else:
            with st.spinner("OpenAI가 답변을 생성하고 있습니다..."):
                response = call_openai_api(api_prompt)
            st.markdown(response)

    # AI 응답을 세션에 저장
    st.session_state.messages.append({"role": "assistant", "content": response})

# 통계 표시
if show_stats and st.session_state.messages:
    st.markdown("---")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("💬 총 대화 수", len(st.session_state.messages)//2)

    with col2:
        st.metric("🎯 현재 모델", model_name)

    with col3:
        st.metric("📊 예상 토큰", st.session_state.total_tokens)

# 하단 정보 및 컨트롤
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    st.info("💡 **팁**: 구체적이고 명확한 질문을 하시면 더 좋은 답변을 받을 수 있습니다.")

with col2:
    if st.button("🗑️ 대화 초기화"):
        st.session_state.messages = []
        st.session_state.total_tokens = 0
        st.rerun()

with col3:
    if st.button("💾 대화 저장"):
        if st.session_state.messages:
            chat_history = ""
            for msg in st.session_state.messages:
                role = "사용자" if msg["role"] == "user" else "AI"
                chat_history += f"**{role}**: {msg['content']}\n\n"

            st.download_button(
                label="📥 대화 내용 다운로드",
                data=chat_history,
                file_name=f"wonq_chat_{time.strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )
        else:
            st.warning("저장할 대화가 없습니다.")

# API 키 안내
if not API_KEY or API_KEY == "your-openai-api-key-here":
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

    .stMetric {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #e0e0e0;
    }
</style>
""", unsafe_allow_html=True)
