# -*- coding: utf-8 -*-

import os
import streamlit as st
import pandas as pd

# 스크립트 위치 기준 data 폴더 경로
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_DATA_DIR = os.path.join(_SCRIPT_DIR, "data")

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
.tag-partial { background-color: #f9a825; }
.tag-diff { background-color: #e57373; }
.tag-same { background-color: #66bb6a; }
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

    # 도면 탭: data 폴더 내 drawing.jpg, drawing02.jpg ~ drawing06.jpg
    drawing_files = [
        "drawing.jpg",
        "drawing02.jpg",
        "drawing03.jpg",
        "drawing04.jpg",
        "drawing05.jpg",
        "drawing06.jpg",
    ]
    tab_labels = ["도면 1", "도면 2", "도면 3", "도면 4", "도면 5", "도면 6"]
    drawing_tabs = st.tabs(tab_labels)
    for tab, fname in zip(drawing_tabs, drawing_files):
        path = os.path.join(_DATA_DIR, fname)
        with tab:
            if os.path.isfile(path):
                st.image(path)
            else:
                st.caption(f"파일 없음: {fname}")

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
        <td><a href="#focus-same" class="tag-link"><span class="tag tag-same">일부동일</span></a></td>
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
        '<div class="gazette-title-ko">컨볼루션 신경망을 사용하는 의미적 세그먼트화 및 깊이 완성 방법 및 장치</div>'
        '<div class="gazette-title-en">METHOD AND APPARATUS FOR SEMANTIC SEGMENTATION AND DEPTH COMPLETION USING A CONVOLUTIONAL NEURAL NETWORK</div>'
        '<div class="gazette-tag-row">'
        '<span class="gazette-tag gazette-tag-cpc">G06N 3/08</span>'
        '<span class="gazette-tag gazette-tag-cpc">G06N 3/045</span>'
        '<span class="gazette-tag gazette-tag-cpc">G06F 16/55</span>'
        '<span class="gazette-tag gazette-tag-cpc">G06T 7/11</span>'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown("---")

    # 서지 정보 (접기/펼치기 카드)
    with st.expander("📋 서지 정보", expanded=True):
        st.markdown(
            '<div class="gazette-section">'
            '<div class="gazette-bib">'
            '<div class="gazette-bib-item"><span class="gazette-bib-label">출원번호</span> 1020190168468</div>'
            '<div class="gazette-bib-item"><span class="gazette-bib-label">출원일</span> 2019.12.17</div>'
            '<div class="gazette-bib-item"><span class="gazette-bib-label">공개번호</span> 1020210073416</div>'
            '<div class="gazette-bib-item"><span class="gazette-bib-label">공개일</span> 2021.06.18</div>'
            '<div class="gazette-bib-item"><span class="gazette-bib-label">공보번호</span> —</div>'
            '<div class="gazette-bib-item"><span class="gazette-bib-label">공보일</span> 2022.03.25</div>'
            '<div class="gazette-bib-item"><span class="gazette-bib-label">등록번호</span> 1023788500000</div>'
            '<div class="gazette-bib-item"><span class="gazette-bib-label">등록일</span> 2022.03.22</div>'
            '<div class="gazette-bib-item"><span class="gazette-bib-label">최종상태</span> 등록결정(일반)</div>'
            '<div class="gazette-bib-item"><span class="gazette-bib-label">등록상태</span> 등록</div>'
            '<div class="gazette-bib-item"><span class="gazette-bib-label">재심사청구 Y</span> 2020.01.16</div>'
            '<div class="gazette-bib-item"></div>'
            '</div></div>',
            unsafe_allow_html=True,
        )

    # 초록 (접기/펼치기 카드)
    abstract_text = (
        "입력 시각적 이미지 및/또는 입력 깊이 이미지로부터 컨볼루션 신경망(CNN)을 사용하여 "
        "의미적으로 세그먼트화된 이미지 및 깊이 완성 이미지를 생성하는 컴퓨터 구현된 방법이다. "
        "일 실시예에서, 방법은"
        "<span id=\"focus-same\" style=\"background-color: #66bb6a;\">트레이닝 세트의 이미지 쌍들을 사용하여 이미지들의 의미적 세그먼트화 및 깊이 완성을 위한 CNN을 트레이닝시키는 단계</span>를 포함한다."
        "트레이닝된 CNN은 입력 이미지로부터 "
        "의미적으로 세그먼트화된 이미지 및 깊이 완성 이미지를 생성하는 데 사용될 수 있다."
    )
    with st.expander("📄 초록", expanded=True):
        st.markdown(
            f'<div class="gazette-section"><div style="font-size: 0.95rem; line-height: 1.6;">{abstract_text}</div></div>',
            unsafe_allow_html=True,
        )

    # 청구항 (접기/펼치기 카드, 내부에 청구항 1·2·3 각각 expander)
    claim1_text = (
        '트레이닝 세트의 이미지 쌍들을 사용하여 이미지들의 의미적 세그먼트화(semantic segmentation) 및 '
        "깊이 완성(depth completion)을 위한 컨볼루션 신경망(convolutional neural network)을 트레이닝시키기 위한 "
        "컴퓨터 구현된 방법으로서, 상기 방법은: 상기 트레이닝 세트로부터 이미지 쌍을 수신하는 단계; "
        "<span id=\"focus-partial\" style=\"background-color: #f9a825;\">상기 이미지 쌍에 기초하여 상기 CNN을 트레이닝시키는 단계</span>; 및 상기 트레이닝된 CNN을 저장하는 단계를 포함하고, "
        "상기 이미지 쌍의 각각은 시각적 이미지 및 대응하는 깊이 이미지를 포함하는, 방법."
    )
    claim2_text = (
        "전항의 방법에 있어서, 상기 트레이닝 세트로부터 이미지 쌍을 수신하는 단계는 "
        "<span id=\"focus-diff\" style=\"background-color: #e57373;\">시각적 이미지와 대응하는 깊이 이미지가 정렬된 쌍을 수신하는 단계</span>를 포함하는, 방법."
    )
    claim3_text = (
        "상기 이미지 쌍에 기초하여 상기 CNN을 트레이닝시키는 단계; 및 상기 트레이닝된 CNN을 저장하는 단계를 포함하고, "
        "<span id=\"focus-same-claim3\" style=\"background-color: #66bb6a;\">상기 이미지 쌍의 각각은 시각적 이미지 및 대응하는 깊이 이미지를 포함하는, 방법</span>."
    )
    with st.expander("📌 청구항", expanded=True):
        with st.expander("청구항 1", expanded=True):
            st.markdown(claim1_text, unsafe_allow_html=True)
        with st.expander("청구항 2", expanded=True):
            st.markdown(claim2_text, unsafe_allow_html=True)
        with st.expander("청구항 3", expanded=True):
            st.markdown(claim3_text, unsafe_allow_html=True)

    # 기술분야 (접기/펼치기 카드)
    with st.expander("🔬 기술분야", expanded=True):
        st.markdown(
            '<div class="gazette-section">'
            '<div style="font-size: 0.95rem; line-height: 1.6;">'
            '본 발명은 컨볼루션 신경망(CNN)을 사용하여 입력 이미지로부터 의미적 세그먼트화(semantic segmentation) 및 '
            '깊이 완성(depth completion)을 수행하는 방법 및 장치에 관한 것이다. '
            '보다 상세하게는, 시각적 이미지 및/또는 깊이 이미지를 입력받아 딥러닝 기반으로 의미 영역을 분할하고 '
            '희소(sparse) 깊이 데이터를 조밀(dense) 깊이 맵으로 완성하는 컴퓨터 구현 기술에 관한 것이다.'
            '</div></div>',
            unsafe_allow_html=True,
        )

    # 배경기술 (접기/펼치기 카드)
    with st.expander("📖 배경기술", expanded=True):
        st.markdown(
            '<div class="gazette-section">'
            '<div style="font-size: 0.95rem; line-height: 1.6;">'
            '자율 주행, 로봇 비전, 증강/가상 현실 등에서는 장면의 의미적 이해와 정확한 깊이 정보가 필수적이다. '
            '의미적 세그먼트화는 픽셀 단위로 객체 클래스를 분류하는 기술이며, 깊이 완성은 LiDAR 등으로 얻은 '
            '희소 깊이를 전체 화면에 대한 조밀 깊이 맵으로 보완하는 기술이다. '
            '종래에는 두 과제를 별도 네트워크로 처리하여 계산 비용이 크고, 시각 정보와 깊이 정보 간의 일관성이 '
            '보장되지 않는 문제가 있었다. 또한 트레이닝 시 시각 이미지와 깊이 이미지의 정렬(alignment)이 '
            '불완전한 경우 성능이 저하되는 한계가 있었다.'
            '</div></div>',
            unsafe_allow_html=True,
        )

    # 해결하려는 과제 (접기/펼치기 카드)
    with st.expander("🎯 해결하려는 과제", expanded=True):
        st.markdown(
            '<div class="gazette-section">'
            '<div style="font-size: 0.95rem; line-height: 1.6;">'
            '본 발명이 해결하려는 과제는, 단일 CNN으로 의미적 세그먼트화와 깊이 완성을 동시에 수행하여 '
            '계산 효율을 높이고 두 출력 간의 일관성을 확보하는 것이다. 또한 트레이닝 단계에서 '
            '시각적 이미지와 대응하는 깊이 이미지가 정렬된 이미지 쌍을 사용함으로써 학습 안정성과 '
            '추론 정확도를 향상시키는 방법 및 장치를 제공하는 것이다.'
            '</div></div>',
            unsafe_allow_html=True,
        )

    # 과제의 해결 수단 (접기/펼치기 카드)
    with st.expander("⚙️ 과제의 해결 수단", expanded=True):
        st.markdown(
            '<div class="gazette-section">'
            '<div style="font-size: 0.95rem; line-height: 1.6;">'
            '상기 과제를 해결하기 위하여, 본 발명은 트레이닝 세트의 이미지 쌍(시각 이미지 및 대응 깊이 이미지)을 '
            '사용하여 의미적 세그먼트화 및 깊이 완성을 위한 CNN을 트레이닝시키는 컴퓨터 구현 방법을 제공한다. '
            '방법은 트레이닝 세트로부터 이미지 쌍을 수신하는 단계, 해당 이미지 쌍에 기초하여 CNN을 트레이닝시키는 단계, '
            '및 트레이닝된 CNN을 저장하는 단계를 포함한다. 일 실시예에서 이미지 쌍 수신 단계는 '
            '시각적 이미지와 대응하는 깊이 이미지가 정렬된 쌍을 수신하는 것을 포함하여, '
            '공동 학습(joint learning)을 통한 성능 향상을 도모한다.'
            '</div></div>',
            unsafe_allow_html=True,
        )

    # 발명의 효과 (접기/펼치기 카드)
    with st.expander("⭐ 발명의 효과", expanded=True):
        st.markdown(
            '<div class="gazette-section">'
            '<div style="font-size: 0.95rem; line-height: 1.6;">'
            '본 발명에 따르면, (1) 하나의 CNN으로 의미적 세그먼트화와 깊이 완성을 동시에 수행함으로써 '
            '계산량 및 메모리 사용을 절감할 수 있고, (2) 공동 학습을 통해 두 태스크 간 일관된 특징 표현을 '
            '얻어 정확도가 향상되며, (3) 정렬된 이미지 쌍을 이용한 트레이닝으로 추론 시 더 안정적인 '
            '세그먼트 및 깊이 결과를 제공할 수 있다.'
            '</div></div>',
            unsafe_allow_html=True,
        )

    # 도면의 간단한 설명 (접기/펼치기 카드)
    with st.expander("🖼️ 도면의 간단한 설명", expanded=True):
        st.markdown(
            '<div class="gazette-section">'
            '<div style="font-size: 0.95rem; line-height: 1.6;">'
            '<strong>도 1</strong>은 본 발명의 일 실시예에 따른 의미적 세그먼트화 및 깊이 완성 방법의 전체 흐름을 나타내는 블록도이다.<br>'
            '<strong>도 2</strong>는 CNN 트레이닝 단계에서 사용되는 이미지 쌍 및 레이블 구조를 개략적으로 나타낸 도면이다.<br>'
            '<strong>도 3</strong>은 추론 단계에서 입력 이미지로부터 세그먼트 맵 및 깊이 완성 맵을 생성하는 장치 구성을 나타낸 도면이다.<br>'
            '<strong>도 4</strong>는 실시예에 따른 처리 장치의 하드웨어 구성 예를 나타낸 블록도이다.'
            '</div></div>',
            unsafe_allow_html=True,
        )

    # 발명을 실시하기 위한 구체적인 내용 (접기/펼치기 카드)
    with st.expander("📝 발명을 실시하기 위한 구체적인 내용", expanded=True):
        st.markdown(
            '<div class="gazette-section">'
            '<div style="font-size: 0.95rem; line-height: 1.6;">'
            '이하, 첨부 도면을 참조하여 본 발명의 실시예를 상세히 설명한다. 도 1에 따르면, 트레이닝 세트는 '
            '시각적 이미지와 대응하는 깊이 이미지(및 필요시 세그먼트/깊이 레이블)로 구성된 이미지 쌍들을 포함한다. '
            '트레이닝 단계에서는 이 쌍들을 입력으로 하여 CNN의 파라미터가 갱신되며, 손실 함수는 세그먼트 오차와 '
            '깊이 오차를 결합한 다중 태스크 손실일 수 있다. 트레이닝이 완료된 CNN은 저장 매체에 저장되고, '
            '추론 시(도 3) 새로운 시각 이미지 및/또는 희소 깊이 이미지를 입력받아 의미적 세그먼트 맵과 '
            '조밀 깊이 완성 맵을 출력한다. 정렬된 이미지 쌍을 사용함으로써 두 모달리티 간의 대응 관계가 '
            '학습에 반영되어 성능이 향상된다. 도 4의 처리 장치(예: CPU, GPU, 메모리)는 상기 방법을 '
            '실행하기 위한 프로그램을 저장하고 실행한다.'
            '</div></div>',
            unsafe_allow_html=True,
        )

    # 부호의 설명 (접기/펼치기 카드)
    with st.expander("🔢 부호의 설명", expanded=True):
        st.markdown(
            '<div class="gazette-section">'
            '<div class="gazette-bib" style="grid-template-columns: 1fr 1fr; gap: 0.5rem 1rem;">'
            '<div class="gazette-bib-item"><span class="gazette-bib-label">100</span> 트레이닝 세트</div>'
            '<div class="gazette-bib-item"><span class="gazette-bib-label">110</span> 이미지 쌍</div>'
            '<div class="gazette-bib-item"><span class="gazette-bib-label">120</span> 시각적 이미지</div>'
            '<div class="gazette-bib-item"><span class="gazette-bib-label">130</span> 깊이 이미지</div>'
            '<div class="gazette-bib-item"><span class="gazette-bib-label">200</span> CNN(컨볼루션 신경망)</div>'
            '<div class="gazette-bib-item"><span class="gazette-bib-label">210</span> 인코더</div>'
            '<div class="gazette-bib-item"><span class="gazette-bib-label">220</span> 디코더(세그먼트)</div>'
            '<div class="gazette-bib-item"><span class="gazette-bib-label">230</span> 디코더(깊이 완성)</div>'
            '<div class="gazette-bib-item"><span class="gazette-bib-label">300</span> 처리 장치</div>'
            '<div class="gazette-bib-item"><span class="gazette-bib-label">310</span> 저장 매체</div>'
            '</div></div>',
            unsafe_allow_html=True,
        )

# 관련도 링크 클릭 시 포커스 이동 후 하이라이트 3회 깜박임
st.components.v1.html(
    """
    <script>
    (function(){
        var win = window.parent;
        var doc = win.document;
        function runBlink(){
            var hash = win.location.hash;
            if (!hash || hash.indexOf("#focus-") !== 0) return;
            var el = doc.querySelector(hash);
            if (!el) return;
            el.classList.remove("focus-blink");
            el.offsetHeight;
            el.classList.add("focus-blink");
            setTimeout(function(){ el.classList.remove("focus-blink"); }, 700);
        }
        win.addEventListener("hashchange", runBlink);
        if (win.location.hash && win.location.hash.indexOf("#focus-") === 0) {
            setTimeout(runBlink, 150);
        }
    })();
    </script>
    """,
    height=0,
)