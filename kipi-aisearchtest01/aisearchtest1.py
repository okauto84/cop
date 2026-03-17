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
        _spec_globals = {"st": st, "pd": pd, "__name__": "__main__", "__file__": str(spec_path)}
        st.set_page_config = lambda *a, **k: None
        exec(compile(spec_content, str(spec_path), "exec"), _spec_globals)
    except Exception as e:
        st.error(f"스펙 실행 오류: {e}")
    finally:
        if _orig is not None:
            st.set_page_config = _orig

# CSS: 헤더 아래로 메인 화면 내려서 탭 클릭 가능하게, 시인성, 구분 라인, 우측 사이드바, 가로 스크롤 방지
st.markdown("""
    <style>
    /* 전체 가로 스크롤 방지 — 뷰포트 너비에 맞춰 동적 조절 */
    html, body, .stApp, [data-testid="stAppViewContainer"], .main {
        max-width: 100vw !important;
        overflow-x: hidden !important;
        box-sizing: border-box;
    }
    /* 메인 화면: 아래로 내려서 헤더에 탭 가리지 않게, 가로는 뷰포트에 맞춤 */
    .block-container {
        padding-top: 3rem;
        padding-bottom: 2rem;
        max-width: 100%;
    }
    .main .block-container {
        padding-top: 3rem;
        max-width: 100% !important;
        width: 100% !important;
        padding-left: 1rem;
        padding-right: 1rem;
        box-sizing: border-box;
    }
    div[data-testid="stText"] { font-size: 14px; }

    /* 메인 4열(좌측|대상|중앙|우측) 한 줄 고정, 상단 정렬, 가로 넘침 방지 */
    div[data-testid="stHorizontalBlock"]:has(> [data-testid="column"]:nth-child(4)) {
        flex-wrap: nowrap !important;
        display: flex !important;
        width: 100% !important;
        max-width: 100% !important;
        align-items: flex-start !important;
        min-width: 0;
    }
    div[data-testid="stHorizontalBlock"]:has(> [data-testid="column"]:nth-child(4)) > [data-testid="column"] {
        min-width: 0;
        flex-shrink: 1;
        overflow-x: hidden;
        align-self: flex-start;
    }
    /* 좌측 | 메인 | 우측 사이드바 구분 라인 (세로), 좌·메인 간격 축소 */
    [data-testid="column"] {
        border-right: 1px solid #dee2e6;
        padding-right: 0.35rem;
        padding-left: 0.1rem;
    }
    [data-testid="column"]:first-of-type { padding-left: 0; padding-right: 0.35rem; }
    /* 우측 사이드바(대표도면 영역): 4열 행의 마지막 열만 적용, 상단 맞춤, 세로 스크롤 없음 */
    div[data-testid="stHorizontalBlock"]:has(> [data-testid="column"]:nth-child(4)) > [data-testid="column"]:last-of-type {
        border-right: none;
        padding-right: 0;
        padding-top: 0;
        overflow-y: visible;
        overflow-x: hidden;
        flex-shrink: 0;
        min-width: 1rem;
    }
    div[data-testid="stHorizontalBlock"]:has(> [data-testid="column"]:nth-child(4)) > [data-testid="column"]:last-of-type > div {
        padding-top: 0;
    }
    div[data-testid="stHorizontalBlock"]:has(> [data-testid="column"]:nth-child(4)) > [data-testid="column"]:last-of-type .stMarkdown { animation: slideIn 0.3s ease-out; }

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

    /* 스펙 팝업(다이얼로그): 세로는 뷰포트에 맞춤, 가로 5cm 확장, 전체 스크롤 최소화 */
    div[data-testid="stDialog"] div[role="dialog"] {
        width: calc(90vw + 5cm) !important;
        max-width: calc(1200px + 5cm) !important;
        min-height: 400px !important;
        max-height: 90vh !important;
        height: auto !important;
        overflow-y: auto !important;
    }
    div[data-testid="stDialog"] div[role="dialog"] [data-testid="stCode"] {
        max-height: none !important;
    }

    /* 테이블·이미지 등 컨테이너 폭 초과 방지(가로 스크롤 방지) */
    [data-testid="stDataFrame"], [data-testid="stDataFrame"] > div,
    .stImage img, [data-testid="column"] .stMarkdown {
        max-width: 100% !important;
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

    /* 청구항 패널: 화면 전체가 슬라이드로 등장, 레이어 순서 명확히 해 첫 클릭부터 탭 전환 동작 */
    .claims-panel-slide {
        position: relative;
        z-index: 1;
        max-height: calc(100vh - 120px);
        overflow: hidden;
        animation: panelSlideIn 0.5s ease-out forwards;
    }
    @keyframes panelSlideIn {
        from { opacity: 0; transform: translateX(-100%); pointer-events: none; }
        to { opacity: 1; transform: translateX(0); pointer-events: auto; }
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
    .claims-panel .claim-item-row { display: flex; align-items: center; gap: 8px; margin-bottom: 6px; cursor: pointer; }
    .claims-panel .claim-item-row input[type="checkbox"] { flex-shrink: 0; accent-color: #1e3a8a; }
    .claims-panel .claim-extract-wrap { margin-top: 14px; padding-top: 12px; border-top: 1px solid #e2e8f0; }
    .claims-panel .claim-extract-btn {
        width: 100%; padding: 10px 16px; background: #1e3a8a; color: #fff; border: none;
        border-radius: 6px; font-size: 14px; font-weight: 600; cursor: pointer;
    }
    .claims-panel .claim-extract-btn:hover { background: #1e40af; }
    /* 대상 AI요약 카드 — 청구항 claim-item과 동일한 헤더/컨테이너 스타일 */
    .summary-cards { padding-top: 0.5rem; }
    .summary-cards .summary-item {
        margin-bottom: 14px;
        padding: 12px;
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        font-size: 13px;
        line-height: 1.55;
    }
    .summary-cards .summary-item-row {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 6px;
    }
    .summary-cards .summary-item-title {
        color: #1e3a8a;
        font-weight: bold;
    }
    .summary-cards .summary-item-body {
        color: #374151;
    }
    /* 대상 보기 패널 내 탭 (청구항 / 대상 AI요약) — 탭 버튼이 항상 최상층에서 클릭되도록 */
    .claims-panel-tabs { max-height: inherit; display: flex; flex-direction: column; position: relative; z-index: 1; }
    .claims-tab-radio { position: absolute; opacity: 0; pointer-events: none; width: 0; height: 0; }
    .claims-tab-headers {
        display: flex; border-bottom: 1px solid #dee2e6; margin-bottom: 6px; gap: 0;
        position: relative; z-index: 10; flex-shrink: 0;
    }
    .claims-tab-btn {
        position: relative; z-index: 11;
        padding: 8px 14px; border: none; background: transparent; cursor: pointer;
        font-size: 14px; color: #6b7280; border-bottom: 2px solid transparent;
        pointer-events: auto;
    }
    .claims-tab-btn:hover { color: #1e3a8a; }
    #claimstab-claim:checked ~ .claims-tab-headers label[for="claimstab-claim"],
    #claimstab-summary:checked ~ .claims-tab-headers label[for="claimstab-summary"] {
        color: #1e3a8a; font-weight: 600; border-bottom-color: #1e3a8a;
    }
    .claims-tab-panel { display: none; max-height: calc(100vh - 180px); overflow-y: auto; position: relative; z-index: 0; }
    #claimstab-claim:checked ~ #panel-claim,
    #claimstab-summary:checked ~ #panel-summary { display: block; }
    /* 우측 대표도면/발명의 3요소 패널: 고정 높이 + 스크롤바, 슬라이드 인 */
    .right-panel-slide {
        position: relative;
        z-index: 1;
        overflow-x: visible;
        animation: rightPanelSlideIn 0.5s ease-out forwards;
    }
    @keyframes rightPanelSlideIn {
        from { opacity: 0; transform: translateX(100%); pointer-events: none; }
        to { opacity: 1; transform: translateX(0); pointer-events: auto; }
    }
    /* 우측 패널 닫기 버튼: 가로로 조금 넓은 X 버튼 */
    .right-panel-slide .stButton > button {
        min-width: 40px !important;
        padding: 0.1rem 0.4rem !important;
        font-weight: 700 !important;
        font-size: 15px !important;
    }
    </style>
""", unsafe_allow_html=True)

