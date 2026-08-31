"""검색 결과 행에서 여는 특허 상세 팝업 UI."""

SPEC_MODAL_CSS = """
#spec-modal-toggle {
  position: absolute;
  width: 1px;
  height: 1px;
  opacity: 0;
  pointer-events: none;
}
.clickable-row td:first-child { position: relative; overflow: visible; }
.row-open {
  position: absolute;
  z-index: 4;
  inset: 0 auto 0 0;
  width: 2500%;
  cursor: pointer;
}
.clickable-row:hover td { background: #eaf3ff !important; }
.spec-modal {
  position: absolute;
  inset: 0;
  z-index: 200;
  display: none;
  grid-template-columns: 96px minmax(430px, 1fr) 400px;
  grid-template-rows: 47px minmax(0, 1fr);
  color: #34404c;
  background: #f7f8fa;
  font-size: 10px;
}
#spec-modal-toggle:checked ~ .spec-modal { display: grid; }
.spec-top {
  grid-column: 1 / -1;
  display: flex;
  align-items: center;
  padding: 0 10px;
  background: #fff;
  border-bottom: 1px solid #dfe4e9;
}
.spec-number { width: 96px; color: #26313c; font-weight: 700; }
.spec-search {
  width: 200px;
  height: 25px;
  display: flex;
  align-items: center;
  padding: 0 8px;
  color: #929ca6;
  border: 1px solid #dce2e8;
  border-radius: 4px;
}
.spec-zoom {
  margin-left: auto;
  padding: 6px 10px;
  color: #53606c;
  border: 1px solid #dce2e8;
  border-radius: 4px;
}
.spec-close {
  width: 28px;
  height: 28px;
  display: grid;
  place-items: center;
  margin-left: 8px;
  color: #6d7884;
  border: 1px solid #dce2e8;
  border-radius: 4px;
  cursor: pointer;
  font-size: 17px;
}
.spec-nav {
  grid-column: 1;
  grid-row: 2;
  padding: 12px 10px;
  background: #fafbfc;
  border-right: 1px solid #e2e7ec;
}
.spec-nav-title { margin-bottom: 18px; color: #36424e; font-weight: 700; }
.spec-nav-item { margin: 0 -10px; padding: 7px 12px; color: #68747f; }
.spec-nav-item.active { color: #2874dc; background: #edf5ff; font-weight: 700; }
.spec-nav-group { margin-top: 12px; color: #3f4b57; font-weight: 700; }
.spec-nav-child { padding: 5px 10px; color: #7a8590; font-weight: 400; }
.spec-document {
  grid-column: 2;
  grid-row: 2;
  min-width: 0;
  display: flex;
  flex-direction: column;
  background: #eef0f2;
  border-right: 1px solid #d9dfe5;
}
.spec-doc-tabs {
  height: 30px;
  display: flex;
  align-items: end;
  gap: 18px;
  padding-left: 17px;
  background: #fff;
  border-bottom: 1px solid #dfe4e9;
}
.spec-doc-tab { height: 28px; padding-top: 8px; color: #697580; }
.spec-doc-tab.active { color: #2874dc; border-bottom: 2px solid #2874dc; font-weight: 700; }
.spec-page-wrap { min-height: 0; flex: 1; padding: 8px 13px; overflow: hidden; }
.spec-page {
  height: 100%;
  padding: 18px 46px;
  background: #fff;
  box-shadow: 0 1px 4px rgba(34, 46, 58, .14);
  overflow: hidden;
  font-family: "Batang", "바탕", serif;
  color: #171717;
  font-size: 12px;
  line-height: 1.62;
}
.spec-page h2 { margin: 0 0 18px; color: #172db0; text-align: center; font-size: 19px; font-weight: 500; }
.spec-biblio { white-space: pre-wrap; }
.spec-line { margin: 10px 0; border-top: 1px solid #777; }
.spec-right {
  grid-column: 3;
  grid-row: 2;
  min-width: 0;
  display: flex;
  flex-direction: column;
  background: #f8fafc;
  overflow: hidden;
}
.spec-result-head {
  height: 31px;
  flex: 0 0 31px;
  display: flex;
  align-items: center;
  padding: 0 10px;
  background: #fff;
  border-bottom: 1px solid #e1e6eb;
}
.spec-ai-badge { padding: 4px 8px; color: #fff; background: #7545e8; border-radius: 3px; font-weight: 700; }
.spec-result-title { margin-left: 7px; color: #26313c; font-weight: 700; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.spec-right-tabs {
  height: 26px;
  flex: 0 0 26px;
  display: flex;
  gap: 17px;
  align-items: end;
  padding-left: 10px;
  background: #fff;
  border-bottom: 1px solid #e1e6eb;
}
.spec-right-tab { height: 25px; padding-top: 7px; color: #6f7a85; }
.spec-right-tab.active { color: #2874dc; border-bottom: 2px solid #2874dc; font-weight: 700; }
.spec-summary-row {
  height: 194px;
  flex: 0 0 194px;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 7px;
  padding: 8px;
}
.spec-panel {
  min-width: 0;
  background: #fff;
  border: 1px solid #e0e5ea;
  border-radius: 6px;
  overflow: hidden;
}
.spec-panel-title { height: 27px; padding: 7px 9px; font-weight: 700; border-bottom: 1px solid #edf0f3; }
.spec-drawing {
  height: 117px;
  margin: 18px 10px;
  display: grid;
  place-items: center;
  color: #a0a8b0;
  background: #f4f5f7;
}
.spec-ai-summary { padding: 7px; }
.spec-ai-box { margin-bottom: 6px; padding: 7px; border: 1px solid; border-radius: 4px; line-height: 1.45; }
.spec-ai-box strong { display: block; margin-bottom: 3px; }
.spec-ai-box.red { color: #c3453e; background: #fffafa; border-color: #efd5d2; }
.spec-ai-box.red span, .spec-ai-box.green span { color: #4e5964; }
.spec-ai-box.green { color: #149b72; background: #f5fffb; border-color: #c8ebdf; }
.spec-components {
  min-height: 0;
  flex: 1;
  margin: 0 8px 8px;
  background: #fff;
  border: 1px solid #e0e5ea;
  border-radius: 6px;
  overflow: hidden;
}
.spec-components-head {
  height: 30px;
  display: flex;
  align-items: center;
  padding: 0 8px;
  border-bottom: 1px solid #e4e8ed;
  font-weight: 700;
}
.spec-components-head span { margin-left: auto; padding: 4px 8px; color: #fff; background: #16a980; border-radius: 3px; }
.spec-component {
  display: grid;
  grid-template-columns: 123px 1fr;
  min-height: 92px;
  border-bottom: 1px solid #e7ebef;
}
.spec-component-name { padding: 12px 8px; background: #fafbfc; }
.spec-component-name strong { display: block; margin-bottom: 8px; color: #7055cf; }
.spec-compare { padding: 8px; }
.spec-compare-box { height: 68px; padding: 8px; background: #effcf7; border: 1px solid #9cdec8; border-radius: 5px; line-height: 1.45; }
"""

