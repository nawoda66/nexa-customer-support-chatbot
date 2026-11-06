# Nexa: AI Customer Support Chatbot

Nexa is an AI customer support assistant for **ABC Electronics**, a sample electronics store. It answers customer questions using only the company's own information. When a customer needs a person, Nexa collects their contact details and creates a support ticket for a human agent.

Built with **Python**, **Streamlit** and the **Groq API** (`openai/gpt-oss-20b` model).


## Features

- **Grounded answers:** Nexa answers only from the company information in `knowledge.txt`. If the answer isn't there, it says so instead of making something up.
- **Hand-over to a human:** for refunds, order status, unresolved complaints or when the customer asks for a person, Nexa asks for their name and phone number, then saves the conversation as a ticket in `tickets.txt`.
- **Chat history:** start a new chat at any time and switch back to earlier chats from the sidebar.
- **Stays on topic:** Nexa politely refuses questions that aren't about the store.
- **Token budget:** older messages are dropped automatically when a conversation gets long, so requests stay within the model's limits.
- **Conversation logs:** every chat is saved with timestamps in the `logs/` folder.
- **Two interfaces:** a web app (`app.py`) and a terminal version (`demo.py`).

## How it works

1. A **system prompt** in `bot.py` gives Nexa its persona and rules, followed by the contents of `knowledge.txt`.
2. Each customer message is sent to the model together with the conversation so far.
3. When a hand-over is needed, the model ends its reply with a hidden `[ESCALATE]` tag. The code removes the tag before the customer sees the reply, saves a ticket and shows a "human agent notified" message.

## Project structure

```
├── app.py                 # Streamlit web app (chat UI, sidebar, chat history)
├── bot.py                 # Chatbot logic: prompt, API call, tickets, logging, token budget
├── demo.py                # Terminal version of the chatbot
├── knowledge.txt          # Company information Nexa answers from (sample data)
├── requirements.txt       # Python dependencies
└── .streamlit/config.toml # Theme colours
```

## Getting started

### 1. Clone the repository
```bash
git clone https://github.com/nawoda66/nexa-customer-support-chatbot.git
cd nexa-customer-support-chatbot
```

### 2. Create a virtual environment and install dependencies
```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS / Linux
pip install -r requirements.txt
```

### 3. Add your Groq API key
Get a free key at [console.groq.com](https://console.groq.com), then create a file named `.env` in the project folder:
```
GROQ_API_KEY=your-key-here
```

### 4. Run the app
```bash
streamlit run app.py
```
Or try the terminal version:
```bash
python demo.py
```

## Using it for your own business

Replace the contents of `knowledge.txt` with your own company's details (products, prices, opening hours, policies). Nexa will answer from that information. To change the bot's name, tone or rules, edit `SYSTEM_PROMPT` in `bot.py`.

## Possible improvements

- Save tickets and chat history in a database, so they persist after a restart
- Send an email or message to the support team when a ticket is created
- Search a larger knowledge base (RAG) instead of putting all company information in the prompt
- Add login for support agents to view and manage tickets

## Note

ABC Electronics is a fictional company. All store information in `knowledge.txt` is sample data.
