# -*- coding: utf-8 -*-
"""AI 특허 검색 로딩 화면 목업."""

import streamlit as st


st.set_page_config(
    page_title="AI 특허 검색 시스템",
    page_icon="⌕",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;600;700&display=swap');

:root {
  --line: #e3e8ef;
  --muted: #778394;
  --blue: #2878ef;
  --purple: #7544ee;
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
  font-size: 11px;
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
  font-size: 10px;
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
  font-size: 13px;
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
  font-size: 11px;
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
  font-size: 9px;
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
  font-size: 9px;
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
.component-title span:last-child { color: #7a8490; font-size: 9px; font-weight: 400; }
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
.copyright { padding-top: 5px; color: #9aa4af; font-size: 8px; text-align: center; }

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
  font-weight: 700;
  border-bottom: 1px solid #edf0f4;
}
.doc-icon { color: #3479ee; font-size: 13px; }
.title-spacer { flex: 1; }
.view-chip { padding: 2px 5px; border-radius: 3px; font-size: 9px; font-weight: 500; }
.view-chip.on { color: #7442df; background: #f2eefe; }
.view-chip.off { color: #738091; background: #f4f6f8; }
.close { color: #8c96a2; font-size: 13px; }
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
  font-size: 9px;
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
.claim-card-head .independent { margin-left: auto; color: #7d8792; font-size: 9px; font-weight: 400; }
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
.step { position: relative; text-align: center; color: #7e8995; font-size: 9px; }
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
  font-size: 9px;
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
.step-status { margin-top: 1px; color: #9aa3ad; font-size: 8px; }
.loading-area { padding: 18px 11% 0; }
.loading-title { margin-bottom: 2px; font-size: 15px; font-weight: 700; letter-spacing: -.45px; }
.loading-subtitle { margin-bottom: 12px; color: #929ca7; font-size: 9px; }
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
  font-size: 10px;
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
#search-result-toggle {
  position: absolute;
  width: 1px;
  height: 1px;
  opacity: 0;
  pointer-events: none;
}
.result-view {
  position: absolute;
  inset: 0;
  display: none;
  width: 100%;
  height: 100%;
  min-width: 0;
}
#search-result-toggle:checked ~ .filter-panel .search-trigger { background: #3478e9; }
#search-result-toggle:checked ~ .filter-panel .search-trigger .searching-label { display: none; }
#search-result-toggle:checked ~ .filter-panel .search-trigger::after { content: "⌕ 검색"; }
#search-result-toggle:checked ~ .workspace .loading-view {
  display: block;
  animation: hide-loading-view .01s linear 3s forwards;
}
#search-result-toggle:checked ~ .workspace .result-view {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 409.5px;
  visibility: hidden;
  opacity: 0;
  animation: show-result-view .01s linear 3s forwards;
}
@keyframes hide-loading-view {
  to { visibility: hidden; opacity: 0; pointer-events: none; }
}
@keyframes show-result-view {
  to { visibility: visible; opacity: 1; }
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
  font-size: 8px;
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
  font-size: 8px;
}
.result-search-btn {
  height: 22px;
  padding: 4px 7px;
  color: #2d73dc;
  border: 1px solid #bed4f5;
  border-radius: 3px;
  font-size: 8px;
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
  font-size: 8px;
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

.result-side { min-width: 0; padding: 0 7px 7px; background: #f8fafc; overflow: hidden; }
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
  font-weight: 700;
  border-bottom: 1px solid #edf0f4;
}
.drawing-box {
  height: 118px;
  margin: 31px 7px 32px;
  display: grid;
  place-items: center;
  color: #9ba5af;
  background: #fbfcfd;
  border: 1px solid #eef1f4;
  border-radius: 4px;
  font-size: 8px;
}
.ai-card { margin-top: 7px; height: calc(100% - 225px); border-color: #eadcff; }
.ai-card .side-heading { color: #7845df; background: #fbf7ff; border-color: #f0e7fb; }
.summary-box {
  margin: 8px 7px 0;
  padding: 8px;
  border: 1px solid;
  border-radius: 5px;
  line-height: 1.45;
  font-size: 8px;
}
.summary-box strong { display: block; margin-bottom: 4px; }
.summary-box.red { color: #c6463d; background: #fff9f8; border-color: #f2d8d5; }
.summary-box.red span { color: #3f4954; }
.summary-box.green { color: #20a57c; background: #f7fffc; border-color: #caeee1; }
.summary-box.blue { color: #3978c8; background: #f7faff; border-color: #d6e2f4; }

@media (min-width: 1300px) {
  .patent-app { grid-template-columns: 336px 0 minmax(0, 1fr); font-size: 13px; }
  .patent-app:has(#ai-panel-toggle:checked) { grid-template-columns: 336px 331.5px minmax(0, 1fr); }
  .topbar { grid-template-columns: 336px 331.5px 1fr; }
  .loading-card { max-width: 635px; }
}
</style>

<div class="patent-app">
  <input type="checkbox" id="ai-panel-toggle">
  <input type="checkbox" id="search-result-toggle">
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
        <div class="section-title">⌕ 검색 일자</div>
        <div class="field select-field">출원일자</div>
        <div class="date-row"><div class="date">연도-월-일 <span>□</span></div><span class="date-sep">-</span><div class="date">2022-12-02 <span>□</span></div></div>
      </div>
      <div class="section">
        <div class="section-title">⌕ CPC 기술분류</div>
        <div class="class-grid">
          <label class="check"><input type="checkbox">A</label><label class="check"><input type="checkbox">B</label>
          <label class="check"><input type="checkbox">C</label><label class="check"><input type="checkbox">D</label>
          <label class="check"><input type="checkbox">E</label><label class="check"><input type="checkbox">F</label>
          <label class="check"><input type="checkbox" checked>G</label><label class="check"><input type="checkbox">H</label>
        </div>
      </div>
      <div class="section-title">⌕ 구성요소</div>
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
      <div class="footer-buttons"><div class="footer-button">↻ 초기화</div><label for="search-result-toggle" class="footer-button primary search-trigger"><span class="searching-label">⌕ 검색 </span></label></div>
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
          <div class="loading-item"><span class="spinner"></span>문헌검색 진행상황</div>
          <div class="loading-item"><span class="spinner"></span>Vector 검색 중...</div>
          <div class="loading-item"><span class="spinner"></span>BM25 검색 중...</div>
          <div class="loading-item"><span class="spinner"></span>Hybrid 결과 병합 중...</div>
          <div class="loading-item"><span class="spinner"></span>Top 200 선정 중...</div>
        </div>
      </section>
    </div>
    <div class="result-view">
      <section class="result-center">
        <div class="result-toolbar">
          <div class="result-tool active">▣ 문헌</div>
          <div class="result-tool">▦ 구성요소</div>
          <div class="result-tool">▣ 대표 도면 일괄조회</div>
          <div class="result-tool">♙ 화학식 일괄조회</div>
          <div class="result-tool">▧ 청구항 일괄조회</div>
          <div class="result-search">⌕ &nbsp; 결과 내 키워드검색...</div>
          <div class="result-search-btn">검색</div>
        </div>
        <div class="patent-table-wrap">
          <table class="patent-table">
            <colgroup><col><col><col><col><col><col><col></colgroup>
            <thead><tr><th>순번</th><th>구분</th><th>CPC</th><th>발명의 명칭</th><th>출원번호</th><th>출원일자</th><th>공개번호</th></tr></thead>
            <tbody>
              <tr><td>1</td><td><span class="state-chip">공개</span></td><td class="cpc">G11C 16/3459<br>G11C 16/10<br>G11C 16/26(i)</td><td class="title">메모리 장치 및 이를 포함하는 메모리 시스템</td><td>1020180133661</td><td>20181102</td><td>1020200050705</td></tr>
              <tr><td>2</td><td><span class="state-chip">공개</span></td><td class="cpc">G11C 29/38<br>G11C 16/34<br>G11C 16/12(i)</td><td class="title">반도체 메모리 장치 및 그의 동작 방법</td><td>1020140178426</td><td>20141211</td><td>1020160071120</td></tr>
              <tr><td>3</td><td><span class="state-chip">공개</span></td><td class="cpc">G11C 16/10<br>G11C 16/3403<br>G11C 16/3459(i)</td><td class="title">메모리 장치 및 이의 동작 방법</td><td>1020200126702</td><td>20200929</td><td>1020220043365</td></tr>
              <tr><td>4</td><td><span class="state-chip">등록</span></td><td class="cpc">G11C 16/3459<br>G11C 16/08<br>G11C 16/10(i)</td><td class="title">메모리 장치</td><td>1020200098794</td><td>20200806</td><td>1020220018354</td></tr>
              <tr><td>5</td><td><span class="state-chip">공개</span></td><td class="cpc">G11C 16/30<br>G11C 16/08<br>G11C 16/24(i)</td><td class="title">메모리 장치 및 이의 동작 방법</td><td>1020200098765</td><td>20200806</td><td>1020220018341</td></tr>
              <tr><td>6</td><td><span class="state-chip">등록</span></td><td class="cpc">G11C 16/3459<br>G11C 16/10(i)<br>G11C 16/24</td><td class="title">페이지 버퍼, 페이지 버퍼를 포함하는 메모리 장치 및 메모리 장치를 포함하는 메모리 시스템</td><td>1020220164302</td><td>20221130</td><td>1020240080715</td></tr>
              <tr><td>7</td><td><span class="state-chip">공개</span></td><td class="cpc">G11C 16/3445<br>G11C 16/3459<br>G11C 29/26(i)</td><td class="title">메모리 장치 및 그의 동작방법</td><td>1020150172401</td><td>20151204</td><td>1020170065969</td></tr>
              <tr><td>8</td><td><span class="state-chip">공개</span></td><td class="cpc">G11C 16/3459<br>G11C 16/10<br>G11C 16/26(i)</td><td class="title">메모리 장치 및 그 동작 방법</td><td>1020190160174</td><td>20191204</td><td>1020210070107</td></tr>
              <tr><td>9</td><td><span class="state-chip">공개</span></td><td class="cpc">G11C 16/3459<br>G11C 16/24<br>G11C 16/08(i)</td><td class="title">메모리 장치 및 그 동작 방법</td><td>1020200104937</td><td>20200820</td><td>1020220023263</td></tr>
              <tr><td>10</td><td><span class="state-chip">공개</span></td><td class="cpc">G11C 16/3459<br>G11C 16/24<br>G11C 16/10(i)</td><td class="title">메모리 장치 및 그 동작 방법</td><td>1020210025654</td><td>20210223</td><td>1020230120033</td></tr>
              <tr><td>11</td><td><span class="state-chip">등록</span></td><td class="cpc">G11C 16/06<br>G11C 16/125(i)</td><td class="title">불휘발성 메모리 장치 및 그것의 동작 방법</td><td>1020140093320</td><td>20140723</td><td>1020160012300</td></tr>
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
          <div class="drawing-box">도면 이미지 없음</div>
        </div>
        <div class="side-card ai-card">
          <div class="side-heading">AI 요약</div>
          <div class="summary-box red"><strong>해결과제 및 목적</strong><span>메모리 장치 및 이를 포함하는 메모리 시스템</span></div>
          <div class="summary-box green"><strong>발명의 효과</strong><span>(향후 LLM 연동)</span></div>
          <div class="summary-box blue"><strong>청구범위 요약</strong><span>(향후 LLM 연동)</span></div>
        </div>
      </aside>
    </div>
  </main>
</div>
""",
    unsafe_allow_html=True,
)
