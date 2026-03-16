# -*- coding: utf-8 -*-

import streamlit as st
from openai import OpenAI
import time
import pandas as pd
import re
import json
import html

# 페이지 설정
st.set_page_config(
    page_title="Stock",
    page_icon="🔍",
    layout="wide"
)

# API 키 설정 (secrets에서 가져오거나 기본값 사용)
try:
    API_KEY = st.secrets.get("openai_api_key", "")
except:
    API_KEY = ""

# Google Sheet URL (secrets에서 가져오거나 기본값 사용)
try:
    google_sheet_url = st.secrets.get("google_sheet_url", "")
except:
    google_sheet_url = ""

# 사이드바 제거 후 사용하던 설정값 (메인에서 기본값으로 사용)
output_method = "실시간 출력"
# model_name = "gpt-5-mini"
model_name = "gpt-5.4"

# 메인 화면
st.markdown("### Stock-set")


def _sheet_url_to_export_csv(url: str, sheet_name: str | None = None) -> str:
    """공개 스프레드시트 URL을 CSV 내보내기 URL로 변환.
    sheet_name이 주어지면 해당 이름의 시트를, 없으면 첫 번째 시트를 CSV로 내보낸다.
    """
    url = (url or "").strip()
    if not url:
        return ""
    # /d/SPREADSHEET_ID/ 형태 추출
    m = re.search(r"/d/([a-zA-Z0-9_-]+)", url)
    if not m:
        return ""
    sid = m.group(1)
    # sheet 이름이 명시되면 gviz/tq API로 해당 시트만 CSV로 가져온다.
    if sheet_name:
        return (
            f"https://docs.google.com/spreadsheets/d/{sid}/gviz/tq"
            f"?tqx=out:csv&sheet={sheet_name}"
        )
    # sheet_name이 없으면 첫 번째 시트를 기본으로 export
    return f"https://docs.google.com/spreadsheets/d/{sid}/export?format=csv"


def _read_gsheet(url: str = None, sheet_name: str | None = None) -> tuple[pd.DataFrame, str]:
    """공개 Google Sheet URL에서 지정된 시트를 읽기.
    sheet_name이 None이면 첫 번째 시트(기본 시트)를 읽는다.
    (DataFrame, 에러메시지) 반환. 성공 시 에러메시지는 ''.
    """
    u = (url or "").strip()
    if not u:
        return pd.DataFrame(), "google_sheet_url이 비어 있습니다."
    export_url = _sheet_url_to_export_csv(u, sheet_name=sheet_name)
    if not export_url:
        return pd.DataFrame(), "URL 형식이 올바르지 않습니다. 예: https://docs.google.com/spreadsheets/d/스프레드시트ID/edit"
    try:
        # header=None: 첫 행부터 데이터로 사용(첫 행이 잘리지 않음)
        df = pd.read_csv(export_url, header=None)
        if df is not None and len(df.columns) > 0:
            df.columns = df.columns.astype(str).str.strip()
            return df, ""
        return pd.DataFrame(), "시트에 컬럼이 없거나 비어 있습니다."
    except Exception as e:
        err = str(e).strip()
        if "403" in err or "Forbidden" in err or "Access" in err.lower():
            return pd.DataFrame(), "시트에 대한 접근이 거부되었습니다. 시트를 '링크가 있는 모든 사용자에게 공개'로 설정하세요."
        if "404" in err or "Not Found" in err:
            return pd.DataFrame(), "시트를 찾을 수 없습니다. URL과 시트 존재 여부를 확인하세요."
        return pd.DataFrame(), f"읽기 오류: {err}"


# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []


# Google Sheet URL로 불러와 시트 영역을 테이블(DataFrame)로 변환하여 변수에 저장
def load_sheet_as_table(url: str) -> tuple[pd.DataFrame, pd.DataFrame, str]:
    """Google Sheet URL을 받아
    - 첫 번째 시트 'Total'
    - 두 번째 시트 'RAW'
    를 각각 table 형태(DataFrame)로 변환하여 반환.
    (total_df, raw_df, 에러메시지) 반환. (둘 중 하나라도 실패 시 에러메시지에 포함)
    """
    total_df, err_total = _read_gsheet(url, sheet_name="Total")
    raw_df, err_raw = _read_gsheet(url, sheet_name="RAW")
    errs = []
    if err_total:
        errs.append(f"Total 시트 오류: {err_total}")
    if err_raw:
        errs.append(f"RAW 시트 오류: {err_raw}")
    return total_df, raw_df, "\n".join(errs)