# 대상 AI요약 — 청구항 탭과 동일 스타일(굵은 타이틀 행, 하단 내용 한 칸씩)
SUMMARY_TABLE_HTML = """
<div class="summary-cards" style="font-family: 'Malgun Gothic', '맑은 고딕', sans-serif; max-width: 600px;">
    <div class="summary-item">
        <div class="summary-item-row">
            <span class="summary-item-title">기술분야</span>
        </div>
        <div class="summary-item-body">반도체 패키지 기술에 관한 것으로, 서로 다른 피치를 갖는 기판 패키지 사이에 인터포저를 배치하여 반도체 칩을 적층하는 스택 패키지 및 그 제조 방법</div>
    </div>
    <div class="summary-item">
        <div class="summary-item-row">
            <span class="summary-item-title">문제점</span>
        </div>
        <div class="summary-item-body">기존 기술에서는 인터포저를 ABF 패키지 또는 HDI 패키지 중 하나에만 적용하는 경우 대면적 스택 패키지 제조 비용이 증가하거나 인터포저 내부에 수평 신호 라인을 형성해야 하므로 저항 증가로 인해 패키지 성능이 저하되는 문제</div>
    </div>
    <div class="summary-item">
        <div class="summary-item-row">
            <span class="summary-item-title">해결과제(목적)</span>
        </div>
        <div class="summary-item-body">서로 다른 피치를 갖는 기판 패키지를 효율적으로 연결하면서 인터포저의 수평 신호 라인을 제거하여 제조 비용을 절감하고 성능을 향상시킨 스택 패키지를 제공</div>
    </div>
    <div class="summary-item">
        <div class="summary-item-row">
            <span class="summary-item-title">해결수단</span>
        </div>
        <div class="summary-item-body">제1 피치의 패드를 갖는 ABF 기반 제1 기판 패키지(110)와 제2 피치의 패드를 갖는 HDI 기반 제2 기판 패키지(120)를 적층하고, 제1 기판 패키지 상부에 제3 피치의 패드를 갖는 인터포저(130)를 배치하며, 인터포저 내부에 수직 신호 라인(138)을 형성하여 제1·제2 기판 패키지와 반도체 칩(140)을 도전성 범프(170,172,174)로 전기적으로 연결하도록 구성</div>
    </div>
    <div class="summary-item">
        <div class="summary-item-row">
            <span class="summary-item-title">핵심기술</span>
        </div>
        <div class="summary-item-body">•ABF 패키지와 HDI 패키지를 순차적으로 적층하고 그 사이에 인터포저를 배치하는 스택 패키지 구조<br>•ABF 패키지와 인터포저가 실질적으로 동일한 피치를 갖도록 하여 인터포저 내부의 수직 신호 라인만으로 전기 연결하는 기술<br>•제1·제2·제3 도전성 범프를 이용하여 기판 패키지와 인터포저 및 반도체 칩을 단계적으로 연결하는 패키지 구조<br>•인터포저 상부에 ASIC 및 HBM 반도체 칩을 배치하여 고대역폭 신호 연결을 구현하는 구조</div>
    </div>
    <div class="summary-item">
        <div class="summary-item-row">
            <span class="summary-item-title">발명의 효과</span>
        </div>
        <div class="summary-item-body">인터포저에 수평 신호 라인을 형성할 필요가 없어 저항 증가를 방지하고 성능을 향상시키며 동시에 대면적 스택 패키지의 제조 비용을 절감</div>
    </div>
    <div class="summary-item">
        <div class="summary-item-row">
            <span class="summary-item-title">응용분야</span>
        </div>
        <div class="summary-item-body">인공지능 디바이스, 네트워크 장치, 고대역폭 메모리 기반 고성능 반도체 패키지 등 고집적 반도체 시스템에 적용</div>
    </div>
    <div class="summary-item">
        <div class="summary-item-row">
            <span class="summary-item-title">보충설명</span>
        </div>
        <div class="summary-item-body">본 발명의 스택 패키지는 HDI 패키지, ABF 패키지, 인터포저 및 반도체 칩을 계단형 피라미드 구조로 적층하고 인터포저 내부의 수직 신호 라인을 이용해 전기적으로 연결하는 구조를 통해 신호 전달 효율을 향상시킨다</div>
    </div>
</div>
"""

