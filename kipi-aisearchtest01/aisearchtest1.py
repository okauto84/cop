# -*- coding: utf-8 -*-


import streamlit as st
import pandas as pd
from pathlib import Path

# 화면 넓게 쓰기
st.set_page_config(layout="wide", page_title="AI 특허 검색 시스템")

# CSS: 헤더 아래로 메인 화면 내려서 탭 클릭 가능하게, 시인성, 구분 라인, 우측 사이드바
st.markdown("""
    <style>
    /* 메인 화면 전체를 아래로 내려서 Streamlit 헤더에 탭이 가리지 않게 */
    .block-container {
        padding-top: 3rem;
        padding-bottom: 2rem;
        max-width: 100%;
    }
    .main .block-container { padding-top: 3rem; }
    div[data-testid="stText"] { font-size: 14px; }

    /* 좌측 | 메인 | 우측 사이드바 구분 라인 (세로) */
    [data-testid="column"] {
        border-right: 1px solid #dee2e6;
        padding-right: 1rem;
        padding-left: 0.5rem;
    }
    [data-testid="column"]:first-of-type { padding-left: 0; }
    /* 우측 사이드바: 고정 높이 + 스크롤바 */
    [data-testid="column"]:last-of-type {
        border-right: none;
        padding-right: 0;
        padding-top: 0.5rem;
        max-height: calc(100vh - 120px);
        overflow-y: auto;
        overflow-x: visible;
        min-height: 200px;
    }
    [data-testid="column"]:last-of-type > div {
        padding-top: 0.25rem;
        max-height: inherit;
    }
    [data-testid="column"]:last-of-type .stMarkdown { animation: slideIn 0.3s ease-out; }

    /* 탭 구분: 탭 버튼 영역 하단 라인, 탭 내용 영역 테두리 */
    [data-testid="stTabs"] {
        border: 1px solid #dee2e6;
        border-radius: 6px;
        padding: 0 8px 8px;
        margin-bottom: 8px;
    }
    [data-testid="stTabs"] > div:first-child {
        border-bottom: 1px solid #dee2e6;
        margin-bottom: 4px;
    }

    @keyframes slideIn {
        from { opacity: 0; transform: translateX(20px); }
        to { opacity: 1; transform: translateX(0); }
    }
    </style>
""", unsafe_allow_html=True)

# 선택된 문헌(게시글) 인덱스 — 행 선택 시 사이드바에 상세 표시
if "selected_row_index" not in st.session_state:
    st.session_state.selected_row_index = None

# 발명의 3요소 (AI 요약) HTML — tab_summary와 right_sidebar에서 공통 사용
SUMMARY_HTML = """
<div style="font-family: 'Malgun Gothic', '맑은 고딕', sans-serif; max-width: 600px;">
    <div style="color: #1e3a8a; font-size: 1.15rem; font-weight: bold; margin-bottom: 16px;">
        💡 발명의 3요소 (AI 요약)
    </div>
    <div style="background-color: #fdf2f2; border: 1.5px solid #fecaca; border-radius: 8px; padding: 14px 12px; margin-bottom: 12px;">
        <div style="color: #b91c1c; font-weight: bold; font-size: 0.95rem; margin-bottom: 6px;">
            ⚠️ 해결과제 <span style="font-size: 0.8em; font-weight: normal;">(Problem)</span>
        </div>
        <div style="color: #374151; font-size: 0.9rem; line-height: 1.6;">
            창문형 에어컨 설치 시 본체와 커텐프레임 사이의 유격으로 인한 냉기 누설 및 조립 공정의 복잡함을 해결하고자 함.
        </div>
    </div>
    <div style="background-color: #f0fdf4; border: 1.5px solid #bbf7d0; border-radius: 8px; padding: 14px 12px; margin-bottom: 12px;">
        <div style="color: #15803d; font-weight: bold; font-size: 0.95rem; margin-bottom: 6px;">
            🎯 발명의 목적 <span style="font-size: 0.8em; font-weight: normal;">(Object)</span>
        </div>
        <div style="color: #374151; font-size: 0.9rem; line-height: 1.6;">
            베이스팬 내부에 관통형 가이드공을 형성하여 커텐프레임의 슬라이딩 기밀성을 극대화하고 외관을 미려하게 함.
        </div>
    </div>
    <div style="background-color: #eff6ff; border: 1.5px solid #bfdbfe; border-radius: 8px; padding: 14px 12px; margin-bottom: 12px;">
        <div style="color: #1d4ed8; font-weight: bold; font-size: 0.95rem; margin-bottom: 6px;">
            ✨ 발명의 효과 <span style="font-size: 0.8em; font-weight: normal;">(Effect)</span>
        </div>
        <div style="color: #374151; font-size: 0.9rem; line-height: 1.6;">
            부품 수 절감으로 제조 원가를 낮추며, 완벽한 밀폐를 통해 에어컨의 냉방 효율을 획기적으로 향상시킴.
        </div>
    </div>
</div>
"""

