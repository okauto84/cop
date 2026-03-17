# -*- coding: utf-8 -*-

import streamlit as st
import pandas as pd
from pathlib import Path
from PIL import Image

try:
    from gazette_detail_content import (
        GAZETTE_BIB_ITEMS,
        GAZETTE_ABSTRACT,
        GAZETTE_CLAIMS,
        GAZETTE_TECHNICAL_FIELD,
        GAZETTE_BACKGROUND,
        GAZETTE_PROBLEM,
        GAZETTE_SOLUTION,
        GAZETTE_EFFECT,
        GAZETTE_DRAWING_DESC_LINES,
        GAZETTE_SYMBOLS,
        GAZETTE_DETAIL,
    )
except ImportError:
    GAZETTE_BIB_ITEMS = []
    GAZETTE_ABSTRACT = ""
    GAZETTE_CLAIMS = []
    GAZETTE_TECHNICAL_FIELD = ""
    GAZETTE_BACKGROUND = ""
    GAZETTE_PROBLEM = ""
    GAZETTE_SOLUTION = ""
    GAZETTE_EFFECT = ""
    GAZETTE_DRAWING_DESC_LINES = []
    GAZETTE_SYMBOLS = []
    GAZETTE_DETAIL = ""

# AI분석 탭 - 발명 3요소 블록 스타일
st.markdown("""
<style>
/* 발명의 3요소 블록: 스크롤바 없음(내용 높이만 사용), 옆 간격 축소 */
section[data-testid="stHorizontalBlock"]:has(.ai-summary-block),
div[data-testid="stHorizontalBlock"]:has(.ai-summary-block) {
    align-items: stretch;
    gap: 0.2rem !important;
}
[data-testid="column"]:has(.ai-summary-block) {
    padding-left: 0.2rem !important;
    padding-right: 0.2rem !important;
    min-width: 0;
}
.ai-summary-block {
    display: block;
    width: 100%;
    min-width: 0;
    /* 텍스트 길이에 맞춰 세로로 자유롭게 늘어남 */
    height: auto !important;
    box-sizing: border-box;
    border-radius: 8px;
    padding: 0.5rem 0.65rem;
    margin-bottom: 0;
    text-align: left;
    font-size: 0.9rem;
    line-height: 1.45;
    word-break: keep-all;
    overflow-wrap: break-word;
    overflow: visible !important;
}
.ai-summary-block .block-title {
    font-weight: bold;
    margin-bottom: 0.25rem;
    font-size: 0.95rem;
    line-height: 1.3;
    white-space: normal;
}
.ai-summary-table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0.5rem;
    table-layout: fixed;
}
.ai-summary-table td {
    vertical-align: top;
    padding: 0;
}
.claim-table { width: 100%; border-collapse: collapse; margin-top: 0.5rem; font-size: 0.9rem; }
.claim-table th, .claim-table td { border: 1px solid #ddd; padding: 0.75rem 1rem; text-align: left; vertical-align: top; }
.claim-table th { background-color: #f5f5f5; font-weight: bold; }
.claim-table .comp-name { font-weight: bold; display: block; margin-bottom: 0.25rem; }
.claim-table .comp-desc { color: #555; font-size: 0.85em; }
.tag { display: inline-block; padding: 0.25rem 0.75rem; border-radius: 999px; color: white; font-size: 0.85em; font-weight: 500; }
.tag-partial { background-color: #2e7d32; }        /* 동일: 진한 녹색 */
.tag-diff { background-color: #c62828; }           /* 차이: 빨강 */
.tag-same-partial { background-color: #ef6c00; }   /* 일부 동일: 주황 */
.tag-same { background-color: #1565c0; }           /* 실질적 동일: 파랑 */
.tag-link { text-decoration: none; color: inherit; cursor: pointer; display: inline-block; }
.tag-link:hover { opacity: 0.9; }
[id^="focus-"] { scroll-margin-top: 2rem; }
@keyframes focus-blink {
    0%, 40% { opacity: 1; }
    20% { opacity: 0.25; }
    100% { opacity: 1; }
}
[id^="focus-"].focus-blink {
    animation: focus-blink 0.2s ease-in-out 3;
}
.compare-box { border-radius: 10px; padding: 0.75rem 1rem; margin-bottom: 0.6rem; background: #fafafa; border: 1px solid #eee; box-shadow: 0 1px 3px rgba(0,0,0,0.08); text-align: left; font-size: 0.85rem; line-height: 1.5; }
.compare-box.common { border-left: 4px solid #66bb6a; border-right: 4px solid #66bb6a; }
.compare-box.diff { border-left: 4px solid #ffb74d; }
.compare-box-title { font-weight: bold; margin-bottom: 0.5rem; font-size: 0.95rem; }
.compare-box.common .compare-box-title { color: #2e7d32; }
.compare-box.diff .compare-box-title { color: #e65100; }
.compare-box ul { margin: 0; padding-left: 1.25rem; }
.compare-box li { margin-bottom: 0.5rem; }
.compare-box .highlight { color: #1565c0; font-weight: 500; }
/* 좌(공보) 우(AI분석) 컬럼 각각 독립 스크롤 (Streamlit 1.35.0+ 구조) - 팝업 세로에 맞춤 */
/* 1.35+ 가로 블록: 최상위 2단 레이아웃만 높이 제한 (75vh로 축소해 팝업 내 스크롤 방지) */
section[data-testid="stHorizontalBlock"]:first-of-type,
div[data-testid="stHorizontalBlock"]:first-of-type {
    max-height: 75vh !important;
    min-height: 0;
    display: flex !important;
    flex-direction: row;
}
/* 1.35+ 첫 번째 가로 블록 직계 컬럼만 독립 스크롤 (좌/우 2개) */
section[data-testid="stHorizontalBlock"]:first-of-type > div,
div[data-testid="stHorizontalBlock"]:first-of-type > div {
    max-height: 75vh !important;
    min-height: 0;
    flex: 1 1 0;
    min-width: 0;
    overflow-y: auto !important;
    overflow-x: hidden !important;
    -webkit-overflow-scrolling: touch;
}
/* 컬럼에 data-testid="column"이 있는 경우 (1.35+ 호환) */
section[data-testid="stHorizontalBlock"]:first-of-type [data-testid="column"],
div[data-testid="stHorizontalBlock"]:first-of-type [data-testid="column"] {
    max-height: 75vh !important;
    height: 75vh !important;
    overflow-y: auto !important;
    overflow-x: hidden !important;
    min-height: 160px;
    flex: 1 1 0;
    min-width: 0;
    -webkit-overflow-scrolling: touch;
}
/* 좌측 컬럼: 구분선 없음 */
section[data-testid="stHorizontalBlock"]:first-of-type > div:first-child,
div[data-testid="stHorizontalBlock"]:first-of-type > div:first-child,
section[data-testid="stHorizontalBlock"]:first-of-type [data-testid="column"]:first-of-type,
div[data-testid="stHorizontalBlock"]:first-of-type [data-testid="column"]:first-of-type {
    border-right: none;
    padding-right: 1rem;
}
/* 우측 컬럼 */
section[data-testid="stHorizontalBlock"]:first-of-type > div:last-child,
div[data-testid="stHorizontalBlock"]:first-of-type > div:last-child,
section[data-testid="stHorizontalBlock"]:first-of-type [data-testid="column"]:last-of-type,
div[data-testid="stHorizontalBlock"]:first-of-type [data-testid="column"]:last-of-type {
    padding-left: 1rem;
}
/* 공보 탭 스타일 */
.gazette-doc-tabs { display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.75rem; padding-bottom: 0.5rem; border-bottom: 1px solid #e0e0e0; }
.gazette-doc-tabs span { padding: 0.4rem 0.9rem; border-radius: 6px; font-size: 0.9rem; cursor: pointer; }
.gazette-doc-tabs .tab-inactive { background: #f5f5f5; color: #666; }
.gazette-doc-tabs .tab-active { background: #1565c0; color: white; }
.gazette-doc-tabs .tab-arrow { margin-left: auto; font-size: 1.2rem; color: #666; }
.gazette-title-ko { font-size: 1.2rem; font-weight: bold; margin-bottom: 0.25rem; }
.gazette-title-en { font-size: 0.85rem; color: #555; margin-bottom: 0.5rem; }
.gazette-tag-row { margin-bottom: 0.5rem; }
.gazette-tag { display: inline-block; padding: 0.2rem 0.6rem; border-radius: 999px; font-size: 0.8rem; margin-right: 0.35rem; margin-bottom: 0.25rem; }
.gazette-tag-cpc { background: #1976d2; color: white; }
.gazette-tag-ipc { background: #388e3c; color: white; }
.gazette-section { background: #fafafa; border-radius: 8px; padding: 0.65rem 1rem; margin-bottom: 0.6rem; border: 1px solid #eee; }
.gazette-section-title { font-weight: bold; margin-bottom: 0.5rem; font-size: 0.95rem; }
.gazette-bib { display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem 1.5rem; font-size: 0.9rem; }
.gazette-bib-item { display: flex; }
.gazette-bib-label { min-width: 100px; color: #555; }
.gazette-claims-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem; }
.gazette-claim-btns { font-size: 0.8rem; }
.gazette-claim-item { margin-bottom: 0.5rem; padding: 0.5rem; background: white; border-radius: 6px; border: 1px solid #eee; }
.gazette-claim-item-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem; }
</style>
""", unsafe_allow_html=True)