# 우측 사이드바(대표도면 아래) — 대상 AI요약과 동일한 카드 스타일 (대표청구항, 해결과제, 해결수단, 효과)
RIGHT_SIDEBAR_CONTENT_HTML = """
<div class="summary-cards" style="font-family: 'Malgun Gothic', '맑은 고딕', sans-serif; max-width: 100%;">
    <div class="summary-item">
        <div class="summary-item-row">
            <span class="summary-item-title">대표청구항</span>
        </div>
        <div class="summary-item-body">패키지 기판;<br>상기 패키지 기판의 상부에 위치하고 상기 패키지 기판과 전기적으로 연결된 인터포저;<br>상기 인터포저의 상부에 위치하고 상기 인터포저와 전기적으로 연결된 프로세싱 소자;<br>상기 인터포저의 상부에 위치하고 상기 인터포저 및 프로세싱 소자와 전기적으로 연결된 적어도 하나의 고대역폭 메모리 소자;<br>상기 인터포저의 상부에 위치하고 상기 인터포저 및 상기 프로세싱 소자와 전기적으로 연결된 전력 관리 집적 회로 소자; 및<br>상기 인터포저의 상부 또는 내부에 위치하고 상기 전력 관리 집적 회로 소자와 전기적으로 연결된 수동 소자를 포함하는 전자 소자 패키지.</div>
    </div>
    <div class="summary-item">
        <div class="summary-item-row">
            <span class="summary-item-title">해결과제(목적)</span>
        </div>
        <div class="summary-item-body">인터포저 기반 패키지 구조에서 수동소자와 전력 관리 회로를 효율적으로 통합하여 패키지 실장 면적을 줄이면서도 전력 공급 안정성과 시스템 성능을 향상시킬 수 있는 전자 소자 패키지를 제공</div>
    </div>
    <div class="summary-item">
        <div class="summary-item-row">
            <span class="summary-item-title">해결수단</span>
        </div>
        <div class="summary-item-body">패키지 기판 상부에 인터포저를 배치하고, 인터포저 상부에 프로세싱 소자와 고대역폭 메모리 소자 및 전력 관리 집적 회로 소자를 탑재하며, 인터포저 내부 또는 상부에 인덕터 및 커패시터와 같은 수동소자를 형성한다. 특히 인덕터는 인터포저 상하부에 형성된 자석층과 이를 연결하는 관통 실리콘 비아 및 재배선층을 이용하여 형성되며, 전력 관리 집적 회로와 전기적으로 연결되어 안정적인 전력 공급을 구현한다.</div>
    </div>
    <div class="summary-item">
        <div class="summary-item-row">
            <span class="summary-item-title">발명의 효과</span>
        </div>
        <div class="summary-item-body">인터포저 내부에 수동소자와 전력 관리 회로를 통합함으로써 패키지 기판 상의 실장 면적을 줄일 수 있고, 프로세싱 소자와 고대역폭 메모리에 안정적인 전력 공급을 제공하여 전체 전자 시스템의 성능 및 전력 효율을 향상</div>
    </div>
</div>
"""

