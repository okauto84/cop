"""Всплывающий интерфейс подробностей патента, открываемый из строки результатов поиска."""

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
.spec-modal-backdrop {
  position: absolute;
  inset: 0;
  z-index: 199;
  display: none;
  background: rgba(33, 43, 54, .48);
  pointer-events: none;
}
#spec-modal-toggle:checked ~ .spec-modal-backdrop {
  display: block;
  animation: backdrop-fade-in .18s ease-out;
}
.spec-modal {
  position: absolute;
  top: 36px;
  right: 48px;
  bottom: 36px;
  left: 48px;
  z-index: 200;
  display: none;
  grid-template-columns: 96px minmax(0, 1fr) minmax(0, 1fr);
  grid-template-rows: 47px minmax(0, 1fr);
  color: #34404c;
  background: #f7f8fa;
  border: 1px solid #dfe5ec;
  border-radius: 10px;
  box-shadow: 0 10px 36px rgba(23, 36, 50, .14);
  overflow: hidden;
  --fs-body: 12px;
  --fs-caption: 12px;
  --fs-label: 13px;
  --fs-subtitle: 14px;
  --fs-title: 15px;
  --fs-display: 18px;
  font-size: var(--fs-body);
}
#spec-modal-toggle:checked ~ .spec-modal {
  display: grid;
  animation: modal-fade-in .18s ease-out;
}
.spec-top {
  grid-column: 1 / -1;
  display: flex;
  align-items: center;
  padding: 0 10px;
  background: #fff;
  border-bottom: 1px solid #dfe4e9;
}
.spec-number { width: 96px; color: #26313c; font-size: var(--fs-label); font-weight: 700; }
.spec-search {
  width: 200px;
  height: 25px;
  display: flex;
  align-items: center;
  padding: 0 8px;
  color: #929ca6;
  font-size: var(--fs-body);
  border: 1px solid #dce2e8;
  border-radius: 4px;
}
.spec-zoom {
  margin-left: auto;
  padding: 6px 10px;
  color: #53606c;
  font-size: var(--fs-body);
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
  font-size: var(--fs-display);
}
.spec-nav {
  grid-column: 1;
  grid-row: 2;
  padding: 12px 10px;
  background: #fafbfc;
  border-right: 1px solid #e2e7ec;
}
.spec-nav-title { margin-bottom: 18px; color: #36424e; font-size: var(--fs-subtitle); font-weight: 700; }
.spec-nav-item { margin: 0 -10px; padding: 7px 12px; color: #68747f; font-size: var(--fs-body); }
.spec-nav-item.active { color: #2874dc; background: #edf5ff; font-weight: 700; }
.spec-nav-group { margin-top: 12px; color: #3f4b57; font-size: var(--fs-label); font-weight: 700; }
.spec-nav-child { padding: 5px 10px; color: #7a8590; font-size: var(--fs-body); font-weight: 400; }
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
.spec-doc-tab { height: 28px; padding-top: 8px; color: #697580; font-size: var(--fs-label); }
.spec-doc-tab.active { color: #2874dc; border-bottom: 2px solid #2874dc; font-weight: 700; }
.spec-page-wrap { min-height: 0; flex: 1; padding: 8px 13px; overflow: hidden; }
.spec-page {
  height: 100%;
  padding: 18px 46px;
  background: #fff;
  box-shadow: 0 1px 4px rgba(34, 46, 58, .14);
  overflow: hidden;
  font-family: "Noto Serif", "Times New Roman", serif;
  color: #171717;
  font-size: var(--fs-body);
  line-height: 1.62;
}
.spec-page.spec-pdf-view {
  padding: 10px 12px;
  overflow-y: auto;
  scroll-behavior: smooth;
  font-family: "Noto Sans", "Segoe UI", sans-serif;
  background: #e8eaed;
}
.spec-pdf-page-wrap {
  position: relative;
  width: 100%;
  margin: 0 auto 10px;
  background: #fff;
  box-shadow: 0 1px 4px rgba(34, 46, 58, .14);
  overflow: hidden;
}
.spec-pdf-page-wrap img.spec-pdf-bg {
  display: block;
  width: 100%;
  height: auto;
  pointer-events: none;
  user-select: none;
}
.spec-pdf-text-layer {
  position: absolute;
  inset: 0;
  z-index: 2;
}
.spec-pdf-text {
  position: absolute;
  margin: 0;
  padding: 0;
  color: rgba(0, 0, 0, .01);
  background: transparent;
  white-space: pre;
  line-height: 1;
  user-select: text;
  cursor: text;
}
.spec-pdf-text::selection {
  color: #1d2733;
  background: rgba(66, 133, 244, .35);
}
.spec-pdf-highlight {
  position: absolute;
  z-index: 3;
  margin: 0;
  padding: 0;
  border: 2px solid transparent;
  border-radius: 2px;
  background: transparent;
  scroll-margin-top: 72px;
  pointer-events: none;
}
.spec-pdf-highlight:target {
  background: rgba(255, 230, 0, .48);
  border-color: #ffc400;
  box-shadow: 0 0 0 4px rgba(255, 196, 0, .22);
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
.spec-ai-badge { padding: 4px 8px; color: #fff; background: #7545e8; border-radius: 3px; font-size: var(--fs-caption); font-weight: 700; }
.spec-result-title { margin-left: 7px; color: #26313c; font-size: var(--fs-subtitle); font-weight: 700; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.spec-summary-row {
  height: 291px;
  flex: 0 0 291px;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 7px;
  padding: 8px;
}
.spec-panel {
  min-width: 0;
  min-height: 0;
  display: flex;
  flex-direction: column;
  background: #fff;
  border: 1px solid #e0e5ea;
  border-radius: 6px;
  overflow: hidden;
}
.spec-panel-title {
  height: 27px;
  flex: 0 0 27px;
  padding: 7px 9px;
  font-size: var(--fs-subtitle);
  font-weight: 700;
  border-bottom: 1px solid #edf0f3;
}
.spec-drawing {
  flex: 1;
  min-height: 0;
  margin: 7px;
  display: grid;
  place-items: center;
  color: #a0a8b0;
  background: #f4f5f7;
  border: 1px solid #eef1f4;
  border-radius: 4px;
  overflow: auto;
}
.spec-drawing img {
  display: block;
  width: 100%;
  height: auto;
  object-fit: contain;
}
.spec-ai-summary {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  padding: 7px;
}
.spec-ai-box { margin-bottom: 6px; padding: 7px; border: 1px solid; border-radius: 4px; line-height: 1.45; font-size: var(--fs-body); }
.spec-ai-box strong { display: block; margin-bottom: 3px; font-size: var(--fs-label); }
.spec-ai-box.red { color: #c3453e; background: #fffafa; border-color: #efd5d2; }
.spec-ai-box.red span, .spec-ai-box.green span, .spec-ai-box.blue span { color: #4e5964; }
.spec-ai-box.green { color: #149b72; background: #f5fffb; border-color: #c8ebdf; }
.spec-ai-box.blue { color: #3978c8; background: #f7faff; border-color: #d6e2f4; }
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
  font-size: var(--fs-subtitle);
  font-weight: 700;
}
.spec-components-actions {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 6px;
}
.spec-components-actions .spec-btn {
  padding: 4px 8px;
  border-radius: 3px;
  font-size: var(--fs-caption);
  font-weight: 600;
  cursor: pointer;
  white-space: nowrap;
}
.spec-btn-research {
  color: #fff;
  background: #2c6fc9;
}
.spec-btn-save {
  color: #fff;
  background: #16a980;
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
  font-size: var(--fs-label);
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
  font-size: var(--fs-label);
  font-weight: 700;
}
.spec-applied-text { color: #4e5964; font-size: var(--fs-body); line-height: 1.45; }
.spec-compare-card {
  min-height: 118px;
  display: flex;
  flex-direction: column;
  border: 1px solid #dce3ea;
  border-radius: 6px;
  overflow: hidden;
  line-height: 1.45;
  background: #fff;
}
.spec-compare-card.same { border-color: #9cdec8; }
.spec-compare-card.partial { border-color: #e8d27a; }
.spec-compare-card.diff { border-color: #efb8b8; }
.spec-compare-card.substantial { border-color: #9ec5ef; }
.spec-compare-card-head {
  height: 28px;
  flex: 0 0 28px;
  display: grid;
  grid-template-columns: 1fr 1fr;
  align-items: center;
  font-size: var(--fs-label);
  font-weight: 700;
  border-bottom: 1px solid #e7ebef;
}
.spec-compare-card-head > * {
  display: flex;
  align-items: center;
  height: 100%;
  padding: 0 10px;
}
.spec-compare-card-head > *:first-child {
  border-right: 1px solid #e7ebef;
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
  font-size: var(--fs-caption);
  font-weight: 600;
}
.spec-status-tag.doc { color: #2d73dc; background: #f3f8ff; border-color: #b8d4f5; }
.spec-status-tag.sentence { color: #149b72; background: #f5fffb; border-color: #b8e8d5; }
.spec-compare-card-head .result-label { color: inherit; }
.spec-compare-card-body {
  flex: 1;
  min-height: 0;
  display: grid;
  grid-template-columns: 1fr 1fr;
  color: #4e5964;
  font-size: var(--fs-body);
}
.spec-compare-cited {
  padding: 10px;
  border-right: 1px solid #e7ebef;
  color: #697582;
}
.spec-compare-result {
  min-height: 0;
  display: flex;
  flex-direction: column;
}
.spec-compare-result-text {
  flex: 1;
  padding: 10px;
  color: #697582;
}
.spec-compare-card-foot {
  display: flex;
  justify-content: flex-end;
  padding: 8px 10px;
  border-top: 1px solid #eef1f4;
}
.spec-source-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  color: #2874dc;
  background: #fff;
  border: 1px solid #d9e1e9;
  border-radius: 4px;
  font-size: var(--fs-caption);
  font-weight: 600;
  text-decoration: none;
  cursor: pointer;
}
.spec-source-btn:hover { color: #1a5fbe; border-color: #93bbf1; background: #f3f8ff; }
"""

SPEC_MODAL_HTML_TEMPLATE = """
<div class="spec-modal-backdrop" aria-hidden="true"></div>
<section class="spec-modal">
  <header class="spec-top">
    <div class="spec-number">1020180133661</div>
    <div class="spec-search">⌕ Поиск слова в документе...</div>
    <div class="spec-zoom">− &nbsp; 100% &nbsp; ＋</div>
    <label for="spec-modal-toggle" class="spec-close">×</label>
  </header>
  <nav class="spec-nav">
    <div class="spec-nav-title">☰ Оглавление</div>
    <div class="spec-nav-item">Библиография</div>
    <div class="spec-nav-item">Реферат</div>
    <div class="spec-nav-item">Описание</div>
    <div class="spec-nav-group">Формула изобретения　⌃</div>
    <div class="spec-nav-child">Пункт 1</div><div class="spec-nav-child">Пункт 2</div>
    <div class="spec-nav-child">Пункт 3</div><div class="spec-nav-child">Пункт 4</div>
    <div class="spec-nav-child">Пункт 5</div><div class="spec-nav-child">Пункт 6</div>
    <div class="spec-nav-child">Пункт 7</div><div class="spec-nav-child">Пункт 8</div>
    <div class="spec-nav-child">Пункт 9</div><div class="spec-nav-child">Пункт 10</div>
    <div class="spec-nav-group">Описание чертежей　⌃</div>
    <div class="spec-nav-child active">Основной чертёж</div><div class="spec-nav-child">Чертёж 1</div>
    <div class="spec-nav-child">Чертёж 2</div><div class="spec-nav-child">Чертёж 3</div>
  </nav>
  <main class="spec-document">
    <div class="spec-doc-tabs"><div class="spec-doc-tab">Полный текст публикации</div><div class="spec-doc-tab active">Охранный документ</div></div>
    <div class="spec-page-wrap"><div class="spec-page spec-pdf-view">__SPEC_PDF_VIEW__</div></div>
  </main>
  <aside class="spec-right">
    <div class="spec-result-head"><span class="spec-ai-badge">⚡ Анализ ИИ</span><span class="spec-result-title">Устройство обработки подложек с транспортным манипулятором и фрикционными прокладками</span></div>
    <div class="spec-summary-row">
      <div class="spec-panel"><div class="spec-panel-title">▧ Чертёж</div><div class="spec-drawing">__SPEC_DRAWING_VIEW__</div></div>
      <div class="spec-panel"><div class="spec-panel-title">⚡ Реферат ИИ</div><div class="spec-ai-summary">
        <div class="spec-ai-box red"><strong>Решаемая задача и цель</strong><span>Предоставление корпуса электронного устройства, в котором пассивные элементы и схемы управления питанием эффективно интегрированы в структуру на основе интерпозера, что позволяет уменьшить площадь монтажа корпуса и одновременно повысить стабильность электропитания и производительность системы</span></div>
        <div class="spec-ai-box green"><strong>Эффект изобретения</strong><span>Интерпозер размещается над подложкой корпуса; на интерпозере монтируются процессорный элемент, элемент памяти с высокой пропускной способностью и интегральная схема управления питанием; пассивные элементы, такие как индукторы и конденсаторы, формируются внутри или на поверхности интерпозера.</span></div>
        <div class="spec-ai-box blue"><strong>Средство решения</strong><span>Интеграция пассивных элементов и схем управления питанием внутри интерпозера позволяет уменьшить площадь монтажа на подложке корпуса и обеспечить стабильное электропитание процессорного элемента и памяти с высокой пропускной способностью, повышая производительность и энергоэффективность всей электронной системы</span></div>
      </div></div>
    </div>
    <div class="spec-components">
      <div class="spec-components-head">▣ Таблица сравнения элементов <div class="spec-components-actions"><span class="spec-btn spec-btn-research">⌕ Повторный поиск выбранных элементов</span><span class="spec-btn spec-btn-save">Сохранить выбранные элементы</span></div></div>
      <div class="spec-compare-table">
        <div class="spec-compare-columns">
          <div class="spec-compare-col-title"><input type="checkbox" checked>Элементы заявленного изобретения</div>
          <div>Элементы цитируемого изобретения</div>
        </div>
        <div class="spec-compare-row">
          <div class="spec-applied"><input type="checkbox" checked><div><span class="spec-applied-badge">Элемент 1</span><div class="spec-applied-text">Массив ячеек флэш-памяти, соединённый с множеством линий слов и битовых линий в перекрёстной схеме, при этом каждая ячейка памяти электрически соединена с соответствующей битовой линией через транзистор выбора</div></div></div>
          <div class="spec-compare-card same">
            <div class="spec-compare-card-head"><div class="spec-status-wrap"><span>Идентично</span></div><div class="result-label">Результат сравнения</div></div>
            <div class="spec-compare-card-body">
              <div class="spec-compare-cited">(Пример соответствующего содержания цитируемого документа, извлечённого LLM)</div>
              <div class="spec-compare-result">
                <div class="spec-compare-result-text">Результат анализа соответствия элементов заявленного изобретения и цитируемого изобретения.</div>
                <div class="spec-compare-card-foot"><a href="#spec-highlight-source" class="spec-source-btn">⌕ Проверить место в оригинале</a></div>
              </div>
            </div>
          </div>
        </div>
        <div class="spec-compare-row">
          <div class="spec-applied"><input type="checkbox" checked><div><span class="spec-applied-badge">Элемент 2</span><div class="spec-applied-text">Основной процессор, ступенчато регулирующий амплитуду и длительность программного напряжения, подаваемого на линию слов при операции программирования, и управляющий таймингом операции проверки прохождения/отказа</div></div></div>
          <div class="spec-compare-card partial">
            <div class="spec-compare-card-head"><div class="spec-status-wrap"><span>Частичное отличие</span></div><div class="result-label">Результат сравнения</div></div>
            <div class="spec-compare-card-body">
              <div class="spec-compare-cited">В документе указано, что контроллер управляет программным напряжением, однако проверка прохождения/отказа выполняется отдельным субпроцессором параллельно, что отличается от заявленного изобретения.</div>
              <div class="spec-compare-result">
                <div class="spec-compare-result-text">Сама функция управления напряжением соответствует, однако выявлены частичные различия в субъекте управления и способе управления таймингом. Таким образом, общая конструкция сходна, но детали реализации частично отличаются.</div>
                <div class="spec-compare-card-foot"><a href="#spec-highlight-source" class="spec-source-btn">⌕ Проверить место в оригинале</a></div>
              </div>
            </div>
          </div>
        </div>
        <div class="spec-compare-row">
          <div class="spec-applied"><input type="checkbox" checked><div><span class="spec-applied-badge">Элемент 3</span><div class="spec-applied-text">Схема буфера страницы, считывающая напряжение битовой линии при операции считывания, преобразующая его в цифровые данные и определяющая необходимость перепрограммирования по результату проверки программирования</div></div></div>
          <div class="spec-compare-card diff">
            <div class="spec-compare-card-head"><div class="spec-status-wrap"><span>Отличие</span></div><div class="result-label">Результат сравнения</div></div>
            <div class="spec-compare-card-body">
              <div class="spec-compare-cited">Указано лишь, что регистр данных временно сохраняет результат считывания; логика принятия решения о перепрограммировании по результату проверки программирования явно не раскрыта.</div>
              <div class="spec-compare-result">
                <div class="spec-compare-result-text">Связанная структура считывания и проверки буфера страницы не имеет прямого соответствия в цитируемом изобретении, поэтому техническая конструкция может считаться иной. Одна лишь функция хранения данных вряд ли позволяет считать элемент идентичным.</div>
                <div class="spec-compare-card-foot"><a href="#spec-highlight-source" class="spec-source-btn">⌕ Проверить место в оригинале</a></div>
              </div>
            </div>
          </div>
        </div>
        <div class="spec-compare-row">
          <div class="spec-applied"><input type="checkbox" checked><div><span class="spec-applied-badge">Элемент 4</span><div class="spec-applied-text">Схема считывания, сравнивающая ток считывания с опорным током при проверке прохождения/отказа для верификации распределения порогового напряжения ячеек памяти и регулирующая последующее программное напряжение в зависимости от числа отказавших ячеек</div></div></div>
          <div class="spec-compare-card substantial">
            <div class="spec-compare-card-head"><div class="spec-status-wrap"><span>По существу идентично</span></div><div class="result-label">Результат сравнения</div></div>
            <div class="spec-compare-card-body">
              <div class="spec-compare-cited">Указано, что схема считывания сравнивает ток битовой линии с опорным током для определения состояния ячейки, а последовательность повторной настройки программного напряжения при неудачной проверке сходна с заявленным изобретением.</div>
              <div class="spec-compare-result">
                <div class="spec-compare-result-text">Названия схемных узлов и способ настройки детальных параметров несколько различаются, однако технический эффект и средства считывания, сравнения и последующей регулировки напряжения анализируются как по существу идентичные.</div>
                <div class="spec-compare-card-foot"><a href="#spec-highlight-source" class="spec-source-btn">⌕ Проверить место в оригинале</a></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </aside>
</section>
"""


SOURCE_HIGHLIGHT_ID = "spec-highlight-source"
SOURCE_HIGHLIGHT_PHRASES = (
    "상기 트렌치들 사이에 정의되는 메사 영역의 상면으로 상기 제1 도전형의 고농도 바디 컨택 영역",
    "상기 트렌치들 사이에 정의되는메사 영역의 상면으로 상기 제1 도전형의 고농도 바디 컨택 영역",
    "상기 트렌치들 사이에 정의되는 메사 영역의 상면으로 상기 제1 도전형의 고농도 바디 컨택 영",
    "상기 트렌치들 사이에 정의되는 메사(mesa) 영역의 상면으로 상기 제1 도전형의 고농도 바디",
)


def _html_escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _bbox_to_style(x0: float, y0: float, x1: float, y1: float, pw: float, ph: float, pad: float = 1.0) -> str:
    left = max(0.0, x0 - pad) / pw * 100
    top = max(0.0, y0 - pad) / ph * 100
    width = min(pw, (x1 - x0) + pad * 2) / pw * 100
    height = min(ph, (y1 - y0) + pad * 2) / ph * 100
    return (
        f"left:{left:.4f}%;top:{top:.4f}%;width:{width:.4f}%;height:{height:.4f}%"
    )


def _find_source_highlight_rect(page):
    """Ищет координаты целевого предложения для проверки места в оригинале PDF."""
    import fitz

    for phrase in SOURCE_HIGHLIGHT_PHRASES:
        rects = page.search_for(phrase)
        if rects:
            return rects[0]

    prefix = "상기 트렌치들 사이에 정의되는 메사 영역의 상면으로 상기 제1 도전형의 고농도 바디 컨택 영"
    suffix = "역 및"
    prefix_rects = page.search_for(prefix)
    suffix_rects = page.search_for(suffix)
    if prefix_rects and suffix_rects:
        for pre in prefix_rects:
            for suf in suffix_rects:
                if abs(pre.y1 - suf.y0) < 8 and suf.x0 >= pre.x0 - 2:
                    return fitz.Rect(pre.x0, pre.y0, suf.x1, suf.y1)
    return None


def build_registration_pdf_view(pdf_path: Path = REGISTRATION_PDF_PATH, zoom: float = 1.1) -> str:
    """Рендерит PDF охранного документа как слои изображения и текста и возвращает HTML с возможностью выделения."""
    if not pdf_path.is_file():
        return (
            f'<div class="spec-pdf-fallback">Файл PDF не найден.<br>{pdf_path.name}</div>'
        )

    try:
        import fitz  # PyMuPDF
    except ImportError:
        return (
            '<div class="spec-pdf-fallback">'
            "PyMuPDF не установлен.<br>"
            "Установите <code>pip install pymupdf</code> и запустите снова."
            "</div>"
        )

    pages: list[str] = []
    matrix = fitz.Matrix(zoom, zoom)
    source_highlight_placed = False
    doc = fitz.open(str(pdf_path))
    try:
        for page_index in range(len(doc)):
            page = doc.load_page(page_index)
            pixmap = page.get_pixmap(matrix=matrix, alpha=False)
            pw, ph = float(pixmap.width), float(pixmap.height)
            page_rect = page.rect
            scale_x = pw / page_rect.width
            scale_y = ph / page_rect.height

            image_b64 = base64.standard_b64encode(pixmap.tobytes("png")).decode("ascii")
            text_spans: list[str] = []
            for block in page.get_text("dict")["blocks"]:
                if block.get("type") != 0:
                    continue
                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        text = span.get("text", "")
                        if not text.strip():
                            continue
                        x0, y0, x1, y1 = span["bbox"]
                        sx0, sy0, sx1, sy1 = (
                            x0 * scale_x,
                            y0 * scale_y,
                            x1 * scale_x,
                            y1 * scale_y,
                        )
                        font_px = max((sy1 - sy0) * 0.92, 12)
                        pos = _bbox_to_style(sx0, sy0, sx1, sy1, pw, ph, pad=0.2)
                        text_spans.append(
                            f'<span class="spec-pdf-text" style="{pos};font-size:{font_px:.2f}px">{_html_escape(text)}</span>'
                        )

            highlight_spans: list[str] = []
            if not source_highlight_placed:
                rect = _find_source_highlight_rect(page)
                if rect is not None:
                    source_highlight_placed = True
                    sx0, sy0, sx1, sy1 = (
                        rect.x0 * scale_x,
                        rect.y0 * scale_y,
                        rect.x1 * scale_x,
                        rect.y1 * scale_y,
                    )
                    pos = _bbox_to_style(sx0, sy0, sx1, sy1, pw, ph, pad=2.0)
                    highlight_spans.append(
                        f'<span class="spec-pdf-highlight" id="{SOURCE_HIGHLIGHT_ID}" tabindex="-1" style="{pos}"></span>'
                    )

            page_no = page_index + 1
            pages.append(
                '<div class="spec-pdf-page-wrap" id="spec-pdf-page-'
                f'{page_no}">'
                f'<img class="spec-pdf-bg" src="data:image/png;base64,{image_b64}" alt="Охранный документ, стр. {page_no}">'
                '<div class="spec-pdf-text-layer">'
                + "".join(text_spans)
                + "".join(highlight_spans)
                + "</div></div>"
            )
    finally:
        doc.close()

    if not pages:
        return '<div class="spec-pdf-fallback">Не удалось загрузить страницы PDF.</div>'
    return "".join(pages)


def build_drawing_view(drawing_path: Path = DRAWING_PATH) -> str:
    """Возвращает изображение основного чертежа как HTML-фрагмент."""
    if not drawing_path.is_file():
        return f"Изображение не найдено<br>{drawing_path.name}"

    suffix = drawing_path.suffix.lower().lstrip(".")
    mime = "jpeg" if suffix in {"jpg", "jpeg"} else suffix
    image_b64 = base64.standard_b64encode(drawing_path.read_bytes()).decode("ascii")
    return (
        f'<img src="data:image/{mime};base64,{image_b64}" alt="Основной чертёж">'
    )


def get_spec_modal_html() -> str:
    pdf_view = build_registration_pdf_view()
    drawing_view = build_drawing_view()
    return (
        SPEC_MODAL_HTML_TEMPLATE.replace("__SPEC_PDF_VIEW__", pdf_view)
        .replace("__SPEC_DRAWING_VIEW__", drawing_view)
    )


SPEC_MODAL_HTML = get_spec_modal_html()