# 세션에 저장된 테이블(내용) 초기화
if "sheet_table_total" not in st.session_state:
    st.session_state.sheet_table_total = pd.DataFrame()
if "sheet_table_raw" not in st.session_state:
    st.session_state.sheet_table_raw = pd.DataFrame()
if "sheet_table_raw_range" not in st.session_state:
    # RAW 시트에서 A2:F53 구간을 잘라낸 DataFrame
    st.session_state.sheet_table_raw_range = pd.DataFrame()
if "expand_object_name" not in st.session_state:
    st.session_state.expand_object_name = None
if "expand_all" not in st.session_state:
    st.session_state.expand_all = None  # None=개별, True=모두 펼치기, False=모두 접기

# google sheet 불러오기 버튼
load_clicked = st.button("google sheet 불러오기")

if load_clicked:
    url = (google_sheet_url or "").strip()
    if not url:
        st.error("Streamlit secrets에 google_sheet_url을 설정하세요.")
    else:
        # URL로 불러와 table 형태로 변환 후 변수에 저장
        sheet_table_total, sheet_table_raw, err_msg = load_sheet_as_table(url)
        if err_msg:
            st.error(f"시트를 불러올 수 없습니다.\n{err_msg}")
        elif sheet_table_total is not None and len(sheet_table_total.columns) > 0:
            st.session_state.sheet_table_total = sheet_table_total
            st.session_state.sheet_table_raw = sheet_table_raw if sheet_table_raw is not None else pd.DataFrame()

            # RAW 시트에서 A2:F53 범위를 잘라 A2 행을 헤더로 사용하는 DataFrame 생성
            raw_df = st.session_state.sheet_table_raw
            raw_range_df = pd.DataFrame()
            if raw_df is not None and not raw_df.empty:
                # A~F 열(0~5), 2행~53행 → index 기준 1~52
                raw_slice = raw_df.iloc[1:53, 0:6].copy()
                # 첫 행(원래 A2:F2)을 헤더로 사용
                raw_slice.columns = (
                    raw_slice.iloc[0].astype(str).str.strip()
                )
                raw_range_df = raw_slice.iloc[1:].reset_index(drop=True)
            st.session_state.sheet_table_raw_range = raw_range_df
            st.session_state.expand_object_name = None
            st.session_state.expand_all = True  # 불러오기 시 모든 카드(expander) 펼침
            st.success("Google Sheet를 불러왔습니다.")
            st.rerun()
        else:
            st.error("시트를 불러올 수 없습니다. google_sheet_url과 시트 공개(링크로 볼 수 있음) 설정을 확인하세요.")

# 저장된 테이블 변수 (시트 내용 = context)
context_total = st.session_state.sheet_table_total
context_raw = st.session_state.sheet_table_raw
context_raw_range = st.session_state.sheet_table_raw_range


def _parse_sheet_to_objects(df: pd.DataFrame, empty_rows: int = 3) -> list[dict]:
    """연속 empty_rows줄의 빈 행으로 구분된 블록을 별도 object로 파싱. A열=key, B열=value. JSON 형식 리스트 반환."""
    if df is None or len(df) == 0 or df.columns.size < 2:
        return []
    # 첫 두 컬럼(A열=0, B열=1) 사용
    col_a, col_b = df.columns[0], df.columns[1]
    objects: list[dict] = []
    current: list[tuple[str, str]] = []
    empty_streak = 0

    for _, row in df.iterrows():
        a = row[col_a]
        b = row[col_b]
        a_str = "" if pd.isna(a) else str(a).strip()
        b_str = "" if pd.isna(b) else str(b).strip()
        if a_str == "" and b_str == "":
            empty_streak += 1
            if empty_streak >= empty_rows:
                if current:
                    objects.append(dict(current))
                current = []
        else:
            empty_streak = 0
            current.append((a_str, b_str))

    if current:
        objects.append(dict(current))
    return objects


