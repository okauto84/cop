# -*- coding: utf-8 -*-
"""AI 특허 검색 로딩 화면 목업."""

import base64
from pathlib import Path

import streamlit as st
from index_spec import SPEC_MODAL_CSS, get_spec_modal_html


st.set_page_config(
    page_title="AI 특허 검색 시스템",
    page_icon="⌕",
    layout="wide",
    initial_sidebar_state="collapsed",
)

drawing_path = Path(__file__).parent / "data" / "drawing.JPG"
DATA_DIR = Path(__file__).parent / "data"
drawing_data_uri = (
    "data:image/jpeg;base64,"
    + base64.b64encode(drawing_path.read_bytes()).decode("ascii")
)

DRAWING_BATCH_ITEMS = [
    {"no": 1, "state": "공개", "app_no": "1020180133661", "date": "20181102", "title": "메모리 장치 및 이를 포함하는 메모리 시스템"},
    {"no": 2, "state": "공개", "app_no": "1020140178426", "date": "20141211", "title": "반도체 메모리 장치 및 그의 동작 방법"},
    {"no": 3, "state": "공개", "app_no": "1020200126702", "date": "20200929", "title": "메모리 장치 및 이의 동작 방법"},
    {"no": 4, "state": "등록", "app_no": "1020200098794", "date": "20200806", "title": "메모리 장치"},
    {"no": 5, "state": "공개", "app_no": "1020200098765", "date": "20200806", "title": "메모리 장치 및 이의 동작 방법"},
    {"no": 6, "state": "공개", "app_no": "1020220164302", "date": "20221130", "title": "페이지 버퍼, 페이지 버퍼를 포함하는 메모리 장치 및 메모리 장치를 포함하는 메모리 시스템"},
    {"no": 7, "state": "공개", "app_no": "1020150172401", "date": "20151204", "title": "메모리 장치 및 그의 동작방법"},
    {"no": 8, "state": "공개", "app_no": "1020190160174", "date": "20191204", "title": "메모리 장치 및 그 동작 방법"},
]


def _image_data_uri(path: Path) -> str:
    suffix = path.suffix.lower()
    mime = "image/png" if suffix == ".png" else "image/jpeg"
    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode("ascii")


def _load_drawing_batch_uris() -> list[str]:
    return [_image_data_uri(path) for path in sorted(DATA_DIR.glob("d_*.png"))]


def build_bulk_drawings_modal_html() -> str:
    image_uris = _load_drawing_batch_uris()
    cards: list[str] = []
    for index, item in enumerate(DRAWING_BATCH_ITEMS):
        if index < len(image_uris):
            drawing_html = f'<img src="{image_uris[index]}" alt="대표도면 {item["no"]}">'
        else:
            drawing_html = '<span class="bulk-drawing-empty">이미지 없음</span>'
        cards.append(
            f'<article class="bulk-drawing-card">'
            f'<div class="bulk-meta"><span class="bulk-number">{item["no"]}</span>'
            f'<span class="bulk-state">{item["state"]}</span>'
            f'<span>출원번호 : {item["app_no"]} ({item["date"]})</span></div>'
            f'<div class="bulk-invention-title">{item["title"]}</div>'
            f'<div class="bulk-drawing-frame">{drawing_html}</div>'
            f"</article>"
        )
    return (
        '<section class="bulk-drawings-modal">'
        '<header class="bulk-modal-header">'
        '<div class="bulk-title-icon bulk-title-icon-drawing">▣</div>'
        "<div><div class=\"bulk-title\">대표 도면 일괄조회</div>"
        '<div class="bulk-subtitle">필터링된 데이터 200건 중 8개씩 보기</div></div>'
        '<div class="bulk-header-spacer"></div>'
        '<div class="bulk-sort">배열: <strong>4열⌄</strong><span>|</span><strong>2행⌄</strong></div>'
        '<div class="bulk-nav"><span class="disabled">이전</span><strong>1 / 25</strong><span>다음</span></div>'
        '<label for="bulk-drawings-toggle" class="bulk-close">×</label>'
        "</header>"
        f'<div class="bulk-card-grid">{"".join(cards)}</div>'
        "</section>"
    )


drawing_batch_modal_html = build_bulk_drawings_modal_html()

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;600;700&display=swap');

:root {
  --line: #e3e8ef;
  --muted: #778394;
  --blue: #2878ef;
  --purple: #7544ee;
  --fs-body: 12px;
  --fs-caption: 12px;
  --fs-label: 13px;
  --fs-subtitle: 14px;
  --fs-title: 15px;
  --fs-heading: 16px;
  --fs-display: 18px;
}
* { box-sizing: border-box; }
html, body, [class*="css"] {
  font-family: "Noto Sans KR", "Malgun Gothic", sans-serif;
}
html, body, .stApp {
  margin: 0;
  background: #f8fafc;
  color: #1d2733;
  overflow: hidden;
}
[data-testid="stHeader"], [data-testid="stToolbar"],
[data-testid="stDecoration"], #MainMenu, footer { display: none !important; }
.block-container {
  max-width: none !important;
  width: 100vw !important;
  height: 100vh !important;
  padding: 0 !important;
  margin: 0 !important;
}

