# -*- coding: utf-8 -*-


import streamlit as st
import pandas as pd

# 화면 넓게 쓰기
st.set_page_config(layout="wide", page_title="AI 특허 검색 시스템")

# CSS: 여백, 시인성, 우측 사이드바 슬라이드 인
st.markdown("""
    <style>
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    div[data-testid="stText"] { font-size: 14px; }
    [data-testid="column"]:last-of-type .stMarkdown { animation: slideIn 0.3s ease-out; }
    @keyframes slideIn {
        from { opacity: 0; transform: translateX(20px); }
        to { opacity: 1; transform: translateX(0); }
    }
    </style>
""", unsafe_allow_html=True)

# 선택된 문헌(게시글) 인덱스 — 행 선택 시 사이드바에 상세 표시
if "selected_row_index" not in st.session_state:
    st.session_state.selected_row_index = None

# 검색 결과 샘플 데이터 (게시판 목록) — 상단 정의로 선택/사이드바에서 공유
RESULT_DATA = {
    "순번": [1, 2, 3, 4, 5],
    "구분": ["등록", "등록", "등록", "취하", "등록"],
    "CPC분류": ["G06V 20/70\nG06V 20/60", "G06V 10/774\nG06V 10/764", "G06V 20/41\nG06V 10/762", "G06T 7/10\nG06V 20/56", "G06N 3/084\nG06N 3/045"],
    "발명의 명칭": [
        "제로샷 시맨틱 분할 장치 및 방법",
        "소프트 교차-엔트로피 손실을 갖는 시맨틱 분할",
        "도메인 적응형 의미론적 영상 분할 장치 및 방법",
        "실시간 픽셀 단위 기반 시맨틱 분할 장치 및 시스템",
        "시맨틱 분할 모델을 위한 훈련 방법 및 장치, 전자 기기, 저장 매체"
    ],
    "출원번호": ["1020210165598", "1020217012976", "1020200176963", "1020210049720", "1020197038767"],
    "출원일자": ["20211126", "20191010", "20201217", "20210416", "20180727"]
}
df_result = pd.DataFrame(RESULT_DATA)
# 테이블 표시용: 순번 제거 (체크박스는 data_editor에서 selection_mode 없이 제거)
df_display = df_result.drop(columns=["순번"]).copy()

if "result_table_df" not in st.session_state:
    st.session_state.result_table_df = df_display.copy()
if "selected_row_index" not in st.session_state:
    st.session_state.selected_row_index = None

# 구분 선택 시 우측 사이드바 슬라이드 표시 (좌측+메인+우측)
_selected = st.session_state.selected_row_index
if _selected is not None:
    left_col, right_col, right_sidebar = st.columns([1, 3, 1])
else:
    left_col, right_col = st.columns([1, 4])
    right_sidebar = None

# ==========================================
# 좌측 패널: 검색 조건 및 구성요소
# ==========================================
with left_col:
    # 요청하신 '요약정보' 탭 추가
    tab_search, tab_summary = st.tabs(["입력 검색", "AI 요약"])
    
    with tab_search:
        # 출원번호 입력
        st.text_input("출원번호", value="1070210165598", label_visibility="collapsed")
        
        # 문장검색 영역
        st.radio("검색구분", ["문장검색"], label_visibility="collapsed")
        st.caption("문장검색은 청구항, 초록 등 일부 발췌 문장을 기반으로 유사 문서를 찾습니다. AND(&), OR(|) 연산자는 사용할 수 없습니다.")
        
        
        
        btn_col1, btn_col2 = st.columns(2)
        with btn_col1: st.button("🔍 검색", use_container_width=True)
        with btn_col2: st.button("🔄 초기화", use_container_width=True)
        
        st.divider()
        
        # 구성요소관련 영역
        st.markdown("**⚙️ 기술 구성요소**")
        comp_btn_col1, comp_btn_col2 = st.columns(2)
        with comp_btn_col1: st.button("구성요소추가", use_container_width=True)
        with comp_btn_col2: st.button("청구항", use_container_width=True)
        
        # 구성요소 리스트 (체크박스 + 텍스트)
        components = [
            "입력 이미지를 입력받아 신경망 연산을 통해 비주얼 특징맵을 출력하는 비주얼 인코더",
            "신경망 연산을 통해 클래스별 프로토타입 벡터를 출력하는 시맨틱 인코더",
            "상기 비주얼 특징맵의 픽셀별 채널 벡터를 비교하여 상기 비주얼 특징맵..."
        ]
        
        
        for i, comp in enumerate(components):
            c1, c2 = st.columns([1, 9])
            with c1: st.checkbox("", value=True, key=f"comp_{i}")
            with c2: st.info(comp) # 박스 형태로 텍스트 출력
            
        st.button("🔍 재검색", use_container_width=True, type="primary")

    with tab_summary:
        # 발명의 3요소 (AI 요약) — 그림과 동일한 카드 UI
        summary_html = """
<div style="font-family: 'Malgun Gothic', '맑은 고딕', sans-serif; max-width: 600px;">
    <div style="color: #1e3a8a; font-size: 1.15rem; font-weight: bold; margin-bottom: 16px;">
        💡 발명의 3요소 (AI 요약)
    </div>
    <div style="background-color: #fdf2f2; border: 1.5px solid #fecaca; border-radius: 8px; padding: 14px 12px; margin-bottom: 12px;">
        <div style="color: #b91c1c; font-weight: bold; font-size: 0.95rem; margin-bottom: 6px;">
            ⚠️ 해결과제 <span style="font-size: 0.8em; font-weight: normal;">(Problem)</span>
        </div>
        <div style="color: #374151; font-size: 0.9rem; line-height: 1.6;">
            창문형 에어컨 설치 시 본체와 커텐프레임 사이의 유격으로 인한 냉기 누설 및 조립 공정의 복잡함을 해결하고자 함.
        </div>
    </div>
    <div style="background-color: #f0fdf4; border: 1.5px solid #bbf7d0; border-radius: 8px; padding: 14px 12px; margin-bottom: 12px;">
        <div style="color: #15803d; font-weight: bold; font-size: 0.95rem; margin-bottom: 6px;">
            🎯 발명의 목적 <span style="font-size: 0.8em; font-weight: normal;">(Object)</span>
        </div>
        <div style="color: #374151; font-size: 0.9rem; line-height: 1.6;">
            베이스팬 내부에 관통형 가이드공을 형성하여 커텐프레임의 슬라이딩 기밀성을 극대화하고 외관을 미려하게 함.
        </div>
    </div>
    <div style="background-color: #eff6ff; border: 1.5px solid #bfdbfe; border-radius: 8px; padding: 14px 12px; margin-bottom: 12px;">
        <div style="color: #1d4ed8; font-weight: bold; font-size: 0.95rem; margin-bottom: 6px;">
            ✨ 발명의 효과 <span style="font-size: 0.8em; font-weight: normal;">(Effect)</span>
        </div>
        <div style="color: #374151; font-size: 0.9rem; line-height: 1.6;">
            부품 수 절감으로 제조 원가를 낮추며, 완벽한 밀폐를 통해 에어컨의 냉방 효율을 획기적으로 향상시킴.
        </div>
    </div>
</div>
"""
        st.markdown(summary_html, unsafe_allow_html=True)