# 대상 보기 패널 표시 여부 (대상 보기 버튼 토글)
if "claims_visible" not in st.session_state:
    st.session_state.claims_visible = False

if "sidebar_visible" not in st.session_state:
    # 최초 진입 시부터 우측 대표도면/발명의 3요소 영역이 열려 있도록 기본값을 True로 설정
    st.session_state.sidebar_visible = True


def toggle_claims():
    st.session_state.claims_visible = not st.session_state.claims_visible


def show_sidebar():
    st.session_state.sidebar_visible = True


def hide_sidebar():
    st.session_state.sidebar_visible = False

# 기술 구성요소 목록 (요소 추가 시 마지막에 빈칸 추가)
DEFAULT_COMPONENTS = [
    "제1 기판 패키지(110): 제1 피치(P1)의 제1 패드(114)를 포함하는 ABF 패키지",
    "제2 기판 패키지(120): 제2 피치(P2)의 제2 패드(124)를 포함하는 HDI 패키지",
    "인터포저(130): 제3 패드(134)와 수직 신호 라인(138)을 포함하는 반도체 인터포저",
]
if "components" not in st.session_state:
    st.session_state.components = list(DEFAULT_COMPONENTS)


def add_component():
    st.session_state.components.append("")


# 청구항 샘플 데이터 (항별)
CLAIMS_DATA = [
    ("청구항 1", "흐름전극기반 축전식 탈염을 위한 슬러리 탄소 양극을 제조하는 방법에 있어서, 집전체와 음이온교환막을 포함하는 양극유로를 준비하는 단계와; 상기 양극유로의 집전체와 전기적으로 분리된 집전체 및 양이온교환막을 포함하는 음극유로를 준비하는 단계와; 상기 양극유로와 상기 음극유로를 적층하여 유로 일체형 전극을 형성하는 단계를 포함하는 것을 특징으로 하는 흐름전극기반 축전식 탈염을 위한 슬러리 탄소 양극의 제조방법."),
    ("청구항 2", "제1항에 있어서, 상기 양극유로를 준비하는 단계는 상기 집전체 상에 음이온교환막을 코팅하거나 라미네이션하는 단계를 포함하는 것을 특징으로 하는 방법."),
    ("청구항 3", "제1항에 있어서, 상기 음극유로를 준비하는 단계는 상기 집전체 상에 양이온교환막을 코팅하거나 라미네이션하는 단계를 포함하는 것을 특징으로 하는 방법."),
    ("청구항 4", "제1항 내지 제3항 중 어느 한 항에 있어서, 상기 유로 일체형 전극은 롤-투-롤 공정으로 형성되는 것을 특징으로 하는 방법."),
]

