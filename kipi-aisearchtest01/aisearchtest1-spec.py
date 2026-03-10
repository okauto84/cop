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

with tab2:
    st.header("공보")
    st.write("공보 탭 내용을 여기에 작성하세요.") 