# ==========================================
# 우측 패널: 검색 결과 데이터프레임
# ==========================================
with right_col:
    tab_info, tab_result = st.tabs(["⌂ INFO", "1020210165598 검색 ✕"])

    with tab_info:
        st.info("INFO 탭입니다. 필요한 안내 또는 정보를 여기에 표시할 수 있습니다.")

    with tab_result:
        # 보기 옵션
        st.selectbox("보기 옵션", ["50 건씩 보기", "100 건씩 보기", "200 건씩 보기"], label_visibility="collapsed", key="view_opt")

        # 게시판(검색 결과) — 순번·체크박스 없음, 구분 선택 시 우측 사이드바 표시
        구분_옵션 = list(df_display["구분"].unique())
        column_config = {
            "구분": st.column_config.SelectboxColumn("구분", options=구분_옵션, required=True),
            "CPC분류": st.column_config.TextColumn("CPC분류", disabled=True),
            "발명의 명칭": st.column_config.TextColumn("발명의 명칭", disabled=True),
            "출원번호": st.column_config.TextColumn("출원번호", disabled=True),
            "출원일자": st.column_config.TextColumn("출원일자", disabled=True),
        }
        edited_df = st.data_editor(
            st.session_state.result_table_df,
            column_config=column_config,
            key="result_editor",
            use_container_width=True,
            hide_index=True,
            height=600
        )
        # 구분 셀 선택(변경) 시 해당 행을 선택하고 우측 사이드바 표시
        prev_df = st.session_state.result_table_df
        for i in range(len(edited_df)):
            if i < len(prev_df) and edited_df.iloc[i]["구분"] != prev_df.iloc[i]["구분"]:
                st.session_state.selected_row_index = i
                break
        st.session_state.result_table_df = edited_df
        st.caption("테이블에서 '구분'을 선택하면 우측에 해당 문헌 상세가 슬라이드로 표시됩니다.")

        # 하단 페이징 (UI 모방)
        page_col1, page_col2, page_col3, page_col4 = st.columns([8, 0.5, 0.5, 0.5])
        with page_col1:
            st.caption("총 100 건 중 1 ~ 50")
        with page_col2:
            st.button("1")
        with page_col3:
            st.button("2")
        with page_col4:
            st.button("›")

# ==========================================
# 우측 사이드바 (문헌 선택 시에만 표시)
# ==========================================
if right_sidebar is not None and st.session_state.selected_row_index is not None:
    row = df_result.iloc[st.session_state.selected_row_index]
    with right_sidebar:
        st.markdown("**📌 선택 문헌 상세**")
        st.divider()
        st.markdown("**출원번호**")
        st.write(row["출원번호"])
        st.markdown("**발명의 명칭**")
        st.caption(row["발명의 명칭"])
        st.markdown("**구분**")
        st.write(row["구분"])
        st.markdown("**CPC분류**")
        st.caption(row["CPC분류"].replace("\n", " "))
        st.markdown("**출원일자**")
        st.write(row["출원일자"])
        st.divider()
        st.button("📥 내보내기", use_container_width=True, key="export_btn")
        st.button("📋 클립보드", use_container_width=True, key="clipboard_btn")
        if st.button("✕ 사이드바 닫기", use_container_width=True, key="close_sidebar_btn"):
            st.session_state.selected_row_index = None
            st.rerun()