# 검색 결과 샘플 데이터 (게시판 목록) — 상단 정의로 선택/사이드바에서 공유
RESULT_DATA = {
    "순번": [1, 2, 3, 4, 5],
    "구분": ["등록", "등록", "등록", "취하", "등록"],
    "CPC분류": ["G06V 20/70\nG06V 20/60", "G06V 10/774\nG06V 10/764", "G06V 20/41\nG06V 10/762", "G06T 7/10\nG06V 20/56", "G06N 3/084\nG06N 3/045"],
    "발명의 명칭": [
        "제로샷 시맨틱 분할 장치 및 방법",
        "소프트 교차-엔트로피 손실을 갖는 시맨틱 분할",
        "도메인 적응형 의미론적 영상 분할 장치 및 방법",
        "실시간 픽셀 단위 기반 시맨틱 분할 장치 및 시스템",
        "시맨틱 분할 모델을 위한 훈련 방법 및 장치, 전자 기기, 저장 매체"
    ],
    "출원번호": ["1020210165598", "1020217012976", "1020200176963", "1020210049720", "1020197038767"],
    "출원일자": ["20211126", "20191010", "20201217", "20210416", "20180727"]
}
df_result = pd.DataFrame(RESULT_DATA)
# 테이블 표시용: 순번 제거 (체크박스는 data_editor에서 selection_mode 없이 제거)
df_display = df_result.drop(columns=["순번"]).copy()

if "selected_row_index" not in st.session_state:
    st.session_state.selected_row_index = None

# 좌측 + 메인 + 우측 사이드바 항상 표시
left_col, right_col, right_sidebar = st.columns([1, 3, 1])

# ==========================================
# 좌측 패널: 검색 조건 및 구성요소
# ==========================================
with left_col:
    # 요청하신 '요약정보' 탭 추가
    tab_search, tab_summary = st.tabs(["입력 검색", "AI 요약"])
    
    with tab_search:
        # 출원번호 입력
        st.markdown("**⚙️ 심사 대상 건 입력**")
        st.text_input("출원번호", value="1070210165598", label_visibility="collapsed")
        
        # 문장검색 영역
        st.caption("입력한 문장으로 유사 문서를 찾습니다. AND(&), OR(|) 연산자는 사용할 수 없습니다.")
        
        
        
        btn_col1, btn_col2 = st.columns(2)
        with btn_col1: st.button("🔍 검색", use_container_width=True, key="btn_search")
        with btn_col2: st.button("🔄 초기화", use_container_width=True, key="btn_reset")
        
        st.divider()
        
        # 구성요소관련 영역
        st.markdown("**⚙️ 기술 구성요소**")
        comp_btn_col1, comp_btn_col2 = st.columns(2)
        with comp_btn_col1: st.button("구성요소추가", use_container_width=True, key="btn_comp_add")
        with comp_btn_col2: st.button("청구항", use_container_width=True, key="btn_claim")
        
        # 구성요소 리스트 (체크박스 + 텍스트)
        components = [
            "입력 이미지를 입력받아 신경망 연산을 통해 비주얼 특징맵을 출력하는 비주얼 인코더",
            "신경망 연산을 통해 클래스별 프로토타입 벡터를 출력하는 시맨틱 인코더",
            "상기 비주얼 특징맵의 픽셀별 채널 벡터를 비교하여 상기 비주얼 특징맵..."
        ]
        
        
        for i, comp in enumerate(components):
            c1, c2 = st.columns([1, 9])
            with c1: st.checkbox("", value=True, key=f"comp_{i}")
            with c2: st.info(comp) # 박스 형태로 텍스트 출력
            
        st.button("🔍 재검색", use_container_width=True, type="primary", key="btn_research")

    with tab_summary:
        st.markdown(SUMMARY_HTML, unsafe_allow_html=True)

