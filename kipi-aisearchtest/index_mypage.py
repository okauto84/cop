"""마이페이지 나만의 참조 저장소 팝업 UI."""

import html

MYPAGE_APP_NO = "1020017004375"
MYPAGE_CITED_DOCS = [
    "1020017000723",
    "1020017001933",
    "1020007001612",
]
MYPAGE_COMPONENTS = [
    {
        "text": (
            "주된 가스 터빈 시스템의 편익이 일반적으로 가연기의 입구단, 압축기, 연소실 및 터빈을 "
            "포함하는 전체 경로적 부분이 기체온도와 압력에 표면에 최대 노출되는 순간, 그리고 반전된 "
            "순간에 변화되는 비틀림 구배의 변화를 바이패스된다."
        ),
        "cells": [
            ("same", "명세서 0006문단"),
            ("same", "명세서 0006문단"),
            ("same", "명세서 0006문단"),
        ],
    },
    {
        "text": (
            "주된 가스 터빈 시스템의 편익이 일반적으로 가연기의 입구단, 압축기, 연소실 및 터빈을 "
            "포함하는 전체 경로적 부분이 기체온도와 압력에 표면에 최대 노출되는 순간, 그리고 반전된 "
            "순간에 가연기 다음에 직상기 단열 내주차구에 뜨거운 가스가 충돌하는 순간에 변화되는 "
            "대형 직사각 보강 방식을 포함한다."
        ),
        "cells": [
            ("partial", "청구항 1"),
            ("partial", "청구항 1"),
            ("partial", "청구항 1"),
        ],
    },
    {
        "text": (
            "혼합 장치는 혼합 챔버를 포함하고, 혼합 챔버는 혼합 챔버의 입구단에 배치된 혼합 챔버 "
            "입구, 혼합 챔버의 출구단에 배치된 혼합 챔버 출구, 및 혼합 챔버 입구와 혼합 챔버 출구 "
            "사이에 배치된 혼합 챔버 내부를 포함한다."
        ),
        "cells": [
            ("diff", "명세서 0010문단"),
            ("none", ""),
            ("none", ""),
        ],
    },
]

