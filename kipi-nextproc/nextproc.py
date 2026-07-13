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
    iframe 환경에서도 proc.html과 동일하게 보이도록 보정합니다.
    - 긴 흐름도에서도 팝업이 '현재 보이는 화면' 중앙에 뜨도록 처리
    """
    head_injection = """
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

  /* 팝업: 현재 보이는 화면(뷰포트) 중앙 고정 */
  .popup-overlay {
    position: fixed !important;
    inset: 0 !important;
    top: 0 !important;
    left: 0 !important;
    right: 0 !important;
    bottom: 0 !important;
    width: 100% !important;
    height: 100% !important;
    height: 100vh !important;
    height: 100dvh !important;
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

    # showPopup 직후 오버레이를 보이는 영역 중앙에 맞추고, 스크롤로 밀리지 않게 보정
    body_injection = """
<script>
(function () {
  function viewportHeight() {
    if (window.visualViewport && window.visualViewport.height) {
      return window.visualViewport.height;
    }
    return window.innerHeight || document.documentElement.clientHeight || 800;
  }

  function viewportOffsetTop() {
    if (window.visualViewport && typeof window.visualViewport.offsetTop === "number") {
      return window.visualViewport.offsetTop + (window.scrollY || window.pageYOffset || 0);
    }
    return window.scrollY || window.pageYOffset || 0;
  }

  function centerPopupOverlay() {
    var overlay = document.getElementById("popup-overlay");
    if (!overlay || !overlay.classList.contains("open")) return;

    var top = viewportOffsetTop();
    var height = viewportHeight();

    // 긴 문서 + iframe 스크롤에서도 보이는 화면 중앙에 오도록 absolute로 보정
    overlay.style.position = "absolute";
    overlay.style.top = top + "px";
    overlay.style.left = "0";
    overlay.style.right = "0";
    overlay.style.bottom = "auto";
    overlay.style.width = "100%";
    overlay.style.height = height + "px";
    overlay.style.display = "flex";
    overlay.style.alignItems = "center";
    overlay.style.justifyContent = "center";
    overlay.scrollTop = 0;

    var popup = overlay.querySelector(".popup");
    if (popup) {
      popup.scrollTop = 0;
      // 레이아웃 반영 후 팝업 자체가 보이게 보장
      requestAnimationFrame(function () {
        try {
          popup.scrollIntoView({ block: "center", inline: "nearest", behavior: "instant" });
        } catch (e) {
          popup.scrollIntoView(true);
        }
      });
    }
  }

  function resetPopupOverlayStyle() {
    var overlay = document.getElementById("popup-overlay");
    if (!overlay) return;
    overlay.style.position = "";
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
      setTimeout(centerPopupOverlay, 50);
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

    window.addEventListener("resize", function () {
      if (document.getElementById("popup-overlay")?.classList.contains("open")) {
        centerPopupOverlay();
      }
    });
    window.addEventListener("scroll", function () {
      if (document.getElementById("popup-overlay")?.classList.contains("open")) {
        centerPopupOverlay();
      }
    }, { passive: true });

    return true;
  }

  function boot() {
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
