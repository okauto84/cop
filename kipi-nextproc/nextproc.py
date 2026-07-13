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

# iframe 높이(px). CSS로 100vh에 맞추므로 대략적인 값이면 됩니다.
IFRAME_HEIGHT = 900

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
    Streamlit iframe 안에서 세로 스크롤이 하나만 생기도록 보정합니다.
    - body는 스크롤하지 않음
    - .diagram-scroll만 세로/가로 스크롤
    - 팝업은 iframe 뷰포트(보이는 화면) 중앙
    """
    head_injection = """
<style>
  /* 문서 전체 스크롤 제거 → 다이어그램 영역만 스크롤 */
  html, body {
    height: 100% !important;
    max-height: 100vh !important;
    max-height: 100dvh !important;
    margin: 0 !important;
    overflow: hidden !important;
  }
  .app-header {
    position: sticky;
    top: 0;
    z-index: 100;
  }
  .diagram-scroll {
    max-height: calc(100vh - 150px) !important;
    max-height: calc(100dvh - 150px) !important;
    overflow-x: auto !important;
    overflow-y: auto !important;
  }

  /* 팝업: iframe 보이는 화면 중앙 */
  .popup-overlay {
    position: fixed !important;
    inset: 0 !important;
    width: 100% !important;
    height: 100% !important;
    margin: 0 !important;
    z-index: 99999 !important;
    display: none;
    align-items: center !important;
    justify-content: center !important;
    overflow: auto !important;
    padding: 16px !important;
    box-sizing: border-box !important;
  }
  .popup-overlay.open {
    display: flex !important;
  }
  .popup-overlay .popup {
    position: relative !important;
    margin: auto !important;
    max-height: min(85vh, 85dvh) !important;
    flex-shrink: 0;
  }
</style>
"""

    body_injection = """
<script>
(function () {
  function syncDiagramScrollHeight() {
    var scroll = document.querySelector(".diagram-panel.active .diagram-scroll")
      || document.querySelector(".diagram-scroll");
    if (!scroll) return;

    var reserved = 0;
    [".app-header", ".main-tabs", ".sub-tabs.visible", ".legend"].forEach(function (sel) {
      var el = document.querySelector(sel);
      if (el) reserved += el.getBoundingClientRect().height;
    });
    // 여유 픽셀(테두리/스크롤바)
    reserved += 8;
    var h = Math.max(240, window.innerHeight - reserved);
    scroll.style.maxHeight = h + "px";
  }

  function centerPopupOverlay() {
    var overlay = document.getElementById("popup-overlay");
    if (!overlay || !overlay.classList.contains("open")) return;

    // fixed + flex 중앙 정렬이 보이도록 인라인 보정
    overlay.style.position = "fixed";
    overlay.style.inset = "0";
    overlay.style.top = "0";
    overlay.style.left = "0";
    overlay.style.right = "0";
    overlay.style.bottom = "0";
    overlay.style.width = "100%";
    overlay.style.height = "100%";
    overlay.style.display = "flex";
    overlay.style.alignItems = "center";
    overlay.style.justifyContent = "center";
    overlay.scrollTop = 0;

    var popup = overlay.querySelector(".popup");
    if (popup) popup.scrollTop = 0;
  }

  function resetPopupOverlayStyle() {
    var overlay = document.getElementById("popup-overlay");
    if (!overlay) return;
    overlay.style.position = "";
    overlay.style.inset = "";
    overlay.style.top = "";
    overlay.style.left = "";
    overlay.style.right = "";
    overlay.style.bottom = "";
    overlay.style.width = "";
    overlay.style.height = "";
    overlay.style.display = "";
    overlay.style.alignItems = "";
    overlay.style.justifyContent = "";
  }

  function patchPopupCentering() {
    if (typeof window.showPopup !== "function") return false;
    if (window.showPopup.__centerPatched) return true;

    var originalShow = window.showPopup;
    window.showPopup = function (id) {
      originalShow(id);
      centerPopupOverlay();
      requestAnimationFrame(centerPopupOverlay);
    };
    window.showPopup.__centerPatched = true;

    if (typeof window.closePopupBtn === "function" && !window.closePopupBtn.__centerPatched) {
      var originalClose = window.closePopupBtn;
      window.closePopupBtn = function () {
        originalClose();
        resetPopupOverlayStyle();
      };
      window.closePopupBtn.__centerPatched = true;
    }
    return true;
  }

  function boot() {
    syncDiagramScrollHeight();
    window.addEventListener("resize", syncDiagramScrollHeight);

    // 탭 전환 시 활성 패널의 스크롤 높이 재계산
    document.querySelectorAll(".main-tab, .sub-tab").forEach(function (tab) {
      tab.addEventListener("click", function () {
        setTimeout(syncDiagramScrollHeight, 0);
        setTimeout(syncDiagramScrollHeight, 80);
      });
    });

    if (patchPopupCentering()) return;
    var tries = 0;
    var timer = setInterval(function () {
      tries += 1;
      if (patchPopupCentering() || tries > 40) clearInterval(timer);
    }, 50);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
</script>
"""

    result = html
    if "</head>" in result:
        result = result.replace("</head>", head_injection + "</head>", 1)
    else:
        result = head_injection + result

    if "</body>" in result:
        result = result.replace("</body>", body_injection + "</body>", 1)
    else:
        result = result + body_injection

    return result


# Streamlit 페이지 스크롤을 제거하고, iframe만 화면을 채우도록 설정
st.markdown(
    """
<style>
  html, body, [data-testid="stAppViewContainer"],
  [data-testid="stAppViewContainer"] > .main,
  section.main,
  .main .block-container {
    height: 100% !important;
    max-height: 100vh !important;
    max-height: 100dvh !important;
    overflow: hidden !important;
  }

  [data-testid="stHeader"],
  [data-testid="stToolbar"],
  [data-testid="stDecoration"],
  [data-testid="stStatusWidget"],
  #MainMenu,
  footer {
    display: none !important;
  }

  .block-container {
    padding: 0 !important;
    margin: 0 !important;
    max-width: 100% !important;
  }

  /* components.html iframe을 뷰포트에 맞춤 → 바깥 스크롤 제거 */
  iframe {
    border: none !important;
    width: 100% !important;
    height: 100vh !important;
    height: 100dvh !important;
    min-height: 100vh !important;
    min-height: 100dvh !important;
  }

  /* iframe을 감싸는 요소도 높이 고정 */
  [data-testid="stIFrame"],
  div:has(> iframe) {
    height: 100vh !important;
    height: 100dvh !important;
    overflow: hidden !important;
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

# scrolling=False: iframe 자체 스크롤바 제거 → 내부 .diagram-scroll만 스크롤
components.html(
    html_content,
    height=IFRAME_HEIGHT,
    scrolling=False,
)