MYPAGE_MODAL_CSS = """
#mypage-toggle {
  position: absolute;
  width: 1px;
  height: 1px;
  opacity: 0;
  pointer-events: none;
}
.mypage-trigger {
  cursor: pointer;
  user-select: none;
  display: inline-block;
  text-decoration: none;
  line-height: 1;
}
.mypage-modal-backdrop {
  position: absolute;
  inset: 0;
  z-index: 199;
  display: none;
  background: rgba(33, 43, 54, .48);
  pointer-events: none;
}
#mypage-toggle:checked ~ .mypage-modal-backdrop {
  display: block;
  animation: mp-backdrop-fade-in .18s ease-out;
}
.mypage-modal {
  position: absolute;
  top: 28px;
  right: 32px;
  bottom: 28px;
  left: 32px;
  z-index: 200;
  display: none;
  flex-direction: column;
  color: #34404c;
  background: #fff;
  border: 1px solid #dfe5ec;
  border-radius: 10px;
  box-shadow: 0 10px 36px rgba(23, 36, 50, .14);
  overflow: hidden;
  --fs-body: 12px;
  --fs-caption: 12px;
  --fs-label: 13px;
  --fs-subtitle: 14px;
  --fs-title: 16px;
  --fs-display: 18px;
  font-size: var(--fs-body);
}
#mypage-toggle:checked ~ .mypage-modal {
  display: flex;
  animation: mp-modal-fade-in .18s ease-out;
}
@keyframes mp-backdrop-fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}
@keyframes mp-modal-fade-in {
  from { opacity: 0; transform: scale(.985); }
  to { opacity: 1; transform: scale(1); }
}
.mp-modal-header {
  height: 52px;
  flex: 0 0 52px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
  background: #fff;
  border-bottom: 1px solid #e6e9ed;
}
.mp-title-wrap {
  display: flex;
  align-items: center;
  gap: 10px;
}
.mp-title-icon {
  width: 28px;
  height: 28px;
  display: grid;
  place-items: center;
  color: #2c6fc9;
  background: #fff;
  border: 1.5px solid #93bbf1;
  border-radius: 6px;
  font-size: 14px;
  line-height: 1;
}
.mp-title-text {
  display: flex;
  align-items: baseline;
  gap: 8px;
}
.mp-title {
  color: #27323d;
  font-size: var(--fs-title);
  font-weight: 700;
}
.mp-subtitle {
  color: #8a949e;
  font-size: var(--fs-body);
  font-weight: 400;
}
.mp-header-controls {
  display: flex;
  align-items: center;
  gap: 10px;
}
.mp-view-toggle {
  display: flex;
  align-items: center;
  gap: 6px;
}
.mp-view-opt {
  height: 28px;
  display: grid;
  place-items: center;
  padding: 0 12px;
  color: #6b7785;
  background: #fff;
  border: 1px solid #dfe4ea;
  border-radius: 5px;
  font-size: var(--fs-body);
  white-space: nowrap;
}
.mp-view-opt.active {
  color: #2c6fc9;
  font-weight: 700;
  border-color: #93bbf1;
  background: #f7fbff;
}
.mp-app-select {
  display: flex;
  align-items: center;
  gap: 6px;
  height: 28px;
  padding: 0 10px;
  background: #fff;
  border: 1px solid #dfe4ea;
  border-radius: 5px;
  font-size: var(--fs-body);
}
.mp-app-select-label { color: #6b7785; white-space: nowrap; }
.mp-app-select-value { color: #27323d; font-weight: 700; }
.mp-close {
  width: 28px;
  height: 28px;
  display: grid;
  place-items: center;
  color: #7d8791;
  background: #fff;
  border: 1px solid #dfe4ea;
  border-radius: 5px;
  font-size: var(--fs-display);
  cursor: pointer;
}
.mp-info-bar {
  flex: 0 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 16px;
  background: #eef6ff;
  border-bottom: 1px solid #dce8f8;
}
.mp-info-left {
  display: flex;
  align-items: center;
  gap: 10px;
}
.mp-info-badge {
  padding: 3px 10px;
  color: #2c6fc9;
  background: #dceeff;
  border-radius: 5px;
  font-size: 11px;
  font-weight: 700;
}
.mp-info-app-no {
  color: #27323d;
  font-size: var(--fs-display);
  font-weight: 700;
  letter-spacing: -.02em;
}
.mp-info-right {
  color: #5d6978;
  font-size: var(--fs-body);
}
.mp-content {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  padding: 14px 16px 16px;
  background: #fff;
}
.mp-section-head {
  flex: 0 0 auto;
  margin-bottom: 10px;
}
.mp-section-title {
  color: #27323d;
  font-size: var(--fs-subtitle);
  font-weight: 700;
}
.mp-section-hint {
  margin-top: 4px;
  color: #8a949e;
  font-size: 11px;
  line-height: 1.45;
}
.mp-table-wrap {
  flex: 1;
  min-height: 0;
  overflow: auto;
  background: #fff;
  border: 1px solid #e3e8ee;
  border-radius: 8px;
}
.mp-compare-table {
  width: max-content;
  min-width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  font-size: var(--fs-body);
}
.mp-compare-table th,
.mp-compare-table td {
  vertical-align: top;
  border-bottom: 1px solid #edf0f3;
  border-right: 1px solid #edf0f3;
}
.mp-compare-table th:last-child,
.mp-compare-table td:last-child { border-right: 0; }
.mp-component-head,
.mp-component-cell {
  position: sticky;
  left: 0;
  z-index: 2;
  width: 290px;
  min-width: 290px;
  max-width: 290px;
  background: #fff;
}
.mp-component-head {
  top: 0;
  z-index: 3;
  padding: 10px 12px;
  color: #4c5966;
  font-weight: 700;
  background: #f8f9fb;
  border-bottom: 1px solid #e3e8ee;
}
.mp-cited-col {
  position: sticky;
  top: 0;
  z-index: 1;
  min-width: 220px;
  max-width: 220px;
  padding: 8px 10px;
  background: #f8f9fb;
  border-bottom: 1px solid #e3e8ee;
}
.mp-cited-top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 6px;
  margin-bottom: 4px;
}
.mp-cited-label {
  color: #8a949e;
  font-size: 10px;
  font-weight: 600;
  line-height: 1.3;
}
.mp-cited-no {
  color: #2c6fc9;
  font-size: var(--fs-body);
  font-weight: 700;
  text-decoration: underline;
  cursor: pointer;
}
.mp-col-controls {
  display: flex;
  align-items: center;
  gap: 3px;
  flex-shrink: 0;
}
.mp-col-btn {
  width: 20px;
  height: 20px;
  display: grid;
  place-items: center;
  color: #7d8791;
  background: #fff;
  border: 1px solid #dfe4ea;
  border-radius: 3px;
  font-size: 10px;
  cursor: pointer;
}
.mp-col-drag { letter-spacing: -1px; font-weight: 700; }
.mp-col-del {
  color: #d64545;
  border-color: #e8c4c4;
}
.mp-row-check {
  display: inline-flex;
  align-items: flex-start;
  margin-right: 8px;
}
.mp-component-cell {
  padding: 10px 12px;
  background: #fff;
}
.mp-component-body { display: inline-block; width: calc(100% - 28px); vertical-align: top; }
.mp-component-badge {
  display: inline-block;
  margin-bottom: 6px;
  padding: 2px 8px;
  color: #7c5fd4;
  background: #f3edff;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 700;
}
.mp-component-text {
  margin: 0;
  color: #3d4855;
  line-height: 1.55;
  font-size: var(--fs-body);
}
.mp-compare-cell {
  min-width: 220px;
  max-width: 220px;
  padding: 8px;
  background: #fff;
}
.mp-compare-card {
  min-height: 120px;
  display: flex;
  flex-direction: column;
  border: 1px solid #e3e8ee;
  border-radius: 6px;
  overflow: hidden;
}
.mp-status-strip {
  padding: 4px 10px;
  font-size: 11px;
  font-weight: 700;
}
.mp-compare-body {
  flex: 1;
  padding: 8px 10px;
  color: #5d6978;
  line-height: 1.45;
  font-size: 11px;
}
.mp-compare-foot {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 6px;
  padding: 6px 10px 8px;
}
.mp-compare-link {
  color: #2c6fc9;
  font-size: 11px;
  font-weight: 600;
  cursor: pointer;
}
.mp-compare-ref {
  color: #9aa3ad;
  font-size: 10px;
  white-space: nowrap;
}
.mp-status-same .mp-compare-card { background: #f3fbf4; border-color: #c8e6c9; }
.mp-status-same .mp-status-strip { color: #fff; background: #43a047; }
.mp-status-partial .mp-compare-card { background: #fffdf5; border-color: #ffe082; }
.mp-status-partial .mp-status-strip { color: #fff; background: #f9a825; }
.mp-status-diff .mp-compare-card { background: #fff8f8; border-color: #ef9a9a; }
.mp-status-diff .mp-status-strip { color: #fff; background: #e53935; }
.mp-compare-none {
  text-align: center;
  vertical-align: middle;
  background: #f8f9fb;
}
.mp-compare-none span {
  display: block;
  padding: 40px 8px;
  color: #b8c0c8;
  font-size: 11px;
}
"""


