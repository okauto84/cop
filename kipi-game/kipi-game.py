# -*- coding: utf-8 -*-
"""
로봇 잡기 멀티플레이어 아케이드 게임

실행:
    python kipi-game.py

브라우저에서 http://localhost:8765 접속
"""

from __future__ import annotations

import argparse
import asyncio
import json
import math
import random
import uuid
from dataclasses import dataclass, field
from typing import Any

from aiohttp import WSMsgType, web

# ── 게임 설정 ────────────────────────────────────────────────────────────────
ARENA_W = 900
ARENA_H = 520
ROBOT_RADIUS = 28
HIT_RADIUS = 42
TARGET_SCORE = 10
MAX_ROBOTS = 10
TICK_MS = 50
PORT = 8765

# ── 게임 상태 ────────────────────────────────────────────────────────────────
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
    ws: web.WebSocketResponse | None = None


@dataclass
class GameState:
    robots: dict[str, Robot] = field(default_factory=dict)
    players: dict[str, Player] = field(default_factory=dict)
    winner: str | None = None
    lock: asyncio.Lock = field(default_factory=asyncio.Lock)

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
        for bot in list(self.robots.values()):
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

    def snapshot(self) -> dict[str, Any]:
        board = sorted(
            [{"name": p.name, "score": p.score} for p in self.players.values()],
            key=lambda r: (-r["score"], r["name"]),
        )
        return {
            "type": "state",
            "arena": {"w": ARENA_W, "h": ARENA_H},
            "robots": [
                {"id": r.rid, "x": round(r.x, 1), "y": round(r.y, 1)}
                for r in self.robots.values()
            ],
            "leaderboard": board,
            "target": TARGET_SCORE,
            "winner": self.winner,
        }

    def try_catch(self, player_id: str, x: float, y: float) -> str | None:
        if self.winner or player_id not in self.players:
            return None
        best_id: str | None = None
        best_dist = HIT_RADIUS + 1
        for rid, bot in self.robots.items():
            d = math.hypot(bot.x - x, bot.y - y)
            if d <= HIT_RADIUS and d < best_dist:
                best_dist = d
                best_id = rid
        if not best_id:
            return None
        del self.robots[best_id]
        player = self.players[player_id]
        player.score += 1
        if player.score >= TARGET_SCORE:
            self.winner = player.name
        self.ensure_robots()
        return best_id


STATE = GameState()
CLIENTS: set[web.WebSocketResponse] = set()


async def broadcast(payload: dict[str, Any]) -> None:
    dead: list[web.WebSocketResponse] = []
    msg = json.dumps(payload, ensure_ascii=False)
    for ws in CLIENTS:
        try:
            await ws.send_str(msg)
        except Exception:
            dead.append(ws)
    for ws in dead:
        CLIENTS.discard(ws)


async def broadcast_state() -> None:
    async with STATE.lock:
        snap = STATE.snapshot()
    await broadcast(snap)


async def game_loop() -> None:
    while True:
        async with STATE.lock:
            STATE.tick()
            if STATE.winner is None:
                STATE.ensure_robots()
        await broadcast_state()
        await asyncio.sleep(TICK_MS / 1000)


def sanitize_name(raw: str) -> str:
    name = (raw or "").strip()[:16]
    cleaned = "".join(
        c for c in name
        if c.isalnum() or c in "_-" or ("\uac00" <= c <= "\ud7a3")
    )
    return cleaned or f"player_{random.randint(100, 999)}"


