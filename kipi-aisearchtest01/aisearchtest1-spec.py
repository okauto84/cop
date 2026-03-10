# -*- coding: utf-8 -*-

import streamlit as st
import pandas as pd

# AI분석 탭 - 발명 3요소 블록 스타일
st.markdown("""
<style>
.ai-summary-block {
    border-radius: 8px;
    padding: 1rem 1.25rem;
    margin-bottom: 1rem;
    text-align: left;
    font-size: 0.95rem;
    line-height: 1.5;
}
.ai-summary-block .block-title {
    font-weight: bold;
    margin-bottom: 0.5rem;
    font-size: 1rem;
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
.compare-box { border-radius: 10px; padding: 1.25rem 1.5rem; margin-bottom: 1rem; background: #fafafa; border: 1px solid #eee; box-shadow: 0 1px 3px rgba(0,0,0,0.08); text-align: left; font-size: 0.9rem; line-height: 1.6; }
.compare-box.common { border-left: 4px solid #66bb6a; }
.compare-box.diff { border-left: 4px solid #ffb74d; }
.compare-box-title { font-weight: bold; margin-bottom: 0.75rem; font-size: 1rem; }
.compare-box.common .compare-box-title { color: #2e7d32; }
.compare-box.diff .compare-box-title { color: #e65100; }
.compare-box ul { margin: 0; padding-left: 1.25rem; }
.compare-box li { margin-bottom: 0.5rem; }
.compare-box .highlight { color: #1565c0; font-weight: 500; }
/* 탭별 스크롤: 탭 패널 내용 영역에 최대 높이 및 세로 스크롤 */
[data-testid="stTabs"] [data-testid="stVerticalBlock"] { max-height: 75vh; overflow-y: auto; }
/* 공보 탭 스타일 */
.gazette-doc-tabs { display: flex; align-items: center; gap: 0.5rem; margin-bottom: 1.5rem; padding-bottom: 0.75rem; border-bottom: 1px solid #e0e0e0; }
.gazette-doc-tabs span { padding: 0.4rem 0.9rem; border-radius: 6px; font-size: 0.9rem; cursor: pointer; }
.gazette-doc-tabs .tab-inactive { background: #f5f5f5; color: #666; }
.gazette-doc-tabs .tab-active { background: #1565c0; color: white; }
.gazette-doc-tabs .tab-arrow { margin-left: auto; font-size: 1.2rem; color: #666; }
.gazette-title-ko { font-size: 1.35rem; font-weight: bold; margin-bottom: 0.35rem; }
.gazette-title-en { font-size: 0.9rem; color: #555; margin-bottom: 0.75rem; }
.gazette-tag-row { margin-bottom: 0.5rem; }
.gazette-tag { display: inline-block; padding: 0.2rem 0.6rem; border-radius: 999px; font-size: 0.8rem; margin-right: 0.35rem; margin-bottom: 0.25rem; }
.gazette-tag-cpc { background: #1976d2; color: white; }
.gazette-tag-ipc { background: #388e3c; color: white; }
.gazette-section { background: #fafafa; border-radius: 8px; padding: 1rem 1.25rem; margin-bottom: 1rem; border: 1px solid #eee; }
.gazette-section-title { font-weight: bold; margin-bottom: 0.75rem; font-size: 1rem; }
.gazette-bib { display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem 1.5rem; font-size: 0.9rem; }
.gazette-bib-item { display: flex; }
.gazette-bib-label { min-width: 100px; color: #555; }
.gazette-legend { font-size: 0.8rem; color: #555; }
.gazette-legend-item { display: flex; align-items: center; gap: 0.35rem; margin-bottom: 0.2rem; }
.gazette-legend-dot { width: 10px; height: 10px; border-radius: 2px; }
.gazette-claims-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem; }
.gazette-claim-btns { font-size: 0.8rem; }
.gazette-claim-item { margin-bottom: 0.75rem; padding: 0.75rem; background: white; border-radius: 6px; border: 1px solid #eee; }
.gazette-claim-item-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem; }
/* 공보 탭 - 스크롤 따라다니는 구성요소 범례 위젯 */
.gazette-legend-widget { position: fixed; right: 24px; top: 50%; transform: translateY(-50%); z-index: 999; background: #fff; padding: 12px 14px; border-radius: 8px; box-shadow: 0 2px 12px rgba(0,0,0,0.12); border: 1px solid #e0e0e0; font-size: 0.8rem; color: #333; }
.gazette-legend-widget .legend-item { display: flex; align-items: center; gap: 8px; margin-bottom: 6px; }
.gazette-legend-widget .legend-item:last-child { margin-bottom: 0; }
.gazette-legend-widget .legend-dot { width: 12px; height: 12px; border-radius: 2px; flex-shrink: 0; }
</style>
""", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["AI분석", "공보"])

