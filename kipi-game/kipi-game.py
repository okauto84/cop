# -*- coding: utf-8 -*-
"""
KIPI 로봇 잡기 — Streamlit 래퍼

게임 본체는 game.html (60fps Canvas)에서 실행됩니다.
Streamlit Cloud:
    streamlit run kipi-game.py

로컬 WebSocket 멀티플레이(선택):
    secrets.toml 에 game_ws_url = "ws://localhost:8765/ws" 설정 후
    별도 WS 서버 실행 (로컬 개발용)
"""

from __future__ import annotations

import html as html_lib
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

BASE_DIR = Path(__file__).resolve().parent
GAME_HTML_PATH = BASE_DIR / "game.html"

st.set_page_config(page_title="kipi-game", page_icon="🤖", layout="wide")

try:
    ws_url = st.secrets.get("game_ws_url", "")
except Exception:
    ws_url = ""

if not GAME_HTML_PATH.is_file():
    st.error(f"게임 파일을 찾을 수 없습니다: {GAME_HTML_PATH}")
    st.stop()

game_html = GAME_HTML_PATH.read_text(encoding="utf-8")
game_html = game_html.replace("__WS_URL__", ws_url or "")

# 별도 iframe 프레임에 game.html 임베드 (Streamlit 리런과 분리)
escaped = html_lib.escape(game_html, quote=True)
frame_html = f"""
<div style="width:100%;max-width:960px;margin:0 auto;">
  <iframe
    id="kipi-game-frame"
    title="KIPI 로봇 잡기"
    srcdoc="{escaped}"
    style="
      width:100%;
      height:780px;
      border:none;
      border-radius:12px;
      overflow:hidden;
      background:#0b0d17;
      box-shadow:0 4px 24px #00000055;
    "
    sandbox="allow-scripts allow-same-origin"
  ></iframe>
</div>
"""

components.html(frame_html, height=790, scrolling=False)

with st.expander("게임 안내", expanded=False):
    st.markdown(
        """
- **입장**: 프레임 안에서 플레이어 ID 입력 후 입장
- **조작**: 움직이는 🤖 로봇을 **마우스 클릭** (터치 지원)
- **승리**: 로봇 **10마리**를 먼저 잡은 사람
- **승리 후**: 승자 배너의 **[다시시작]** 버튼으로 점수·로봇을 초기화하고 새 게임 시작
- **중간 합류**: 게임이 진행 중이어도 멈추지 않으며, 새 ID로 **바로 입장**해 참여 (점수 0부터)
- 게임 루프는 HTML Canvas **requestAnimationFrame(60fps)** 으로 동작합니다.
        """
    )