# 검색 결과 샘플 데이터 (게시판 목록) — 상단 정의로 선택/사이드바에서 공유
RESULT_DATA = {
    "순번": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    "구분": ["등록", "등록", "취하", "등록", "등록", "소멸", "등록", "거절", "등록", "거절"],
    "CPC분류": [
        "H01L 23/49816\nH01L 23/481\nH01L 24/97",
        "H01L 23/12\nH01L 2021/60",
        "H01L 25/0657\nH01L 25/0655\nH01L 25/0652",
        "H01L 23/12\nH01L 23/28",
        "H01L 23/12\nH01L 2021/60",
        "H01L 23/48",
        "H01L 23/48",
        "H01L 23/48",
        "H01L 25/0657\nH01L 24/97\nH01L 23/525",
        "H01L 23/48\nH01L 23/12\nH01L 2021/60",
    ],
    "발명의 명칭": [
        "스택 패키지 및 그의 제조 방법",
        "반도체 패키지",
        "협곡 인터포저를 갖는 반도체 패키지",
        "반도체 패키지",
        "반도체 패키지",
        "인터포저를 이용한 적층형 반도체 패키지",
        "반도체 패키지",
        "인터포저를 이용한 적층형 반도체 패키지",
        "인터포저 브리지를 포함한 스택 패키지",
        "반도체 패키지 및 반도체 패키지 제조 방법",
    ],
    "출원번호": ["1020200026921", "1020080016774", "1020150010834", "1020080016771", "1020080016775", "1020130000681", "1020140107844", "1020130000685", "1020190143816", "1020110141402"],
    "출원일자": ["20200304", "20080225", "20150122", "20080225", "20080225", "20130103", "20140819", "20130103", "20191111", "20111223"],
}
df_result = pd.DataFrame(RESULT_DATA)
# 테이블 표시용: 순번 제거 (체크박스는 data_editor에서 selection_mode 없이 제거)
df_display = df_result.drop(columns=["순번"]).copy()

# 좌측 | 대상 보기(토글) | 메인 | 우측 사이드바 — 대상/우측 패널 표시 여부에 따라 폭 조정
# - 최초: 좌측을 조금 더 좁게([0.8, 0.01, 3.2, 0.01])
# - 우측 사이드바가 열리면 메인 테이블 폭을 함께 줄여 가로 스크롤이 생기지 않도록 비율 조정
if st.session_state.claims_visible and st.session_state.sidebar_visible:
    # 좌측 + 대상 패널 + 메인 + 우측(슬라이드)
    left_col, claims_col, right_col, right_sidebar = st.columns([0.8, 0.9, 2.3, 1])
elif st.session_state.claims_visible and not st.session_state.sidebar_visible:
    # 좌측 + 대상 패널 + 메인 (우측 최소)
    left_col, claims_col, right_col, right_sidebar = st.columns([0.8, 0.9, 3.2, 0.01])
elif (not st.session_state.claims_visible) and st.session_state.sidebar_visible:
    # 좌측 + 메인 + 우측(슬라이드)
    left_col, claims_col, right_col, right_sidebar = st.columns([0.8, 0.01, 2.3, 1])
else:
    # 기본: 좌측(조금 더 좁게) + 메인 (우측 최소)
    left_col, claims_col, right_col, right_sidebar = st.columns([0.8, 0.01, 3.2, 0.01])

