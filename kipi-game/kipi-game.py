# -*- coding: utf-8 -*-
"""
로봇 잡기 멀티플레이어 아케이드 (Streamlit)

Streamlit Cloud / 로컬 모두:
    streamlit run kipi-game.py
"""

from __future__ import annotations

import math
import random
import threading
import uuid
from dataclasses import dataclass, field
from typing import Any

import plotly.graph_objects as go
import streamlit as st
from streamlit_autorefresh import st_autorefresh

# ── 게임 설정 ────────────────────────────────────────────────────────────────
ARENA_W = 900
ARENA_H = 520
ROBOT_RADIUS = 28
TARGET_SCORE = 10
MAX_ROBOTS = 10
TICK_MS = 120

st.set_page_config(page_title="kipi-game", page_icon="🤖", layout="wide")


# ── 게임 상태 (앱 전체 공유 — Streamlit Cloud 단일 워커 기준) ─────────────────
@dataclass
class Robot:
    rid: str
    x: float
    y: float
    vx: float
    vy: float


@dataclass
class Player:
    pid: str
    name: str
    score: int = 0


@dataclass
class GameState:
    robots: dict[str, Robot] = field(default_factory=dict)
    players: dict[str, Player] = field(default_factory=dict)
    winner: str | None = None
    lock: threading.Lock = field(default_factory=threading.Lock)

    def spawn_robot(self) -> None:
        margin = ROBOT_RADIUS + 8
        x = random.uniform(margin, ARENA_W - margin)
        y = random.uniform(margin, ARENA_H - margin)
        speed = random.uniform(2.2, 4.8)
        angle = random.uniform(0, math.tau)
        rid = uuid.uuid4().hex[:8]
        self.robots[rid] = Robot(
            rid=rid,
            x=x,
            y=y,
            vx=math.cos(angle) * speed,
            vy=math.sin(angle) * speed,
        )

    def ensure_robots(self) -> None:
        while len(self.robots) < MAX_ROBOTS and self.winner is None:
            self.spawn_robot()

    def tick(self) -> None:
        if self.winner:
            return
        margin = ROBOT_RADIUS
        for bot in self.robots.values():
            bot.x += bot.vx
            bot.y += bot.vy
            if bot.x < margin:
                bot.x = margin
                bot.vx = abs(bot.vx) * random.uniform(0.9, 1.1)
            elif bot.x > ARENA_W - margin:
                bot.x = ARENA_W - margin
                bot.vx = -abs(bot.vx) * random.uniform(0.9, 1.1)
            if bot.y < margin:
                bot.y = margin
                bot.vy = abs(bot.vy) * random.uniform(0.9, 1.1)
            elif bot.y > ARENA_H - margin:
                bot.y = ARENA_H - margin
                bot.vy = -abs(bot.vy) * random.uniform(0.9, 1.1)
            if random.random() < 0.02:
                bot.vx += random.uniform(-0.8, 0.8)
                bot.vy += random.uniform(-0.8, 0.8)
                spd = math.hypot(bot.vx, bot.vy) or 1
                scale = random.uniform(2.0, 5.0) / spd
                bot.vx *= scale
                bot.vy *= scale

    def leaderboard(self) -> list[dict[str, Any]]:
        return sorted(
            [{"name": p.name, "score": p.score} for p in self.players.values()],
            key=lambda r: (-r["score"], r["name"]),
        )

    def try_catch_by_id(self, player_id: str, robot_id: str) -> bool:
        if self.winner or player_id not in self.players:
            return False
        if robot_id not in self.robots:
            return False
        del self.robots[robot_id]
        player = self.players[player_id]
        player.score += 1
        if player.score >= TARGET_SCORE:
            self.winner = player.name
        self.ensure_robots()
        return True

    def join(self, name: str) -> tuple[str | None, str | None]:
        """(player_id, error_message)"""
        if any(p.name == name for p in self.players.values()):
            return None, "이미 사용 중인 ID입니다."
        pid = uuid.uuid4().hex[:10]
        self.players[pid] = Player(pid=pid, name=name)
        if not self.robots:
            self.ensure_robots()
        return pid, None


@st.cache_resource
def get_game() -> GameState:
    game = GameState()
    game.ensure_robots()
    return game


def sanitize_name(raw: str) -> str:
    name = (raw or "").strip()[:16]
    cleaned = "".join(
        c for c in name
        if c.isalnum() or c in "_-" or ("\uac00" <= c <= "\ud7a3")
    )
    return cleaned


def extract_selected_robot_ids(selection_event: Any) -> list[str]:
    if selection_event is None:
        return []
    sel = getattr(selection_event, "selection", None)
    if sel is None and isinstance(selection_event, dict):
        sel = selection_event.get("selection")
    if sel is None:
        return []
    points = getattr(sel, "points", None) or (
        sel.get("points", []) if isinstance(sel, dict) else []
    )
    ids: list[str] = []
    for pt in points:
        if isinstance(pt, dict):
            cd = pt.get("customdata")
        else:
            cd = getattr(pt, "customdata", None)
        if cd is None:
            continue
        rid = cd[0] if isinstance(cd, (list, tuple)) else cd
        ids.append(str(rid))
    return ids


