import streamlit as st
from bot import new_conversation, new_log_file, chat, log

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


# 1. Keep ALL chats of this visitor (survives reruns)
#    chats = {1: {"messages": [...], "log_file": "...", "escalated": False}, 2: {...}}
if "chats" not in st.session_state:
    st.session_state.chats = {}
    start_new_chat()

current = st.session_state.chats[st.session_state.current_id]

# 2. Handle a new message FIRST, so the sidebar below already shows its title
user_input = st.chat_input("Type your message...")
if user_input:
    log(current["log_file"], "Customer", user_input)
    with st.spinner("Nexa is typing..."):
        reply, escalated = chat(current["messages"], user_input)
    log(current["log_file"], "Nexa", reply)
    if escalated:
        current["escalated"] = True

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
