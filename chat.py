import os
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

SYSTEM_PROMPT = "You are a concise, helpful assistant. Keep answers under 3 sentences unless asked for more detail."
conversation_history = []

print("Chat started. Type 'exit' to quit.\n")

while True:
    user_input = input("You: ")
    if user_input.lower() == "exit":
        break

    conversation_history.append({"role": "user", "content": user_input})

    response = client.messages.create(
        model="claude-haiku-5-5",
        max_tokens=1000,
        system=SYSTEM_PROMPT,
        messages=conversation_history
    )

    reply = response.content[0].text
    print(f"Claude: {reply}\n")

    conversation_history.append({"role": "assistant", "content": reply})