if context_total is not None and len(context_total) > 0:
    # 행 3줄 빈 곳으로 구분 → A열=key, B열=value 객체 리스트(JSON)로 변수 저장 (Total 시트)
    sheet_objects_total = _parse_sheet_to_objects(context_total, empty_rows=3)
    if "sheet_objects_total_json" not in st.session_state:
        st.session_state.sheet_objects_total_json = []
    st.session_state.sheet_objects_total_json = sheet_objects_total

    # RAW 시트도 동일하게 파싱
    sheet_objects_raw = []
    if context_raw is not None and len(context_raw) > 0:
        sheet_objects_raw = _parse_sheet_to_objects(context_raw, empty_rows=3)
    if "sheet_objects_raw_json" not in st.session_state:
        st.session_state.sheet_objects_raw_json = []
    st.session_state.sheet_objects_raw_json = sheet_objects_raw

    # Total 시트 Objects 출력
    if sheet_objects_total:
        col_title, col_collapse, col_expand = st.columns([2, 0.5, 0.5])
        with col_title:
            st.markdown("#### Total 시트 Objects")
        with col_collapse:
            if st.button("모두 접기", key="collapse_all"):
                st.session_state.expand_all = False
                st.rerun()
        with col_expand:
            if st.button("모두 펼치기", key="expand_all_btn"):
                st.session_state.expand_all = True
                st.rerun()
        expand_all = st.session_state.get("expand_all")
        expand_name = st.session_state.get("expand_object_name")
        for obj in sheet_objects_total:
            object_name = next(iter(obj.keys()), "") if obj else ""
            label = object_name or "(빈 객체)"
            if expand_all is True:
                expanded = True
            elif expand_all is False:
                expanded = False
            else:
                expanded = (expand_name is not None and object_name == expand_name)
            with st.expander(label, expanded=expanded):
                bold_keys = {"이평 배열", "이평 분류", "거래량 배열", "거래량 분류", "종합 분류"}

                def _parse_num(s):
                    if s is None or str(s).strip() == "":
                        return None
                    try:
                        return float(str(s).strip().replace(",", ""))
                    except (ValueError, TypeError):
                        return None

                # 거래량 막대 비교를 위한 값 수집
                volume_keys = ["거래량(현재)", "거래량(10)", "거래량(30)", "거래량(50)"]
                volume_values = {vk: _parse_num(obj.get(vk)) for vk in volume_keys}
                max_vol = max((v for v in volume_values.values() if v is not None), default=None)

                # 이평/가격 막대 비교를 위한 값 수집
                price_keys = ["이평(5)", "이평(10)", "이평(20)", "이평(50)", "현재가", "평균단가"]
                price_values = {pk: _parse_num(obj.get(pk)) for pk in price_keys}
                max_price = max((v for v in price_values.values() if v is not None), default=None)

                table_rows = []
                for k, v in obj.items():
                    k_esc = html.escape(str(k))
                    v_esc = html.escape(str(v))
                    row_style = ""
                    if k == "평균단가":
                        avg_price = _parse_num(v)
                        curr_price = _parse_num(obj.get("현재가"))
                        if avg_price is not None and curr_price is not None:
                            if avg_price > curr_price:
                                row_style = ' style="color:blue;"'
                            elif avg_price < curr_price:
                                row_style = ' style="color:red;"'
                    elif k == "수익률":
                        # 화면에는 % 포함 그대로 표시, 색 판단 시에만 % 제거 후 숫자로 파싱
                        rate_str = str(v).replace("%", "").strip() if v is not None else ""
                        rate = _parse_num(rate_str) if rate_str else None
                        if rate is not None:
                            if rate > 0:
                                row_style = ' style="color:red;"'
                            elif rate < 0:
                                row_style = ' style="color:blue;"'

                    # 거래량 및 이평/가격 값은 막대 그래프 형태로 표현
                    cell_b_html = None
                    if k in volume_keys and max_vol and volume_values.get(k) is not None:
                        ratio = max(volume_values[k] / max_vol, 0)
                        bar_blocks = int(ratio * 20)  # 최대 20칸
                        bar_color = "#1f2933"
                    elif k in price_keys and max_price and price_values.get(k) is not None:
                        ratio = max(price_values[k] / max_price, 0)
                        bar_blocks = int(ratio * 20)  # 최대 20칸
                        bar_color = "#1f2933"  # 이평/가격도 동일하게 검은색 막대 사용
                    if cell_b_html is None and (k in volume_keys or k in price_keys) and (max_vol or max_price):
                        if (k in volume_keys and volume_values.get(k) is not None) or (k in price_keys and price_values.get(k) is not None):
                            bar_html = (
                                '<div style="display:flex;align-items:center;gap:8px;">'
                                f'<div style="display:inline-block;height:12px;">'
                                f'{"".join([f"<span style=\'display:inline-block;width:4px;height:10px;background-color:{bar_color};margin-right:1px;\'></span>" for _ in range(bar_blocks)])}'
                                f"</div>"
                                f'<span style="font-family:monospace;font-size:0.8rem;">{v_esc}</span>'
                                "</div>"
                            )
                            cell_b_html = bar_html

                    if cell_b_html is None:
                        wrap_val = "<b>{}</b>" if k in bold_keys else "{}"
                        cell_b_html = wrap_val.format(v_esc)

                    wrap_key = "<b>{}</b>" if k in bold_keys else "{}"
                    cell_a_html = wrap_key.format(k_esc)
                    table_rows.append(f"<tr{row_style}><td>{cell_a_html}</td><td>{cell_b_html}</td></tr>")

                table_html = (
                    '<div style="font-size:0.8rem;">'
                    '<table style="width:100%; border-collapse: collapse;">'
                    "<thead><tr><th style=\"text-align:left; padding:4px 8px;\">key</th>"
                    "<th style=\"text-align:left; padding:4px 8px;\">value</th></tr></thead>"
                    "<tbody>" + "".join(table_rows) + "</tbody></table>"
                    "</div>"
                )
                st.markdown(table_html, unsafe_allow_html=True)

    # RAW 시트 Objects 출력
    if sheet_objects_raw:
        st.markdown("#### RAW 시트 Objects")
        for obj in sheet_objects_raw:
            object_name = next(iter(obj.keys()), "") if obj else ""
            label = object_name or "(빈 객체)"
            with st.expander(label, expanded=False):
                rows = []
                for k, v in obj.items():
                    k_esc = html.escape(str(k))
                    v_esc = html.escape(str(v))
                    rows.append(f"<tr><td>{k_esc}</td><td>{v_esc}</td></tr>")
                table_html = (
                    '<div style="font-size:0.8rem;">'
                    '<table style="width:100%; border-collapse: collapse;">'
                    "<thead><tr><th style=\"text-align:left; padding:4px 8px;\">key</th>"
                    "<th style=\"text-align:left; padding:4px 8px;\">value</th></tr></thead>"
                    "<tbody>" + "".join(rows) + "</tbody></table>"
                    "</div>"
                )
                st.markdown(table_html, unsafe_allow_html=True)

    # RAW 시트 A2:F53 DataFrame 출력 (첫 행 A2:F2를 헤더로 사용)
    if context_raw_range is not None and not context_raw_range.empty:
        st.markdown("#### RAW 시트 DataFrame (A2:F53)")
        st.dataframe(context_raw_range)
