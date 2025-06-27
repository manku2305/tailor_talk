# frontend/app.py

import streamlit as st
import requests

st.title("🧵 TailorTalk Booking Assistant")
st.write("Talk to the bot to book a meeting!")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

user_input = st.chat_input("Say something...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.chat_message("user").write(user_input)

    try:
        res = requests.post("http://localhost:8000/chat", json={"message": user_input})
        res.raise_for_status()
        ai_response = res.json()["response"]
    except requests.exceptions.RequestException as e:
        ai_response = f"❌ Backend error: {e}"
    except ValueError:
        ai_response = f"❌ Invalid JSON response: {res.text}"

    st.session_state.messages.append({"role": "assistant", "content": ai_response})
    st.chat_message("assistant").write(ai_response)