# ==========================================
# 우측 패널: 검색 결과 데이터프레임
# ==========================================
with right_col:
    tab_result, tab_info = st.tabs(["1020210165598 검색 ✕", "⌂ INFO"])

    with tab_info:
        st.info("INFO 탭입니다. 필요한 안내 또는 정보를 여기에 표시할 수 있습니다.")

    with tab_result:
        # 보기 옵션
        st.selectbox("보기 옵션", ["50 건씩 보기", "100 건씩 보기", "200 건씩 보기"], label_visibility="collapsed", key="view_opt")

        # 게시판(검색 결과) — 행 클릭 시 우측 사이드바 표시 (Streamlit 1.35+)
        event = st.dataframe(
            df_display,
            key="result_table",
            selection_mode="single-row",
            on_select="rerun",
            use_container_width=True,
            hide_index=True,
            height=600
        )
        if event and getattr(event, "selection", None):
            if event.selection.rows:
                st.session_state.selected_row_index = event.selection.rows[0]
            else:
                st.session_state.selected_row_index = None
        st.caption("행을 클릭하면 우측에 선택 문헌 상세가 표시됩니다.")

        # 하단 페이징 (UI 모방)
        page_col1, page_col2, page_col3, page_col4 = st.columns([8, 0.5, 0.5, 0.5])
        with page_col1:
            st.caption("총 100 건 중 1 ~ 50")
        with page_col2:
            st.button("1", key="page_1")
        with page_col3:
            st.button("2", key="page_2")
        with page_col4:
            st.button("›", key="page_next")

# ==========================================
# 우측 사이드바 (항상 표시): 선택 문헌 상세 + 대표도면 + 발명의 3요소
# ==========================================
with right_sidebar:
    _idx = st.session_state.selected_row_index
    _valid = _idx is not None and 0 <= _idx < len(df_result)
    if _valid:
        row = df_result.iloc[_idx]
        st.markdown("**📌 선택 문헌 상세**")
        st.divider()
        st.markdown("**출원번호**")
        st.write(row["출원번호"])
        st.markdown("**발명의 명칭**")
        st.caption(row["발명의 명칭"])
        st.markdown("**구분**")
        st.write(row["구분"])
        st.markdown("**CPC분류**")
        st.caption(row["CPC분류"].replace("\n", " "))
        st.markdown("**출원일자**")
        st.write(row["출원일자"])
        st.divider()
    else:
        st.divider()
    st.markdown('<div style="padding-top: 6px; margin-bottom: 4px;"><strong>🖼️ 대표도면</strong></div>', unsafe_allow_html=True)
    drawing_path = Path(__file__).parent / "data" / "drawing.jpg"
    if drawing_path.exists():
        st.image(str(drawing_path), use_container_width=True)
    else:
        st.caption("`./data/drawing.jpg` 파일을 추가하면 대표도면이 표시됩니다.")
    st.divider()
    st.markdown("**발명의 3요소 (AI 요약)**")
    st.markdown(SUMMARY_HTML, unsafe_allow_html=True)