# ==========================================
# 좌측 패널: 검색 조건 및 구성요소
# ==========================================
with left_col:
    # 대상 검색 (기존 '대상 AI요약' 탭은 슬라이드 패널로 이전)
    st.markdown("**⚙️ 심사 대상 건 입력**")
    st.text_input("출원번호", value="1020200026921", label_visibility="collapsed")
    
    st.text_area(
        "문장 검색",
        placeholder="입력한 문장으로 유사 문서를 찾습니다. AND(&), OR(|) 연산자는 사용할 수 없습니다.",
        height=100,
        label_visibility="collapsed",
        key="search_sentence"
    )
        
    st.markdown('<hr style="border:1px solid #ddd; margin: 5px 0px;">', unsafe_allow_html=True)
    
    st.markdown("**⚙️ 기술 구성요소**")
    comp_btn_col1, comp_btn_col2 = st.columns(2)
    with comp_btn_col1: st.button("추가", use_container_width=True, key="btn_comp_add", on_click=add_component)
    toggle_label = "접기 ◀" if st.session_state.claims_visible else "보기 ▶"
    with comp_btn_col2:
        st.button(toggle_label, use_container_width=True, key="btn_claim", on_click=toggle_claims)
    
    components = st.session_state.components
    for i, comp in enumerate(components):
        if f"comp_{i}" not in st.session_state:
            st.session_state[f"comp_{i}"] = comp
        c1, c2 = st.columns([1, 9])
        with c1: st.checkbox("", value=True, key=f"comp_cb_{i}")
        with c2: st.text_area("구성요소", key=f"comp_{i}", placeholder="구성요소 입력...", label_visibility="collapsed", height=90)
    
    st.button("🔍 검색", use_container_width=True, type="primary", key="btn_research", on_click=show_sidebar)

# ==========================================
# 대상 보기 패널 (좌측 오른쪽, 토글 시 슬라이드) — 청구항 / 대상 AI요약 탭
# ==========================================
with claims_col:
    if st.session_state.claims_visible:
        claims_items_html = "".join(
            f'<div class="claim-item">'
            f'<label class="claim-item-row">'
            f'<input type="checkbox" class="claim-cb" name="claim_selection" value="{i}">'
            f'<span style="color: #1e3a8a; font-weight: bold;">{title}</span>'
            f'</label>'
            f'<div style="color: #374151;">{text}</div></div>'
            for i, (title, text) in enumerate(CLAIMS_DATA)
        )
        extract_block = (
            '<div class="claim-extract-wrap">'
            '<button type="button" class="claim-extract-btn">구성요소 추출</button>'
            '</div>'
        )
        st.markdown(
            '<div class="claims-panel-slide">'
            '<div class="claims-panel-tabs">'
            '<input type="radio" name="claimstab" id="claimstab-claim" class="claims-tab-radio" checked>'
            '<input type="radio" name="claimstab" id="claimstab-summary" class="claims-tab-radio">'
            '<div class="claims-tab-headers">'
            '<label for="claimstab-claim" class="claims-tab-btn">청구항</label>'
            '<label for="claimstab-summary" class="claims-tab-btn">대상 AI요약</label>'
            '</div>'
            '<div id="panel-claim" class="claims-tab-panel">'
            '<div class="claims-panel">' + claims_items_html + extract_block + '</div>'
            '</div>'
            '<div id="panel-summary" class="claims-tab-panel">' + SUMMARY_TABLE_HTML + '</div>'
            '</div></div>',
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
# 우측 사이드바 (검색 후 표시): 대표도면 + 발명의 3요소
# ==========================================
with right_sidebar:
    if st.session_state.sidebar_visible:
        st.markdown(
            '<div class="right-panel-slide">',
            unsafe_allow_html=True,
        )
        header_col1, header_col2 = st.columns([8, 0.6])
        with header_col1:
            st.markdown(
                '<div style="padding-top: 6px; margin-bottom: 4px;"><strong>🖼️ 대표도면</strong></div>',
                unsafe_allow_html=True,
            )
        with header_col2:
            st.button("X", key="btn_close_sidebar", on_click=hide_sidebar, use_container_width=True)
        drawing_path = Path(__file__).parent / "data" / "drawing.jpg"
        if drawing_path.exists():
            st.image(str(drawing_path), use_container_width=True)
        else:
            st.caption("`./data/drawing.jpg` 파일을 추가하면 대표도면이 표시됩니다.")
        
        st.markdown(RIGHT_SIDEBAR_CONTENT_HTML, unsafe_allow_html=True)
        st.markdown(
            '</div>',
            unsafe_allow_html=True,
        )