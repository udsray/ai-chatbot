import os

import anthropic
from dotenv import load_dotenv

MODEL = "claude-haiku-5-5"
SYSTEM_PROMPT = "You are a concise, helpful assistant. Keep answers under 3 sentences unless asked for more detail."


def send_message(client, history, user_input):
    """Send user_input to Claude and return the reply, or None if the call failed.

    On success, the user message and the reply are appended to history.
    On failure, history is left exactly as it was.
    """
    history.append({"role": "user", "content": user_input})

    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=1000,
            system=SYSTEM_PROMPT,
            messages=history,
        )
    except anthropic.APIConnectionError:
        history.pop()
        print("Error: couldn't reach the Anthropic API. Check your connection and try again.\n")
        return None
    except anthropic.APIError as e:
        history.pop()
        print(f"Error: the API request failed ({e.message}). Please try again.\n")
        return None
    except KeyboardInterrupt:
        history.pop()
        raise

    # Thinking blocks can come before the text, so find the first text block.
    reply = next((block.text for block in response.content if block.type == "text"), "")
    history.append({"role": "assistant", "content": reply})
    return reply


def run_chat(client, input_fn=input):
    """Run the chat loop until the user types 'exit' or presses Ctrl+C / Ctrl+D."""
    history = []
    print("Chat started. Type 'exit' to quit.\n")

    while True:
        try:
            user_input = input_fn("You: ").strip()
            if not user_input:
                continue
            if user_input.lower() == "exit":
                break

            reply = send_message(client, history, user_input)
            if reply is not None:
                print(f"Claude: {reply}\n")
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break

    return history


def main():
    load_dotenv()
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    run_chat(client)


if __name__ == "__main__":
    main()