async def ws_handler(request: web.Request) -> web.WebSocketResponse:
    ws = web.WebSocketResponse(heartbeat=20)
    await ws.prepare(request)
    CLIENTS.add(ws)
    player_id: str | None = None

    try:
        await ws.send_str(json.dumps({"type": "hello", "target": TARGET_SCORE}, ensure_ascii=False))
        async for msg in ws:
            if msg.type != WSMsgType.TEXT:
                continue
            try:
                data = json.loads(msg.data)
            except json.JSONDecodeError:
                continue
            mtype = data.get("type")
            if mtype == "join":
                name = sanitize_name(data.get("name", ""))
                async with STATE.lock:
                    for p in STATE.players.values():
                        if p.name == name and p.ws is not ws:
                            await ws.send_str(
                                json.dumps(
                                    {"type": "error", "message": "이미 사용 중인 ID입니다."},
                                    ensure_ascii=False,
                                )
                            )
                            break
                    else:
                        player_id = uuid.uuid4().hex[:10]
                        STATE.players[player_id] = Player(pid=player_id, name=name, ws=ws)
                        if not STATE.robots:
                            STATE.ensure_robots()
                        await ws.send_str(
                            json.dumps(
                                {"type": "joined", "playerId": player_id, "name": name},
                                ensure_ascii=False,
                            )
                        )
                        await broadcast_state()
                continue
            if mtype == "catch" and player_id:
                x = float(data.get("x", -9999))
                y = float(data.get("y", -9999))
                async with STATE.lock:
                    caught = STATE.try_catch(player_id, x, y)
                    if caught:
                        pname = STATE.players[player_id].name
                        payload = {
                            "type": "caught",
                            "player": pname,
                            "robotId": caught,
                            "leaderboard": STATE.snapshot()["leaderboard"],
                            "winner": STATE.winner,
                        }
                        if STATE.winner:
                            payload["type"] = "game_over"
                        await broadcast(payload)
                    await broadcast_state()
    finally:
        CLIENTS.discard(ws)
        if player_id:
            async with STATE.lock:
                STATE.players.pop(player_id, None)
            await broadcast_state()
    return ws


