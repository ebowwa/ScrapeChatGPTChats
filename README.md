# ScrapeChatGPTChats

This repository contains a small utility for collecting information from shared ChatGPT conversations.
It parses a share link and outputs structured data about the chat.

## Requirements
- Python 3.8+
- `requests`
- `beautifulsoup4`

Install dependencies with:

```bash
pip install -r requirements.txt
```

## Usage
Run the main script with a ChatGPT share link:

```bash
python main.py <share_link>
```

Example:

```bash
python main.py https://chat.openai.com/share/1234abcd
```

The command prints JSON with two keys:

- `analysis` – meta data, user info and experiment layer details.
- `chat_messages` – a list of all messages, including author, content and timestamp.

## service.py
The scraping logic resides in `service.py` and exposes two functions:

- `scrape_chatgpt_conversation(share_link)` – returns meta information about the conversation.
- `extract_chat_messages(share_link)` – extracts the messages in order.

Each function returns `None` if the relevant data cannot be obtained.
