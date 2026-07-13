# -*- coding: utf-8 -*-
"""
차세대 지식재산행정시스템 ISP/BPR — 권리별 행정절차 흐름도
proc.html과 동일한 UI/동작을 Streamlit에서 실행합니다.
"""

from __future__ import annotations

from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

BASE_DIR = Path(__file__).resolve().parent
PROC_HTML_PATH = BASE_DIR / "proc.html"

st.set_page_config(
    page_title="차세대 지식재산행정시스템 ISP/BPR — 권리별 행정절차 흐름도",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def load_proc_html() -> str:
    if not PROC_HTML_PATH.is_file():
        raise FileNotFoundError(f"proc.html을 찾을 수 없습니다: {PROC_HTML_PATH}")
    return PROC_HTML_PATH.read_text(encoding="utf-8")


def prepare_html_for_streamlit(html: str) -> str:
    """
    iframe 환경에서도 proc.html과 동일하게 보이도록
    스크롤/높이 관련 CSS만 최소 보정합니다.
    """
    injection = """
<style>
  /* Streamlit iframe 안에서 전체 콘텐츠가 잘리지 않도록 보정 */
  html, body {
    height: auto !important;
    min-height: 100% !important;
    overflow: auto !important;
  }
  .diagram-scroll {
    max-height: none !important;
    overflow: visible !important;
  }
  .app-header {
    position: sticky;
    top: 0;
  }
</style>
"""
    if "</head>" in html:
        return html.replace("</head>", injection + "</head>", 1)
    return injection + html


# Streamlit 기본 여백/크롬을 줄여 HTML 화면을 최대한 그대로 표시
st.markdown(
    """
<style>
  [data-testid="stHeader"] { display: none; }
  [data-testid="stToolbar"] { display: none; }
  .block-container {
    padding-top: 0.5rem !important;
    padding-bottom: 0.5rem !important;
    padding-left: 0.5rem !important;
    padding-right: 0.5rem !important;
    max-width: 100% !important;
  }
  iframe {
    border: none !important;
  }
</style>
""",
    unsafe_allow_html=True,
)

try:
    html_content = prepare_html_for_streamlit(load_proc_html())
except FileNotFoundError as error:
    st.error(str(error))
    st.stop()

# proc.html 전체(탭·스윔레인·팝업·연결선 JS)를 그대로 임베드
components.html(
    html_content,
    height=1400,
    scrolling=True,
)