with tab1:
    st.markdown("### 💡 발명의 3요소 (AI 요약)")
    st.markdown("")  # 간격

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            '<div class="ai-summary-block" style="background-color: #FEE7E7;">'
            '<div class="block-title" style="color: #c62828;">⚠️ 해결과제 (Problem)</div>'
            "창문형 에어컨 설치 시 본체와 커텐프레임 사이의 유격으로 인한 냉기 누설 및 조립 공정의 복잡함을 해결하고자 함."
            "</div>",
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            '<div class="ai-summary-block" style="background-color: #E7FEE7;">'
            '<div class="block-title" style="color: #2e7d32;">🎯 발명의 목적 (Object)</div>'
            "베이스팬 내부에 관통형 가이드공을 형성하여 커텐프레임의 슬라이딩 기밀성을 극대화하고 외관을 미려하게 함."
            "</div>",
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            '<div class="ai-summary-block" style="background-color: #E7EEFE;">'
            '<div class="block-title" style="color: #1565c0;">⭐ 발명의 효과 (Effect)</div>'
            "부품 수 절감으로 제조 원가를 낮추며, 완벽한 밀폐를 통해 에어컨의 냉방 효율을 획기적으로 향상시킴."
            "</div>",
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.markdown("### 💡 구성요소 대비표 (Claim Analysis Table)")
    st.markdown(
        """
        <table class="claim-table">
        <thead>
        <tr>
        <th>출원발명 구성요소</th>
        <th>인용발명 구성요소</th>
        <th>관련도</th>
        <th>대비 결과 요약</th>
        </tr>
        </thead>
        <tbody>
        <tr>
        <td><span class="comp-name">베이스팬(100)</span><span class="comp-desc">양측면에 가이드공(170)이 관통 형성됨</span></td>
        <td><span class="comp-name">베리어(73)</span><span class="comp-desc">양단에 실내측을 향해 연장된 단부측판(75) 구비</span></td>
        <td><span class="tag tag-partial">일부동일</span></td>
        <td>본체 구조물에 결합 기능을 통합한 점은 유사하나, 관통공 vs 측판 구조의 형태적 차이 존재</td>
        </tr>
        <tr>
        <td><span class="comp-name">상측캐비넷(650)</span><span class="comp-desc">삽입채널(662) 및 삽입가이드편(664) 형성</span></td>
        <td><span class="comp-name">측면브라켓(80)</span><span class="comp-desc">절곡된 스프링고정부(81)가 일체로 성형됨</span></td>
        <td><span class="tag tag-diff">차이</span></td>
        <td>슬라이딩 안내를 위한 레일 채널 구조와 스냅 결합을 위한 개별 절곡부의 물리적 형상 차이</td>
        </tr>
        <tr>
        <td><span class="comp-name">커텐프레임(710)</span><span class="comp-desc">가이드공 및 단차부에 삽입되어 슬라이딩됨</span></td>
        <td><span class="comp-name">전면패널(95)</span><span class="comp-desc">체결스프링(99)을 통해 본체에 고정됨</span></td>
        <td><span class="tag tag-diff">차이</span></td>
        <td>가동형 부품의 길이 조절(Sliding) 방식과 고정형 외장재의 단순 결합(Snap) 방식의 차이</td>
        </tr>
        <tr>
        <td><span class="comp-name">탈거방지턱(718)</span><span class="comp-desc">탄성채널(719)에 의한 임의 이탈 방지</span></td>
        <td><span class="comp-name">체결스프링(99)</span><span class="comp-desc">안착부(99c)와 걸림부(99d)로 탈거 방지</span></td>
        <td><span class="tag tag-same">실질적동일</span></td>
        <td>재료의 탄성 변형을 이용하여 결합 후 역방향 이탈을 방지하는 기구적 메커니즘이 매우 유사함</td>
        </tr>
        </tbody>
        </table>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("")  # 간격
    st.markdown("### 💡 유사점 및 차이점")
    comp_col1, comp_col2 = st.columns(2)
    with comp_col1:
        st.markdown(
            '<div class="compare-box common">'
            '<div class="compare-box-title">✓ 유사점 (Commonalities)</div>'
            '<ul>'
            '<li>부품 일체화 설계: 두 발명 모두 별도의 체결 부품(나사 등) 없이 본체 구조물 사출 시 결합 기능을 <span class="highlight">일체화</span>하여 공정 단순화를 달성함.</li>'
            '<li>탄성 결합 원리: 출원발명의 탄성채널과 인용발명의 체결 스프링은 모두 재료의 <span class="highlight">탄성 복원력</span>을 이용한 스냅 핏 (Snap-fit) 방식을 공유함.</li>'
            '</ul>'
            '</div>',
            unsafe_allow_html=True,
        )
    with comp_col2:
        st.markdown(
            '<div class="compare-box diff">'
            '<div class="compare-box-title">💡 차이점 (Differences)</div>'
            '<ul>'
            '<li>운동 및 기구 형태: 출원발명은 이동형 부품을 위한 <span class="highlight">선형 가이드(Sliding)</span> 구조이나, 인용발명은 고정형 부품을 위한 <span class="highlight">점 결합(Point)</span> 구조임.</li>'
            '<li>기술적 과제: 출원발명은 <span class="highlight">기밀성(냉기 누설 차단)</span> 확보가 핵심이며, 인용발명은 <span class="highlight">부품 호환성(좌우 공용화)</span> 확보에 초점을 맞춤.</li>'
            '</ul>'
            '</div>',
            unsafe_allow_html=True,
        )

with tab2:
    # 스크롤 따라다니는 구성요소 범례 위젯 (오른쪽 고정)
    legend_colors = [
        ("#ffeb3b", "구성요소 1"),   # yellow
        ("#66bb6a", "구성요소 2"),   # bright green
        ("#f06292", "구성요소 3"),   # pink
        ("#4dd0e1", "구성요소 4"),   # cyan
        ("#ab47bc", "구성요소 5"),   # magenta/purple
        ("#ff9800", "구성요소 6"),   # orange
        ("#aed581", "구성요소 7"),   # lime green
        ("#00897b", "구성요소 8"),   # teal
    ]
    legend_items = "".join(
        f'<div class="legend-item"><span class="legend-dot" style="background:{c}"></span>{label}</div>'
        for c, label in legend_colors
    )
    st.markdown(
        f'<div class="gazette-legend-widget">{legend_items}</div>',
        unsafe_allow_html=True,
    )

    # 제목 영역 + 분류코드
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

    # 서지 정보
    st.markdown('<div class="gazette-section-title">서지 정보</div>', unsafe_allow_html=True)
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

    # 초록
    st.markdown('<div class="gazette-section-title">초록</div>', unsafe_allow_html=True)
    abstract_text = (
        "입력 시각적 이미지 및/또는 입력 깊이 이미지로부터 컨볼루션 신경망(CNN)을 사용하여 "
        "의미적으로 세그먼트화된 이미지 및 깊이 완성 이미지를 생성하는 컴퓨터 구현된 방법이다. "
        "일 실시예에서, 방법은 <span style="background-color: #fff59d;">트레이닝 세트의 이미지 쌍들을 사용하여 이미지들의 의미적 세그먼트화 및 "
        "깊이 완성을 위한 CNN을 트레이닝시키는 단계</span>를 포함한다. 트레이닝된 CNN은 입력 이미지로부터 "
        "의미적으로 세그먼트화된 이미지 및 깊이 완성 이미지를 생성하는 데 사용될 수 있다."
    )
    st.markdown(
        f'<div class="gazette-section"><div style="font-size: 0.95rem; line-height: 1.6;">{abstract_text}</div></div>',
        unsafe_allow_html=True,
    )

    # 청구항
    st.markdown(
        '<div class="gazette-claims-header">'
        '<span class="gazette-section-title">청구항</span>'
        '<span class="gazette-claim-btns">모두 접기 &nbsp; 모두 펼치기</span>'
        '</div>',
        unsafe_allow_html=True,
    )
    claim1_text = (
        '트레이닝 세트의 이미지 쌍들을 사용하여 이미지들의 의미적 세그먼트화(semantic segmentation) 및 '
        "깊이 완성(depth completion)을 위한 컨볼루션 신경망(convolutional neural network)을 트레이닝시키기 위한 "
        "컴퓨터 구현된 방법으로서, 상기 방법은: 상기 트레이닝 세트로부터 이미지 쌍을 수신하는 단계; "
        "<span style=\"background-color: #c8e6c9;\">상기 이미지 쌍에 기초하여 상기 CNN을 트레이닝시키는 단계</span>; 및 상기 트레이닝된 CNN을 저장하는 단계를 포함하고, "
        "상기 이미지 쌍의 각각은 시각적 이미지 및 대응하는 깊이 이미지를 포함하는, 방법."
    )
    with st.expander("1. 청구항 1  접기", expanded=True):
        st.markdown(claim1_text, unsafe_allow_html=True) 