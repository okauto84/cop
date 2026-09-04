# -*- coding: utf-8 -*-
"""Макет экрана загрузки ИИ-поиска патентов."""

import base64
import html
import random
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components
from index_mypage import MYPAGE_MODAL_CSS, get_mypage_modal_html
from index_spec import SPEC_MODAL_CSS, get_spec_modal_html


st.set_page_config(
    page_title="Система ИИ-поиска патентов",
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
    {"no": 1, "state": "Опубликовано", "app_no": "1020180133661", "date": "20181102", "title": "Устройство памяти и система памяти, включающая его"},
    {"no": 2, "state": "Отклонено", "app_no": "1020140178426", "date": "20141211", "title": "Полупроводниковое устройство памяти и способ его работы"},
    {"no": 3, "state": "Опубликовано", "app_no": "1020200126702", "date": "20200929", "title": "Устройство памяти и способ его работы"},
    {"no": 4, "state": "Зарегистрировано", "app_no": "1020200098794", "date": "20200806", "title": "Устройство памяти"},
    {"no": 5, "state": "Опубликовано", "app_no": "1020200098765", "date": "20200806", "title": "Устройство памяти и способ его работы"},
    {"no": 6, "state": "Отозвано", "app_no": "1020220164302", "date": "20221130", "title": "Буфер страницы, устройство памяти, включающее буфер страницы, и система памяти, включающая устройство памяти"},
    {"no": 7, "state": "Опубликовано", "app_no": "1020150172401", "date": "20151204", "title": "Устройство памяти и способ его работы"},
    {"no": 8, "state": "Опубликовано", "app_no": "1020190160174", "date": "20191204", "title": "Устройство памяти и способ его работы"},
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
            drawing_html = f'<img src="{image_uris[index]}" alt="Основной чертёж {item["no"]}">'
        else:
            drawing_html = '<span class="bulk-drawing-empty">Нет изображения</span>'
        cards.append(
            f'<article class="bulk-drawing-card">'
            f'<div class="bulk-meta"><span class="bulk-number">{item["no"]}</span>'
            f'<span class="bulk-state">{item["state"]}</span>'
            f'<span>№ заявки: {item["app_no"]} ({item["date"]})</span></div>'
            f'<div class="bulk-invention-title">{item["title"]}</div>'
            f'<div class="bulk-drawing-frame">{drawing_html}</div>'
            f"</article>"
        )
    return (
        '<section class="bulk-drawings-modal">'
        '<header class="bulk-modal-header">'
        '<div class="bulk-title-icon bulk-title-icon-drawing">▣</div>'
        "<div><div class=\"bulk-title\">Пакетный просмотр основных чертежей</div>"
        '<div class="bulk-subtitle">Просмотр по 8 из 200 отфильтрованных записей</div></div>'
        '<div class="bulk-header-spacer"></div>'
        '<div class="bulk-sort">Сетка: <strong>4 столбца⌄</strong><span>|</span><strong>2 ряда⌄</strong></div>'
        '<div class="bulk-nav"><span class="disabled">Previous</span><strong>1 / 25</strong><span>Next</span></div>'
        '<label for="bulk-drawings-toggle" class="bulk-close">×</label>'
        "</header>"
        f'<div class="bulk-card-grid">{"".join(cards)}</div>'
        "</section>"
    )


drawing_batch_modal_html = build_bulk_drawings_modal_html()

PATENT_TABLE_BASE_ROWS = [
    {"state": "Опубликовано", "cpc": "G11C 16/3459<br>G11C 16/10<br>G11C 16/26(i)", "title": "Устройство памяти и система памяти, включающая его", "app_no": "1020180133661", "app_date": "20181102", "pub_no": "1020200050705"},
    {"state": "Опубликовано", "cpc": "G11C 29/38<br>G11C 16/34<br>G11C 16/12(i)", "title": "Полупроводниковое устройство памяти и способ его работы", "app_no": "1020140178426", "app_date": "20141211", "pub_no": "1020160071120"},
    {"state": "Отклонено", "cpc": "G11C 16/10<br>G11C 16/3403<br>G11C 16/3459(i)", "title": "Устройство памяти и способ его работы", "app_no": "1020200126702", "app_date": "20200929", "pub_no": "1020220043365"},
    {"state": "Зарегистрировано", "cpc": "G11C 16/3459<br>G11C 16/08<br>G11C 16/10(i)", "title": "Устройство памяти", "app_no": "1020200098794", "app_date": "20200806", "pub_no": "1020220018354"},
    {"state": "Опубликовано", "cpc": "G11C 16/30<br>G11C 16/08<br>G11C 16/24(i)", "title": "Устройство памяти и способ его работы", "app_no": "1020200098765", "app_date": "20200806", "pub_no": "1020220018341"},
    {"state": "Зарегистрировано", "cpc": "G11C 16/3459<br>G11C 16/10(i)<br>G11C 16/24", "title": "Буфер страницы, устройство памяти, включающее буфер страницы, и система памяти, включающая устройство памяти", "app_no": "1020220164302", "app_date": "20221130", "pub_no": "1020240080715"},
    {"state": "Отозвано", "cpc": "G11C 16/3445<br>G11C 16/3459<br>G11C 29/26(i)", "title": "Устройство памяти и способ его работы", "app_no": "1020150172401", "app_date": "20151204", "pub_no": "1020170065969"},
    {"state": "Опубликовано", "cpc": "G11C 16/3459<br>G11C 16/10<br>G11C 16/26(i)", "title": "Устройство памяти и способ его работы", "app_no": "1020190160174", "app_date": "20191204", "pub_no": "1020210070107"},
    {"state": "Опубликовано", "cpc": "G11C 16/3459<br>G11C 16/24<br>G11C 16/08(i)", "title": "Устройство памяти и способ его работы", "app_no": "1020200104937", "app_date": "20200820", "pub_no": "1020220023263"},
    {"state": "Отклонено", "cpc": "G11C 16/3459<br>G11C 16/24<br>G11C 16/10(i)", "title": "Устройство памяти и способ его работы", "app_no": "1020210025654", "app_date": "20210223", "pub_no": "1020230120033"},
    {"state": "Зарегистрировано", "cpc": "G11C 16/06<br>G11C 16/125(i)", "title": "Энергонезависимое устройство памяти и способ его работы", "app_no": "1020140093320", "app_date": "20140723", "pub_no": "1020160012300"},
]

PATENT_TABLE_EXTRA_TITLES = [
    "Устройство NAND-флэш-памяти и способ его управления",
    "Контроллер памяти с низким энергопотреблением и полупроводниковое устройство",
    "Многослойная структура массива ячеек памяти",
    "Система памяти с высокоскоростным последовательным интерфейсом",
    "Устройство памяти, включающее схему коррекции ошибок на кристалле",
    "Схема возбуждения линии слов и устройство памяти",
    "Устройство памяти, включающее усилитель считывания битовой линии",
    "Способ проверки на основе тока ячейки и устройство памяти",
    "Система памяти с одновременной работой нескольких плоскостей",
    "Устройство управления программным напряжением ячейки памяти",
    "Модуль хранения, включающий интеллектуальный контроллер",
    "Способ обновления полупроводникового устройства памяти",
    "Массив памяти высокой плотности и способ изготовления",
    "Устройство памяти с компенсацией утечки заряда",
    "Интерфейс памяти и способ передачи данных",
    "Схема управления операцией стирания флэш-памяти",
    "Схема выбора блока памяти и способ работы",
    "Устройство работы памяти на основе температурной компенсации",
    "Схема определения состояния ячейки памяти",
]

PATENT_TABLE_EXTRA_CPC = [
    "G11C 16/04<br>G11C 7/10",
    "G11C 16/06<br>G11C 16/34",
    "G11C 16/08<br>G11C 16/26(i)",
    "G11C 16/12<br>G11C 16/30",
    "G11C 16/18<br>G11C 16/24",
    "G11C 16/26<br>G11C 16/3459",
    "G11C 16/28<br>G11C 16/10(i)",
    "G11C 16/32<br>G11C 16/08",
    "G11C 29/06<br>G11C 16/34",
    "G11C 29/50<br>G11C 16/10",
]


def build_patent_table_rows_html(count: int = 30) -> str:
    rng = random.Random(42)
    states = ["Опубликовано", "Зарегистрировано"]
    rows: list[str] = []
    for index in range(1, count + 1):
        if index <= len(PATENT_TABLE_BASE_ROWS):
            row = PATENT_TABLE_BASE_ROWS[index - 1]
        else:
            year = rng.randint(2014, 2024)
            month = rng.randint(1, 12)
            day = rng.randint(1, 28)
            row = {
                "state": rng.choice(states),
                "cpc": rng.choice(PATENT_TABLE_EXTRA_CPC),
                "title": rng.choice(PATENT_TABLE_EXTRA_TITLES),
                "app_no": f"10{year}{rng.randint(10000000, 99999999)}",
                "app_date": f"{year}{month:02d}{day:02d}",
                "pub_no": f"10{year + 2}{rng.randint(10000000, 99999999)}",
            }
        rows.append(
            f'<tr class="clickable-row">'
            f'<td><label for="spec-modal-toggle" class="row-open"></label>{index}</td>'
            f'<td><span class="state-chip">{row["state"]}</span></td>'
            f'<td class="cpc">{row["cpc"]}</td>'
            f'<td class="title">{html.escape(row["title"])}</td>'
            f'<td>{row["app_no"]}</td>'
            f'<td>{row["app_date"]}</td>'
            f'<td>{row["pub_no"]}</td>'
            f"</tr>"
        )
    return "\n              ".join(rows)


patent_table_rows_html = build_patent_table_rows_html()

DEFAULT_COMPONENT_ITEMS = [
    "Ячейки памяти, соединённые с линиями слов и битовыми линиями",
    "Основной процессор, управляющий напряжениями программирования, подаваемыми на указанные линии слов и битовые линии",
    "Буфер страницы, сохраняющий данные, считанные на основе физического напряжения указанных ячеек памяти",
    "Схема сравнения, сравнивающая ток считывания, соответствующий считанным данным, с указанным считанным током",
    "Конфигурация, в которой основной процессор управляет указанным напряжением программирования",
]


def build_component_row(index: int, text: str) -> str:
    return (
        f'<div class="component">'
        f'<label class="component-check-label">'
        f'<input type="checkbox" class="component-check" checked="checked" aria-label="Select component {index}">'
        f"</label>"
        f"<div>"
        f'<div class="component-title"><span>Элемент {index}</span><span>☆ Ключевой</span></div>'
        f'<textarea class="component-text" rows="2">{html.escape(text)}</textarea>'
        f"</div></div>"
    )


def build_components_list_html() -> str:
    rows = "".join(
        build_component_row(index, text)
        for index, text in enumerate(DEFAULT_COMPONENT_ITEMS, start=1)
    )
    return f'<div id="components-list" class="components-list">{rows}</div>'


components_list_html = build_components_list_html()

COMPONENT_INTERACTION_HTML = """
<script>
(function () {
  function collectDocuments(rootDoc) {
    const docs = [];
    const seen = new Set();
    function add(doc) {
      if (!doc || seen.has(doc)) return;
      seen.add(doc);
      docs.push(doc);
    }
    add(rootDoc);
    try {
      rootDoc.querySelectorAll("iframe").forEach(function (frame) {
        try { add(frame.contentDocument); } catch (error) {}
      });
    } catch (error) {}
    return docs;
  }

  function getAppDocument() {
    const roots = [];
    try { roots.push(window.document); } catch (error) {}
    try {
      if (window.parent && window.parent.document) roots.push(window.parent.document);
    } catch (error) {}
    for (let r = 0; r < roots.length; r += 1) {
      const docs = collectDocuments(roots[r]);
      for (let i = 0; i < docs.length; i += 1) {
        const doc = docs[i];
        if (doc.getElementById("mypage-open-btn") || doc.getElementById("components-list")) {
          return doc;
        }
      }
    }
    return null;
  }

  function createComponentHtml(index) {
    return (
      '<div class="component">' +
      '<label class="component-check-label">' +
      '<input type="checkbox" class="component-check" checked="checked" aria-label="Select component ' + index + '">' +
      "</label>" +
      "<div>" +
      '<div class="component-title"><span>Элемент ' + index + '</span><span>☆ Ключевой</span></div>' +
      '<textarea class="component-text" rows="2" placeholder="Введите содержание элемента"></textarea>' +
      "</div></div>"
    );
  }

  function bindComponentCheckboxes() {
    const doc = getAppDocument();
    if (!doc) return;
    doc.querySelectorAll(".component-check").forEach(function (checkbox) {
      if (checkbox.dataset.bound === "true") return;
      checkbox.dataset.bound = "true";
      checkbox.checked = true;
      checkbox.addEventListener("click", function (event) {
        event.stopPropagation();
      });
    });
  }

  function bindAddButton() {
    const doc = getAppDocument();
    if (!doc) return false;
    const button = doc.getElementById("component-add-btn");
    const list = doc.getElementById("components-list");
    if (!button || !list || button.dataset.bound === "true") return !!button;
    button.dataset.bound = "true";
    button.addEventListener("click", function () {
      const index = list.querySelectorAll(".component").length + 1;
      list.insertAdjacentHTML("beforeend", createComponentHtml(index));
      bindComponentCheckboxes();
      const textareas = list.querySelectorAll(".component-text");
      const lastTextarea = textareas[textareas.length - 1];
      if (lastTextarea) lastTextarea.focus();
    });
    return true;
  }

  function randomInt(min, max) {
    return Math.floor(Math.random() * (max - min + 1)) + min;
  }

  function buildComponentChipsCell() {
    const td = document.createElement("td");
    td.className = "component-chips-cell";
    const wrap = document.createElement("div");
    wrap.className = "component-chips";
    const count = randomInt(2, 6);
    for (let i = 1; i <= count; i += 1) {
      const chip = document.createElement("span");
      chip.className = "comp-chip tone-" + randomInt(1, 6);
      chip.textContent = String(i);
      wrap.appendChild(chip);
    }
    td.appendChild(wrap);
    return td;
  }

  function updateRowNumbers(tbody) {
    tbody.querySelectorAll("tr").forEach(function (row, index) {
      const cell = row.cells[0];
      const label = cell.querySelector(".row-open");
      cell.textContent = "";
      if (label) cell.appendChild(label);
      cell.appendChild(document.createTextNode(String(index + 1)));
    });
  }

  function shuffleRows(tbody) {
    const rows = Array.from(tbody.querySelectorAll("tr"));
    for (let i = rows.length - 1; i > 0; i -= 1) {
      const j = randomInt(0, i);
      const temp = rows[i];
      rows[i] = rows[j];
      rows[j] = temp;
    }
    rows.forEach(function (row) { tbody.appendChild(row); });
    updateRowNumbers(tbody);
  }

  function ensureComponentColumn(table, tbody) {
    if (table.classList.contains("has-component-col")) {
      tbody.querySelectorAll(".component-chips-cell").forEach(function (cell) {
        cell.replaceWith(buildComponentChipsCell());
      });
      return;
    }
    const headerRow = table.querySelector("thead tr");
    const th = document.createElement("th");
    th.textContent = "Элементы";
    headerRow.insertBefore(th, headerRow.cells[3]);
    const colgroup = table.querySelector("colgroup");
    const col = document.createElement("col");
    colgroup.insertBefore(col, colgroup.children[3]);
    tbody.querySelectorAll("tr").forEach(function (row) {
      row.insertBefore(buildComponentChipsCell(), row.cells[3]);
    });
    table.classList.add("has-component-col");
  }

  let originalPatentTableState = null;

  function captureOriginalPatentTable(doc) {
    const table = doc.querySelector(".patent-table");
    const tbody = doc.getElementById("patent-table-body");
    const thead = table ? table.querySelector("thead") : null;
    const colgroup = table ? table.querySelector("colgroup") : null;
    if (!table || !tbody || !thead || !colgroup || originalPatentTableState) return;
    originalPatentTableState = {
      tbodyHtml: tbody.innerHTML,
      theadHtml: thead.innerHTML,
      colgroupHtml: colgroup.innerHTML,
      tableClass: table.className,
    };
  }

  function resetPatentTable(doc) {
    const table = doc.querySelector(".patent-table");
    const tbody = doc.getElementById("patent-table-body");
    const thead = table ? table.querySelector("thead") : null;
    const colgroup = table ? table.querySelector("colgroup") : null;
    if (!table || !tbody || !thead || !colgroup || !originalPatentTableState) return;
    tbody.innerHTML = originalPatentTableState.tbodyHtml;
    thead.innerHTML = originalPatentTableState.theadHtml;
    colgroup.innerHTML = originalPatentTableState.colgroupHtml;
    table.className = originalPatentTableState.tableClass;
  }

  function applyLlmRerank(doc) {
    const table = doc.querySelector(".patent-table");
    const tbody = doc.getElementById("patent-table-body");
    if (!table || !tbody) return;
    ensureComponentColumn(table, tbody);
    shuffleRows(tbody);
  }

  function bindSearchButtons() {
    const doc = getAppDocument();
    if (!doc) return false;
    const startToggle = doc.getElementById("search-start-toggle");
    const resultToggle = doc.getElementById("search-result-toggle");
    if (!startToggle || !resultToggle || startToggle.dataset.searchBound === "true") {
      return !!(startToggle && resultToggle);
    }
    startToggle.dataset.searchBound = "true";
    startToggle.addEventListener("change", function () {
      if (startToggle.checked) resetPatentTable(doc);
    });
    resultToggle.addEventListener("change", function () {
      if (resultToggle.checked) resetPatentTable(doc);
    });
    return true;
  }

  function bindLlmRerankButton() {
    const doc = getAppDocument();
    if (!doc) return false;
    const button = doc.getElementById("llm-rerank-btn");
    if (!button || button.dataset.bound === "true") return !!button;
    button.dataset.bound = "true";
    button.addEventListener("click", function (event) {
      event.preventDefault();
      event.stopPropagation();
      applyLlmRerank(doc);
    });
    return true;
  }

  function setMypageOpen(doc, open) {
    const toggle = doc.getElementById("mypage-toggle");
    const backdrop = doc.querySelector(".mypage-modal-backdrop");
    const modal = doc.querySelector(".mypage-modal");
    if (toggle) toggle.checked = open;
    if (backdrop) backdrop.classList.toggle("is-open", open);
    if (modal) modal.classList.toggle("is-open", open);
  }

  function bindMypageModal() {
    const doc = getAppDocument();
    if (!doc) return false;
    const modal = doc.querySelector(".mypage-modal");
    if (!modal) return false;

    const triggers = [
      doc.getElementById("mypage-open-btn"),
      doc.getElementById("spec-save-evidence-btn"),
    ].filter(Boolean);

    if (!triggers.length) return false;

    triggers.forEach(function (trigger) {
      if (trigger.dataset.bound === "true") return;
      trigger.dataset.bound = "true";
      trigger.addEventListener("click", function (event) {
        event.preventDefault();
        event.stopPropagation();
        setMypageOpen(doc, true);
      });
    });

    doc.querySelectorAll(".mp-close").forEach(function (closeBtn) {
      if (closeBtn.dataset.bound === "true") return;
      closeBtn.dataset.bound = "true";
      closeBtn.addEventListener("click", function (event) {
        event.preventDefault();
        event.stopPropagation();
        setMypageOpen(doc, false);
      });
    });
    return true;
  }

  function initInteractions() {
    const doc = getAppDocument();
    if (doc) captureOriginalPatentTable(doc);
    bindComponentCheckboxes();
    const addOk = bindAddButton();
    const searchOk = bindSearchButtons();
    const rerankOk = bindLlmRerankButton();
    const mypageOk = bindMypageModal();
    return addOk && searchOk && rerankOk && mypageOk;
  }

  if (!initInteractions()) {
    const timer = window.setInterval(function () {
      if (initInteractions()) window.clearInterval(timer);
    }, 200);
    window.setTimeout(function () { window.clearInterval(timer); }, 8000);
  }

  const mypageTimer = window.setInterval(function () {
    if (bindMypageModal()) window.clearInterval(mypageTimer);
  }, 200);
  window.setTimeout(function () { window.clearInterval(mypageTimer); }, 15000);
})();
</script>
"""

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans:wght@400;500;600;700&display=swap');

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
  font-family: "Noto Sans", "Segoe UI", sans-serif;
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
  isolation: isolate;
}
.patent-app:has(#ai-panel-toggle:checked) {
  grid-template-columns: 270px 560px minmax(0, 1fr);
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
.patent-app:has(#ai-panel-toggle:checked) .topbar {
  grid-template-columns: 270px 560px 1fr;
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
#search-start-toggle:checked ~ .topbar .tab.info-tab,
#search-result-toggle:checked ~ .topbar .tab.info-tab {
  color: #677383;
  font-weight: 400;
  background: #f8fafc;
  border-color: transparent;
  border-bottom-color: transparent;
}
#search-start-toggle:checked ~ .topbar .tab.app-tab,
#search-result-toggle:checked ~ .topbar .tab.app-tab {
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
  overflow-x: hidden;
  overflow-y: auto;
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
.component {
  display: grid;
  grid-template-columns: 22px 1fr;
  gap: 4px;
  padding: 6px 2px 7px;
  border-bottom: 1px solid #edf0f4;
}
.component-check-label {
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding-top: 3px;
  cursor: pointer;
  pointer-events: auto;
}
.component-check {
  width: 14px;
  height: 14px;
  margin: 0;
  cursor: pointer;
  pointer-events: auto;
  accent-color: #2778ed;
  flex-shrink: 0;
}
.components-head {
  display: grid;
  grid-template-columns: 1fr 90px 90px;
  align-items: center;
  height: 40px;
  color: #5f6b78;
  border-bottom: 1px solid #e8edf2;
}
.components-head > :nth-child(1) { grid-column: 2; }
.components-head > :nth-child(2) { grid-column: 3; }
.mini-button {
  margin-left: 2px;
  padding: 3px 8px;
  min-width: 84px;
  color: white;
  text-align: center;
  font-size: var(--fs-label);
  background: #7a48eb;
  border: none;
  border-radius: 3px;
  cursor: pointer;
  user-select: none;
  font-family: inherit;
  transition: filter .15s ease, transform .15s ease;
}
button.mini-button { width: 100%; }
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
.component-text {
  width: 100%;
  min-height: 42px;
  padding: 4px 6px;
  color: #44505d;
  line-height: 1.5;
  font-family: inherit;
  font-size: var(--fs-body);
  background: #fff;
  border: 1px solid #dfe5ec;
  border-radius: 4px;
  resize: vertical;
}
.component-text:focus {
  outline: none;
  border-color: #93bbf1;
  box-shadow: 0 0 0 2px rgba(40, 120, 239, .12);
}
.component-text::placeholder { color: #9aa3ad; }
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
  background: #f7f8fa;
  border: 1px solid #dfe5ec;
  border-radius: 8px;
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
  height: 40px;
  flex: 0 0 40px;
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 0 10px;
  background: #fff;
  border-bottom: 1px solid #edf0f4;
  font-size: var(--fs-subtitle);
  font-weight: 700;
  color: #27323d;
}
.doc-icon { color: #3479ee; font-size: var(--fs-label); }
.title-spacer { flex: 1; }
.ai-view-toggle {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-right: 4px;
}
.ai-view-opt {
  height: 24px;
  display: grid;
  place-items: center;
  padding: 0 9px;
  color: #738091;
  background: #fff;
  border: 1px solid #dfe4ea;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 500;
  white-space: nowrap;
  cursor: pointer;
}
.ai-view-opt.active {
  color: #7442df;
  border-color: #b9a3ef;
  background: #f7f3ff;
  font-weight: 700;
}
.close {
  width: 24px;
  height: 24px;
  display: grid;
  place-items: center;
  color: #8c96a2;
  font-size: 16px;
  cursor: pointer;
  user-select: none;
  border-radius: 4px;
}
.close:hover { background: #f3f5f7; }
.ai-split-body {
  flex: 1;
  min-height: 0;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0;
}
.ai-summary-pane,
.ai-claims-pane {
  min-width: 0;
  min-height: 0;
  display: flex;
  flex-direction: column;
  background: #fff;
}
.ai-summary-pane {
  border-right: 1px solid #e9edf2;
  padding: 10px 10px 12px;
}
.ai-claims-pane {
  padding: 10px 10px 8px;
}
.ai-pane-head {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
}
.ai-pane-title {
  font-size: 13px;
  font-weight: 700;
}
.ai-pane-title.summary { color: #7442df; }
.ai-pane-title.claims { color: #2c6fc9; }
.select-all {
  margin-left: auto;
  height: 24px;
  padding: 0 8px;
  display: grid;
  place-items: center;
  color: #65717e;
  background: #f7f8fa;
  border: 1px solid #e1e6eb;
  border-radius: 4px;
  font-size: 11px;
  cursor: pointer;
}
.ai-summary-list {
  flex: 1;
  min-height: 0;
  overflow: auto;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.ai-summary-card {
  padding: 10px;
  border: 1px solid;
  border-radius: 6px;
  line-height: 1.5;
  font-size: 12px;
}
.ai-summary-card strong {
  display: block;
  margin-bottom: 6px;
  font-size: 12px;
  font-weight: 700;
}
.ai-summary-card.red {
  color: #3f4954;
  background: #fff8f7;
  border-color: #f0d0cc;
}
.ai-summary-card.red strong { color: #c6463d; }
.ai-summary-card.green {
  color: #3f4954;
  background: #f5fcf9;
  border-color: #c5e8da;
}
.ai-summary-card.green strong { color: #1fa67a; }
.claim-list {
  min-height: 0;
  flex: 1;
  overflow: auto;
  padding: 0;
}
.claim-card {
  margin-bottom: 7px;
  padding: 8px 9px;
  color: #3d4855;
  line-height: 1.5;
  background: #fff;
  border: 1px solid #e3e8ee;
  border-radius: 6px;
  box-shadow: 0 1px 2px rgba(35, 47, 60, .04);
  font-size: 12px;
}
.claim-card-head {
  display: flex;
  align-items: center;
  gap: 5px;
  margin-bottom: 5px;
  color: #2472d4;
  font-weight: 700;
  font-size: 12px;
}
.claim-card-head input { margin: 0; }
.extract-button {
  flex: 0 0 auto;
  height: 34px;
  margin-top: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  color: #fff;
  background: linear-gradient(90deg, #9348e9, #693ce8);
  border-radius: 6px;
  font-size: 12px;
  font-weight: 700;
  cursor: pointer;
  box-shadow: 0 2px 6px rgba(105, 60, 232, .25);
}

.workspace {
  position: relative;
  grid-column: 3;
  grid-row: 2;
  min-width: 0;
  overflow: hidden;
  background: #f8fafc;
}
.welcome-view {
  position: absolute;
  inset: 0;
  display: grid;
  place-items: center;
  width: 100%;
  height: 100%;
  background:
    radial-gradient(ellipse 70% 50% at 50% 42%, rgba(120, 80, 230, .06), transparent 70%),
    #f8fafc;
}
.welcome-title {
  margin: 0;
  color: #1d2733;
  font-size: clamp(28px, 3.2vw, 42px);
  font-weight: 700;
  letter-spacing: -.04em;
  text-align: center;
  line-height: 1.35;
}
#search-start-toggle:checked ~ .workspace .welcome-view,
#search-result-toggle:checked ~ .workspace .welcome-view {
  display: none;
}
.loading-view {
  position: absolute;
  inset: 0;
  display: none;
  width: 100%;
  height: 100%;
}
.progress-wrap {
  height: 100px;
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
  height: 30px;
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
  grid-template-columns: minmax(0, 1fr) 340px;
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
button.result-tool {
  font-family: inherit;
  cursor: pointer;
}
.llm-rerank-btn {
  color: #7055cf;
  background: #f6f2ff;
  border-color: #d8ccf8;
}
.llm-rerank-btn:hover { background: #efe8ff; }
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
.patent-table-wrap {
  min-height: 0;
  flex: 1;
  overflow-x: auto;
  overflow-y: auto;
}
.patent-table {
  width: 100%;
  min-width: 920px;
  height: auto;
  table-layout: fixed;
  border-collapse: collapse;
  color: #4e5b68;
  font-size: 12px;
}
.patent-table col:nth-child(1) { width: 36px; }
.patent-table col:nth-child(2) { width: 44px; }
.patent-table col:nth-child(3) { width: 132px; }
.patent-table col:nth-child(4) { width: auto; }
.patent-table col:nth-child(5) { width: 112px; }
.patent-table col:nth-child(6) { width: 72px; }
.patent-table col:nth-child(7) { width: 112px; }
.patent-table.has-component-col {
  min-width: 992px;
}
.patent-table.has-component-col col:nth-child(1) { width: 36px; }
.patent-table.has-component-col col:nth-child(2) { width: 44px; }
.patent-table.has-component-col col:nth-child(3) { width: 124px; }
.patent-table.has-component-col col:nth-child(4) { width: 108px; }
.patent-table.has-component-col col:nth-child(5) { width: auto; }
.patent-table.has-component-col col:nth-child(6) { width: 112px; }
.patent-table.has-component-col col:nth-child(7) { width: 72px; }
.patent-table.has-component-col col:nth-child(8) { width: 112px; }
.patent-table th {
  height: 24px;
  padding: 4px 3px;
  color: #4b5865;
  background: #f8fafc;
  border-bottom: 1px solid #dfe5eb;
  text-align: center;
  font-weight: 600;
  white-space: nowrap;
}
.patent-table td {
  min-height: 34px;
  height: auto;
  padding: 3px 4px;
  border-bottom: 1px solid #e7ebf0;
  text-align: center;
  vertical-align: middle;
  overflow: visible;
}
.patent-table td:nth-child(1),
.patent-table td:nth-child(2) {
  padding: 3px 2px;
}
.patent-table:not(.has-component-col) td:nth-child(5),
.patent-table:not(.has-component-col) td:nth-child(6),
.patent-table:not(.has-component-col) td:nth-child(7),
.patent-table.has-component-col td:nth-child(6),
.patent-table.has-component-col td:nth-child(7),
.patent-table.has-component-col td:nth-child(8) {
  padding: 3px 4px;
  white-space: nowrap;
  font-size: var(--fs-caption);
}
.patent-table.has-component-col td {
  height: auto;
  vertical-align: middle;
}
.patent-table tr:first-child td { background: #f1f6fd; }
.patent-table tr:first-child td:first-child { border-left: 2px solid #4e94ee; }
.patent-table td.cpc {
  line-height: 1.25;
  padding: 3px 4px;
  text-align: left;
  font-size: var(--fs-caption);
}
.patent-table.has-component-col td.cpc,
.patent-table.has-component-col td.title {
  vertical-align: middle;
}
.patent-table td.component-chips-cell {
  padding: 5px 4px;
  vertical-align: middle;
  text-align: left;
}
.component-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  align-items: center;
  justify-content: flex-start;
  align-content: flex-start;
  width: 92px;
  max-width: 100%;
  min-height: 20px;
}
.comp-chip {
  width: 20px;
  height: 20px;
  min-width: 20px;
  flex: 0 0 20px;
  padding: 0;
  display: inline-grid;
  place-items: center;
  border-radius: 3px;
  font-size: var(--fs-caption);
  font-weight: 700;
  line-height: 1;
  box-sizing: border-box;
}
.comp-chip.tone-1 { background: #dce9fb; color: #2a5080; border: 1px solid #b8d4f5; }
.comp-chip.tone-2 { background: #b8d4f5; color: #234870; border: 1px solid #93bbf1; }
.comp-chip.tone-3 { background: #93bbf1; color: #fff; border: 1px solid #6fa3eb; }
.comp-chip.tone-4 { background: #5f94e8; color: #fff; border: 1px solid #4a7fd4; }
.comp-chip.tone-5 { background: #3d7ad8; color: #fff; border: 1px solid #2f66bb; }
.comp-chip.tone-6 { background: #2a5fa8; color: #fff; border: 1px solid #1f4a85; }
.patent-table td.title {
  color: #1d6ed7;
  text-align: left;
  font-weight: 600;
  white-space: normal;
  line-height: 1.3;
  padding: 3px 6px 3px 4px;
}
.state-chip {
  display: inline-block;
  padding: 1px 4px;
  color: #5c6671;
  background: #f1f3f5;
  border-radius: 3px;
  font-size: var(--fs-caption);
  white-space: nowrap;
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
#bulk-claims-toggle, #bulk-drawings-toggle, #mypage-toggle {
  position: absolute;
  width: 1px;
  height: 1px;
  opacity: 0;
  pointer-events: none;
}
.bulk-modal-backdrop {
  position: absolute;
  inset: 0;
  z-index: 99;
  display: none;
  background: rgba(33, 43, 54, .48);
  pointer-events: none;
}
#bulk-claims-toggle:checked ~ .bulk-modal-backdrop,
#bulk-drawings-toggle:checked ~ .bulk-modal-backdrop {
  display: block;
  animation: backdrop-fade-in .18s ease-out;
}
@keyframes backdrop-fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}
.bulk-claims-modal, .bulk-drawings-modal {
  position: absolute;
  top: 36px;
  right: 48px;
  bottom: 36px;
  left: 48px;
  z-index: 100;
  display: none;
  flex-direction: column;
  background: #f7f8fa;
  border: 1px solid #dfe5ec;
  border-radius: 10px;
  box-shadow: 0 10px 36px rgba(23, 36, 50, .14);
  overflow: hidden;
}
#bulk-claims-toggle:checked ~ .bulk-claims-modal,
#bulk-drawings-toggle:checked ~ .bulk-drawings-modal {
  display: flex;
  animation: modal-fade-in .18s ease-out;
}
@keyframes modal-fade-in {
  from { opacity: 0; transform: scale(.985); }
  to { opacity: 1; transform: scale(1); }
}
.bulk-modal-header {
  height: 54px;
  flex: 0 0 54px;
  display: flex;
  align-items: center;
  padding: 0 12px;
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
  gap: 10px;
  padding: 12px;
}
.bulk-claim-card {
  min-width: 0;
  padding: 10px;
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
  margin: 5px 0 7px;
  color: #266fcf;
  font-size: var(--fs-subtitle);
  font-weight: 700;
  line-height: 1.35;
}
.bulk-claim-body {
  padding-top: 6px;
  color: #727d87;
  border-top: 1px solid #eef1f4;
  font-size: 12px;
  line-height: 1.5;
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
  padding: 10px;
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
  margin-top: 6px;
  padding: 4px;
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
  .patent-app:has(#ai-panel-toggle:checked) { grid-template-columns: 336px 620px minmax(0, 1fr); }
  .topbar { grid-template-columns: 336px 620px 1fr; }
  .section-title { font-size: var(--fs-subtitle); }
  .loading-card { max-width: 635px; }
}
__SPEC_MODAL_CSS__
__MYPAGE_MODAL_CSS__
</style>

<div class="patent-app">
  <input type="checkbox" id="ai-panel-toggle">
  <input type="checkbox" id="search-start-toggle">
  <input type="checkbox" id="search-result-toggle">
  <input type="checkbox" id="bulk-claims-toggle">
  <input type="checkbox" id="bulk-drawings-toggle">
  <input type="checkbox" id="spec-modal-toggle">
  <input type="checkbox" id="mypage-toggle">
  __MYPAGE_MODAL_HTML__
  <header class="topbar">
    <div class="top-left">▏Поиск патентов <button>Manual Input</button></div>
    <div class="tabs"><div class="tab info-tab active">⌂&nbsp; INFO</div><div class="tab app-tab">1020220167018</div></div>
    <div class="main-actions">
      <button type="button" class="action-pill mypage-trigger" id="mypage-open-btn">▱&nbsp; Save Evidence</button>
      <div class="icon-box">✎</div><div class="icon-box">▣</div>
      <div class="icon-box">▥</div><div class="icon-box">⚙</div>
    </div>
  </header>
  <aside class="filter-panel">
    <div class="filter-scroll">
      <div class="field">1020220167018</div>
      <div class="section">
        <div class="section-title">▏Дата поиска</div>
        <div class="field select-field">Дата подачи</div>
        <div class="date-row"><div class="date">ГГГГ-ММ-ДД <span>□</span></div><span class="date-sep">-</span><div class="date">2022-12-02 <span>□</span></div></div>
      </div>
      <div class="section">
        <div class="section-title">▏Классификация CPC</div>
        <div class="class-grid">
          <label class="check"><input type="checkbox">A</label><label class="check"><input type="checkbox">B</label>
          <label class="check"><input type="checkbox">C</label><label class="check"><input type="checkbox">D</label>
          <label class="check"><input type="checkbox">E</label><label class="check"><input type="checkbox">F</label>
          <label class="check"><input type="checkbox" checked>G</label><label class="check"><input type="checkbox">H</label>
        </div>
      </div>
      <div class="section-title">▏Элементы</div>
      <div class="components-head">
        <label for="ai-panel-toggle" class="mini-button">AI More</label><button type="button" class="mini-button blue" id="component-add-btn">+ Add</button>
      </div>
      __COMPONENTS_LIST_HTML__
    </div>
    <div class="filter-footer">
      <div class="footer-buttons"><div class="footer-button">↻ Reset</div><label for="search-start-toggle" class="footer-button primary search-trigger search-first-trigger">⌕ Search</label><label for="search-result-toggle" class="footer-button primary search-trigger search-second-trigger">⌕ Search</label></div>
      <div class="copyright">Copyright © 2026 KIPI. All rights reserved. Version 2.0</div>
    </div>
  </aside>
  <aside class="claims-panel">
    <div class="claims-title">
      <span class="doc-icon">▧</span>
      <span>Подробнее ИИ (реферат и пункты формулы)</span>
      <span class="title-spacer"></span>
      <div class="ai-view-toggle">
        <span class="ai-view-opt">Tab View</span>
        <span class="ai-view-opt active">Split View</span>
      </div>
      <label for="ai-panel-toggle" class="close">×</label>
    </div>
    <div class="ai-split-body">
      <section class="ai-summary-pane">
        <div class="ai-pane-head"><span class="ai-pane-title summary">Реферат</span></div>
        <div class="ai-summary-list">
          <div class="ai-summary-card red">
            <strong>Решаемая задача и цель</strong>
            Цель — устранить утечку холодного воздуха из-за зазора между корпусом и рамой шторы при установке оконного кондиционера, а также упростить процесс сборки.
          </div>
          <div class="ai-summary-card green">
            <strong>Эффект изобретения</strong>
            Снижение числа деталей уменьшает себестоимость изготовления, а полная герметизация существенно повышает эффективность охлаждения кондиционера.
          </div>
        </div>
      </section>
      <section class="ai-claims-pane">
        <div class="ai-pane-head">
          <span class="ai-pane-title claims">Пункты формулы</span>
          <span class="select-all">Select All</span>
        </div>
        <div class="claim-list">
          <div class="claim-card"><div class="claim-card-head"><input type="checkbox">Пункт 1</div>Отрицательный электрод для вторичной батареи, включающий токосъёмник; и первый и второй слои активного материала, расположенные на токосъёмнике и содержащие природный графит, искусственный графит и кремнийсодержащее вещество.</div>
          <div class="claim-card"><div class="claim-card-head"><input type="checkbox">Пункт 2</div>Отрицательный электрод для вторичной батареи по пункту 1, в котором первый слой активного материала не содержит проводящего материала.</div>
          <div class="claim-card"><div class="claim-card-head"><input type="checkbox">Пункт 3</div>Отрицательный электрод для вторичной батареи по пункту 1, в котором массовое отношение искусственного графита к природному графиту в первом слое активного материала составляет от 1,5 до 6.</div>
          <div class="claim-card"><div class="claim-card-head"><input type="checkbox">Пункт 4</div>Отрицательный электрод для вторичной батареи по пункту 1, в котором содержание искусственного графита в первом слое активного материала составляет от 30 мас.% до 85 мас.% в расчёте на 100 мас.% всего первого слоя активного материала.</div>
          <div class="claim-card"><div class="claim-card-head"><input type="checkbox">Пункт 5</div>Отрицательный электрод для вторичной батареи по пункту 1, в котором содержание природного графита в первом слое активного материала составляет от 10 мас.% до 50 мас.% в расчёте на 100 мас.% всего первого слоя активного материала.</div>
          <div class="claim-card"><div class="claim-card-head"><input type="checkbox">Пункт 6</div>Отрицательный электрод для вторичной батареи по пункту 1, в котором содержание кремнийсодержащего вещества составляет от 1 мас.% до 20 мас.% в расчёте на 100 мас.% всего первого слоя активного материала.</div>
        </div>
        <div class="extract-button">✧&nbsp; Extract &amp; Add Components from Selected Claims via LLM</div>
      </section>
    </div>
  </aside>
  <main class="workspace">
    <div class="welcome-view">
      <h1 class="welcome-title">Система ИИ-поиска сходных патентов</h1>
    </div>
    <div class="loading-view">
      <div class="progress-wrap">
        <div class="progress">
          <div class="step done"><div class="step-dot">✓</div><div class="step-name">Анализ эталонного документа</div><div class="step-status">Готово</div></div>
          <div class="step active"><div class="step-dot">○</div><div class="step-name">Поиск по сходству</div><div class="step-status">Выполняется</div></div>
          <div class="step"><div class="step-dot">3</div><div class="step-name">Переранжирование</div><div class="step-status">Top 100</div></div>
          <div class="step"><div class="step-dot">4</div><div class="step-name">Элементы</div><div class="step-status">RRF Top 100</div></div>
        </div>
      </div>
      <section class="loading-area">
        <div class="loading-title">Выполняется поиск</div>
        <div class="loading-subtitle">Проверяется состояние фактического поиска и обработки ИИ.</div>
        <div class="loading-card">
          <div class="loading-item"><span class="spinner"></span>Извлечение эмбеддинг-вектора заявленного изобретения</div>
          <div class="loading-item"><span class="spinner"></span>Поиск по сходству ключевых слов...</div>
          <div class="loading-item"><span class="spinner"></span>Поиск по сходству эмбеддинг-векторов...</div>
          <div class="loading-item"><span class="spinner"></span>Объединение гибридных результатов...</div>
          <div class="loading-item"><span class="spinner"></span>Отбор Top100 результатов поиска...</div>
        </div>
      </section>
    </div>
    <div class="result-view">
      <section class="result-center">
        <div class="result-toolbar">
          <div class="result-tool active">▣ Documents</div>
          <div class="result-tool">▦ Components</div>
          <label for="bulk-drawings-toggle" class="result-tool bulk-drawings-trigger">▣ Bulk Drawing View</label>
          <div class="result-tool">♙ Bulk Formula View</div>
          <label for="bulk-claims-toggle" class="result-tool bulk-claims-trigger">▧ Bulk Claims View</label>
          <button type="button" class="result-tool llm-rerank-btn" id="llm-rerank-btn">⚡ LLM Rerank</button>
          <div class="result-search">⌕ &nbsp; Поиск ключевых слов в результатах...</div>
          <div class="result-search-btn">Search</div>
        </div>
        <div class="patent-table-wrap">
          <table class="patent-table">
            <colgroup><col><col><col><col><col><col><col></colgroup>
            <thead><tr><th>№</th><th>Статус</th><th>CPC</th><th>Название изобретения</th><th>№ заявки</th><th>Дата подачи</th><th>№ публикации</th></tr></thead>
            <tbody id="patent-table-body">
              __PATENT_TABLE_ROWS__
            </tbody>
          </table>
        </div>
        <div class="result-pager">
          <span>Показать:</span><span class="page-size">50⌄</span><span>1–30 из 200 записей</span>
          <span class="pager-spacer"></span><span class="page">Previous</span><span class="page active">1</span><span class="page">2</span><span class="page">3</span><span class="page">4</span><span class="page">Next</span>
        </div>
      </section>
      <aside class="result-side">
        <div class="side-card">
          <div class="side-heading">Основной чертёж</div>
          <div class="drawing-box"><img src="__DRAWING_DATA_URI__" alt="Основной чертёж"></div>
        </div>
        <div class="side-card ai-card">
          <div class="side-heading">Реферат ИИ</div>
          <div class="summary-box red"><strong>Решаемая задача и цель</strong><span>Предоставление корпуса электронного устройства, в котором пассивные элементы и схемы управления питанием эффективно интегрированы в структуру на основе интерпозера, что позволяет уменьшить площадь монтажа корпуса и одновременно повысить стабильность электропитания и производительность системы</span></div>
          <div class="summary-box green"><strong>Эффект изобретения</strong><span>Интерпозер размещается над подложкой корпуса; на интерпозере монтируются процессорный элемент, элемент памяти с высокой пропускной способностью и интегральная схема управления питанием; пассивные элементы, такие как индукторы и конденсаторы, формируются внутри или на поверхности интерпозера.</span></div>
          <div class="summary-box blue"><strong>Средство решения</strong><span>Интеграция пассивных элементов и схем управления питанием внутри интерпозера позволяет уменьшить площадь монтажа на подложке корпуса и обеспечить стабильное электропитание процессорного элемента и памяти с высокой пропускной способностью, повышая производительность и энергоэффективность всей электронной системы</span></div>
        </div>
      </aside>
    </div>
  </main>
  <div class="bulk-modal-backdrop" aria-hidden="true"></div>
  <section class="bulk-claims-modal">
    <header class="bulk-modal-header">
      <div class="bulk-title-icon">▧</div>
      <div><div class="bulk-title">Пакетный просмотр пунктов формулы</div><div class="bulk-subtitle">Просмотр по 8 из 200 отфильтрованных записей</div></div>
      <div class="bulk-header-spacer"></div>
      <div class="bulk-sort">Сетка: <strong>4 столбца⌄</strong><span>|</span><strong>2 ряда⌄</strong></div>
      <div class="bulk-nav"><span class="disabled">Previous</span><strong>1 / 25</strong><span>Next</span></div>
      <label for="bulk-claims-toggle" class="bulk-close">×</label>
    </header>
    <div class="bulk-card-grid">
      <article class="bulk-claim-card">
        <div class="bulk-meta"><span class="bulk-number">1</span><span class="bulk-state">Опубликовано</span><span>№ заявки: 1020180133661 (20181102)</span></div>
        <div class="bulk-invention-title">Устройство памяти и система памяти, включающая его</div>
        <div class="bulk-claim-body"><span class="bulk-claim-label">[Пункт 1]</span>Устройство памяти, включающее массив ячеек памяти, соединённых с множеством линий слов и битовых линий; генератор напряжения, подающий программное напряжение на массив ячеек памяти; и логику управления, управляющую операцией программирования в зависимости от состояния выбранной ячейки памяти.</div>
      </article>
      <article class="bulk-claim-card">
        <div class="bulk-meta"><span class="bulk-number">2</span><span class="bulk-state">Опубликовано</span><span>№ заявки: 1020140178426 (20141211)</span></div>
        <div class="bulk-invention-title">Полупроводниковое устройство памяти и способ его работы</div>
        <div class="bulk-claim-body"><span class="bulk-claim-label">[Пункт 1]</span>Способ работы полупроводникового устройства памяти, включающий этапы: приём команды чтения для ячеек памяти; подача напряжения чтения на выбранную линию слов; определение данных по изменению тока битовой линии; и вывод определённых данных во внешнее устройство.</div>
      </article>
      <article class="bulk-claim-card">
        <div class="bulk-meta"><span class="bulk-number">3</span><span class="bulk-state">Опубликовано</span><span>№ заявки: 1020200126702 (20200929)</span></div>
        <div class="bulk-invention-title">Устройство памяти и способ его работы</div>
        <div class="bulk-claim-body"><span class="bulk-claim-label">[Пункт 1]</span>Устройство памяти, включающее множество ячеек памяти с различными распределениями пороговых напряжений; буфер страницы, соединённый с множеством ячеек памяти; и схему управления, регулирующую амплитуду и длительность последующего программного импульса в зависимости от результата проверки программирования.</div>
      </article>
      <article class="bulk-claim-card">
        <div class="bulk-meta"><span class="bulk-number">4</span><span class="bulk-state">Зарегистрировано</span><span>№ заявки: 1020200098794 (20200806)</span></div>
        <div class="bulk-invention-title">Устройство памяти</div>
        <div class="bulk-claim-body"><span class="bulk-claim-label">[Пункт 1]</span>Энергонезависимое устройство памяти, включающее множество цепочек ячеек, вертикально уложенных на подложке; транзистор выбора, расположенный между цепочками ячеек и общей линией истока; и периферийную схему, ступенчато повышающую потенциал общей линии истока при операции стирания.</div>
      </article>
      <article class="bulk-claim-card">
        <div class="bulk-meta"><span class="bulk-number">5</span><span class="bulk-state">Опубликовано</span><span>№ заявки: 1020200098765 (20200806)</span></div>
        <div class="bulk-invention-title">Устройство памяти и способ его работы</div>
        <div class="bulk-claim-body"><span class="bulk-claim-label">[Пункт 1]</span>Устройство хранения, включающее буферную память для временного хранения данных записи, принятых от хоста; схему коррекции ошибок, формирующую код коррекции ошибок данных записи; и контроллер памяти, избирательно изменяющий интенсивность коррекции ошибок в зависимости от степени деградации блока памяти.</div>
      </article>
      <article class="bulk-claim-card">
        <div class="bulk-meta"><span class="bulk-number">6</span><span class="bulk-state">Опубликовано</span><span>№ заявки: 1020220164302 (20221130)</span></div>
        <div class="bulk-invention-title">Буфер страницы, устройство памяти, включающее буфер страницы, и система памяти, включающая устройство памяти</div>
        <div class="bulk-claim-body"><span class="bulk-claim-label">[Пункт 1]</span>Буфер страницы, включающий сенсорный защёлкивающий триггер, соединённый с узлом считывания и считывающий напряжение битовой линии; защёлкивающий триггер данных для временного хранения считанных данных; и коммутационную схему, соединяющую путь передачи данных между сенсорным защёлкивающим триггером и защёлкивающим триггером данных в соответствии с сигналом выбора.</div>
      </article>
      <article class="bulk-claim-card">
        <div class="bulk-meta"><span class="bulk-number">7</span><span class="bulk-state">Опубликовано</span><span>№ заявки: 1020150172401 (20151204)</span></div>
        <div class="bulk-invention-title">Устройство памяти и способ его работы</div>
        <div class="bulk-claim-body"><span class="bulk-claim-label">[Пункт 1]</span>Способ работы, включающий этапы: выполнение операции проверки программирования путём подачи первого проходного напряжения на выбранный блок памяти; подсчёт числа ячеек с неудачной проверкой; и подача второго проходного напряжения, более высокого, чем первое, если подсчитанное число превышает пороговое значение.</div>
      </article>
      <article class="bulk-claim-card">
        <div class="bulk-meta"><span class="bulk-number">8</span><span class="bulk-state">Опубликовано</span><span>№ заявки: 1020190160174 (20191204)</span></div>
        <div class="bulk-invention-title">Устройство памяти и способ его работы</div>
        <div class="bulk-claim-body"><span class="bulk-claim-label">[Пункт 1]</span>Устройство памяти, включающее массив ячеек памяти, разделённый на множество плоскостей; независимые схемы буфера страницы, соответствующие каждой плоскости; и контроллер, управляющий параллельным выполнением операции чтения первой плоскости и операции программирования второй плоскости в ответ на внешнюю команду.</div>
      </article>
    </div>
  </section>
  __BULK_DRAWINGS_MODAL_HTML__
  __SPEC_MODAL_HTML__
</div>
""".replace("__DRAWING_DATA_URI__", drawing_data_uri)
    .replace("__PATENT_TABLE_ROWS__", patent_table_rows_html)
    .replace("__COMPONENTS_LIST_HTML__", components_list_html)
    .replace("__BULK_DRAWINGS_MODAL_HTML__", drawing_batch_modal_html)
    .replace("__SPEC_MODAL_CSS__", SPEC_MODAL_CSS.strip())
    .replace("__SPEC_MODAL_HTML__", get_spec_modal_html().strip())
    .replace("__MYPAGE_MODAL_CSS__", MYPAGE_MODAL_CSS.strip())
    .replace("__MYPAGE_MODAL_HTML__", get_mypage_modal_html(DEFAULT_COMPONENT_ITEMS).strip()),
    unsafe_allow_html=True,
)

components.html(COMPONENT_INTERACTION_HTML, height=0, scrolling=False)