def _compare_cell(status: str, ref: str) -> str:
    if status == "none":
        return (
            '<td class="mp-compare-cell mp-compare-none">'
            "<span>저장된 대응 구성요소 없음</span></td>"
        )
    status_map = {
        "same": ("동일", "mp-status-same"),
        "partial": ("일부 차이", "mp-status-partial"),
        "diff": ("차이", "mp-status-diff"),
    }
    label, cls = status_map[status]
    return (
        f'<td class="mp-compare-cell {cls}">'
        f'<div class="mp-compare-card">'
        f'<div class="mp-status-strip">{label}</div>'
        f'<div class="mp-compare-body">(LLM이 추출한 인용문헌 대응 내용 예시)</div>'
        f'<div class="mp-compare-foot">'
        f'<span class="mp-compare-link">▶ 대비결과 보기</span>'
        f'<span class="mp-compare-ref">{ref}</span>'
        f"</div></div></td>"
    )


def _build_cited_headers() -> str:
    headers = []
    for doc_no in MYPAGE_CITED_DOCS:
        headers.append(
            f'<th class="mp-cited-col">'
            f'<div class="mp-cited-top">'
            f'<span class="mp-cited-label">인용발명 출원번호</span>'
            f'<div class="mp-col-controls">'
            f'<span class="mp-col-btn" title="왼쪽으로">←</span>'
            f'<span class="mp-col-btn" title="오른쪽으로">→</span>'
            f'<span class="mp-col-btn mp-col-drag" title="순서 변경">⋮⋮</span>'
            f'<span class="mp-col-btn mp-col-del" title="삭제">×</span>'
            f"</div></div>"
            f'<div class="mp-cited-no">{doc_no}</div>'
            f"</th>"
        )
    return "".join(headers)