def build_arena_figure(robots: list[Robot]) -> go.Figure:
    xs = [r.x for r in robots]
    ys = [r.y for r in robots]
    ids = [r.rid for r in robots]
    fig = go.Figure()
    if robots:
        fig.add_trace(
            go.Scatter(
                x=xs,
                y=ys,
                mode="markers+text",
                marker=dict(
                    size=52,
                    color="#35d0ff",
                    line=dict(width=2, color="#9efcff"),
                    symbol="circle",
                ),
                text=["🤖"] * len(robots),
                textfont=dict(size=20),
                textposition="middle center",
                customdata=ids,
                hoverinfo="skip",
                showlegend=False,
            )
        )
    fig.update_layout(
        height=520,
        xaxis=dict(
            range=[0, ARENA_W],
            showgrid=True,
            gridcolor="#1a2550",
            zeroline=False,
            visible=False,
            fixedrange=True,
        ),
        yaxis=dict(
            range=[0, ARENA_H],
            scaleanchor="x",
            scaleratio=1,
            showgrid=True,
            gridcolor="#1a2550",
            zeroline=False,
            visible=False,
            fixedrange=True,
        ),
        plot_bgcolor="#060a18",
        paper_bgcolor="#0f1430",
        margin=dict(l=8, r=8, t=8, b=8),
        dragmode=False,
    )
    return fig


def render_leaderboard(rows: list[dict[str, Any]], my_name: str | None) -> None:
    st.markdown("#### 🏆 리더보드")
    if not rows:
        st.caption("입장한 플레이어가 없습니다.")
        return
    cols = st.columns(min(len(rows), 6))
    for i, row in enumerate(rows):
        with cols[i % len(cols)]:
            label = row["name"] + (" (나)" if row["name"] == my_name else "")
            st.metric(label, f"{row['score']} / {TARGET_SCORE}")


# ── UI ───────────────────────────────────────────────────────────────────────
st.markdown("# 🤖 KIPI 로봇 잡기")
st.caption(f"로봇 {TARGET_SCORE}마리를 먼저 잡은 사람이 승리합니다 · 실시간 멀티플레이")

if "player_id" not in st.session_state:
    st.session_state.player_id = None
if "player_name" not in st.session_state:
    st.session_state.player_name = None
if "last_winner" not in st.session_state:
    st.session_state.last_winner = None
if "processed_selection" not in st.session_state:
    st.session_state.processed_selection = ()

game = get_game()

# 입장 전
if not st.session_state.player_id:
    with st.form("join_form", clear_on_submit=False):
        name_input = st.text_input("플레이어 ID", max_chars=16, placeholder="예: kipi01")
        submitted = st.form_submit_button("입장", type="primary")
    if submitted:
        name = sanitize_name(name_input)
        if not name:
            st.error("ID를 입력하세요.")
        else:
            with game.lock:
                pid, err = game.join(name)
            if err:
                st.error(err)
            else:
                st.session_state.player_id = pid
                st.session_state.player_name = name
                st.rerun()
    st.info("여러 브라우저/탭에서 서로 다른 ID로 접속해 함께 플레이할 수 있습니다.")
    st.stop()

# 입장 후 — 자동 갱신으로 로봇 이동
st_autorefresh(interval=TICK_MS, key="game_tick")

# 클릭(선택) 처리 — 동일 선택이 자동 갱신마다 반복 처리되지 않도록
caught_msg: str | None = None
sel_ids = extract_selected_robot_ids(st.session_state.get("arena"))
sel_sig = tuple(sel_ids)
with game.lock:
    if sel_ids and sel_sig != st.session_state.processed_selection:
        for rid in sel_ids:
            if game.try_catch_by_id(st.session_state.player_id, rid):
                st.session_state.processed_selection = sel_sig
                caught_msg = f"{st.session_state.player_name}님이 로봇을 잡았습니다!"
                break
    if not game.winner:
        game.tick()
        game.ensure_robots()
    board = game.leaderboard()
    robots = list(game.robots.values())
    winner = game.winner

render_leaderboard(board, st.session_state.player_name)

if caught_msg:
    st.toast(caught_msg, icon="🤖")

if winner and st.session_state.last_winner != winner:
    st.session_state.last_winner = winner
    st.balloons()
    st.success(f"🎉 승자: **{winner}** — 로봇 {TARGET_SCORE}마리 달성!")

if winner:
    st.warning(f"게임 종료 · 승자: **{winner}**")
else:
    st.caption(
        f"**{st.session_state.player_name}** 님 플레이 중 · "
        "아래 필드에서 **🤖 로봇을 클릭**하면 잡힙니다."
    )

st.plotly_chart(
    build_arena_figure(robots),
    use_container_width=True,
    on_select="rerun",
    selection_mode="points",
    key="arena",
)
