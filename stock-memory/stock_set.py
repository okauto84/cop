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
model_name = "gpt-5-mini"
# model_name = "gpt-5.4"

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

            # RAW 시트에서 A1:F52 범위를 잘라 A1 행을 헤더로 사용하는 DataFrame 생성
            raw_df = st.session_state.sheet_table_raw
            raw_range_df = pd.DataFrame()
            if raw_df is not None and not raw_df.empty:
                # A~F 열(0~5), 1행~52행 → index 기준 0~51
                raw_slice = raw_df.iloc[0:52, 0:6].copy()
                # 첫 행(원래 A1:F1)을 헤더로 사용하되, 중복 헤더는 _1, _2 ... 를 붙여 유니크하게 만든다.
                header_row = raw_slice.iloc[0].astype(str).str.strip().tolist()
                seen: dict[str, int] = {}
                unique_headers: list[str] = []
                for h in header_row:
                    if h in seen:
                        seen[h] += 1
                        unique_headers.append(f"{h}_{seen[h]}")
                    else:
                        seen[h] = 0
                        unique_headers.append(h)
                raw_slice.columns = unique_headers
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
    # Total 시트: 기존 stock.py의 Objects 렌더링 스타일을 그대로 사용하기 위해
    # A/B 컬럼을 object 하나로 간주하여 dict 로 변환 (한 종목 row 라는 가정)
    col_a, col_b = context_total.columns[0], context_total.columns[1]
    obj: dict[str, str] = {}
    for _, row in context_total.iterrows():
        k = row[col_a]
        v = row[col_b]
        k_str = "" if pd.isna(k) else str(k).strip()
        v_str = "" if pd.isna(v) else str(v).strip()
        if k_str == "" and v_str == "":
            continue
        obj[k_str] = v_str

    # ===== 이평 배열 / 거래량 배열 계산 =====
    def _parse_num_for_ordering(s: str | None):
        if s is None:
            return None
        txt = str(s).strip().replace(",", "")
        if txt == "":
            return None
        try:
            return float(txt)
        except (ValueError, TypeError):
            return None

    # 이평 배열: 현재가, 이평(5), 이평(10), 이평(20), 이평(50) 큰 값 순서
    price_order_targets = [
        ("현재가", "현재가"),
        ("이평(5)", "이평(5)"),
        ("이평(10)", "이평(10)"),
        ("이평(20)", "이평(20)"),
        ("이평(50)", "이평(50)"),
    ]
    price_pairs: list[tuple[str, float]] = []
    for key_name, label in price_order_targets:
        val = _parse_num_for_ordering(obj.get(key_name))
        if val is not None:
            price_pairs.append((label, val))
    if price_pairs:
        price_pairs.sort(key=lambda x: x[1], reverse=True)
        obj["이평 배열"] = " > ".join(label for label, _ in price_pairs)

    # 거래량 배열: 거래량(현재), 거래량(10), 거래량(30), 거래량(50) 큰 값 순서
    volume_order_targets = [
        ("거래량(현재)", "거래량(현재)"),
        ("거래량(10)", "거래량(10)"),
        ("거래량(30)", "거래량(30)"),
        ("거래량(50)", "거래량(50)"),
    ]
    volume_pairs: list[tuple[str, float]] = []
    for key_name, label in volume_order_targets:
        val = _parse_num_for_ordering(obj.get(key_name))
        if val is not None:
            volume_pairs.append((label, val))
    if volume_pairs:
        volume_pairs.sort(key=lambda x: x[1], reverse=True)
        obj["거래량 배열"] = " > ".join(label for label, _ in volume_pairs)

    # ===== 이평 분류 / 거래량 분류 / 종합 분류 (OpenAI + RAW data 기반, 단일 호출) =====
    try:
        raw_df_for_ma = context_raw_range
        if API_KEY and raw_df_for_ma is not None and not raw_df_for_ma.empty:
            # RAW data 전체를 그대로 전달
            raw_ma_data = raw_df_for_ma.to_dict(orient="records")

            client = OpenAI(api_key=API_KEY)

            ma_class_labels = [
                "🚀 [정배열] 상승 가속 (최적 매수)",
                "💣 [역배열] 하락 확정 (접근 금지)",
                "🎯 [상승 중 눌림목] VCP 셋업 대기 (기회)",
                "⚠️ [데드캣 바운스] 역배열 내 반등 (주의)",
                "⚡ [추세 재개] 골든크로스 발생 (추격)",
                "🔍 [혼조세] 방향성 탐색 구간",
            ]
            vol_class_labels = [
                "🔥 에너지 분출 (돌파/추세 가속)",
                "📉 거래량 고갈 (Dry-up/매도 소진)",
                "💤 단기 과열 후 휴식 (관망)",
                "🔍 거래량 혼조 (추세 탐색)",
            ]
            total_class_labels = [
                "🚀 [최적 매수] 추세 가속 구간",
                "🎯 [VCP 셋업] 폭발 전 수렴 구간",
                "💣 [강력 매도] 하락 가속/투매 발생",
                "⏸️ [보유/눌림목] 건전한 조정 구간",
                "📉 [바닥 탐색] 하락 에너지 소진",
                "⚡ [신규 진입] 단기 모멘텀 발생",
                "🔍 [관망] 확실한 신호 대기",
            ]

            system_msg = (
                "당신은 마크 미너비니, 윌리엄 오닐의 수제자로, 추세 추종 돌파 매매를 전문으로 하는 전문 주식 투자자이다. "
                "아래 Total 객체 정보(요약 데이터)와 RAW 시계열 데이터(가격, 이동평균선, 거래량, 거래량 평균)를 함께 분석하라. "
                "다음 세 가지 분류 값을 각각 하나씩 선택해야 한다.\n\n"
                "1) 이평 분류: 이동평균선 배열과 추세를 기준으로 아래 [이평 분류표] 중 1개 선택\n"
                "2) 거래량 분류: 거래량 및 거래량(평균)을 기준으로 아래 [거래량 분류표] 중 1개 선택\n"
                "3) 종합 분류: 가격, 이평, 거래량, 수익률 등을 모두 고려한 종합 판단으로 [종합 분류표] 중 1개 선택\n\n"
                "반드시 아래 JSON 형식으로만 답하라.\n"
                '{\"ma_class\": \"<이평 분류표의 라벨 중 하나>\", '
                '\"volume_class\": \"<거래량 분류표의 라벨 중 하나>\", '
                '\"total_class\": \"<종합 분류표의 라벨 중 하나>\"}\n\n'
                "다른 설명, 문장, 코멘트는 절대 쓰지 마라.\n\n"
                "[이평 분류표]\n- "
                + "\n- ".join(ma_class_labels)
                + "\n\n[거래량 분류표]\n- "
                + "\n- ".join(vol_class_labels)
                + "\n\n[종합 분류표]\n- "
                + "\n- ".join(total_class_labels)
            )

            user_payload = {
                "Total_Object": obj,
                "RAW_Table": raw_ma_data,
            }
            user_msg = "Total 및 RAW 데이터:\n" + json.dumps(user_payload, ensure_ascii=False, indent=2)

            resp = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": user_msg},
                ],
            )
            raw_content = (resp.choices[0].message.content or "").strip()

            ma_chosen_label = None
            vol_chosen_label = None
            total_chosen_label = None

            try:
                parsed = json.loads(raw_content)
                ma_raw_label = str(parsed.get("ma_class", "")).strip()
                vol_raw_label = str(parsed.get("volume_class", "")).strip()
                total_raw_label = str(parsed.get("total_class", "")).strip()
            except Exception:
                ma_raw_label = raw_content
                vol_raw_label = raw_content
                total_raw_label = raw_content

            for label in ma_class_labels:
                if label in ma_raw_label or ma_raw_label == label:
                    ma_chosen_label = label
                    break
            for label in vol_class_labels:
                if label in vol_raw_label or vol_raw_label == label:
                    vol_chosen_label = label
                    break
            for label in total_class_labels:
                if label in total_raw_label or total_raw_label == label:
                    total_chosen_label = label
                    break

            if ma_chosen_label:
                obj["이평 분류"] = ma_chosen_label
            if vol_chosen_label:
                obj["거래량 분류"] = vol_chosen_label
            if total_chosen_label:
                obj["종합 분류"] = total_chosen_label

            # 프롬프트 내용을 세션에 저장하여 화면 하단에 표시할 수 있도록 함
            st.session_state["ma_prompt_system"] = ma_system_msg
            st.session_state["ma_prompt_user"] = ma_user_msg
            st.session_state["vol_prompt_system"] = vol_system_msg
            st.session_state["vol_prompt_user"] = vol_user_msg
    except Exception:
        # 분류 실패 시 조용히 무시 (이평/거래량 분류 미설정)
        pass

    sheet_objects_total = [obj]
    if "sheet_objects_total_json" not in st.session_state:
        st.session_state.sheet_objects_total_json = []
    st.session_state.sheet_objects_total_json = sheet_objects_total

    # stock.py 의 Objects 와 동일한 스타일로 Total data 출력
    if sheet_objects_total:
        st.markdown("#### Objects")
        for obj in sheet_objects_total:
            object_name = next(iter(obj.keys()), "") if obj else ""
            label = object_name or "(빈 객체)"
            with st.expander(label, expanded=True):
                bold_keys = {"이평 배열", "이평 분류", "거래량 배열", "거래량 분류", "종합 분류"}

                def _parse_num(s):
                    if s is None or str(s).strip() == "":
                        return None
                    try:
                        return float(str(s).strip().replace(",", ""))
                    except (ValueError, TypeError):
                        return None

                # 거래량 막대 비교를 위한 값 수집
                # 내부 데이터는 '거래량(현재)' 를 기준으로 하고,
                # 화면에는 '거래량(현재)' / '거래량(1)' 둘 다 막대를 그려줄 수 있도록 처리
                volume_keys_source = ["거래량(현재)", "거래량(10)", "거래량(30)", "거래량(50)"]
                volume_values_source = {vk: _parse_num(obj.get(vk)) for vk in volume_keys_source}
                max_vol = max((v for v in volume_values_source.values() if v is not None), default=None)

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
                    # --- 거래량 막대 ---
                    src_key_for_volume = None
                    if k == "거래량(1)":
                        # '거래량(1)' 은 내부적으로 '거래량(현재)' 값을 사용
                        src_key_for_volume = "거래량(현재)"
                    elif k in volume_keys_source:
                        src_key_for_volume = k

                    if src_key_for_volume and max_vol and volume_values_source.get(src_key_for_volume) is not None:
                        ratio = max(volume_values_source[src_key_for_volume] / max_vol, 0)
                        bar_blocks = int(ratio * 20)  # 최대 20칸
                        bar_color = "#1f2933"
                    elif k in price_keys and max_price and price_values.get(k) is not None:
                        ratio = max(price_values[k] / max_price, 0)
                        bar_blocks = int(ratio * 20)  # 최대 20칸
                        bar_color = "#1f2933"  # 이평/가격도 동일하게 검은색 막대 사용
                    if cell_b_html is None and (src_key_for_volume or k in price_keys) and (max_vol or max_price):
                        has_volume = src_key_for_volume is not None and volume_values_source.get(src_key_for_volume) is not None
                        has_price = k in price_keys and price_values.get(k) is not None
                        if has_volume or has_price:
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

    # RAW 시트 A1:F52 DataFrame 출력 (첫 행 A1:F1을 헤더로 사용)
    if context_raw_range is not None and not context_raw_range.empty:
        st.markdown("##### RAW Data")
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

    # OpenAI API 호출 (Total objects JSON + RAW DataFrame 기반으로 이해·답변하도록 시스템 프롬프트 구성)
    with st.chat_message("assistant"):
        # Total 시트 object 데이터와 RAW 시트 테이블 데이터를 모두 포함
        objects_total = st.session_state.get("sheet_objects_total_json", [])
        raw_df_for_prompt = st.session_state.get("sheet_table_raw_range", pd.DataFrame())
        raw_records: list[dict] = []
        if raw_df_for_prompt is not None and not raw_df_for_prompt.empty:
            raw_records = raw_df_for_prompt.to_dict(orient="records")
        objects_data = {
            "Total": objects_total,
            "RAW": raw_records,
        }
        system_prompt = (
            "당신은 마크 미너비니, 윌리엄 오닐의 수제자로, 추세 추종 돌파 매매를 전문으로 하는 전문 주식 투자자로서, 아래 objects / RAW data를 참고하여 질문에 답변하고 조언을 하시오. "
            "Objects 데이터는 종목별 요약 객체 목록이며, RAW 데이터는 거래일 날자별 종가, 이동평균선, 거래량, 거래량, 거래량(평균)의 원천 데이터 테이블입니다. "
            "이평 분류, 거래량 분류, 종합 분류 값 등에 구애받지 말고, 두 데이터를 함께 고려해 사용자 질의에 맞게 구체적으로 답변하세요. \n\n"
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