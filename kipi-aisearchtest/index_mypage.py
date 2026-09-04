"""留덉씠?섏씠吏 ?섎쭔??李몄“ ??μ냼 ?앹뾽 UI."""

import html
import random

MYPAGE_COMPONENT_COL_WIDTH = 360
MYPAGE_APP_NO = "1020017004375"
MYPAGE_CITED_DOCS = [
    "1020017000723",
    "1020017001933",
    "1020007001612",
]
MYPAGE_CELL_PATTERNS = [
    [
        ("same", "紐낆꽭??0006臾몃떒"),
        ("same", "紐낆꽭??0006臾몃떒"),
        ("same", "紐낆꽭??0006臾몃떒"),
    ],
    [
        ("partial", "泥?뎄??1"),
        ("partial", "泥?뎄??1"),
        ("partial", "泥?뎄??1"),
    ],
    [
        ("diff", "紐낆꽭??0010臾몃떒"),
        ("none", ""),
        ("none", ""),
    ],
    [
        ("same", "紐낆꽭??0008臾몃떒"),
        ("partial", "泥?뎄??2"),
        ("same", "紐낆꽭??0008臾몃떒"),
    ],
    [
        ("partial", "泥?뎄??3"),
        ("diff", "紐낆꽭??0012臾몃떒"),
        ("partial", "泥?뎄??3"),
    ],
]

CITED_TEXT_MIN_LEN = 40
CITED_TEXT_MAX_LEN = 49

CITED_CONTENT_SAMPLES = [
    "?뚮뱶?쇱씤 諛?鍮꾪듃?쇱씤???곌껐??蹂듭닔??硫붾え由??怨??곴린 ???援щ룞?섎뒗 ?쒖뼱?뚮줈",
    "?꾨줈洹몃옩 愿???꾩븬???쒖뼱?섎뒗 硫붿씤 ?꾨줈?몄꽌? ?곴린 ?꾩븬???앹꽦?섎뒗 二쇰??뚮줈遺",
    "硫붾え由????臾쇰━ ?꾩븬??湲곗큹濡??쇱떛???곗씠?곕? ??ν븯???섏씠吏 踰꾪띁 ?뚮줈",
    "?쇱떛???곗씠?곗뿉 ??묓븯???쇱떛 ?꾨쪟? 湲곗? ?꾨쪟瑜?鍮꾧탳?섏뿬 異쒕젰?섎뒗 鍮꾧탳 ?뚮줈",
    "?곴린 硫붿씤 ?꾨줈?몄꽌媛 ?꾨줈洹몃옩 愿???꾩븬???쒖뼱?섎룄濡?援ъ꽦??硫붾え由??μ튂",
    "?좏깮???뚮뱶?쇱씤???꾨줈洹몃옩 ?꾩븬???멸??섍퀬 寃利??숈옉???섑뻾?섎뒗 ?쒖뼱?뚮줈",
    "鍮꾪듃?쇱씤???꾩븬 蹂?붾? 媛먯??섏뿬 ?곗씠?곕? ?먮퀎?섍퀬 利앺룺?섎뒗 ?쇱떛 利앺룺湲??뚮줈",
    "?꾨줈洹몃옩 ?꾩뒪 ?숈옉?먯꽌 ?뚮뱶?쇱씤 ?꾩븬 ?ш린瑜??④퀎?곸쑝濡?議곗젅?섎뒗 ?쒖뼱 ?뚮줈",
    "?⑥뒪 ?덈꺼 泥댄겕 ?숈옉??蹂묐젹?곸쑝濡??섑뻾?섎룄濡??섏씠吏 踰꾪띁瑜??쒖뼱?섎뒗 ?쒕툕 ?꾨줈?몄꽌",
    "寃利??ㅽ뙣 ? ?섏뿉 ?곕씪 ?꾩냽 ?꾨줈洹몃옩 ?꾩뒪 ?ш린? ?쒓컙??議곗젅?섎뒗 ?쒖뼱 濡쒖쭅",
]

