import sys
import json
from service import scrape_chatgpt_conversation, extract_chat_messages


def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <share_link>")
        return

    share_link = sys.argv[1]

    analysis = scrape_chatgpt_conversation(share_link)
    chat_messages = extract_chat_messages(share_link)

    result = {
        "analysis": analysis,
        "chat_messages": chat_messages,
    }

    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
