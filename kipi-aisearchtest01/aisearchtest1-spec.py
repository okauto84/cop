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
.compare-box { border-radius: 10px; padding: 1.25rem 1.5rem; margin-bottom: 1rem; background: #fafafa; border: 1px solid #eee; box-shadow: 0 1px 3px rgba(0,0,0,0.08); text-align: left; font-size: 0.9rem; line-height: 1.6; }
.compare-box.common { border-left: 4px solid #66bb6a; }
.compare-box.diff { border-left: 4px solid #ffb74d; }
.compare-box-title { font-weight: bold; margin-bottom: 0.75rem; font-size: 1rem; }
.compare-box.common .compare-box-title { color: #2e7d32; }
.compare-box.diff .compare-box-title { color: #e65100; }
.compare-box ul { margin: 0; padding-left: 1.25rem; }
.compare-box li { margin-bottom: 0.5rem; }
.compare-box .highlight { color: #1565c0; font-weight: 500; }
/* 좌(공보) 우(AI분석) 컬럼 각각 독립 스크롤바 */
[data-testid="column"] {
    max-height: 85vh;
    overflow-y: auto;
    overflow-x: hidden;
    min-height: 200px;
}
[data-testid="column"]:first-child {
    border-right: 2px solid #bdbdbd;
    padding-right: 1rem;
}
[data-testid="column"]:last-child {
    padding-left: 1rem;
}
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
.gazette-claims-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem; }
.gazette-claim-btns { font-size: 0.8rem; }
.gazette-claim-item { margin-bottom: 0.75rem; padding: 0.75rem; background: white; border-radius: 6px; border: 1px solid #eee; }
.gazette-claim-item-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem; }
</style>
""", unsafe_allow_html=True)

# 좌측: 공보 | 우측: AI분석 (동시 표시)
left_col, right_col = st.columns(2)

# ========== 우측: AI분석 ==========
with right_col:
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
        <td><a href="#focus-partial" class="tag-link"><span class="tag tag-partial">일부동일</span></a></td>
        <td>본체 구조물에 결합 기능을 통합한 점은 유사하나, 관통공 vs 측판 구조의 형태적 차이 존재</td>
        </tr>
        <tr>
        <td><span class="comp-name">상측캐비넷(650)</span><span class="comp-desc">삽입채널(662) 및 삽입가이드편(664) 형성</span></td>
        <td><span class="comp-name">측면브라켓(80)</span><span class="comp-desc">절곡된 스프링고정부(81)가 일체로 성형됨</span></td>
        <td><a href="#focus-diff" class="tag-link"><span class="tag tag-diff">차이</span></a></td>
        <td>슬라이딩 안내를 위한 레일 채널 구조와 스냅 결합을 위한 개별 절곡부의 물리적 형상 차이</td>
        </tr>
        <tr>
        <td><span class="comp-name">커텐프레임(710)</span><span class="comp-desc">가이드공 및 단차부에 삽입되어 슬라이딩됨</span></td>
        <td><span class="comp-name">전면패널(95)</span><span class="comp-desc">체결스프링(99)을 통해 본체에 고정됨</span></td>
        <td><a href="#focus-diff" class="tag-link"><span class="tag tag-diff">차이</span></a></td>
        <td>가동형 부품의 길이 조절(Sliding) 방식과 고정형 외장재의 단순 결합(Snap) 방식의 차이</td>
        </tr>
        <tr>
        <td><span class="comp-name">탈거방지턱(718)</span><span class="comp-desc">탄성채널(719)에 의한 임의 이탈 방지</span></td>
        <td><span class="comp-name">체결스프링(99)</span><span class="comp-desc">안착부(99c)와 걸림부(99d)로 탈거 방지</span></td>
        <td><a href="#focus-same" class="tag-link"><span class="tag tag-same">실질적동일</span></a></td>
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
        "일 실시예에서, 방법은"
        "<span id=\"focus-same\" style=\"background-color: #66bb6a;\">트레이닝 세트의 이미지 쌍들을 사용하여 이미지들의 의미적 세그먼트화 및 깊이 완성을 위한 CNN을 트레이닝시키는 단계</span>를 포함한다."
        "트레이닝된 CNN은 입력 이미지로부터 "
        "의미적으로 세그먼트화된 이미지 및 깊이 완성 이미지를 생성하는 데 사용될 수 있다."
    )
    st.markdown(
        f'<div class="gazette-section"><div style="font-size: 0.95rem; line-height: 1.6;">{abstract_text}</div></div>',
        unsafe_allow_html=True,
    )

    # 청구항 (초기: 청구항 1, 2 모두 펼침)
    st.markdown("**청구항**")
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
    with st.expander("청구항 1", expanded=True):
        st.markdown(claim1_text, unsafe_allow_html=True)
    with st.expander("청구항 2", expanded=True):
        st.markdown(claim2_text, unsafe_allow_html=True)
    with st.expander("청구항 3", expanded=True):
        st.markdown(claim3_text, unsafe_allow_html=True)

    # 기술분야
    st.markdown('<div class="gazette-section-title">기술분야</div>', unsafe_allow_html=True)
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

    # 배경기술
    st.markdown('<div class="gazette-section-title">배경기술</div>', unsafe_allow_html=True)
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

    # 해결하려는 과제
    st.markdown('<div class="gazette-section-title">해결하려는 과제</div>', unsafe_allow_html=True)
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

    # 과제의 해결 수단
    st.markdown('<div class="gazette-section-title">과제의 해결 수단</div>', unsafe_allow_html=True)
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

    # 발명의 효과
    st.markdown('<div class="gazette-section-title">발명의 효과</div>', unsafe_allow_html=True)
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

    # 도면의 간단한 설명
    st.markdown('<div class="gazette-section-title">도면의 간단한 설명</div>', unsafe_allow_html=True)
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

    # 발명을 실시하기 위한 구체적인 내용
    st.markdown('<div class="gazette-section-title">발명을 실시하기 위한 구체적인 내용</div>', unsafe_allow_html=True)
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

    # 부호의 설명
    st.markdown('<div class="gazette-section-title">부호의 설명</div>', unsafe_allow_html=True)
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