INDEX_HTML = """<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>kipi-game · 로봇 잡기</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: "Segoe UI", system-ui, sans-serif;
    background: radial-gradient(ellipse at top, #1a1f3c 0%, #0b0d17 55%, #05060a 100%);
    color: #e8ecff;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 16px;
  }
  h1 {
    font-size: 1.6rem;
    letter-spacing: 0.06em;
    margin-bottom: 8px;
    text-shadow: 0 0 18px #6cf0ff88;
  }
  .sub { color: #9aa8d8; font-size: 0.9rem; margin-bottom: 14px; }
  #joinPanel {
    background: #141a33cc;
    border: 1px solid #3d4f9a;
    border-radius: 12px;
    padding: 20px 24px;
    display: flex;
    gap: 10px;
    align-items: center;
    margin-bottom: 16px;
  }
  #joinPanel input {
    padding: 10px 14px;
    border-radius: 8px;
    border: 1px solid #4b5fbf;
    background: #0d1228;
    color: #fff;
    width: 200px;
    font-size: 1rem;
  }
  #joinPanel button, #resetBtn {
    padding: 10px 18px;
    border: none;
    border-radius: 8px;
    background: linear-gradient(135deg, #4f7cff, #35d0ff);
    color: #041018;
    font-weight: 700;
    cursor: pointer;
  }
  #joinPanel button:disabled { opacity: 0.5; cursor: not-allowed; }
  #board {
    width: min(900px, 96vw);
    background: #0f1430aa;
    border: 1px solid #334080;
    border-radius: 12px;
    padding: 12px 16px 10px;
    margin-bottom: 12px;
  }
  #board h2 { font-size: 0.95rem; color: #8ea4ff; margin-bottom: 8px; }
  #leaderboard {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    min-height: 36px;
  }
  .lb-item {
    background: #1b2550;
    border: 1px solid #3a4f9a;
    border-radius: 999px;
    padding: 6px 14px;
    font-size: 0.88rem;
  }
  .lb-item.me { border-color: #5dffb0; box-shadow: 0 0 10px #5dffb055; }
  .lb-item.lead { background: #2a1f4a; border-color: #c9a0ff; }
  #arenaWrap { position: relative; width: min(900px, 96vw); }
  canvas {
    display: block;
    width: 100%;
    height: auto;
    border-radius: 12px;
    border: 2px solid #2f3f8a;
    cursor: crosshair;
    background: #060a18;
    touch-action: none;
  }
  #status {
    margin-top: 10px;
    text-align: center;
    font-size: 0.92rem;
    color: #a8b8ee;
    min-height: 1.4em;
  }
  #winnerBanner {
    display: none;
    margin-top: 12px;
    padding: 14px 20px;
    border-radius: 10px;
    background: linear-gradient(90deg, #3d1f6e, #1f4a6e);
    border: 1px solid #c9a0ff;
    font-size: 1.1rem;
    font-weight: 700;
    text-align: center;
  }
  #winnerBanner.show { display: block; animation: pulse 1.2s ease infinite alternate; }
  @keyframes pulse { from { box-shadow: 0 0 8px #c9a0ff55; } to { box-shadow: 0 0 22px #c9a0ffaa; } }
  .hidden { display: none !important; }
</style>
</head>
<body>
  <h1>🤖 KIPI 로봇 잡기</h1>
  <p class="sub">로봇 10마리를 먼저 잡은 사람이 승리합니다 · 실시간 멀티플레이</p>

  <div id="joinPanel">
    <label for="playerName">플레이어 ID</label>
    <input id="playerName" maxlength="16" placeholder="예: kipi01" />
    <button id="joinBtn">입장</button>
  </div>

  <div id="board" class="hidden">
    <h2>🏆 리더보드</h2>
    <div id="leaderboard"></div>
  </div>

  <div id="arenaWrap" class="hidden">
    <canvas id="arena" width="900" height="520"></canvas>
  </div>
  <p id="status">ID를 입력하고 입장하세요.</p>
  <div id="winnerBanner"></div>

<script>
(() => {
  const WS_URL = `${location.protocol === "https:" ? "wss" : "ws"}://${location.host}/ws`;
  const canvas = document.getElementById("arena");
  const ctx = canvas.getContext("2d");
  const joinPanel = document.getElementById("joinPanel");
  const joinBtn = document.getElementById("joinBtn");
  const playerInput = document.getElementById("playerName");
  const board = document.getElementById("board");
  const lbEl = document.getElementById("leaderboard");
  const arenaWrap = document.getElementById("arenaWrap");
  const statusEl = document.getElementById("status");
  const winnerBanner = document.getElementById("winnerBanner");

  let ws = null;
  let myId = null;
  let myName = null;
  let robots = [];
  let targetScore = 10;
  let winner = null;
  let animId = null;

  function connect() {
    ws = new WebSocket(WS_URL);
    ws.onopen = () => { statusEl.textContent = "서버에 연결되었습니다. ID를 입력해 입장하세요."; };
    ws.onclose = () => {
      statusEl.textContent = "연결이 끊어졌습니다. 페이지를 새로고침하세요.";
      joinBtn.disabled = false;
    };
    ws.onmessage = (ev) => {
      const data = JSON.parse(ev.data);
      if (data.type === "error") {
        statusEl.textContent = data.message;
        joinBtn.disabled = false;
        return;
      }
      if (data.type === "joined") {
        myId = data.playerId;
        myName = data.name;
        joinPanel.classList.add("hidden");
        board.classList.remove("hidden");
        arenaWrap.classList.remove("hidden");
        statusEl.textContent = `${myName}님 입장 · 로봇을 클릭해 잡으세요!`;
        startRender();
      }
      if (data.type === "state" || data.type === "caught" || data.type === "game_over") {
        if (data.robots) robots = data.robots;
        if (data.leaderboard) renderLeaderboard(data.leaderboard);
        if (data.target) targetScore = data.target;
        if (data.winner) showWinner(data.winner);
        if (data.type === "caught" && data.player) {
          statusEl.textContent = `${data.player}님이 로봇을 잡았습니다!`;
        }
      }
      if (data.type === "hello" && data.target) targetScore = data.target;
    };
  }

  function renderLeaderboard(rows) {
    lbEl.innerHTML = "";
    rows.forEach((row, i) => {
      const el = document.createElement("div");
      el.className = "lb-item" + (row.name === myName ? " me" : "") + (i === 0 && row.score > 0 ? " lead" : "");
      el.textContent = `${row.name}: ${row.score} / ${targetScore}`;
      lbEl.appendChild(el);
    });
  }

  function showWinner(name) {
    winner = name;
    winnerBanner.classList.add("show");
    winnerBanner.textContent = `🎉 승자: ${name} (로봇 ${targetScore}마리 달성!)`;
    statusEl.textContent = "게임 종료";
  }

  function draw() {
    const w = canvas.width;
    const h = canvas.height;
    ctx.fillStyle = "#060a18";
    ctx.fillRect(0, 0, w, h);
    ctx.strokeStyle = "#1a2550";
    ctx.lineWidth = 1;
    for (let x = 0; x < w; x += 40) {
      ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, h); ctx.stroke();
    }
    for (let y = 0; y < h; y += 40) {
      ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(w, y); ctx.stroke();
    }
  }

  function drawRobots() {
    const t = performance.now() / 1000;
    robots.forEach((r) => {
      const bob = Math.sin(t * 6 + r.x * 0.02) * 3;
      const x = r.x;
      const y = r.y + bob;
      const grad = ctx.createRadialGradient(x - 8, y - 10, 4, x, y, 30);
      grad.addColorStop(0, "#9efcff");
      grad.addColorStop(1, "#2a5cff");
      ctx.fillStyle = grad;
      ctx.beginPath();
      ctx.arc(x, y, 26, 0, Math.PI * 2);
      ctx.fill();
      ctx.fillStyle = "#0a1030";
      ctx.font = "22px sans-serif";
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText("🤖", x, y - 1);
      ctx.strokeStyle = "#6cf0ff88";
      ctx.lineWidth = 2;
      ctx.stroke();
    });
  }

  function renderLoop() {
    draw();
    drawRobots();
    animId = requestAnimationFrame(renderLoop);
  }

  function startRender() {
    if (!animId) renderLoop();
  }

  function canvasPos(evt) {
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;
    const clientX = evt.clientX ?? (evt.touches && evt.touches[0].clientX);
    const clientY = evt.clientY ?? (evt.touches && evt.touches[0].clientY);
    return {
      x: (clientX - rect.left) * scaleX,
      y: (clientY - rect.top) * scaleY,
    };
  }

  function tryCatch(evt) {
    if (!ws || ws.readyState !== WebSocket.OPEN || !myId || winner) return;
    const { x, y } = canvasPos(evt);
    ws.send(JSON.stringify({ type: "catch", x, y }));
  }

  canvas.addEventListener("click", tryCatch);
  canvas.addEventListener("touchstart", (e) => { e.preventDefault(); tryCatch(e); }, { passive: false });

  joinBtn.addEventListener("click", () => {
    const name = playerInput.value.trim();
    if (!name) { statusEl.textContent = "ID를 입력하세요."; return; }
    if (!ws || ws.readyState !== WebSocket.OPEN) { statusEl.textContent = "서버 연결 대기 중..."; return; }
    joinBtn.disabled = true;
    ws.send(JSON.stringify({ type: "join", name }));
  });
  playerInput.addEventListener("keydown", (e) => { if (e.key === "Enter") joinBtn.click(); });

  connect();
})();
</script>
</body>
</html>
"""


async def index_handler(_request: web.Request) -> web.Response:
    return web.Response(text=INDEX_HTML, content_type="text/html")


def create_app() -> web.Application:
    app = web.Application()
    app.router.add_get("/", index_handler)
    app.router.add_get("/ws", ws_handler)
    return app


async def on_startup(app: web.Application) -> None:
    app["game_task"] = asyncio.create_task(game_loop())


async def on_cleanup(app: web.Application) -> None:
    task = app.get("game_task")
    if task:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass


def main() -> None:
    parser = argparse.ArgumentParser(description="kipi-game 로봇 잡기 멀티플레이어")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=PORT)
    args = parser.parse_args()

    app = create_app()
    app.on_startup.append(on_startup)
    app.on_cleanup.append(on_cleanup)
    print(f"kipi-game 실행 중 → http://localhost:{args.port}")
    print("여러 브라우저/탭에서 서로 다른 ID로 접속해 플레이하세요.")
    web.run_app(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
