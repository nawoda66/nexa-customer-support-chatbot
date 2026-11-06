import os
from datetime import datetime

import tiktoken
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv() 

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
)
MODEL = "openai/gpt-oss-20b"
TEMPERATURE = 0.2
TOKEN_BUDGET = 6000

os.makedirs("logs", exist_ok=True)

with open("knowledge.txt", encoding="utf-8") as f:
    KNOWLEDGE = f.read()

SYSTEM_PROMPT = """You are "Nexa", the friendly customer support assistant for ABC Electronics.

Rules:
- Answer ONLY using the COMPANY INFORMATION below. If the answer is not there,
  say you are not sure and offer to connect the customer with a human agent.
  Never make up prices, policies or order details.
- Be polite, warm and short (2-4 sentences). Use simple language.
- If the request is unclear, ask a clarifying question (for example, ask for the order number).
- If the customer is upset, apologize sincerely and focus on solving the problem.
- Politely refuse questions that are not related to ABC Electronics.
- If the customer asks for a human, has a complaint you cannot solve, asks about
  a specific order's status, or asks for a refund, you must hand them over to a human agent:
  1. First ask for their name and phone number (if you don't have them yet).
     Do NOT add any tag in this message.
  2. Only after you have BOTH the name and phone number, tell them a human agent
     will contact them and end that reply with the tag [ESCALATE].
  Use [ESCALATE] only once per conversation.

"""

ENCODING = tiktoken.get_encoding("cl100k_base")


def new_conversation():
    """Start a conversation that contains only the system prompt."""
    return [{"role": "system", "content": SYSTEM_PROMPT + "\n\nCOMPANY INFORMATION:\n" + KNOWLEDGE}]


def new_log_file():
    return f"logs/chat_{datetime.now():%Y%m%d_%H%M%S}.txt"


def log(log_file, role, text):
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now():%H:%M:%S}] {role}: {text}\n")


def count_tokens(text):
    return len(ENCODING.encode(text))


def total_tokens_used(messages):
    try:
        return sum(count_tokens(m["content"]) for m in messages)
    except Exception as e:
        print(f"[token count error]: {e}")
        return 0


def enforce_token_budget(messages, budget=TOKEN_BUDGET):
    """Remove the oldest messages (never the system prompt) until under budget."""
    try:
        while total_tokens_used(messages) > budget:
            if len(messages) <= 2:
                break
            messages.pop(1)
    except Exception as e:
        print(f"[token budget error]: {e}")


def save_ticket(messages):
    """Append the whole conversation to tickets.txt for a human agent."""
    with open("tickets.txt", "a", encoding="utf-8") as f:
        f.write(f"--Ticket {datetime.now():%Y-%m-%d %H:%M:%S}--\n")
        for m in messages[1:]:  # [1:] skips the system prompt
            f.write(f"{m['role']}: {m['content']}\n")
        f.write("\n")


def chat(messages, user_input):

    messages.append({"role": "user", "content": user_input})

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=TEMPERATURE,
        )
        reply = response.choices[0].message.content
    except Exception as e:
        print(f"[API error]: {e}")
        messages.pop()  # remove the failed user message
        return "Sorry, I'm having trouble right now. Please try again in a moment.", False

   
    escalated = "[ESCALATE]" in reply
    reply = reply.replace("[ESCALATE]", "").strip()

    messages.append({"role": "assistant", "content": reply})

    if escalated:
        save_ticket(messages)

    enforce_token_budget(messages)
    return reply, escalated
