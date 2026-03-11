# -*- coding: utf-8 -*-


import streamlit as st
import pandas as pd
from pathlib import Path

# 화면 넓게 쓰기
st.set_page_config(layout="wide", page_title="AI 특허 검색 시스템")


@st.dialog("aisearchtest1-spec.py", width="stretch")
def show_spec_popup():
    """테이블 행 클릭 시 스펙 파일을 실행해 팝업(모달)에 결과 화면 표시"""
    # 팝업이 열릴 때 스크롤바를 맨 위로 위치시킴
    try:
        st.components.v1.html(
            """
            <script>
            (function(){
                var doc = window.parent.document;
                function scrollTop() {
                    var d = doc.querySelector('div[data-testid="stDialog"] div[role="dialog"]');
                    if (d) d.scrollTop = 0;
                }
                scrollTop();
                setTimeout(scrollTop, 100);
                setTimeout(scrollTop, 300);
            })();
            </script>
            """,
            height=0,
        )
    except Exception:
        pass
    spec_path = Path(__file__).parent / "aisearchtest1-spec.py"
    if not spec_path.exists():
        st.warning(f"파일을 찾을 수 없습니다: {spec_path}")
        return
    _orig = getattr(st, "set_page_config", None)
    try:
        spec_content = spec_path.read_text(encoding="utf-8")
        _spec_globals = {"st": st, "pd": pd, "__name__": "__main__"}
        st.set_page_config = lambda *a, **k: None
        exec(compile(spec_content, str(spec_path), "exec"), _spec_globals)
    except Exception as e:
        st.error(f"스펙 실행 오류: {e}")
    finally:
        if _orig is not None:
            st.set_page_config = _orig

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

    /* 스펙 팝업(다이얼로그): 내용 길이에 따라 세로로 늘어남 */
    div[data-testid="stDialog"] div[role="dialog"] {
        width: 90vw !important;
        max-width: 1200px !important;
        min-height: 600px !important;
        max-height: 95vh !important;
        height: auto !important;
        overflow-y: auto !important;
    }
    div[data-testid="stDialog"] div[role="dialog"] [data-testid="stCode"] {
        max-height: none !important;
    }

    /* 테이블 행 선택: 체크박스 → 라디오 버튼 모양(원형) */
    [data-testid="stDataFrame"] input[type="checkbox"],
    [data-testid="stDataFrame"] [data-testid="stCheckbox"] input {
        border-radius: 50% !important;
        width: 16px !important;
        height: 16px !important;
        accent-color: #1e3a8a;
    }
    [data-testid="stDataFrame"] [data-testid="stCheckbox"] {
        padding-left: 0;
    }
    </style>
""", unsafe_allow_html=True)

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

# 좌측 + 메인 + 우측 사이드바 항상 표시
left_col, right_col, right_sidebar = st.columns([1, 3, 1])

# ==========================================
# 좌측 패널: 검색 조건 및 구성요소
# ==========================================
with left_col:
    # 요청하신 '요약정보' 탭 추가
    tab_search, tab_summary = st.tabs(["대상 검색", "대상 AI요약"])
    
    with tab_search:
        # 출원번호 입력
        st.markdown("**⚙️ 심사 대상 건 입력**")
        st.text_input("출원번호", value="1070210165598", label_visibility="collapsed")
        
        # 문장검색 영역
        st.text_area(
            "문장 검색",
            placeholder="입력한 문장으로 유사 문서를 찾습니다. AND(&), OR(|) 연산자는 사용할 수 없습니다.",
            height=100,
            label_visibility="collapsed",
            key="search_sentence"
        )
        
        
        
        btn_col1, btn_col2 = st.columns(2)
        with btn_col1: st.button("🔍 검색", use_container_width=True, key="btn_search")
        with btn_col2: st.button("🔄 초기화", use_container_width=True, key="btn_reset")
        
        st.markdown('<hr style="border:1px solid #ddd; margin: 5px 0px;">', unsafe_allow_html=True)
        
        # 구성요소관련 영역
        st.markdown("**⚙️ 기술 구성요소**")
        comp_btn_col1, comp_btn_col2 = st.columns(2)
        with comp_btn_col1: st.button("요소 추가", use_container_width=True, key="btn_comp_add")
        with comp_btn_col2: st.button("청구항 보기", use_container_width=True, key="btn_claim")
        
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
        pass

    with tab_result:
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
        # 테이블 행(체크박스) 선택이 바뀐 경우에만 팝업 오픈 (다른 버튼 클릭 시에는 미동작)
        if "result_table_last_selection" not in st.session_state:
            st.session_state.result_table_last_selection = None
        current_selection = None
        if event and getattr(event, "selection", None):
            current_selection = event.selection.rows[0] if event.selection.rows else None
        if current_selection is not None and current_selection != st.session_state.result_table_last_selection:
            st.session_state.result_table_last_selection = current_selection
            show_spec_popup()
        if event and getattr(event, "selection", None) and current_selection is None:
            st.session_state.result_table_last_selection = None
        st.caption("행의 체크박스를 클릭하면 상세화면이 팝업으로 열립니다.")

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
# 우측 사이드바 (항상 표시): 대표도면 + 발명의 3요소
# ==========================================
with right_sidebar:
    st.markdown('<div style="padding-top: 6px; margin-bottom: 4px;"><strong>🖼️ 대표도면</strong></div>', unsafe_allow_html=True)
    drawing_path = Path(__file__).parent / "data" / "drawing.jpg"
    if drawing_path.exists():
        st.image(str(drawing_path), use_container_width=True)
    else:
        st.caption("`./data/drawing.jpg` 파일을 추가하면 대표도면이 표시됩니다.")
    
    st.markdown(SUMMARY_HTML, unsafe_allow_html=True)