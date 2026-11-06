from bot import new_conversation, new_log_file, chat, log

messages = new_conversation()
log_file = new_log_file()

print("Nexa: Hi! I'm Nexa from ABC Electronics. How can I help you today? (type 'exit' to quit)")

while True:
    user_input = input("You: ")
    if not user_input.strip():
        continue
    if user_input.strip().lower() in {"exit", "quit"}:
        print("Exiting the chat. Goodbye!")
        break
    log(log_file, "Customer", user_input)
    answer, escalated = chat(messages, user_input)
    log(log_file, "Nexa", answer)
    print("Nexa:", answer)
    if escalated:
        print(">>> [A human agent has been notified]")