# 좌측: 공보 | 우측: AI분석 (동시 표시)
left_col, right_col = st.columns(2)

# ========== 우측: AI분석 ==========
with right_col:
    st.markdown("### 💡 발명의 3요소 (AI 요약)")
    st.markdown(
        """
        <table class="ai-summary-table">
          <tr>
            <td style="background-color: #FEE7E7;">
              <div class="ai-summary-block">
                <div class="block-title">⚠️ 해결 과제(목적)</div>
                인터포저 기반 패키지 구조에서 수동소자와 전력 관리 회로를 효율적으로 통합하여 패키지 실장 면적을 줄이면서도 전력 공급 안정성과 시스템 성능을 향상시킬 수 있는 전자 소자 패키지를 제공
              </div>
            </td>
            <td style="background-color: #E7EEFE;">
              <div class="ai-summary-block">
                <div class="block-title">⭐ 발명의 효과</div>
                인터포저 내부에 수동소자와 전력 관리 회로를 통합함으로써 패키지 기판 상의 실장 면적을 줄일 수 있고, 프로세싱 소자와 고대역폭 메모리에 안정적인 전력 공급을 제공하여 전체 전자 시스템의 성능 및 전력 효율을 향상
              </div>
            </td>
          </tr>
          <tr>
            <td colspan="2" style="background-color: #E7FEE7;">
              <div class="ai-summary-block">
                <div class="block-title">🎯 해결 수단</div>
                패키지 기판 상부에 인터포저를 배치하고, 인터포저 상부에 프로세싱 소자와 고대역폭 메모리 소자 및 전력 관리 집적 회로 소자를 탑재하며, 인터포저 내부 또는 상부에 인덕터 및 커패시터와 같은 수동소자를 형성한다. 특히 인덕터는 인터포저 상하부에 형성된 자석층과 이를 연결하는 관통 실리콘 비아 및 재배선층을 이용하여 형성되며, 전력 관리 집적 회로와 전기적으로 연결되어 안정적인 전력 공급을 구현한다.
              </div>
            </td>
          </tr>
        </table>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("---")

    st.markdown("### 💡 도면")

    # ./data 폴더 이미지 파일 목록 (스크립트 위치 기준, exec 시 __file__ 전달됨)
    try:
        _script_dir = Path(__file__).resolve().parent
    except NameError:
        _script_dir = Path.cwd()
    _data_dir = _script_dir / "data"
    _img_ext = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp"}
    _image_files = []
    if _data_dir.is_dir():
        _image_files = sorted(
            [f for f in _data_dir.iterdir() if f.is_file() and f.suffix.lower() in _img_ext]
        )
    if _image_files:
        _tab_names = [f.stem for f in _image_files]
        _tabs = st.tabs(_tab_names)
        for _tab, _img_path in zip(_tabs, _image_files):
            with _tab:
                try:
                    with Image.open(_img_path) as _img:
                        _w, _h = _img.size
                    _display_w = int(_w * 0.8)
                    st.image(str(_img_path), width=_display_w)
                except Exception:
                    st.image(str(_img_path), use_container_width=True)
    else:
        st.info("도면 이미지가 없습니다. `./data` 폴더에 이미지 파일(.png, .jpg 등)을 넣어 주세요.")

    st.markdown("---")
    st.markdown("### 💡 구성요소 대비표 (Claim Analysis Table)")
    st.markdown(
        """
        <table class="claim-table">
        <thead>
        <tr>
        <th>출원발명</th>
        <th>인용발명</th>
        <th>관련도</th>
        <th>대비결과</th>
        </tr>
        </thead>
        <tbody>
        <tr>
        <td>제 1 피치의 간격을 두고 배열된 제 1 패드들을 포함하는 제 1 기판 패키지</td>
        <td>전자 소자 패키지(100)의 하부에서 전자 요소들을 지지하고 전기적으로 연결되는 패키지 기판(102)</td>
        <td><a href="#focus-partial" class="tag-link"><span class="tag tag-partial">동일</span></a></td>
        <td>출원발명의 제1 패드가 일정 피치 간격으로 배열된 제1 기판 패키지는 선행발명의 패키지 기판에 상부 패드가 배열되어 있는 구성과 구조적으로 대응한다</td>
        </tr>
        <tr>
        <td>상기 제 1 기판 패키지의 하부에 배치되고, 상기 제 1 피치와 다른 제 2 피치의 간격을 두고 배열된 제 2 패드들을 포함하는 제 2 기판 패키지</td>
        <td>(대응되는 내용 없음)</td>
        <td><a href="#focus-diff" class="tag-link"><span class="tag tag-diff">차이</span></a></td>
        <td>선행발명에서는 하부에 별도의 ‘제 2 기판 패키지’ 혹은 서로 다른 피치로 배열된 패드에 대한 기술이 존재하지 않는다. 주로 패키지 기판·인터포저·패시브 소자에 초점을 두고 있어, 해당 구성요소와 직접적인 대응이 없으며 차이로 판단한다.</td>
        </tr>
        <tr>
        <td>상기 제 1 기판 패키지의 상부에 배치되고, 제 3 피치의 간격을 두고 배열된 제 3 패드들을 포함하는 인터포저</td>
        <td>패키지 기판(102)의 상부에 위치하고 패키지 기판과 전기적으로 연결되는 인터포저(110)</td>
        <td><a href="#focus-same-partial" class="tag-link"><span class="tag tag-same-partial">일부동일</span></a></td>
        <td>선행발명에서 인터포저가 패키지 기판 위에 배치되고, ‘상부 패드(109)’ 및 ‘배선 패드(119)’가 배열된 구조가 명시되어 있다. 이는 출원발명의 인터포저가 상부에 배치되고, 일정 피치로 배열된 패드들을 포함한다는 점과 구조·배치·전기적 연결 기능이 실질적으로 동일함을 보여준다.</td>
        </tr>
        <tr>
        <td>상기 인터포저의 상부에 배치된 적어도 하나의 제 1 반도체 칩</td>
        <td>인터포저의 상부에 배치된 프로세싱 소자를 포함하는 전자 소자</td>
        <td><a href="#focus-same" class="tag-link"><span class="tag tag-same">실질적동일</span></a></td>
        <td>선행발명에서는 인터포저의 상부에 ‘프로세싱 소자(또는 반도체 칩)’가 전기적으로 연결된 형태가 기술되어 있다. 이는 출원발명의 인터포저 상부에 배치된 반도체 칩과 동일한 구조·기능(전기적 연결 및 상부 배치)으로 실질적 동일성을 가진다.</td>
        </tr>
        </tbody>
        </table>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### 💡 종합 의견")
    st.markdown(
        '<div class="compare-box common" style="border-left-color: #1565c0; border-right-color: #1565c0;">'
        '<div style="font-size: 0.9rem; line-height: 1.7;">'
        '출원발명의 제1 기판 패키지(110), 인터포저(130), 및 제1 반도체 칩(140)에 대응하는 구성은 '
        '선행발명의 패키지 기판(102), 인터포저(110), 및 프로세싱 소자(120)에 의해 대응되나, '
        '출원발명의 제1 기판 패키지 하부에 배치되는 제2 기판 패키지(120)에 대응되는 구성은 '
        '선행발명에 개시되어 있지 않다.'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )

# ========== 좌측: 공보 ==========
with left_col:
    # 제목 영역 + 분류코드
    st.markdown("### 💡 특허 공보")
    st.markdown(
        '<div class="gazette-title-ko">전자 소자 패키지</div>'
        '<div class="gazette-title-en">Electronic device package</div>'
        '<div class="gazette-tag-row">'
        '<span class="gazette-tag gazette-tag-cpc">H01L 25/06</span>'
        '<span class="gazette-tag gazette-tag-cpc">H01L 23/52</span>'
        '<span class="gazette-tag gazette-tag-cpc">H01L 25/10</span>'
        '<span class="gazette-tag gazette-tag-cpc">H01L 23/00</span>'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown("---")

    # 서지 정보 (접기/펼치기 카드)
    bib_html = "".join(
        f'<div class="gazette-bib-item"><span class="gazette-bib-label">{label}</span> {value}</div>'
        for label, value in GAZETTE_BIB_ITEMS
    ) + '<div class="gazette-bib-item"></div>'
    with st.expander("📋 서지 정보", expanded=True):
        st.markdown(
            f'<div class="gazette-section"><div class="gazette-bib">{bib_html}</div></div>',
            unsafe_allow_html=True,
        )

    # 초록 (접기/펼치기 카드)
    with st.expander("📄 초록", expanded=True):
        st.markdown(
            f'<div class="gazette-section"><div style="font-size: 0.95rem; line-height: 1.6;">{GAZETTE_ABSTRACT}</div></div>',
            unsafe_allow_html=True,
        )

    # 청구항 (접기/펼치기 카드, 내부에 청구항 1~6 각각 expander)
    with st.expander("📌 청구항", expanded=True):
        for i, claim_text in enumerate(GAZETTE_CLAIMS, start=1):
            with st.expander(f"청구항 {i}", expanded=True):
                st.markdown(
                    f'<div class="gazette-section"><div style="font-size: 0.95rem; line-height: 1.6;">{claim_text}</div></div>',
                    unsafe_allow_html=True,
                )

    # 기술분야 (접기/펼치기 카드)
    with st.expander("🔬 기술분야", expanded=True):
        st.markdown(
            f'<div class="gazette-section"><div style="font-size: 0.95rem; line-height: 1.6;">{GAZETTE_TECHNICAL_FIELD}</div></div>',
            unsafe_allow_html=True,
        )

    # 배경기술 (접기/펼치기 카드)
    with st.expander("📖 배경기술", expanded=True):
        st.markdown(
            f'<div class="gazette-section"><div style="font-size: 0.95rem; line-height: 1.6;">{GAZETTE_BACKGROUND}</div></div>',
            unsafe_allow_html=True,
        )

    # 해결하고자 하는 과제 (접기/펼치기 카드)
    with st.expander("🎯 해결하고자 하는 과제", expanded=True):
        st.markdown(
            f'<div class="gazette-section"><div style="font-size: 0.95rem; line-height: 1.6;">{GAZETTE_PROBLEM}</div></div>',
            unsafe_allow_html=True,
        )

    # 해결수단 (접기/펼치기 카드)
    with st.expander("⚙️ 해결수단", expanded=True):
        st.markdown(
            f'<div class="gazette-section"><div style="font-size: 0.95rem; line-height: 1.6;">{GAZETTE_SOLUTION}</div></div>',
            unsafe_allow_html=True,
        )

    # 효과 (접기/펼치기 카드)
    with st.expander("⭐ 효과", expanded=True):
        st.markdown(
            f'<div class="gazette-section"><div style="font-size: 0.95rem; line-height: 1.6;">{GAZETTE_EFFECT}</div></div>',
            unsafe_allow_html=True,
        )

    # 도면의 간단한 설명 (접기/펼치기 카드)
    drawing_desc_html = "<br>".join(GAZETTE_DRAWING_DESC_LINES)
    with st.expander("🖼️ 도면의 간단한 설명", expanded=True):
        st.markdown(
            f'<div class="gazette-section"><div style="font-size: 0.95rem; line-height: 1.6;">{drawing_desc_html}</div></div>',
            unsafe_allow_html=True,
        )

    # 발명의 상세한 설명 (접기/펼치기 카드)
    with st.expander("📝 발명의 상세한 설명", expanded=False):
        detail_html = (
            '<div class="gazette-section">'
            '<div style="font-size: 0.95rem; line-height: 1.6; white-space: pre-wrap;">'
            + GAZETTE_DETAIL.replace("\n", "<br>")
            + "</div></div>"
        )
        st.markdown(detail_html, unsafe_allow_html=True)

    # 부호의 설명 (접기/펼치기 카드)
    symbols_html = "".join(
        f'<div class="gazette-bib-item"><span class="gazette-bib-label">{num}</span> {desc}</div>'
        for num, desc in GAZETTE_SYMBOLS
    )
    with st.expander("🔢 부호의 설명", expanded=True):
        st.markdown(
            f'<div class="gazette-section"><div class="gazette-bib" style="grid-template-columns: 1fr 1fr; gap: 0.5rem 1rem;">{symbols_html}</div></div>',
            unsafe_allow_html=True,
        )