else:
    st.info("Google Sheet를 불러오기 클릭하면 여기에 내용이 표시됩니다.")

st.markdown("---")

# 챗봇 섹션
st.markdown("#### 💬 위 데이터 기반 질의응답")


# OpenAI API 호출 함수
def call_openai_api(messages: list) -> str:
    """OpenAI API를 호출하는 함수"""
    try:
        if not API_KEY or API_KEY == "":
            return "⚠️ API 키가 설정되지 않았습니다. Streamlit secrets의 openai_api_key 또는 코드의 API_KEY 변수를 설정해주세요."

        client = OpenAI(api_key=API_KEY)

        response = client.chat.completions.create(
            model=model_name,
            messages=messages,
        )

        return response.choices[0].message.content

    except Exception as e:
        error_msg = str(e)
        if "API_KEY" in error_msg or "authentication" in error_msg.lower() or "invalid" in error_msg.lower():
            return f"🔑 API 키 오류: API 키를 확인해주세요.\n\n에러 상세: {error_msg}"
        elif "quota" in error_msg.lower() or "limit" in error_msg.lower() or "rate" in error_msg.lower():
            return f"📊 사용량 한도 초과: API 사용량을 확인해주세요.\n\n에러 상세: {error_msg}"
        else:
            return f"❌ API 호출 중 오류가 발생했습니다: {error_msg}"