.patent-app {
  position: fixed;
  inset: 12px 18px;
  display: grid;
  grid-template-columns: 300px 0 minmax(0, 1fr);
  grid-template-rows: 34px minmax(0, 1fr);
  background: #f8fafc;
  font-size: var(--fs-body);
  letter-spacing: -.15px;
  border: 1px solid #e0e6ed;
  border-radius: 8px;
  box-shadow: 0 3px 14px rgba(35, 48, 64, .08);
  overflow: hidden;
  transition: grid-template-columns .38s ease;
}
.patent-app:has(#ai-panel-toggle:checked) {
  grid-template-columns: 270px 261.3px minmax(0, 1fr);
}
#ai-panel-toggle {
  position: absolute;
  width: 1px;
  height: 1px;
  opacity: 0;
  pointer-events: none;
}
.topbar {
  grid-column: 1 / -1;
  display: grid;
  grid-template-columns: 270px 261.3px 1fr;
  height: 34px;
  background: #fff;
  border-bottom: 1px solid var(--line);
}
.top-left {
  padding: 7px 5px;
  color: #0e65cf;
  font-size: var(--fs-subtitle);
  font-weight: 700;
  border-right: 1px solid var(--line);
  white-space: nowrap;
}
.top-left button {
  float: right;
  height: 20px;
  margin-top: -1px;
  padding: 0 8px;
  color: #4d5966;
  font-size: var(--fs-body);
  background: #fff;
  border: 1px solid #d6dde6;
  border-radius: 3px;
  white-space: nowrap;
}
.tabs { display: flex; align-items: end; padding-left: 15px; }
.tab {
  height: 30px;
  min-width: 76px;
  padding: 9px 14px 0;
  color: #677383;
  font-size: var(--fs-label);
  background: #f8fafc;
  border: 1px solid transparent;
}
.tab.active {
  color: #273343;
  font-weight: 600;
  background: #fff;
  border-color: var(--line);
  border-bottom-color: #fff;
}
.main-actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 6px;
  padding: 0 8px;
}
.action-pill {
  height: 22px;
  padding: 4px 10px;
  color: #5d6978;
  background: #fff;
  border: 1px solid #dfe5ec;
  border-radius: 5px;
}
.icon-box {
  width: 23px;
  height: 22px;
  display: grid;
  place-items: center;
  color: #8793a1;
  background: #fff;
  border: 1px solid #dfe5ec;
  border-radius: 5px;
  font-size: var(--fs-label);
}

