"""Clinic Appointment Assistant on Streamlit.
The chatbot logic is in chatbot.py. This file is the web page, the privacy notice and the log.
Secrets (never in this file): LOG_URL, set in Streamlit's Secrets box.
"""
import os
import re
import uuid
from datetime import datetime

import joblib
import requests
import streamlit as st

import chatbot

HERE = os.path.dirname(os.path.abspath(__file__))
MODEL_FILE = os.path.join(HERE, "intent_classifier.joblib")

st.set_page_config(page_title=chatbot.BOT_NAME, page_icon="🏥")


@st.cache_resource
def load_classifier():
    """The trained intent classifier, loaded once. None if the file cannot be read."""
    try:
        return joblib.load(MODEL_FILE)
    except Exception as error:
        return None


def log_url():
    try:
        return st.secrets.get("LOG_URL")
    except Exception:
        return None


def mask(text):
    """Phone numbers never go in the log."""
    return re.sub(r"\d[\d ]{7,}\d", "[number]", str(text))


def log_row(row):
    """Send one row to the private Google Sheet. True if it was saved (or logging is off)."""
    url = log_url()
    if not url:
        return True
    row = {key: mask(value) if key in ("message", "reply") else value for key, value in row.items()}
    try:
        answer = requests.post(url, json=row, timeout=10)
        return answer.ok and answer.text.strip() == "ok"
    except Exception:
        return False


# ---------------------------------------------------------------- one visitor = one session
if "user" not in st.session_state:
    st.session_state.user = uuid.uuid4().hex[:6]      # a random code, never a name
    st.session_state.state = chatbot.new_state()
    st.session_state.messages = []
    st.session_state.turn = 0
    st.session_state.log_failed = False
    st.session_state.errors = []

st.title("🏥 " + chatbot.BOT_NAME)
st.caption("I am an automated assistant, a computer program, not a member of staff. "
           f"I can help with {chatbot.TOPICS}. Type 'human' for a person, 'bye' to finish.")
st.info("Your messages are recorded to improve this chatbot (Law N°058/2021). "
        "Please do not type your name. Phone numbers are hidden in the record.", icon="🔒")

if not log_url():
    st.info("The log is off: LOG_URL is not in this app's secrets, so nothing is saved.")
elif st.session_state.log_failed:
    st.warning("Some messages could not be saved to the Google Sheet.")


def on_feedback(index):
    """👍 or 👎 on one reply: one more row in the log."""
    value = st.session_state.get(f"fb_{index}")
    if value is None:
        return
    message = st.session_state.messages[index]
    ok = log_row({"time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                  "user": st.session_state.user, "turn": message["turn"],
                  "message": message["question"], "intent": message["intent"],
                  "confidence": "", "answered_by": message["by"], "reply": "",
                  "feedback": "👍" if value == 1 else "👎"})
    if not ok:
        st.session_state.log_failed = True


# the conversation so far
for index, message in enumerate(st.session_state.messages):
    with st.chat_message("user"):
        st.write(message["question"])
    with st.chat_message("assistant"):
        st.write(message["reply"])
        st.caption(f"answered by: {message['by']}")
        st.feedback("thumbs", key=f"fb_{index}", on_change=on_feedback, args=(index,))

# a new message
text = st.chat_input("Type your message")
if text is not None:
    classifier = load_classifier()
    reply, by, intent, confidence = chatbot.reply_to(
        text, st.session_state.state, classifier, st.session_state.errors)
    st.session_state.turn += 1
    st.session_state.messages.append({"question": text, "reply": reply, "by": by,
                                      "intent": intent, "turn": st.session_state.turn})
    ok = log_row({"time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                  "user": st.session_state.user, "turn": st.session_state.turn,
                  "message": text, "intent": intent, "confidence": round(confidence, 2),
                  "answered_by": by, "reply": reply, "feedback": ""})
    if not ok:
        st.session_state.log_failed = True
    st.rerun()