CITED_TEXT_CHUNKS = [
    "?뚮뱶?쇱씤", "鍮꾪듃?쇱씤", "硫붾え由??", "?꾨줈洹몃옩 ?꾩븬", "硫붿씤 ?꾨줈?몄꽌",
    "?섏씠吏 踰꾪띁", "?쇱떛 ?곗씠??, "?쇱떛 ?꾨쪟", "鍮꾧탳 ?뚮줈", "?쒖뼱 ?좏샇",
    "湲곗? ?꾨쪟", "臾쇰━ ?꾩븬", "寃利??숈옉", "?꾨줈洹몃옩 ?꾩뒪", "?좏깮 ?뚮뱶?쇱씤",
    "???곌껐??, "瑜??쒖뼱?섎뒗", "瑜???ν븯??, "? 鍮꾧탳?섎뒗", "???ы븿?섍퀬",
    "?곴린", "蹂듭닔??, "諛?, "?먮뒗", "?섎룄濡?援ъ꽦??, "瑜?媛먯??섎뒗",
]


def _random_cited_text(seed: int) -> str:
    rng = random.Random(seed)
    target_len = rng.randint(CITED_TEXT_MIN_LEN, CITED_TEXT_MAX_LEN)
    for _ in range(20):
        text = ""
        while len(text) < target_len:
            text += rng.choice(CITED_TEXT_CHUNKS)
        text = text[:target_len]
        if CITED_TEXT_MIN_LEN <= len(text) < 50:
            return text
    sample = rng.choice(CITED_CONTENT_SAMPLES)
    return sample[:CITED_TEXT_MAX_LEN]

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
  color: inherit;
  font: inherit;
  appearance: none;
  -webkit-appearance: none;
}
.mypage-modal-backdrop {
  position: absolute;
  inset: 0;
  z-index: 199;
  display: none;
  background: rgba(33, 43, 54, .48);
  pointer-events: none;
}
#mypage-toggle:checked ~ .mypage-modal-backdrop,
.patent-app:has(#mypage-toggle:checked) .mypage-modal-backdrop,
.mypage-modal-backdrop.is-open {
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
#mypage-toggle:checked ~ .mypage-modal,
.patent-app:has(#mypage-toggle:checked) .mypage-modal,
.mypage-modal.is-open {
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
  padding: 0;
  appearance: none;
  -webkit-appearance: none;
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
  font-size: 12px;
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
  font-size: 12px;
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
  width: __MYPAGE_COMPONENT_COL_WIDTH__px;
  min-width: __MYPAGE_COMPONENT_COL_WIDTH__px;
  max-width: __MYPAGE_COMPONENT_COL_WIDTH__px;
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
  font-size: 12px;
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
  font-size: 12px;
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
  font-size: 12px;
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
  font-size: 12px;
  font-weight: 700;
}
.mp-compare-body {
  flex: 1;
  padding: 8px 10px;
  color: #5d6978;
  line-height: 1.45;
  font-size: 12px;
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
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
}
.mp-compare-ref {
  color: #9aa3ad;
  font-size: 12px;
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
  font-size: 12px;
}
""".replace("__MYPAGE_COMPONENT_COL_WIDTH__", str(MYPAGE_COMPONENT_COL_WIDTH))


def _compare_cell(status: str, ref: str, seed: int) -> str:
    if status == "none":
        return (
            '<td class="mp-compare-cell mp-compare-none">'
            "<span>??λ맂 ???援ъ꽦?붿냼 ?놁쓬</span></td>"
        )
    status_map = {
        "same": ("?숈씪", "mp-status-same"),
        "partial": ("?쇰? 李⑥씠", "mp-status-partial"),
        "diff": ("李⑥씠", "mp-status-diff"),
    }
    label, cls = status_map[status]
    cited_text = html.escape(_random_cited_text(seed))
    return (
        f'<td class="mp-compare-cell {cls}">'
        f'<div class="mp-compare-card">'
        f'<div class="mp-status-strip">{label}</div>'
        f'<div class="mp-compare-body">{cited_text}</div>'
        f'<div class="mp-compare-foot">'
        f'<span class="mp-compare-link">???鍮꾧껐怨?蹂닿린</span>'
        f'<span class="mp-compare-ref">{ref}</span>'
        f"</div></div></td>"
    )


def _build_cited_headers() -> str:
    headers = []
    for doc_no in MYPAGE_CITED_DOCS:
        headers.append(
            f'<th class="mp-cited-col">'
            f'<div class="mp-cited-top">'
            f'<span class="mp-cited-label">?몄슜諛쒕챸 異쒖썝踰덊샇</span>'
            f'<div class="mp-col-controls">'
            f'<span class="mp-col-btn" title="?쇱そ?쇰줈">??/span>'
            f'<span class="mp-col-btn" title="?ㅻⅨ履쎌쑝濡?>??/span>'
            f'<span class="mp-col-btn mp-col-drag" title="?쒖꽌 蹂寃?>??떘</span>'
            f'<span class="mp-col-btn mp-col-del" title="??젣">횞</span>'
            f"</div></div>"
            f'<div class="mp-cited-no">{doc_no}</div>'
            f"</th>"
        )
    return "".join(headers)


def _cells_for_row(row_index: int) -> list[tuple[str, str]]:
    return MYPAGE_CELL_PATTERNS[(row_index - 1) % len(MYPAGE_CELL_PATTERNS)]


def _build_table_body(component_items: list[str]) -> str:
    rows = []
    for index, text in enumerate(component_items, start=1):
        cells = "".join(
            _compare_cell(status, ref, seed=index * 100 + cell_index)
            for cell_index, (status, ref) in enumerate(_cells_for_row(index), start=1)
        )
        rows.append(
            f'<tr class="mp-component-row">'
            f'<td class="mp-component-cell">'
            f'<label class="mp-row-check"><input type="checkbox"></label>'
            f'<div class="mp-component-body">'
            f'<span class="mp-component-badge">援ъ꽦?붿냼 {index}</span>'
            f'<p class="mp-component-text">{html.escape(text)}</p>'
            f"</div></td>{cells}</tr>"
        )
    return "".join(rows)


MYPAGE_MODAL_HTML_TEMPLATE = """
<div class="mypage-modal-backdrop" aria-hidden="true"></div>
<section class="mypage-modal">
  <header class="mp-modal-header">
    <div class="mp-title-wrap">
      <span class="mp-title-icon">??/span>
      <div class="mp-title-text">
        <span class="mp-title">李몄쬆 ???/span>
        <span class="mp-subtitle">?섎쭔??李몄“ ??μ냼</span>
      </div>
    </div>
    <div class="mp-header-controls">
      <div class="mp-view-toggle">
        <span class="mp-view-opt">臾명뿄蹂?蹂닿린</span>
        <span class="mp-view-opt active">?뚯씠釉?蹂닿린</span>
      </div>
      <div class="mp-app-select">
        <span class="mp-app-select-label">異쒖썝踰덊샇 ?좏깮 :</span>
        <span class="mp-app-select-value">__MYPAGE_APP_NO__</span>
      </div>
      <button type="button" class="mp-close" aria-label="?リ린">횞</button>
    </div>
  </header>
  <div class="mp-info-bar">
    <div class="mp-info-left">
      <span class="mp-info-badge">異쒖썝踰덊샇</span>
      <span class="mp-info-app-no">__MYPAGE_APP_NO__</span>
    </div>
    <div class="mp-info-right">??λ맂 ?몄슜臾명뿄 __MYPAGE_CITED_COUNT__媛?/div>
  </div>
  <div class="mp-content">
    <div class="mp-section-head">
      <div class="mp-section-title">湲곗닠 援ъ꽦?붿냼蹂??몄슜臾명뿄 援ъ꽦?붿냼 鍮꾧탳</div>
      <div class="mp-section-hint">
        泥?踰덉㎏ ?댁? 怨좎젙?섍퀬, ?섎㉧吏 ?댁? 媛濡??ㅽ겕濡ㅻ맗?덈떎.
        ???ㅻ뜑???붿궡???먮뒗 ?쒕옒洹몃줈 ???쒖꽌瑜?蹂寃쏀븯怨???젣?????덉뒿?덈떎.
      </div>
    </div>
    <div class="mp-table-wrap">
      <table class="mp-compare-table">
        <thead>
          <tr>
            <th class="mp-component-head">
              <label class="mp-row-check"><input type="checkbox"></label>
              <span>異쒖썝諛쒕챸 援ъ꽦?붿냼</span>
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


def get_mypage_modal_html(component_items: list[str]) -> str:
    return (
        MYPAGE_MODAL_HTML_TEMPLATE.replace("__MYPAGE_APP_NO__", MYPAGE_APP_NO)
        .replace("__MYPAGE_CITED_COUNT__", str(len(MYPAGE_CITED_DOCS)))
        .replace("__MYPAGE_CITED_HEADERS__", _build_cited_headers())
        .replace("__MYPAGE_TABLE_BODY__", _build_table_body(component_items))
    )
