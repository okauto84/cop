"""
Market Breadth — Streamlit 패널
실행:  streamlit run market_breadth_app.py
(작업 디렉터리를 stock-tri 로 두는 것을 권장합니다.)
"""

from __future__ import annotations

import os
import tempfile
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

from market_breadth import EXCEL_FILE, build_excel, calc_breadth, get_market_data, read_tracker_excel

st.set_page_config(
    page_title="Market Breadth",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 세션 상태 초기화
for key, default in (
    ("mb_data", None),
    ("mb_kospi_recs", None),
    ("mb_kosdaq_recs", None),
    ("mb_xlsx_bytes", None),
    ("_mb_autoload_once", False),  # 세션당 자동 로드는 1회만 시도
):
    if key not in st.session_state:
        st.session_state[key] = default


def records_to_frame(records: list, idx_df: pd.DataFrame | None, tail_days: int) -> pd.DataFrame:
    """Breadth 기록 + (선택) 지수 종가 → 차트용 프레임."""
    if not records:
        return pd.DataFrame()
    df = pd.DataFrame(records).copy()
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date")
    if tail_days and len(df) > tail_days:
        df = df.iloc[-tail_days:].copy()
    df = df.set_index("date")
    if idx_df is not None and not idx_df.empty:
        idx = idx_df.copy()
        idx.index = pd.to_datetime(idx.index)
        if "Close" in idx.columns:
            df = df.join(idx[["Close"]].rename(columns={"Close": "지수종가"}), how="left")
    return df


def _run_market_pipeline(days: int, *, from_button: bool) -> None:
    """데이터 수집 + Breadth 계산 후 세션에 저장. 실패 시 메시지만 표시."""
    st.session_state.mb_xlsx_bytes = None
    progress_slot = st.empty()
    try:
        with st.spinner("시장 데이터를 가져오는 중… (최초·증분 수집은 수 분~수십 분 걸릴 수 있습니다)"):
            loaded = get_market_data(days=days)
        if loaded is None:
            st.error("데이터를 가져오지 못했습니다. 네트워크·모듈 설치 상태를 확인하세요.")
            return
        k_r, q_r = run_breadth_calculations(loaded, progress_slot)
        if not k_r and not q_r:
            st.error("계산된 Breadth 데이터가 없습니다.")
            return
        st.session_state.mb_data = loaded
        st.session_state.mb_kospi_recs = k_r
        st.session_state.mb_kosdaq_recs = q_r
        if from_button:
            st.success("계산이 완료되었습니다.")
        else:
            st.success("초기 데이터를 불러왔습니다. 차트를 확인하세요.")
    except Exception as e:  # noqa: BLE001
        progress_slot.empty()
        st.exception(e)


def run_breadth_calculations(data: dict, progress_ph) -> tuple[list, list]:
    kospi_p = data.get("kospi_pivot")
    kosdaq_p = data.get("kosdaq_pivot")
    bar = progress_ph.progress(0, text="준비 중…")

    def on_prog(cur: int, tot: int, label: str) -> None:
        bar.progress(
            min(cur / max(tot, 1), 1.0),
            text=f"[{label}] Breadth {cur} / {tot} 거래일",
        )

    kospi_recs: list = []
    if kospi_p is not None:
        kospi_recs = calc_breadth(kospi_p, "KOSPI", progress_callback=on_prog)

    bar.progress(0, text="KOSDAQ 계산…")
    kosdaq_recs: list = []
    if kosdaq_p is not None:
        kosdaq_recs = calc_breadth(kosdaq_p, "KOSDAQ", progress_callback=on_prog)

    bar.progress(1.0, text="완료")
    return kospi_recs, kosdaq_recs


def render_market(label: str, recs: list, idx_df: pd.DataFrame | None, chart_tail: int) -> None:
    if not recs:
        st.warning(f"{label}: 계산된 데이터가 없습니다.")
        return
    df = records_to_frame(recs, idx_df, chart_tail)
    if df.empty:
        st.warning(f"{label}: 표시할 구간이 없습니다.")
        return

    last = recs[-1]
    r1, r2, r3, r4 = st.columns(4)
    r1.metric("기준일", str(last["date"]))
    r2.metric("200일 상회 비율", f"{last['ma200_pct']}%")
    r3.metric("50일 상회 비율", f"{last['ma50_pct']}%")
    r4.metric("20일 상회 비율", f"{last['ma20_pct']}%")
    r5, r6, r7 = st.columns(3)
    r5.metric("52주 신고가 종목 수", int(last["nh"]))
    r6.metric("52주 신저가 종목 수", int(last["nl"]))
    r7.metric("표시 구간 거래일 수", len(df))

    if "지수종가" in df.columns and df["지수종가"].notna().any():
        st.subheader("지수 종가")
        st.line_chart(df[["지수종가"]])

    st.subheader("이동평균선 상회 비율 (%)")
    st.line_chart(
        df[["ma200_pct", "ma50_pct", "ma20_pct"]].rename(
            columns={
                "ma200_pct": "200일(%)",
                "ma50_pct": "50일(%)",
                "ma20_pct": "20일(%)",
            }
        )
    )

    st.subheader("52주 신고가 / 신저가 (종목 수)")
    st.line_chart(df[["nh", "nl"]].rename(columns={"nh": "신고가", "nl": "신저가"}))

    with st.expander("원본 수치 표"):
        disp = df.reset_index()
        disp["date"] = disp["date"].dt.strftime("%Y-%m-%d")
        st.dataframe(disp, use_container_width=True, hide_index=True)


# ── 사이드바 ──
with st.sidebar:
    st.header("설정")
    days = st.slider(
        "분석 윈도우 (영업일)",
        min_value=60,
        max_value=400,
        value=201,
        help="내부적으로 `get_market_data(days=…)`에 전달됩니다.",
    )
    chart_tail = st.slider(
        "차트·표에 쓸 최근 거래일 수",
        min_value=20,
        max_value=200,
        value=63,
    )
    show_kospi = st.checkbox("KOSPI 표시", value=True)
    show_kosdaq = st.checkbox("KOSDAQ 표시", value=True)
    st.divider()
    also_save_default = st.checkbox(
        f"엑셀 생성 시 기본 파일에도 저장",
        value=False,
        help=f"체크 시 `{EXCEL_FILE.name}` 경로에 복사합니다.",
    )

    run_clicked = st.button(
        "데이터 다시 로드 및 계산",
        type="primary",
        use_container_width=True,
        help="슬라이더의 영업일 수를 바꾼 뒤 여기서 다시 불러올 수 있습니다.",
    )

# ── 본문 ──
st.title("Market Breadth — 웹 패널")
st.caption("로컬 `market_breadth.py`와 동일한 수집·계산 로직 (FinanceDataReader + 피클 캐시) · **첫 방문 시 자동으로 데이터를 불러옵니다.**")

if run_clicked:
    _run_market_pipeline(days, from_button=True)
elif st.session_state.mb_data is None and not st.session_state._mb_autoload_once:
    st.session_state._mb_autoload_once = True
    _run_market_pipeline(days, from_button=False)

data = st.session_state.mb_data
kospi_recs = st.session_state.mb_kospi_recs
kosdaq_recs = st.session_state.mb_kosdaq_recs

if data is None:
    st.warning(
        "실시간 캐시 데이터가 없습니다. **엑셀 저장본** 탭에서 기존 `market_breadth_tracker.xlsx`를 확인하거나, "
        "왼쪽 **데이터 다시 로드 및 계산**으로 재시도하세요."
    )

if not show_kospi and not show_kosdaq:
    st.warning("KOSPI 또는 KOSDAQ 중 하나 이상을 표시로 선택하세요.")
    st.stop()

tab_labels: list[str] = []
if show_kospi:
    tab_labels.append("KOSPI")
if show_kosdaq:
    tab_labels.append("KOSDAQ")

view_src1, view_src2 = st.tabs(["실시간 (캐시·FDR)", "엑셀 저장본"])

with view_src1:
    if data is None:
        st.info("실시간 탭: 데이터가 로드되면 여기에 동일한 차트가 표시됩니다.")
    else:
        tabs = st.tabs(tab_labels)
        idx_tab = 0
        if show_kospi:
            with tabs[idx_tab]:
                render_market("KOSPI", kospi_recs or [], data.get("kospi_index"), chart_tail)
            idx_tab += 1
        if show_kosdaq:
            with tabs[idx_tab]:
                render_market("KOSDAQ", kosdaq_recs or [], data.get("kosdaq_index"), chart_tail)

with view_src2:
    st.caption(f"파일: `{EXCEL_FILE}` (`read_tracker_excel`)")
    if EXCEL_FILE.is_file():
        try:
            mtime = datetime.fromtimestamp(EXCEL_FILE.stat().st_mtime)
            st.caption(f"수정 시각: {mtime:%Y-%m-%d %H:%M:%S}")
        except OSError:
            pass
    excel_bundle = read_tracker_excel(EXCEL_FILE)
    ex_k = excel_bundle.get("kospi_records") or []
    ex_q = excel_bundle.get("kosdaq_records") or []
    if not ex_k and not ex_q:
        st.info(
            "저장된 엑셀이 없거나 시트를 읽지 못했습니다. "
            "`market_breadth.py` 실행 또는 아래 **엑셀 워크북 생성**으로 파일을 만든 뒤 다시 확인하세요."
        )
    else:
        tabs_x = st.tabs(tab_labels)
        xi = 0
        if show_kospi:
            with tabs_x[xi]:
                st.subheader("KOSPI_데이터 시트")
                if ex_k:
                    st.dataframe(pd.DataFrame(ex_k), use_container_width=True, hide_index=True, height=320)
                    render_market(
                        "KOSPI (엑셀)",
                        ex_k,
                        excel_bundle.get("kospi_index"),
                        chart_tail,
                    )
                else:
                    st.warning("KOSPI_데이터 시트가 비어 있거나 없습니다.")
            xi += 1
        if show_kosdaq:
            with tabs_x[xi]:
                st.subheader("KOSDAQ_데이터 시트")
                if ex_q:
                    st.dataframe(pd.DataFrame(ex_q), use_container_width=True, hide_index=True, height=320)
                    render_market(
                        "KOSDAQ (엑셀)",
                        ex_q,
                        excel_bundle.get("kosdaq_index"),
                        chart_tail,
                    )
                else:
                    st.warning("KOSDAQ_데이터 시트가 비어 있거나 없습니다.")

st.divider()
st.subheader("엑셀보내기")
has_any = data is not None and (bool(kospi_recs) or bool(kosdaq_recs))
gen = st.button(
    "엑셀 워크북 생성",
    disabled=not has_any,
    help="Premium Edition과 동일한 시트·차트 구성입니다. (실시간 데이터가 있을 때만)",
)

if gen and has_any and data is not None:
    try:
        fd, tmp_path = tempfile.mkstemp(suffix=".xlsx")
        os.close(fd)
        tmp = Path(tmp_path)
        build_excel(
            data,
            kospi_recs or [],
            kosdaq_recs or [],
            excel_path=tmp,
        )
        st.session_state.mb_xlsx_bytes = tmp.read_bytes()
        tmp.unlink(missing_ok=True)

        if also_save_default:
            EXCEL_FILE.write_bytes(st.session_state.mb_xlsx_bytes)
            st.info(f"기본 경로에 저장했습니다: `{EXCEL_FILE}`")

        st.success("워크북이 준비되었습니다. 아래에서 다운로드하세요.")
    except Exception as e:  # noqa: BLE001
        st.exception(e)

if st.session_state.mb_xlsx_bytes:
    st.download_button(
        label="Excel 파일 다운로드",
        data=st.session_state.mb_xlsx_bytes,
        file_name=f"market_breadth_{datetime.now():%Y%m%d_%H%M}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )
