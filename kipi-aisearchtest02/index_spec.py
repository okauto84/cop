"""검색 결과 행에서 여는 특허 상세 팝업 UI."""

import base64
from pathlib import Path

REGISTRATION_PDF_PATH = Path(__file__).parent / "data" / "1020180011648B1.pdf"
DRAWING_PATH = Path(__file__).parent / "data" / "drawing.JPG"

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
  grid-template-columns: 96px minmax(0, 1fr) minmax(0, 1fr);
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
.spec-page.spec-pdf-view {
  padding: 10px 12px;
  overflow-y: auto;
  font-family: "Noto Sans KR", "Malgun Gothic", sans-serif;
  background: #e8eaed;
}
.spec-pdf-page {
  display: block;
  width: 100%;
  max-width: 100%;
  margin: 0 auto 10px;
  background: #fff;
  box-shadow: 0 1px 4px rgba(34, 46, 58, .14);
}
.spec-pdf-fallback {
  height: 100%;
  display: grid;
  place-items: center;
  padding: 24px;
  color: #697582;
  text-align: center;
  line-height: 1.6;
}
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
  height: auto;
  min-height: 117px;
  margin: 7px;
  display: grid;
  place-items: center;
  color: #a0a8b0;
  background: #f4f5f7;
  border: 1px solid #eef1f4;
  border-radius: 4px;
  overflow: hidden;
}
.spec-drawing img {
  display: block;
  width: 100%;
  height: auto;
  object-fit: contain;
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
  display: flex;
  flex-direction: column;
}
.spec-components-head {
  height: 30px;
  flex: 0 0 30px;
  display: flex;
  align-items: center;
  padding: 0 8px;
  border-bottom: 1px solid #e4e8ed;
  font-weight: 700;
}
.spec-components-head span {
  margin-left: auto;
  padding: 4px 8px;
  color: #fff;
  background: #16a980;
  border-radius: 3px;
  font-size: 9px;
  font-weight: 600;
}
.spec-compare-table {
  min-height: 0;
  flex: 1;
  overflow-y: auto;
}
.spec-compare-columns {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
  gap: 0;
  padding: 8px 8px 4px;
  color: #4f5b67;
  font-weight: 700;
  border-bottom: 1px solid #e7ebef;
}
.spec-compare-col-title {
  display: flex;
  align-items: center;
  gap: 6px;
}
.spec-compare-col-title input[type="checkbox"] {
  width: 11px;
  height: 11px;
  margin: 0;
  accent-color: #2878ef;
}
.spec-compare-row {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
  gap: 8px;
  padding: 8px;
  border-bottom: 1px solid #e7ebef;
}
.spec-compare-row:last-child { border-bottom: 0; }
.spec-applied {
  display: grid;
  grid-template-columns: 14px 1fr;
  gap: 6px;
  align-items: start;
}
.spec-applied input[type="checkbox"] {
  width: 11px;
  height: 11px;
  margin-top: 2px;
  accent-color: #2878ef;
}
.spec-applied-badge {
  display: inline-block;
  margin-bottom: 6px;
  padding: 2px 7px;
  color: #7055cf;
  background: #f3efff;
  border: 1px solid #d8ccf8;
  border-radius: 3px;
  font-weight: 700;
}
.spec-applied-text { color: #4e5964; line-height: 1.45; }
.spec-compare-card {
  min-height: 118px;
  display: flex;
  flex-direction: column;
  border: 1px solid;
  border-radius: 6px;
  overflow: hidden;
  line-height: 1.45;
}
.spec-compare-card.same { border-color: #9cdec8; }
.spec-compare-card.partial { border-color: #e8d27a; }
.spec-compare-card.diff { border-color: #efb8b8; }
.spec-compare-card.substantial { border-color: #9ec5ef; }
.spec-compare-card-head {
  height: 28px;
  display: grid;
  grid-template-columns: 1fr 1fr;
  align-items: center;
  padding: 0 8px;
  font-weight: 700;
}
.spec-compare-card.same .spec-compare-card-head { color: #149b72; background: #effcf7; }
.spec-compare-card.partial .spec-compare-card-head { color: #b88900; background: #fff9e8; }
.spec-compare-card.diff .spec-compare-card-head { color: #d04a4a; background: #fff5f5; }
.spec-compare-card.substantial .spec-compare-card-head { color: #2d73dc; background: #eef5ff; }
.spec-status-wrap { display: flex; align-items: center; gap: 5px; }
.spec-status-tag {
  padding: 1px 5px;
  border: 1px solid;
  border-radius: 3px;
  font-size: 8px;
  font-weight: 600;
}
.spec-status-tag.doc { color: #2d73dc; background: #f3f8ff; border-color: #b8d4f5; }
.spec-status-tag.sentence { color: #149b72; background: #f5fffb; border-color: #b8e8d5; }
.spec-compare-card-head .result-label { text-align: right; color: #4f5b67; }
.spec-compare-card-body {
  flex: 1;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  padding: 8px;
  color: #697582;
  font-size: 9px;
}
.spec-compare-card-foot {
  display: flex;
  justify-content: flex-end;
  padding: 0 8px 8px;
}
.spec-source-btn {
  padding: 4px 8px;
  color: #4f5b67;
  background: #fff;
  border: 1px solid #d9e1e9;
  border-radius: 4px;
  font-size: 9px;
}
"""

SPEC_MODAL_HTML_TEMPLATE = """
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
    <div class="spec-page-wrap"><div class="spec-page spec-pdf-view">__SPEC_PDF_VIEW__</div></div>
  </main>
  <aside class="spec-right">
    <div class="spec-result-head"><span class="spec-ai-badge">⚡ AI 분석</span><span class="spec-result-title">이송 핸들러 및 마찰패드를 이용한 기판 처리장치</span></div>
    <div class="spec-right-tabs"><div class="spec-right-tab active">분석</div><div class="spec-right-tab">무효성 분석개요</div></div>
    <div class="spec-summary-row">
      <div class="spec-panel"><div class="spec-panel-title">▧ 도면</div><div class="spec-drawing">__SPEC_DRAWING_VIEW__</div></div>
      <div class="spec-panel"><div class="spec-panel-title">⚡ AI 요약</div><div class="spec-ai-summary">
        <div class="spec-ai-box red"><strong>해결과제 및 목적</strong><span>기존 방식의 처리장치에서 발생하는 웨이퍼 파손과 공정 불안정 문제를 해결합니다.</span></div>
        <div class="spec-ai-box green"><strong>발명의 효과</strong><span>처리 안정성을 높이고 기판의 오염과 손상을 감소시킵니다.</span></div>
      </div></div>
    </div>
    <div class="spec-components">
      <div class="spec-components-head">▣ 구성요소 대비표 <span>선택 구성요소 저장</span></div>
      <div class="spec-compare-table">
        <div class="spec-compare-columns">
          <div class="spec-compare-col-title"><input type="checkbox" checked>출원발명 구성요소</div>
          <div>인용발명 구성요소</div>
        </div>
        <div class="spec-compare-row">
          <div class="spec-applied"><input type="checkbox" checked><div><span class="spec-applied-badge">구성요소 1</span><div class="spec-applied-text">워드라인 및 비트라인들에 연결된 메모리 셀들</div></div></div>
          <div class="spec-compare-card same">
            <div class="spec-compare-card-head"><div class="spec-status-wrap"><span>동일</span></div><div class="result-label">대비결과</div></div>
            <div class="spec-compare-card-body"><div>(LLM이 추출한 인용문헌 대응 내용 예시)</div><div>출원발명의 구성요소와 인용발명의 대응 관계에 대한 분석 결과입니다.</div></div>
            <div class="spec-compare-card-foot"><span class="spec-source-btn">⌕ 원문 위치 확인</span></div>
          </div>
        </div>
        <div class="spec-compare-row">
          <div class="spec-applied"><input type="checkbox" checked><div><span class="spec-applied-badge">구성요소 2</span><div class="spec-applied-text">상기 워드라인 및 상기 비트라인들에 인가되는 프로그램 관련 전압들을 제어하는 메인 프로세서</div></div></div>
          <div class="spec-compare-card partial">
            <div class="spec-compare-card-head"><div class="spec-status-wrap"><span>일부 차이</span><span class="spec-status-tag doc">문헌</span><span class="spec-status-tag sentence">문장</span></div><div class="result-label">대비결과</div></div>
            <div class="spec-compare-card-body"><div>(LLM이 추출한 인용문헌 대응 내용 예시)</div><div>출원발명의 구성요소와 인용발명의 대응 관계에 대한 분석 결과입니다.</div></div>
            <div class="spec-compare-card-foot"><span class="spec-source-btn">⌕ 원문 위치 확인</span></div>
          </div>
        </div>
        <div class="spec-compare-row">
          <div class="spec-applied"><input type="checkbox" checked><div><span class="spec-applied-badge">구성요소 3</span><div class="spec-applied-text">상기 메모리 셀들의 문턱 전압을 기초로 센싱된 데이터를 저장하는 페이지 버퍼</div></div></div>
          <div class="spec-compare-card diff">
            <div class="spec-compare-card-head"><div class="spec-status-wrap"><span>차이</span><span class="spec-status-tag doc">문헌</span><span class="spec-status-tag sentence">문장</span></div><div class="result-label">대비결과</div></div>
            <div class="spec-compare-card-body"><div>(LLM이 추출한 인용문헌 대응 내용 예시)</div><div>출원발명의 구성요소와 인용발명의 대응 관계에 대한 분석 결과입니다.</div></div>
          </div>
        </div>
        <div class="spec-compare-row">
          <div class="spec-applied"><input type="checkbox" checked><div><span class="spec-applied-badge">구성요소 4</span><div class="spec-applied-text">상기 센싱된 데이터에 대응되는 센싱 전류와 기준 전류를 비교하는 패스 페일 체크 동작을 수행하는 센싱 회로</div></div></div>
          <div class="spec-compare-card substantial">
            <div class="spec-compare-card-head"><div class="spec-status-wrap"><span>실질적 동일</span></div><div class="result-label">대비결과</div></div>
            <div class="spec-compare-card-body"><div>(LLM이 추출한 인용문헌 대응 내용 예시)</div><div>출원발명의 구성요소와 인용발명의 대응 관계에 대한 분석 결과입니다.</div></div>
            <div class="spec-compare-card-foot"><span class="spec-source-btn">⌕ 원문 위치 확인</span></div>
          </div>
        </div>
      </div>
    </div>
  </aside>
</section>
"""


def build_registration_pdf_view(pdf_path: Path = REGISTRATION_PDF_PATH, zoom: float = 1.1) -> str:
    """등록공보 PDF를 페이지 이미지로 렌더링해 HTML 조각으로 반환."""
    if not pdf_path.is_file():
        return (
            f'<div class="spec-pdf-fallback">PDF 파일을 찾을 수 없습니다.<br>{pdf_path.name}</div>'
        )

    try:
        import fitz  # PyMuPDF
    except ImportError:
        return (
            '<div class="spec-pdf-fallback">'
            "PyMuPDF가 설치되지 않았습니다.<br>"
            "<code>pip install pymupdf</code> 후 다시 실행해 주세요."
            "</div>"
        )

    pages: list[str] = []
    matrix = fitz.Matrix(zoom, zoom)
    doc = fitz.open(str(pdf_path))
    try:
        for page_index in range(len(doc)):
            pixmap = doc.load_page(page_index).get_pixmap(matrix=matrix, alpha=False)
            image_b64 = base64.standard_b64encode(pixmap.tobytes("png")).decode("ascii")
            page_no = page_index + 1
            pages.append(
                f'<img class="spec-pdf-page" src="data:image/png;base64,{image_b64}" alt="등록공보 {page_no}페이지">'
            )
    finally:
        doc.close()

    if not pages:
        return '<div class="spec-pdf-fallback">PDF 페이지를 불러올 수 없습니다.</div>'
    return "".join(pages)


def build_drawing_view(drawing_path: Path = DRAWING_PATH) -> str:
    """대표도면 이미지를 HTML 조각으로 반환."""
    if not drawing_path.is_file():
        return f"이미지를 찾을 수 없음<br>{drawing_path.name}"

    suffix = drawing_path.suffix.lower().lstrip(".")
    mime = "jpeg" if suffix in {"jpg", "jpeg"} else suffix
    image_b64 = base64.standard_b64encode(drawing_path.read_bytes()).decode("ascii")
    return (
        f'<img src="data:image/{mime};base64,{image_b64}" alt="대표도면">'
    )


def get_spec_modal_html() -> str:
    pdf_view = build_registration_pdf_view()
    drawing_view = build_drawing_view()
    return (
        SPEC_MODAL_HTML_TEMPLATE.replace("__SPEC_PDF_VIEW__", pdf_view)
        .replace("__SPEC_DRAWING_VIEW__", drawing_view)
    )


SPEC_MODAL_HTML = get_spec_modal_html()
