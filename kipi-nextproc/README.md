# 차세대 지식재산행정시스템 ISP/BPR — 권리별 행정절차 흐름도

`proc.html`과 동일한 UI/동작을 Streamlit에서 실행하는 앱입니다.

## 구성

| 파일 | 역할 |
|------|------|
| `proc.html` | 권리별 행정절차 흐름도 UI (원본 HTML) |
| `nextproc.py` | Streamlit 엔트리포인트. `proc.html`을 읽어 iframe으로 표시 |
| `requirements.txt` | Python 의존성 (`streamlit`) |

## 실행 방법

```bash
pip install -r requirements.txt
streamlit run nextproc.py
```

브라우저에서 Streamlit이 안내하는 주소(기본 `http://localhost:8501`)로 접속합니다.

## `nextproc.py` 동작 요약

1. **HTML 로드** — 같은 디렉터리의 `proc.html`을 UTF-8로 읽어옵니다.
2. **Streamlit용 보정** — iframe 환경에 맞게 CSS/JS를 주입합니다.
   - 문서 전체 스크롤 제거 → `.diagram-scroll` 영역만 스크롤
   - 팝업을 iframe 뷰포트 중앙에 표시
   - 창 크기·탭 전환에 맞춰 다이어그램 스크롤 높이를 재계산
3. **화면 출력** — `streamlit.components.v1.html`로 iframe에 렌더링합니다.
4. **레이아웃** — Streamlit 헤더/푸터를 숨기고, iframe이 뷰포트 전체를 채우도록 스타일을 적용합니다.

## `proc.html` 수정 반영

- `nextproc.py`는 실행(또는 재실행)할 때마다 `proc.html`을 **디스크에서 다시 읽습니다**. HTML 내용을 Streamlit 캐시에 붙잡아 두지 않습니다.
- Streamlit은 기본적으로 `.py` 변경을 감시해 자동 재실행합니다. **`proc.html`만 수정한 경우에는 자동 rerun이 되지 않을 수 있습니다.**
- 이 경우 **브라우저를 새로고침**하면 `nextproc.py`가 다시 실행되며, 저장된 최신 `proc.html`이 반영됩니다.

## 사전 조건

- Python 3.x
- `proc.html`이 `nextproc.py`와 같은 폴더에 있어야 합니다. 없으면 앱이 오류를 표시하고 중단합니다.