def _build_table_body() -> str:
    rows = []
    for index, component in enumerate(MYPAGE_COMPONENTS, start=1):
        cells = "".join(
            _compare_cell(status, ref)
            for status, ref in component["cells"]
        )
        rows.append(
            f'<tr class="mp-component-row">'
            f'<td class="mp-component-cell">'
            f'<label class="mp-row-check"><input type="checkbox"></label>'
            f'<div class="mp-component-body">'
            f'<span class="mp-component-badge">구성요소 {index}</span>'
            f'<p class="mp-component-text">{html.escape(component["text"])}</p>'
            f"</div></td>{cells}</tr>"
        )
    return "".join(rows)


MYPAGE_MODAL_HTML_TEMPLATE = """
<div class="mypage-modal-backdrop" aria-hidden="true"></div>
<section class="mypage-modal">
  <header class="mp-modal-header">
    <div class="mp-title-wrap">
      <span class="mp-title-icon">▱</span>
      <div class="mp-title-text">
        <span class="mp-title">마이페이지</span>
        <span class="mp-subtitle">나만의 참조 저장소</span>
      </div>
    </div>
    <div class="mp-header-controls">
      <div class="mp-view-toggle">
        <span class="mp-view-opt">문헌별 보기</span>
        <span class="mp-view-opt active">테이블 보기</span>
      </div>
      <div class="mp-app-select">
        <span class="mp-app-select-label">출원번호 선택 :</span>
        <span class="mp-app-select-value">__MYPAGE_APP_NO__</span>
      </div>
      <label for="mypage-toggle" class="mp-close">×</label>
    </div>
  </header>
  <div class="mp-info-bar">
    <div class="mp-info-left">
      <span class="mp-info-badge">출원번호</span>
      <span class="mp-info-app-no">__MYPAGE_APP_NO__</span>
    </div>
    <div class="mp-info-right">저장된 인용문헌 __MYPAGE_CITED_COUNT__개</div>
  </div>
  <div class="mp-content">
    <div class="mp-section-head">
      <div class="mp-section-title">기술 구성요소별 인용문헌 구성요소 비교</div>
      <div class="mp-section-hint">
        첫 번째 열은 고정되고, 나머지 열은 가로 스크롤됩니다.
        열 헤더의 화살표 또는 드래그로 열 순서를 변경하고 삭제할 수 있습니다.
      </div>
    </div>
    <div class="mp-table-wrap">
      <table class="mp-compare-table">
        <thead>
          <tr>
            <th class="mp-component-head">
              <label class="mp-row-check"><input type="checkbox"></label>
              <span>출원발명 구성요소</span>
            </th>
            __MYPAGE_CITED_HEADERS__
          </tr>
        </thead>
        <tbody>__MYPAGE_TABLE_BODY__</tbody>
      </table>
    </div>
  </div>
</section>
"""


def get_mypage_modal_html() -> str:
    return (
        MYPAGE_MODAL_HTML_TEMPLATE.replace("__MYPAGE_APP_NO__", MYPAGE_APP_NO)
        .replace("__MYPAGE_CITED_COUNT__", str(len(MYPAGE_CITED_DOCS)))
        .replace("__MYPAGE_CITED_HEADERS__", _build_cited_headers())
        .replace("__MYPAGE_TABLE_BODY__", _build_table_body())
    )


MYPAGE_MODAL_HTML = get_mypage_modal_html()
