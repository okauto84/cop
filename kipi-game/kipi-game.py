# -*- coding: utf-8 -*-

import streamlit as st
from openai import OpenAI

st.set_page_config(
    page_title="kipi-game",
    page_icon="💬",
    layout="wide"
)

try:
    API_KEY = st.secrets.get("openai_api_key", "")
except Exception:
    API_KEY = ""

MODEL_NAME = "gpt-5-mini"

st.markdown("# kipi-game Q&A")


def call_openai(api_key: str, model: str, history: list[dict]) -> str:
    if not api_key:
        return "⚠️ API 키가 설정되지 않았습니다. Streamlit secrets의 openai_api_key를 설정해주세요."
    try:
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(model=model, messages=history)
        return response.choices[0].message.content or ""
    except Exception as e:
        err = str(e)
        if "API_KEY" in err or "authentication" in err.lower() or "invalid" in err.lower():
            return f"🔑 API 키 오류: {err}"
        if "quota" in err.lower() or "limit" in err.lower() or "rate" in err.lower():
            return f"📊 사용량 한도 초과: {err}"
        return f"❌ API 호출 오류: {err}"


if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("질문하세요"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("답변 생성 중..."):
            reply = call_openai(API_KEY, MODEL_NAME, st.session_state.messages)
        st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})

if not API_KEY:
    st.warning("⚠️ OpenAI API 키가 설정되지 않았습니다. Streamlit secrets에 `openai_api_key`를 설정해주세요.")