# 이전 대화 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 사용자 입력 처리
if prompt := st.chat_input("질문해보세요!"):
    # 사용자 메시지 추가
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # OpenAI API 호출 (objects JSON을 바탕으로 이해·답변하도록 시스템 프롬프트 구성)
    with st.chat_message("assistant"):
        # Total / RAW 두 시트 데이터를 모두 포함
        objects_total = st.session_state.get("sheet_objects_total_json", [])
        objects_raw = st.session_state.get("sheet_objects_raw_json", [])
        objects_data = {
            "Total": objects_total,
            "RAW": objects_raw,
        }
        system_prompt = (
            "당신은 마크 미너비니, 윌리엄 오닐의 수제자로, 추세 추종 돌파 매매를 전문으로 하는 전문 주식 투자자로서, objects JSON 데이터를 고려하여 질문에 답변을 하고 조언을 하시오. "
            "아래 [참고 데이터]는 객체 목록이며, 각 객체는 key-value 쌍으로 구성되어 있습니다. "
            "이평 분류, 거래량 분류, 종합 분류 값에 상관없이, 이 데이터를 이해하고 사용자 질의에 맞게 답변하세요. \n\n"
            "[참고 데이터]\n"
            + (json.dumps(objects_data, ensure_ascii=False, indent=2) if objects_data else "(데이터 없음 - 먼저 Google Sheet를 불러오세요.)")
        )
        messages_for_api = [
            {"role": "system", "content": system_prompt},
            *[{"role": msg["role"], "content": msg["content"]} for msg in st.session_state.messages],
        ]

        if output_method == "실시간 출력":
            with st.spinner("OpenAI가 답변을 생성하고 있습니다..."):
                response = call_openai_api(messages_for_api)
            message_placeholder = st.empty()
            displayed_text = ""
            for char in response:
                displayed_text += char
                message_placeholder.markdown(displayed_text + "▌")
                time.sleep(0.01)
            message_placeholder.markdown(response)
        else:
            with st.spinner("OpenAI가 답변을 생성하고 있습니다..."):
                response = call_openai_api(messages_for_api)
            st.markdown(response)

    # AI 응답을 세션에 저장
    st.session_state.messages.append({"role": "assistant", "content": response})

# API 키 안내
if not API_KEY or API_KEY == "":
    st.warning("⚠️ OpenAI API 키가 설정되지 않았습니다. Streamlit secrets 또는 코드를 수정해주세요.")
    with st.expander("API 키 설정 방법"):
        st.markdown("""
        1. [OpenAI Platform](https://platform.openai.com/api-keys)에서 API 키를 발급받으세요.
        2. Streamlit secrets에 `openai_api_key`로 설정하거나
        3. 코드의 `API_KEY` 변수를 직접 수정하세요.

        ```python
        API_KEY = "your-actual-api-key-here"
        ```
        """)

# CSS 스타일 추가
st.markdown("""
<style>
    /* 표 아래 버튼 행: 간격 좁게, 글자·버튼 크기 작게 */
    .main [data-testid="stHorizontalBlock"] [data-testid="column"] .stButton > button {
        font-size: 0.75rem;
        padding: 0.15rem 0.35rem;
        min-height: 1.35rem;
    }
    .main [data-testid="stHorizontalBlock"] > div {
        padding-left: 0.15rem;
        padding-right: 0.15rem;
    }
    .stChatMessage {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .stTextInput > div > div > input {
        border-radius: 20px;
    }
    .main > div {
        padding-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)