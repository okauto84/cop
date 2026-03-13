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

    /* 좌측 | 메인 | 우측 사이드바 구분 라인 (세로), 좌·메인 간격 축소 */
    [data-testid="column"] {
        border-right: 1px solid #dee2e6;
        padding-right: 0.35rem;
        padding-left: 0.35rem;
    }
    [data-testid="column"]:first-of-type { padding-left: 0; padding-right: 0.35rem; }
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

    /* 청구항 패널: 화면 전체가 슬라이드로 등장, 청구항 context도 동일한 슬라이드에 함께 노출 */
    .claims-panel-slide {
        max-height: calc(100vh - 120px);
        overflow: hidden;
        animation: panelSlideIn 0.5s ease-out forwards;
    }
    @keyframes panelSlideIn {
        from { opacity: 0; transform: translateX(-100%); }
        to { opacity: 1; transform: translateX(0); }
    }
    .claims-panel {
        max-height: inherit;
        overflow-y: auto;
        padding-top: 0.5rem;
    }
    .claims-panel .claim-item {
        margin-bottom: 14px;
        padding: 12px;
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        font-size: 13px;
        line-height: 1.55;
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

# 청구항 패널 표시 여부 (청구항 보기 버튼 토글)
if "claims_visible" not in st.session_state:
    st.session_state.claims_visible = False


def toggle_claims():
    st.session_state.claims_visible = not st.session_state.claims_visible


# 청구항 샘플 데이터 (항별)
CLAIMS_DATA = [
    ("청구항 1", "흐름전극기반 축전식 탈염을 위한 슬러리 탄소 양극을 제조하는 방법에 있어서, 집전체와 음이온교환막을 포함하는 양극유로를 준비하는 단계와; 상기 양극유로의 집전체와 전기적으로 분리된 집전체 및 양이온교환막을 포함하는 음극유로를 준비하는 단계와; 상기 양극유로와 상기 음극유로를 적층하여 유로 일체형 전극을 형성하는 단계를 포함하는 것을 특징으로 하는 흐름전극기반 축전식 탈염을 위한 슬러리 탄소 양극의 제조방법."),
    ("청구항 2", "제1항에 있어서, 상기 양극유로를 준비하는 단계는 상기 집전체 상에 음이온교환막을 코팅하거나 라미네이션하는 단계를 포함하는 것을 특징으로 하는 방법."),
    ("청구항 3", "제1항에 있어서, 상기 음극유로를 준비하는 단계는 상기 집전체 상에 양이온교환막을 코팅하거나 라미네이션하는 단계를 포함하는 것을 특징으로 하는 방법."),
    ("청구항 4", "제1항 내지 제3항 중 어느 한 항에 있어서, 상기 유로 일체형 전극은 롤-투-롤 공정으로 형성되는 것을 특징으로 하는 방법."),
]

# 검색 결과 샘플 데이터 (게시판 목록) — 상단 정의로 선택/사이드바에서 공유
RESULT_DATA = {
    "순번": [1, 2, 3, 4, 5],
    "구분": ["거절", "등록", "소멸", "등록", "거절"],
    "CPC분류": ["C02F 1/4691\nC02F 2201/46", "C02F 1/46109\nC02F 1/469", "C02F 1/46109\nC02F 1/4691", "C25B 11/02\nC02F 1/4691", "C25B 11/043\nC25B 11/071"],
    "발명의 명칭": [
        "흐름 축전식 탈염 전극 및 모듈의 제조방법",
        "일체형 축전탈이온 및 전극 및 제조방법",
        "축전식 탈염전극용 탄소복합체 및 이의 제조방법",
        "유로 일체형 축전식 탈염전극 및 이의 제조방법",
        "축전식 전기탈염용 단위셀 및 이의 제조방법"
    ],
    "출원번호": ["1020150049250", "1020130133733", "1020100119911", "1020150043127", "1020130080991"],
    "출원일자": ["20150407", "20131105", "20101129", "20150327", "20130710"]
}
df_result = pd.DataFrame(RESULT_DATA)
# 테이블 표시용: 순번 제거 (체크박스는 data_editor에서 selection_mode 없이 제거)
df_display = df_result.drop(columns=["순번"]).copy()

# 좌측 | 청구항(토글) | 메인 | 우측 사이드바 — 청구항 보기 시 메인 구역 축소
if st.session_state.claims_visible:
    left_col, claims_col, right_col, right_sidebar = st.columns([1, 1, 2, 1])
else:
    left_col, claims_col, right_col, right_sidebar = st.columns([1, 0.01, 3, 1])

# ==========================================
# 좌측 패널: 검색 조건 및 구성요소
# ==========================================
with left_col:
    # 요청하신 '요약정보' 탭 추가
    tab_search, tab_summary = st.tabs(["대상 검색", "대상 AI요약"])
    
    with tab_search:
        # 출원번호 입력
        st.markdown("**⚙️ 심사 대상 건 입력**")
        st.text_input("출원번호", value="1020200091668", label_visibility="collapsed")
        
        # 문장검색 영역
        st.text_area(
            "문장 검색",
            placeholder="입력한 문장으로 유사 문서를 찾습니다. AND(&), OR(|) 연산자는 사용할 수 없습니다.",
            height=100,
            label_visibility="collapsed",
            key="search_sentence"
        )
        
        btn_col1, btn_col2 = st.columns(2)
        with btn_col1: st.button("🔍 요소 추출", use_container_width=True, key="btn_search")
        with btn_col2: st.button("🔄 초기화", use_container_width=True, key="btn_reset")
        
        
        st.markdown('<hr style="border:1px solid #ddd; margin: 5px 0px;">', unsafe_allow_html=True)
        
        # 구성요소관련 영역
        st.markdown("**⚙️ 기술 구성요소**")
        comp_btn_col1, comp_btn_col2 = st.columns(2)
        with comp_btn_col1: st.button("요소 추가", use_container_width=True, key="btn_comp_add")
        with comp_btn_col2: st.button("청구항 보기", use_container_width=True, key="btn_claim", on_click=toggle_claims)
        
        # 구성요소 리스트 (체크박스 + 텍스트)
        components = [
            "흐름전극기반 축전식 탈염을 위한 슬러리 탄소 적극을 제조하는 방법",
            "집전체와 음이온교환막을 포함하는 양극유로를 준비하는 단계",
            "상기 양극유로의 집전체와 전기적으로 분리된 집전체 및 양이온..."
        ]
        
        
        for i, comp in enumerate(components):
            c1, c2 = st.columns([1, 9])
            with c1: st.checkbox("", value=True, key=f"comp_{i}")
            with c2: st.info(comp) # 박스 형태로 텍스트 출력
            
        st.button("🔍 검색", use_container_width=True, type="primary", key="btn_research")

    with tab_summary:
        st.markdown(SUMMARY_HTML, unsafe_allow_html=True)

# ==========================================
# 청구항 패널 (좌측 탭 오른쪽, 토글 시에만 표시)
# ==========================================
with claims_col:
    if st.session_state.claims_visible:
        claims_items_html = "".join(
            f'<div class="claim-item">'
            f'<div style="color: #1e3a8a; font-weight: bold; margin-bottom: 6px;">{title}</div>'
            f'<div style="color: #374151;">{text}</div></div>'
            for title, text in CLAIMS_DATA
        )
        st.markdown(
            f'<div class="claims-panel-slide">'
            f'<div class="claims-panel">'
            f'<div style="color: #1e3a8a; font-weight: bold; margin-bottom: 10px; font-size: 0.95rem;">📋 청구항</div>'
            f'{claims_items_html}'
            f'</div></div>',
            unsafe_allow_html=True,
        )

# ==========================================
# 우측 패널: 검색 결과 데이터프레임
# ==========================================
with right_col:
    tab_result, tab_info = st.tabs(["1020200091668 검색 결과 ✕", "⌂ INFO"])

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