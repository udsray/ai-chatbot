# AI Chatbot

A minimal command-line chatbot built on Anthropic's Claude API. It keeps the
conversation history for the session, so Claude remembers earlier messages.

## Requirements

- Python 3.8+
- An Anthropic API key ([get one here](https://console.anthropic.com/))

## Setup

```bash
git clone https://github.com/udsray/ai-chatbot.git
cd ai-chatbot

python -m venv venv
# macOS/Linux
source venv/bin/activate
# Windows
venv\Scripts\activate

pip install -r requirements.txt
```

Create a `.env` file in the project root:

```
ANTHROPIC_API_KEY=your-api-key-here
```

`.env` is already in `.gitignore`, so your key won't be committed.

## Usage

```bash
python chat.py
```

```
Chat started. Type 'exit' to quit.

You: What's the capital of France?
Claude: The capital of France is Paris.

You: exit
```

## Configuration

You can change these in `chat.py`:

| Setting         | Default                                     | Purpose                          |
|-----------------|---------------------------------------------|----------------------------------|
| `SYSTEM_PROMPT` | Concise assistant, answers under 3 sentences | Sets Claude's tone and behavior  |
| `model`         | `claude-haiku-5-5`                          | Which Claude model to use        |
| `max_tokens`    | `1000`                                      | Maximum length of each reply     |

## License

MIT. See [LICENSE](LICENSE).