SPEC_MODAL_HTML = """
<section class="spec-modal">
  <header class="spec-top">
    <div class="spec-number">1020180133661</div>
    <div class="spec-search">⌕ 문서 내 단어 검색...</div>
    <div class="spec-zoom">− &nbsp; 100% &nbsp; ＋</div>
    <label for="spec-modal-toggle" class="spec-close">×</label>
  </header>
  <nav class="spec-nav">
    <div class="spec-nav-title">☰ 문서 목차</div>
    <div class="spec-nav-item">서지사항</div>
    <div class="spec-nav-item">요약</div>
    <div class="spec-nav-group">청구범위　⌃</div>
    <div class="spec-nav-child">청구항 1</div><div class="spec-nav-child">청구항 2</div>
    <div class="spec-nav-child">청구항 3</div><div class="spec-nav-child">청구항 4</div>
    <div class="spec-nav-child">청구항 5</div><div class="spec-nav-child">청구항 6</div>
    <div class="spec-nav-child">청구항 7</div><div class="spec-nav-child">청구항 8</div>
    <div class="spec-nav-child">청구항 9</div><div class="spec-nav-child">청구항 10</div>
    <div class="spec-nav-group">도면설명　⌃</div>
    <div class="spec-nav-child active">대표도면</div><div class="spec-nav-child">도면 1</div>
    <div class="spec-nav-child">도면 2</div><div class="spec-nav-child">도면 3</div>
  </nav>
  <main class="spec-document">
    <div class="spec-doc-tabs"><div class="spec-doc-tab">공개전문</div><div class="spec-doc-tab active">등록공보</div></div>
    <div class="spec-page-wrap"><div class="spec-page">
      <h2>(19) 대한민국특허청(KR)<br>(12) 공개특허공보(A)</h2>
      <div class="spec-biblio">(51)  Int. Cl. 8
　H01L 21/67 (2005.01)　　　　　　　　(11) 공개번호　10-2025-0106744
　H01L 37/32 (2003.01)　　　　　　　　(43) 공개일자　2025년07월11일
　H01L 21/687 (2005.01)

(52)  C08 C.I.
　H01L 21/6719 (2013.01)
　H01L 31/3244 (2013.01)
　H01L 37/32513 (2013.01)
　H01L 37/32715 (2013.01)
　H01L 31/32890 (2013.01)
　H01L 21/67128 (2013.01)
　H01L 21/68742 (2013.01)</div>
      <div class="spec-line"></div>
      <div>(21) 출원번호　　　10-2024-0006652<br>(22) 출원일자　　　2024년01월08일<br>　　심사청구일자　2024년01월08일</div>
      <div class="spec-line"></div>
      <div>(71) 출원인　　　　주식회사 아이에스티이<br>　　　　　　　　 경기도 화성시 향남읍 토성로 306</div>
      <div>(72) 발명자　　　　박세욱<br>　　　　　　　　 경기도 수원시 두산중앙로 12</div>
    </div></div>
  </main>
  <aside class="spec-right">
    <div class="spec-result-head"><span class="spec-ai-badge">⚡ AI 분석</span><span class="spec-result-title">이송 핸들러 및 마찰패드를 이용한 기판 처리장치</span></div>
    <div class="spec-right-tabs"><div class="spec-right-tab active">분석</div><div class="spec-right-tab">무효성 분석개요</div></div>
    <div class="spec-summary-row">
      <div class="spec-panel"><div class="spec-panel-title">▧ 도면</div><div class="spec-drawing">이미지를 찾을 수 없음</div></div>
      <div class="spec-panel"><div class="spec-panel-title">⚡ AI 요약</div><div class="spec-ai-summary">
        <div class="spec-ai-box red"><strong>해결과제 및 목적</strong><span>기존 방식의 처리장치에서 발생하는 웨이퍼 파손과 공정 불안정 문제를 해결합니다.</span></div>
        <div class="spec-ai-box green"><strong>발명의 효과</strong><span>처리 안정성을 높이고 기판의 오염과 손상을 감소시킵니다.</span></div>
      </div></div>
    </div>
    <div class="spec-components">
      <div class="spec-components-head">▣ 구성요소 대비표 <span>선택 구성요소 저장</span></div>
      <div class="spec-component"><div class="spec-component-name"><strong>구성요소 1</strong>워드라인 및 비트라인들에 연결된 메모리 셀들</div><div class="spec-compare"><div class="spec-compare-box"><strong>동일　　　　　　대비결과</strong><br>메모리 셀들이 워드라인과 비트라인에 연결된 구성이 대응됩니다.</div></div></div>
      <div class="spec-component"><div class="spec-component-name"><strong>구성요소 2</strong>프로그램 관련 전압을 제어하는 메인 프로세서</div><div class="spec-compare"><div class="spec-compare-box"><strong>일부 차이　　　 대비결과</strong><br>전압 제어 구조와 처리 순서에서 일부 차이가 확인됩니다.</div></div></div>
    </div>
  </aside>
</section>
"""
