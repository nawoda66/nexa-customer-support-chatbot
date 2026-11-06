import threading
from datetime import date

import streamlit as st
from bot import new_conversation, new_log_file, chat, log

# Usage limits for the public demo (protects the free Groq quota)
MAX_CHARS = 500                 # longest message a customer can type
MAX_MESSAGES_PER_SESSION = 20   # messages one visitor can send
MAX_MESSAGES_PER_DAY = 200      # messages ALL visitors together can send per day

st.set_page_config(page_title="ABC Electronics Customer Support",    initial_sidebar_state=250)
st.title("ABC Electronics Customer Support")
st.caption("Chat with Nexa, our virtual assistant")


def start_new_chat():
    """Create an empty chat, add it to the chat list and make it the current one."""
    chat_id = len(st.session_state.chats) + 1
    st.session_state.chats[chat_id] = {
        "messages": new_conversation(),
        "log_file": new_log_file(),
        "escalated": False,
    }
    st.session_state.current_id = chat_id


def chat_title(messages):
    """Use the customer's first message as the chat's name in the sidebar."""
    for m in messages[1:]:
        if m["role"] == "user":
            text = m["content"]
            return text[:30] + "..." if len(text) > 30 else text
    return "New chat"


@st.cache_resource
def daily_usage():
    """One shared counter for ALL visitors (st.cache_resource is shared across sessions).
    It resets every new day, and also when the app restarts."""
    return {"date": date.today(), "count": 0, "lock": threading.Lock()}


def daily_limit_reached():
    usage = daily_usage()
    with usage["lock"]:
        if usage["date"] != date.today():  # a new day started: reset the counter
            usage["date"] = date.today()
            usage["count"] = 0
        return usage["count"] >= MAX_MESSAGES_PER_DAY


def count_message():
    st.session_state.messages_sent += 1
    usage = daily_usage()
    with usage["lock"]:
        usage["count"] += 1


# 1. Keep ALL chats of this visitor (survives reruns)
#    chats = {1: {"messages": [...], "log_file": "...", "escalated": False}, 2: {...}}
if "chats" not in st.session_state:
    st.session_state.chats = {}
    start_new_chat()
if "messages_sent" not in st.session_state:
    st.session_state.messages_sent = 0

current = st.session_state.chats[st.session_state.current_id]

# Check the limits before showing the chat box
session_limit = st.session_state.messages_sent >= MAX_MESSAGES_PER_SESSION
day_limit = daily_limit_reached()
limit_reached = session_limit or day_limit

# 2. Handle a new message FIRST, so the sidebar below already shows its title
user_input = st.chat_input(
    "Message limit reached" if limit_reached else "Type your message...",
    max_chars=MAX_CHARS,
    disabled=limit_reached,
)
if user_input and not limit_reached:
    count_message()
    log(current["log_file"], "Customer", user_input)
    with st.spinner("Nexa is typing..."):
        reply, escalated = chat(current["messages"], user_input)
    log(current["log_file"], "Nexa", reply)
    if escalated:
        current["escalated"] = True
    # If that was the last allowed message, redraw now so the chat box locks
    if st.session_state.messages_sent >= MAX_MESSAGES_PER_SESSION or daily_limit_reached():
        st.rerun()

# 3. Sidebar: "New chat" button + list of past chats
with st.sidebar:
    if st.button("New chat", width=250):
        
        if len(current["messages"]) > 1:
            start_new_chat()
        st.rerun()

 
    non_empty = [cid for cid in st.session_state.chats
                 if len(st.session_state.chats[cid]["messages"]) > 1]

    if non_empty:
        st.subheader("Chat History")
    for chat_id in sorted(non_empty, reverse=True):  # newest first
        messages = st.session_state.chats[chat_id]["messages"]
        is_current = chat_id == st.session_state.current_id
        if st.button(
            chat_title(messages),
            key=f"chat_{chat_id}",
            width=250,
            type="primary" if is_current else "secondary",
        ):
            st.session_state.current_id = chat_id
            st.rerun()

# 4. Show the greeting + all messages of the current chat
with st.chat_message("assistant"):
    st.write("Hi! I'm Nexa from ABC Electronics. How can I help you today?")

for m in current["messages"][1:]:
    with st.chat_message(m["role"]):
        st.write(m["content"])

if current["escalated"]:
    st.info("✅ A human agent has been notified and will contact you soon.")

# Tell the visitor why they can't send more messages
if st.session_state.messages_sent >= MAX_MESSAGES_PER_SESSION:
    st.warning(
        f"You've reached the demo limit of {MAX_MESSAGES_PER_SESSION} messages. "
        "Thanks for trying Nexa!"
    )
elif daily_limit_reached():
    st.warning("Nexa has reached today's demo limit. Please try again tomorrow.")