.filter-panel {
  grid-column: 1;
  grid-row: 2;
  min-height: 0;
  display: flex;
  flex-direction: column;
  font-size: 12px;
  background: #fff;
  border-right: 1px solid var(--line);
}
.filter-panel * { font-size: 12px; }
.filter-scroll {
  min-height: 0;
  flex: 1;
  overflow: hidden;
  padding: 7px 4px 4px;
}
.section { margin-bottom: 8px; }
.section-title {
  margin: 0 -4px 5px;
  padding: 4px 4px 5px;
  color: #1269cc;
  font-size: var(--fs-subtitle);
  font-weight: 700;
  border-bottom: 1px solid #edf0f4;
}
.field, .date-row {
  width: 100%;
  height: 23px;
  display: flex;
  align-items: center;
  padding: 0 6px;
  background: #fff;
  border: 1px solid #dfe5ec;
  border-radius: 3px;
  color: #3d4855;
}
.select-field::after { content: "⌄"; margin-left: auto; color: #66717f; }
.date-row { gap: 4px; border: 0; padding: 0; margin-top: 4px; }
.date {
  height: 23px;
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 5px;
  white-space: nowrap;
  border: 1px solid #dfe5ec;
  border-radius: 3px;
  font-size: var(--fs-label);
}
.date-sep { color: #8993a0; }
.class-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  row-gap: 4px;
  padding: 0 8px;
}
.check { display: flex; align-items: center; gap: 4px; }
input[type="checkbox"] {
  width: 9px; height: 9px; margin: 0;
  accent-color: #2778ed;
}
.components-head {
  display: grid;
  grid-template-columns: 19px 1fr 45px 45px;
  align-items: center;
  height: 25px;
  color: #5f6b78;
  border-bottom: 1px solid #e8edf2;
}
.mini-button {
  margin-left: 2px;
  padding: 3px 4px;
  color: white;
  text-align: center;
  font-size: var(--fs-label);
  background: #7a48eb;
  border-radius: 3px;
  cursor: pointer;
  user-select: none;
  transition: filter .15s ease, transform .15s ease;
}
.mini-button:hover { filter: brightness(1.08); }
.mini-button:active { transform: translateY(1px); }
.mini-button.blue { background: #2878ef; }
.component {
  display: grid;
  grid-template-columns: 18px 1fr;
  gap: 2px;
  padding: 6px 2px 7px;
  border-bottom: 1px solid #edf0f4;
}
.component-title {
  display: flex;
  justify-content: space-between;
  margin-bottom: 5px;
  color: #2775da;
  font-weight: 600;
}
.component-title span:last-child { color: #7a8490; font-size: var(--fs-caption); font-weight: 400; }
.component-text { color: #44505d; line-height: 1.5; }
.filter-footer { padding: 5px 4px 4px; border-top: 1px solid var(--line); }
.footer-buttons { display: grid; grid-template-columns: 1fr 1.55fr; gap: 4px; }
.footer-button {
  height: 25px;
  display: grid;
  place-items: center;
  color: #4f5b68;
  background: #fff;
  border: 1px solid #dbe2e9;
  border-radius: 5px;
}
.footer-button.primary { color: #fff; background: #3478e9; border-color: #3478e9; font-weight: 600; }
.copyright { padding-top: 5px; color: #9aa4af; font-size: var(--fs-caption); text-align: center; }

.claims-panel {
  grid-column: 2;
  grid-row: 2;
  min-height: 0;
  display: flex;
  flex-direction: column;
  margin: 7px 4px 7px 7px;
  background: #fff;
  border: 1px solid #dfe5ec;
  border-radius: 7px;
  box-shadow: 0 2px 7px rgba(42, 55, 70, .08);
  overflow: hidden;
  opacity: 0;
  pointer-events: none;
  transform: translateX(-105%);
  transform-origin: left center;
  transition: transform .38s ease, opacity .25s ease;
}
#ai-panel-toggle:checked ~ .claims-panel {
  opacity: 1;
  pointer-events: auto;
  transform: translateX(0);
}
.claims-title {
  height: 31px;
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 0 7px;
  font-size: var(--fs-subtitle);
  font-weight: 700;
  border-bottom: 1px solid #edf0f4;
}
.doc-icon { color: #3479ee; font-size: var(--fs-label); }
.title-spacer { flex: 1; }
.view-chip { padding: 2px 5px; border-radius: 3px; font-size: var(--fs-caption); font-weight: 500; }
.view-chip.on { color: #7442df; background: #f2eefe; }
.view-chip.off { color: #738091; background: #f4f6f8; }
.close { color: #8c96a2; font-size: var(--fs-label); }
.claims-tabs {
  height: 31px;
  display: flex;
  align-items: end;
  padding: 0 7px;
  border-bottom: 1px solid #e9edf2;
}
.claims-tab {
  height: 27px;
  padding: 8px 12px 0;
  color: #6f7a88;
}
.claims-tab.active { color: #3479e6; border-bottom: 2px solid #3479e6; font-weight: 600; }
.select-all {
  margin-left: auto;
  margin-bottom: 6px;
  padding: 3px 7px;
  color: #65717e;
  background: #f7f8fa;
  border: 1px solid #e1e6eb;
  border-radius: 3px;
  font-size: var(--fs-label);
}
.claim-list { min-height: 0; flex: 1; overflow: hidden; padding: 4px 5px; }
.claim-card {
  margin-bottom: 5px;
  padding: 6px;
  color: #3d4855;
  line-height: 1.45;
  background: #f8fbff;
  border: 1px solid #d9e6f7;
  border-radius: 5px;
}
.claim-card-head { display: flex; align-items: center; gap: 4px; margin-bottom: 4px; color: #2472d4; font-weight: 700; }
.claim-card-head .independent { margin-left: auto; color: #7d8792; font-size: var(--fs-caption); font-weight: 400; }
.extract-button {
  height: 27px;
  margin: 0 5px 6px;
  display: grid;
  place-items: center;
  color: #fff;
  background: linear-gradient(90deg, #9348e9, #693ce8);
  border-radius: 4px;
  font-weight: 600;
}

.workspace {
  position: relative;
  grid-column: 3;
  grid-row: 2;
  min-width: 0;
  overflow: hidden;
  background: #f8fafc;
}
.loading-view {
  position: absolute;
  inset: 0;
  display: none;
  width: 100%;
  height: 100%;
}
.progress-wrap {
  height: 62px;
  padding: 15px 8% 0;
  background: #fff;
  border-bottom: 1px solid #edf0f4;
}
.progress {
  position: relative;
  display: grid;
  grid-template-columns: repeat(4, 1fr);
}
.progress::before {
  content: "";
  position: absolute;
  top: 8px;
  left: 12.5%;
  right: 12.5%;
  height: 1px;
  background: #dae2eb;
}
.step { position: relative; text-align: center; color: #7e8995; font-size: var(--fs-caption); }
.step-dot {
  position: relative;
  z-index: 1;
  width: 17px;
  height: 17px;
  display: grid;
  place-items: center;
  margin: 0 auto 3px;
  color: #8a96a2;
  background: #f8fafc;
  border: 1px solid #dce4ec;
  border-radius: 50%;
  font-size: var(--fs-label);
}
.step.done .step-dot { color: #14ae82; background: #d7faee; border-color: #a9ecd8; }
.step.active .step-dot {
  color: #7545ed;
  background: #fff;
  border-color: #b598f7;
  box-shadow: 0 0 0 3px #f0eaff;
}
.step-name { color: #52606d; font-weight: 600; }
.step.active .step-name { color: #7443df; }
.step-status { margin-top: 1px; color: #9aa3ad; font-size: var(--fs-caption); }
.loading-area { padding: 18px 11% 0; }
.loading-title { margin-bottom: 2px; font-size: var(--fs-display); font-weight: 700; letter-spacing: -.45px; }
.loading-subtitle { margin-bottom: 12px; color: #929ca7; font-size: var(--fs-label); }
.loading-card {
  width: 100%;
  max-width: 500px;
  min-height: 103px;
  padding: 10px 12px;
  background: #fff;
  border: 1px solid #dce3ea;
  border-radius: 7px;
  box-shadow: 0 1px 2px rgba(23, 36, 50, .03);
}
.loading-item {
  height: 19px;
  display: flex;
  align-items: center;
  gap: 7px;
  color: #55616e;
  font-size: var(--fs-label);
  font-weight: 500;
}
.spinner {
  width: 10px;
  height: 10px;
  border: 2px solid #ede7ff;
  border-top-color: #8758ee;
  border-radius: 50%;
  animation: spin 1.1s linear infinite;
}
.loading-item:nth-child(2) .spinner { animation-delay: -.2s; }
.loading-item:nth-child(3) .spinner { animation-delay: -.4s; }
.loading-item:nth-child(4) .spinner { animation-delay: -.6s; }
.loading-item:nth-child(5) .spinner { animation-delay: -.8s; }
@keyframes spin { to { transform: rotate(360deg); } }

.search-trigger { cursor: pointer; user-select: none; }
#search-start-toggle,
#search-result-toggle {
  position: absolute;
  width: 1px;
  height: 1px;
  opacity: 0;
  pointer-events: none;
}
.search-second-trigger { display: none; }
#search-start-toggle:checked ~ .filter-panel .search-first-trigger { display: none; }
#search-start-toggle:checked ~ .filter-panel .search-second-trigger { display: grid; }
#search-start-toggle:checked ~ .workspace .loading-view { display: block; }
.result-view {
  position: absolute;
  inset: 0;
  display: none;
  width: 100%;
  height: 100%;
  min-width: 0;
}
#search-result-toggle:checked ~ .workspace .loading-view {
  display: none;
}
#search-result-toggle:checked ~ .workspace .result-view {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 409.5px;
}

.result-center {
  min-width: 0;
  display: flex;
  flex-direction: column;
  background: #fff;
  border-right: 1px solid var(--line);
}
.result-toolbar {
  height: 34px;
  flex: 0 0 34px;
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 5px 8px;
  border-bottom: 1px solid #e5eaf0;
}
.result-tool {
  height: 22px;
  display: flex;
  align-items: center;
  padding: 0 9px;
  color: #4d5966;
  white-space: nowrap;
  background: #fff;
  border: 1px solid #d9e1e9;
  border-radius: 3px;
  font-size: var(--fs-body);
  font-weight: 600;
}
.result-tool.active { color: #2673df; background: #eef5ff; border-color: #bcd5fa; }
.result-search {
  height: 22px;
  min-width: 100px;
  flex: 1;
  margin-left: auto;
  padding: 5px 8px;
  color: #a0a9b3;
  white-space: nowrap;
  overflow: hidden;
  border: 1px solid #dce3ea;
  border-radius: 3px;
  font-size: var(--fs-body);
}
.result-search-btn {
  height: 22px;
  padding: 4px 7px;
  color: #2d73dc;
  border: 1px solid #bed4f5;
  border-radius: 3px;
  font-size: var(--fs-body);
}
.patent-table-wrap { min-height: 0; flex: 1; overflow: hidden; }
.patent-table {
  width: 100%;
  height: 100%;
  table-layout: fixed;
  border-collapse: collapse;
  color: #4e5b68;
  font-size: 12px;
}
.patent-table col:nth-child(1) { width: 4%; }
.patent-table col:nth-child(2) { width: 6%; }
.patent-table col:nth-child(3) { width: 18%; }
.patent-table col:nth-child(4) { width: 39%; }
.patent-table col:nth-child(5) { width: 12%; }
.patent-table col:nth-child(6) { width: 10%; }
.patent-table col:nth-child(7) { width: 11%; }
.patent-table th {
  height: 24px;
  padding: 4px;
  color: #4b5865;
  background: #f8fafc;
  border-bottom: 1px solid #dfe5eb;
  text-align: center;
  font-weight: 600;
}
.patent-table td {
  height: 34px;
  padding: 3px 4px;
  border-bottom: 1px solid #e7ebf0;
  text-align: center;
  vertical-align: middle;
  overflow: hidden;
}
.patent-table tr:first-child td { background: #f1f6fd; }
.patent-table tr:first-child td:first-child { border-left: 2px solid #4e94ee; }
.patent-table td.cpc { line-height: 1.25; }
.patent-table td.title {
  color: #1d6ed7;
  text-align: left;
  font-weight: 600;
  white-space: normal;
  line-height: 1.3;
}
.state-chip {
  display: inline-block;
  padding: 2px 5px;
  color: #5c6671;
  background: #f1f3f5;
  border-radius: 3px;
}
.result-pager {
  height: 29px;
  flex: 0 0 29px;
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 3px 8px;
  color: #697582;
  border-top: 1px solid #e4e9ee;
  font-size: var(--fs-body);
}
.page-size { padding: 3px 18px 3px 7px; border: 1px solid #dce2e8; border-radius: 3px; }
.pager-spacer { flex: 1; }
.page {
  min-width: 19px;
  height: 19px;
  display: grid;
  place-items: center;
  border: 1px solid #dce2e8;
  border-radius: 3px;
  background: #fff;
}
.page.active { color: #2674df; background: #edf5ff; border-color: #93bbf1; }

.result-side {
  min-width: 0;
  display: flex;
  flex-direction: column;
  padding: 0 7px 7px;
  background: #f8fafc;
  overflow: hidden;
}
.side-card {
  margin-top: 0;
  background: #fff;
  border: 1px solid #dfe5eb;
  border-radius: 7px;
  overflow: hidden;
}
.side-heading {
  height: 29px;
  padding: 8px 9px 0;
  color: #3f4b57;
  font-size: var(--fs-subtitle);
  font-weight: 700;
  border-bottom: 1px solid #edf0f4;
}
.drawing-box {
  height: auto;
  margin: 7px;
  display: grid;
  place-items: center;
  color: #9ba5af;
  background: #fbfcfd;
  border: 1px solid #eef1f4;
  border-radius: 4px;
  font-size: var(--fs-body);
}
.drawing-box img {
  display: block;
  width: 100%;
  height: auto;
  object-fit: contain;
}
.ai-card {
  min-height: 0;
  flex: 1;
  margin-top: 7px;
  border-color: #eadcff;
}
.ai-card .side-heading { color: #7845df; background: #fbf7ff; border-color: #f0e7fb; }
.summary-box {
  margin: 8px 7px 0;
  padding: 8px;
  border: 1px solid;
  border-radius: 5px;
  line-height: 1.45;
  font-size: var(--fs-body);
}
.summary-box strong { display: block; margin-bottom: 4px; font-size: var(--fs-label); }
.summary-box.red { color: #c6463d; background: #fff9f8; border-color: #f2d8d5; }
.summary-box.red span { color: #3f4954; }
.summary-box.green { color: #20a57c; background: #f7fffc; border-color: #caeee1; }
.summary-box.blue { color: #3978c8; background: #f7faff; border-color: #d6e2f4; }

.bulk-claims-trigger, .bulk-drawings-trigger { cursor: pointer; user-select: none; }
#bulk-claims-toggle, #bulk-drawings-toggle {
  position: absolute;
  width: 1px;
  height: 1px;
  opacity: 0;
  pointer-events: none;
}
.bulk-claims-modal, .bulk-drawings-modal {
  position: absolute;
  inset: 0;
  z-index: 100;
  display: none;
  flex-direction: column;
  background: #f7f8fa;
}
#bulk-claims-toggle:checked ~ .bulk-claims-modal,
#bulk-drawings-toggle:checked ~ .bulk-drawings-modal {
  display: flex;
  animation: modal-fade-in .18s ease-out;
}
@keyframes modal-fade-in {
  from { opacity: 0; transform: scale(.995); }
  to { opacity: 1; transform: scale(1); }
}
.bulk-modal-header {
  height: 62px;
  flex: 0 0 62px;
  display: flex;
  align-items: center;
  padding: 0 15px;
  background: #fafbfc;
  border-bottom: 1px solid #e6e9ed;
}
.bulk-title-icon {
  width: 28px;
  height: 28px;
  display: grid;
  place-items: center;
  margin-right: 9px;
  color: #3279df;
  background: #eaf3ff;
  border-radius: 5px;
  font-size: var(--fs-title);
}
.bulk-title { color: #27323d; font-size: var(--fs-display); font-weight: 700; }
.bulk-subtitle { margin-top: 2px; color: #8a949e; font-size: var(--fs-label); font-weight: 400; }
.bulk-header-spacer { flex: 1; }
.bulk-sort {
  height: 28px;
  display: flex;
  align-items: center;
  padding: 0 10px;
  color: #4c5966;
  background: #fff;
  border: 1px solid #dfe4ea;
  border-radius: 5px;
  font-size: 12px;
}
.bulk-sort strong { margin: 0 8px; color: #2c6fc9; }
.bulk-nav {
  height: 28px;
  display: flex;
  align-items: center;
  gap: 15px;
  margin-left: 16px;
  padding: 0 12px;
  color: #65717d;
  background: #fff;
  border: 1px solid #e0e5ea;
  border-radius: 5px;
  font-size: 12px;
}
.bulk-nav .disabled { color: #bdc4cb; }
.bulk-nav strong { color: #27323d; }
.bulk-close {
  width: 29px;
  height: 29px;
  display: grid;
  place-items: center;
  margin-left: 17px;
  color: #7d8791;
  background: #fff;
  border: 1px solid #dfe4e9;
  border-radius: 5px;
  cursor: pointer;
  font-size: 18px;
}
.bulk-card-grid {
  min-height: 0;
  flex: 1;
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  grid-template-rows: repeat(2, minmax(0, 1fr));
  gap: 12px;
  padding: 16px 15px 14px;
}
.bulk-claim-card {
  min-width: 0;
  padding: 12px;
  background: #fff;
  border: 1px solid #edf0f3;
  border-radius: 8px;
  box-shadow: 0 2px 5px rgba(35, 47, 60, .07);
  overflow: hidden;
}
.bulk-meta {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #65717c;
  white-space: nowrap;
  font-size: var(--fs-label);
}
.bulk-number {
  min-width: 17px;
  height: 17px;
  display: grid;
  place-items: center;
  color: #65717c;
  background: #f1f3f5;
  border-radius: 2px;
  font-weight: 700;
}
.bulk-state { color: #3e4954; font-weight: 700; }
.bulk-invention-title {
  margin: 7px 0 9px;
  color: #266fcf;
  font-size: var(--fs-subtitle);
  font-weight: 700;
  line-height: 1.35;
}
.bulk-claim-body {
  padding-top: 8px;
  color: #727d87;
  border-top: 1px solid #eef1f4;
  font-size: 12px;
  line-height: 1.55;
}
.bulk-claim-label {
  display: block;
  margin-bottom: 4px;
  color: #7a67d5;
  font-weight: 700;
}

.bulk-title-icon-drawing { color: #3279df; background: #eaf3ff; }
.bulk-drawing-card {
  min-width: 0;
  min-height: 0;
  display: flex;
  flex-direction: column;
  padding: 12px;
  background: #fff;
  border: 1px solid #edf0f3;
  border-radius: 8px;
  box-shadow: 0 2px 5px rgba(35, 47, 60, .07);
  overflow: hidden;
}
.bulk-drawing-card .bulk-invention-title {
  margin-bottom: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.bulk-drawing-frame {
  flex: 1;
  min-height: 0;
  display: grid;
  place-items: center;
  margin-top: 8px;
  padding: 6px;
  background: #f8f9fb;
  border: 1px solid #eef1f4;
  border-radius: 4px;
  overflow: hidden;
}
.bulk-drawing-frame img {
  display: block;
  width: 100%;
  height: 100%;
  max-height: 100%;
  object-fit: contain;
}
.bulk-drawing-empty {
  color: #9aa3ad;
  font-size: var(--fs-label);
}

@media (min-width: 1300px) {
  .patent-app { grid-template-columns: 336px 0 minmax(0, 1fr); font-size: var(--fs-body); }
  .patent-app:has(#ai-panel-toggle:checked) { grid-template-columns: 336px 331.5px minmax(0, 1fr); }
  .topbar { grid-template-columns: 336px 331.5px 1fr; }
  .section-title { font-size: var(--fs-subtitle); }
  .loading-card { max-width: 635px; }
}
__SPEC_MODAL_CSS__
</style>

<div class="patent-app">
  <input type="checkbox" id="ai-panel-toggle">
  <input type="checkbox" id="search-start-toggle">
  <input type="checkbox" id="search-result-toggle">
  <input type="checkbox" id="bulk-claims-toggle">
  <input type="checkbox" id="bulk-drawings-toggle">
  <input type="checkbox" id="spec-modal-toggle">
  <header class="topbar">
    <div class="top-left">▏특허 검색 <button>직접 입력</button></div>
    <div class="tabs"><div class="tab">⌂&nbsp; INFO</div><div class="tab active">1020220167018</div></div>
    <div class="main-actions">
      <div class="action-pill">▱&nbsp; 마이페이지</div>
      <div class="icon-box">✎</div><div class="icon-box">▣</div>
      <div class="icon-box">▥</div><div class="icon-box">⚙</div>
    </div>
  </header>
  <aside class="filter-panel">
    <div class="filter-scroll">
      <div class="field">1020220167018</div>
      <div class="section">
        <div class="section-title">▏검색 일자</div>
        <div class="field select-field">출원일자</div>
        <div class="date-row"><div class="date">연도-월-일 <span>□</span></div><span class="date-sep">-</span><div class="date">2022-12-02 <span>□</span></div></div>
      </div>
      <div class="section">
        <div class="section-title">▏CPC 분류</div>
        <div class="class-grid">
          <label class="check"><input type="checkbox">A</label><label class="check"><input type="checkbox">B</label>
          <label class="check"><input type="checkbox">C</label><label class="check"><input type="checkbox">D</label>
          <label class="check"><input type="checkbox">E</label><label class="check"><input type="checkbox">F</label>
          <label class="check"><input type="checkbox" checked>G</label><label class="check"><input type="checkbox">H</label>
        </div>
      </div>
      <div class="section-title">▏구성요소</div>
      <div class="components-head">
        <input type="checkbox"><span>구성요소 내용</span><label for="ai-panel-toggle" class="mini-button">AI 선택</label><span class="mini-button blue">+ 추가</span>
      </div>
      <div class="component"><input type="checkbox" checked><div><div class="component-title"><span>구성요소 1</span><span>☆ 핵심</span></div><div class="component-text">워드라인 및 비트라인들에 연결된 메모리 셀들</div></div></div>
      <div class="component"><input type="checkbox" checked><div><div class="component-title"><span>구성요소 2</span><span>☆ 핵심</span></div><div class="component-text">상기 워드라인 및 상기 비트라인들에 인가되는 프로그램 관련 전압들을 제어하는 메인 프로세서</div></div></div>
      <div class="component"><input type="checkbox" checked><div><div class="component-title"><span>구성요소 3</span><span>☆ 핵심</span></div><div class="component-text">상기 메모리 셀들의 물리 전압을 기초로 센싱된 데이터를 저장하는 페이지 버퍼</div></div></div>
      <div class="component"><input type="checkbox" checked><div><div class="component-title"><span>구성요소 4</span><span>☆ 핵심</span></div><div class="component-text">상기 센싱된 데이터에 대응되는 센싱 전류와 상기 센싱된 전류를 비교하는 비교 회로</div></div></div>
      <div class="component"><input type="checkbox" checked><div><div class="component-title"><span>구성요소 5</span><span>☆ 핵심</span></div><div class="component-text">상기 메인 프로세서가 상기 프로그램 관련 전압을 제어하는 구성</div></div></div>
    </div>
    <div class="filter-footer">
      <div class="footer-buttons"><div class="footer-button">↻ 초기화</div><label for="search-start-toggle" class="footer-button primary search-trigger search-first-trigger">⌕ 검색</label><label for="search-result-toggle" class="footer-button primary search-trigger search-second-trigger">⌕ 검색</label></div>
      <div class="copyright">Copyright © 2026 KIPI. All rights reserved. Version 2.0</div>
    </div>
  </aside>
  <aside class="claims-panel">
    <div class="claims-title"><span class="doc-icon">▧</span> AI 더보기<span class="title-spacer"></span><span class="close">×</span></div>
    <div class="claims-tabs"><div class="claims-tab">요약</div><div class="claims-tab active">청구항</div><div class="select-all">전체 선택</div></div>
    <div class="claim-list">
      <div class="claim-card"><div class="claim-card-head"><input type="checkbox">청구항 1</div>워드라인 및 비트라인들에 연결된 메모리 셀들; 상기 워드라인 및 상기 비트라인들에 인가되는 프로그램 관련 전압들을 제어하는 메인 프로세서; 상기 메모리 셀들의 물리 전압을 기초로 센싱된 데이터를 저장하는 페이지 버퍼; 상기 센싱된 데이터에 대응하는 센싱 전류와 비교되는 기준 전류를 생성하는 센싱 회로; 및 상기 센싱 전류와 상기 기준 전류를 비교한 결과에 따라 상기 센싱 회로를 제어하는 메모리 장치.</div>
      <div class="claim-card"><div class="claim-card-head"><input type="checkbox">청구항 2</div>제1 항에 있어서, 상기 서브 프로세서는, 상기 메인 프로세서가 제공하는 제어 신호에 응답하여 복수의 프로그램 상태들 중 상기 제어 신호에 대응되는 프로그램 상태에 대한 상기 패스 레벨 체크 동작을 병렬적으로 수행하도록 상기 페이지 버퍼 및 상기 센싱 회로를 제어하는 메모리 장치.</div>
      <div class="claim-card"><div class="claim-card-head"><input type="checkbox">청구항 3</div>제1 항에 있어서, 상기 메인 프로세서는, 프로그램 펄스 동작에서 상기 워드라인에 전압 크기를 프로그램 전압의 크기로 제어하고, 패스 체크 동작에서 상기 워드라인 및 상기 비트라인들의 전압 크기를 정지 전압의 크기로 제어하는 메모리 장치.</div>
      <div class="claim-card"><div class="claim-card-head"><input type="checkbox">청구항 4</div>제1 항에 있어서, 상기 메인 프로세서는 상기 프로그램 관련 동작의 진행 상태에 따라 프로그램 관련 전압들을 조절하는 메모리 장치.</div>
    </div>
    <div class="extract-button">▱&nbsp; 선택한 청구항을 LLM으로 구성요소 추출 및 추가</div>
  </aside>
  <main class="workspace">
    <div class="loading-view">
      <div class="progress-wrap">
        <div class="progress">
          <div class="step done"><div class="step-dot">✓</div><div class="step-name">기준문헌 분석</div><div class="step-status">완료</div></div>
          <div class="step active"><div class="step-dot">○</div><div class="step-name">유사성검색</div><div class="step-status">진행 중</div></div>
          <div class="step"><div class="step-dot">3</div><div class="step-name">리랭킹</div><div class="step-status">Top 100</div></div>
          <div class="step"><div class="step-dot">4</div><div class="step-name">구성요소</div><div class="step-status">RRF Top 100</div></div>
        </div>
      </div>
      <section class="loading-area">
        <div class="loading-title">검색을 진행하고 있습니다</div>
        <div class="loading-subtitle">실제 검색과 AI 처리 상태를 확인하고 있습니다.</div>
        <div class="loading-card">
          <div class="loading-item"><span class="spinner"></span>출원 발명의 임베딩 벡터 추출 중</div>
          <div class="loading-item"><span class="spinner"></span>키워드 유사도 검색 중...</div>
          <div class="loading-item"><span class="spinner"></span>임베딩 벡터 유사도 검색 중...</div>
          <div class="loading-item"><span class="spinner"></span>하이브리드 결과 병합 중...</div>
          <div class="loading-item"><span class="spinner"></span>검색 결과 Top100 선정 중...</div>
        </div>
      </section>
    </div>
    <div class="result-view">
      <section class="result-center">
        <div class="result-toolbar">
          <div class="result-tool active">▣ 문헌</div>
          <div class="result-tool">▦ 구성요소</div>
          <label for="bulk-drawings-toggle" class="result-tool bulk-drawings-trigger">▣ 대표 도면 일괄조회</label>
          <div class="result-tool">♙ 화학식 일괄조회</div>
          <label for="bulk-claims-toggle" class="result-tool bulk-claims-trigger">▧ 청구항 일괄조회</label>
          <div class="result-search">⌕ &nbsp; 결과 내 키워드검색...</div>
          <div class="result-search-btn">검색</div>
        </div>
        <div class="patent-table-wrap">
          <table class="patent-table">
            <colgroup><col><col><col><col><col><col><col></colgroup>
            <thead><tr><th>순번</th><th>구분</th><th>CPC</th><th>발명의 명칭</th><th>출원번호</th><th>출원일자</th><th>공개번호</th></tr></thead>
            <tbody>
              <tr class="clickable-row"><td><label for="spec-modal-toggle" class="row-open"></label>1</td><td><span class="state-chip">공개</span></td><td class="cpc">G11C 16/3459<br>G11C 16/10<br>G11C 16/26(i)</td><td class="title">메모리 장치 및 이를 포함하는 메모리 시스템</td><td>1020180133661</td><td>20181102</td><td>1020200050705</td></tr>
              <tr class="clickable-row"><td><label for="spec-modal-toggle" class="row-open"></label>2</td><td><span class="state-chip">공개</span></td><td class="cpc">G11C 29/38<br>G11C 16/34<br>G11C 16/12(i)</td><td class="title">반도체 메모리 장치 및 그의 동작 방법</td><td>1020140178426</td><td>20141211</td><td>1020160071120</td></tr>
              <tr class="clickable-row"><td><label for="spec-modal-toggle" class="row-open"></label>3</td><td><span class="state-chip">공개</span></td><td class="cpc">G11C 16/10<br>G11C 16/3403<br>G11C 16/3459(i)</td><td class="title">메모리 장치 및 이의 동작 방법</td><td>1020200126702</td><td>20200929</td><td>1020220043365</td></tr>
              <tr class="clickable-row"><td><label for="spec-modal-toggle" class="row-open"></label>4</td><td><span class="state-chip">등록</span></td><td class="cpc">G11C 16/3459<br>G11C 16/08<br>G11C 16/10(i)</td><td class="title">메모리 장치</td><td>1020200098794</td><td>20200806</td><td>1020220018354</td></tr>
              <tr class="clickable-row"><td><label for="spec-modal-toggle" class="row-open"></label>5</td><td><span class="state-chip">공개</span></td><td class="cpc">G11C 16/30<br>G11C 16/08<br>G11C 16/24(i)</td><td class="title">메모리 장치 및 이의 동작 방법</td><td>1020200098765</td><td>20200806</td><td>1020220018341</td></tr>
              <tr class="clickable-row"><td><label for="spec-modal-toggle" class="row-open"></label>6</td><td><span class="state-chip">등록</span></td><td class="cpc">G11C 16/3459<br>G11C 16/10(i)<br>G11C 16/24</td><td class="title">페이지 버퍼, 페이지 버퍼를 포함하는 메모리 장치 및 메모리 장치를 포함하는 메모리 시스템</td><td>1020220164302</td><td>20221130</td><td>1020240080715</td></tr>
              <tr class="clickable-row"><td><label for="spec-modal-toggle" class="row-open"></label>7</td><td><span class="state-chip">공개</span></td><td class="cpc">G11C 16/3445<br>G11C 16/3459<br>G11C 29/26(i)</td><td class="title">메모리 장치 및 그의 동작방법</td><td>1020150172401</td><td>20151204</td><td>1020170065969</td></tr>
              <tr class="clickable-row"><td><label for="spec-modal-toggle" class="row-open"></label>8</td><td><span class="state-chip">공개</span></td><td class="cpc">G11C 16/3459<br>G11C 16/10<br>G11C 16/26(i)</td><td class="title">메모리 장치 및 그 동작 방법</td><td>1020190160174</td><td>20191204</td><td>1020210070107</td></tr>
              <tr class="clickable-row"><td><label for="spec-modal-toggle" class="row-open"></label>9</td><td><span class="state-chip">공개</span></td><td class="cpc">G11C 16/3459<br>G11C 16/24<br>G11C 16/08(i)</td><td class="title">메모리 장치 및 그 동작 방법</td><td>1020200104937</td><td>20200820</td><td>1020220023263</td></tr>
              <tr class="clickable-row"><td><label for="spec-modal-toggle" class="row-open"></label>10</td><td><span class="state-chip">공개</span></td><td class="cpc">G11C 16/3459<br>G11C 16/24<br>G11C 16/10(i)</td><td class="title">메모리 장치 및 그 동작 방법</td><td>1020210025654</td><td>20210223</td><td>1020230120033</td></tr>
              <tr class="clickable-row"><td><label for="spec-modal-toggle" class="row-open"></label>11</td><td><span class="state-chip">등록</span></td><td class="cpc">G11C 16/06<br>G11C 16/125(i)</td><td class="title">불휘발성 메모리 장치 및 그것의 동작 방법</td><td>1020140093320</td><td>20140723</td><td>1020160012300</td></tr>
            </tbody>
          </table>
        </div>
        <div class="result-pager">
          <span>보기:</span><span class="page-size">50⌄</span><span>총 200건 중 1 - 50</span>
          <span class="pager-spacer"></span><span class="page">이전</span><span class="page active">1</span><span class="page">2</span><span class="page">3</span><span class="page">4</span><span class="page">다음</span>
        </div>
      </section>
      <aside class="result-side">
        <div class="side-card">
          <div class="side-heading">대표도면</div>
          <div class="drawing-box"><img src="__DRAWING_DATA_URI__" alt="대표도면"></div>
        </div>
        <div class="side-card ai-card">
          <div class="side-heading">AI 요약</div>
          <div class="summary-box red"><strong>해결과제 및 목적</strong><span>인터포저 기반 패키지 구조에서 수동소자와 전력 관리 회로를 효율적으로 통합하여 패키지 실장 면적을 줄이면서도 전력 공급 안정성과 시스템 성능을 향상시킬 수 있는 전자 소자 패키지를 제공</span></div>
          <div class="summary-box green"><strong>발명의 효과</strong><span>패키지 기판 상부에 인터포저를 배치하고, 인터포저 상부에 프로세싱 소자와 고대역폭 메모리 소자 및 전력 관리 집적 회로 소자를 탑재하며, 인터포저 내부 또는 상부에 인덕터 및 커패시터와 같은 수동소자를 형성한다. 특히 인덕터는 인터포저 상하부에 형성된 자석층과 이를 연결하는 관통 실리콘 비아 및 재배선층을 이용하여 형성되며, 전력 관리 집적 회로와 전기적으로 연결되어 안정적인 전력 공급을 구현한다.</span></div>
          <div class="summary-box blue"><strong>청구범위 요약</strong><span>인터포저 내부에 수동소자와 전력 관리 회로를 통합함으로써 패키지 기판 상의 실장 면적을 줄일 수 있고, 프로세싱 소자와 고대역폭 메모리에 안정적인 전력 공급을 제공하여 전체 전자 시스템의 성능 및 전력 효율을 향상</span></div>
        </div>
      </aside>
    </div>
  </main>
  <section class="bulk-claims-modal">
    <header class="bulk-modal-header">
      <div class="bulk-title-icon">▧</div>
      <div><div class="bulk-title">청구항 일괄조회</div><div class="bulk-subtitle">필터링된 데이터 200건 중 8개씩 보기</div></div>
      <div class="bulk-header-spacer"></div>
      <div class="bulk-sort">배열: <strong>4열⌄</strong><span>|</span><strong>2행⌄</strong></div>
      <div class="bulk-nav"><span class="disabled">이전</span><strong>1 / 25</strong><span>다음</span></div>
      <label for="bulk-claims-toggle" class="bulk-close">×</label>
    </header>
    <div class="bulk-card-grid">
      <article class="bulk-claim-card">
        <div class="bulk-meta"><span class="bulk-number">1</span><span class="bulk-state">공개</span><span>출원번호 : 1020180133661 (20181102)</span></div>
        <div class="bulk-invention-title">메모리 장치 및 이를 포함하는 메모리 시스템</div>
        <div class="bulk-claim-body"><span class="bulk-claim-label">[청구항 1]</span>복수의 워드라인 및 비트라인에 연결된 메모리 셀 어레이; 상기 메모리 셀 어레이에 프로그램 전압을 공급하는 전압 생성기; 및 선택된 메모리 셀의 상태에 기초하여 프로그램 동작을 제어하는 제어 로직을 포함하는 메모리 장치.</div>
      </article>
      <article class="bulk-claim-card">
        <div class="bulk-meta"><span class="bulk-number">2</span><span class="bulk-state">공개</span><span>출원번호 : 1020140178426 (20141211)</span></div>
        <div class="bulk-invention-title">반도체 메모리 장치 및 그의 동작 방법</div>
        <div class="bulk-claim-body"><span class="bulk-claim-label">[청구항 1]</span>메모리 셀들에 대한 독출 명령을 수신하는 단계; 선택 워드라인에 독출 전압을 인가하는 단계; 비트라인의 전류 변화를 감지하여 데이터를 판별하는 단계; 및 판별된 데이터를 외부 장치로 출력하는 단계를 포함하는 반도체 메모리 장치의 동작 방법.</div>
      </article>
      <article class="bulk-claim-card">
        <div class="bulk-meta"><span class="bulk-number">3</span><span class="bulk-state">공개</span><span>출원번호 : 1020200126702 (20200929)</span></div>
        <div class="bulk-invention-title">메모리 장치 및 이의 동작 방법</div>
        <div class="bulk-claim-body"><span class="bulk-claim-label">[청구항 1]</span>서로 다른 문턱 전압 분포를 갖는 복수의 메모리 셀; 상기 복수의 메모리 셀에 연결된 페이지 버퍼; 및 프로그램 검증 결과에 따라 후속 프로그램 펄스의 크기와 인가 시간을 조절하는 제어 회로를 포함하는 메모리 장치.</div>
      </article>
      <article class="bulk-claim-card">
        <div class="bulk-meta"><span class="bulk-number">4</span><span class="bulk-state">등록</span><span>출원번호 : 1020200098794 (20200806)</span></div>
        <div class="bulk-invention-title">메모리 장치</div>
        <div class="bulk-claim-body"><span class="bulk-claim-label">[청구항 1]</span>기판 상에 수직 방향으로 적층된 복수의 셀 스트링; 상기 셀 스트링과 공통 소스 라인 사이에 배치된 선택 트랜지스터; 및 소거 동작 시 상기 공통 소스 라인의 전위를 단계적으로 증가시키는 주변 회로를 포함하는 비휘발성 메모리 장치.</div>
      </article>
      <article class="bulk-claim-card">
        <div class="bulk-meta"><span class="bulk-number">5</span><span class="bulk-state">공개</span><span>출원번호 : 1020200098765 (20200806)</span></div>
        <div class="bulk-invention-title">메모리 장치 및 이의 동작 방법</div>
        <div class="bulk-claim-body"><span class="bulk-claim-label">[청구항 1]</span>호스트로부터 수신한 쓰기 데이터를 임시 저장하는 버퍼 메모리; 상기 쓰기 데이터의 오류 정정 부호를 생성하는 오류 정정 회로; 및 메모리 블록의 열화도에 따라 오류 정정 강도를 선택적으로 변경하는 메모리 컨트롤러를 포함하는 저장 장치.</div>
      </article>
      <article class="bulk-claim-card">
        <div class="bulk-meta"><span class="bulk-number">6</span><span class="bulk-state">공개</span><span>출원번호 : 1020220164302 (20221130)</span></div>
        <div class="bulk-invention-title">페이지 버퍼, 페이지 버퍼를 포함하는 메모리 장치 및 메모리 장치를 포함하는 메모리 시스템</div>
        <div class="bulk-claim-body"><span class="bulk-claim-label">[청구항 1]</span>감지 노드에 연결되어 비트라인의 전압을 센싱하는 센싱 래치; 센싱된 데이터를 임시 저장하는 데이터 래치; 및 상기 센싱 래치와 데이터 래치 사이의 데이터 전달 경로를 선택 신호에 따라 연결하는 스위칭 회로를 포함하는 페이지 버퍼.</div>
      </article>
      <article class="bulk-claim-card">
        <div class="bulk-meta"><span class="bulk-number">7</span><span class="bulk-state">공개</span><span>출원번호 : 1020150172401 (20151204)</span></div>
        <div class="bulk-invention-title">메모리 장치 및 그의 동작방법</div>
        <div class="bulk-claim-body"><span class="bulk-claim-label">[청구항 1]</span>선택된 메모리 블록에 제1 패스 전압을 인가하여 프로그램 검증 동작을 수행하는 단계; 검증 실패 셀의 개수를 산출하는 단계; 및 산출된 개수가 기준값을 초과하면 제1 패스 전압보다 높은 제2 패스 전압을 인가하는 단계를 포함하는 동작 방법.</div>
      </article>
      <article class="bulk-claim-card">
        <div class="bulk-meta"><span class="bulk-number">8</span><span class="bulk-state">공개</span><span>출원번호 : 1020190160174 (20191204)</span></div>
        <div class="bulk-invention-title">메모리 장치 및 그 동작 방법</div>
        <div class="bulk-claim-body"><span class="bulk-claim-label">[청구항 1]</span>복수의 플레인으로 구분된 메모리 셀 어레이; 각 플레인에 대응하는 독립적인 페이지 버퍼 회로; 및 외부 명령에 응답하여 제1 플레인의 독출 동작과 제2 플레인의 프로그램 동작을 병렬로 수행하도록 제어하는 제어기를 포함하는 메모리 장치.</div>
      </article>
    </div>
  </section>
  __BULK_DRAWINGS_MODAL_HTML__
  __SPEC_MODAL_HTML__
</div>
""".replace("__DRAWING_DATA_URI__", drawing_data_uri)
    .replace("__BULK_DRAWINGS_MODAL_HTML__", drawing_batch_modal_html)
    .replace("__SPEC_MODAL_CSS__", SPEC_MODAL_CSS.strip())
    .replace("__SPEC_MODAL_HTML__", get_spec_modal_html().strip()),
    unsafe_allow_html=True,
)
