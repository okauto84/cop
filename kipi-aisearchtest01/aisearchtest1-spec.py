# -*- coding: utf-8 -*-

import streamlit as st
import pandas as pd

st.title("검색 테스트")

tab1, tab2 = st.tabs(["AI분석", "공보"])

with tab1:
    st.header("AI분석")
    st.write("AI분석 탭 내용을 여기에 작성하세요.")

with tab2:
    st.header("공보")
    st.write("공보 탭 내용을 여기에 작성하세요.") 