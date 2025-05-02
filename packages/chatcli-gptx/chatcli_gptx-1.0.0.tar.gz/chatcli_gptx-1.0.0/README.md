# ChatGPT CLI Tool

A flexible, full-featured command-line tool for interacting with OpenAI's ChatGPT API.

## 🔧 Features
- Prompt input from command line
- Configurable model and system prompt
- Conversation sessions with persistent context
- Export sessions to text or Markdown (with YAML front matter)
- Logging and log filtering
- Colorized output (optional)
- Packaged as a command-line tool (`chatgpt-cli`)

## 🚀 Installation
```bash
pip install .
```

## 🛠 Usage Examples
```bash
# Basic prompt
chatgpt-cli --prompt "What is bourbon?"

# Start a named session
chatgpt-cli --prompt "Explain Terraform." --session devops.json

# Export session to Markdown
chatgpt-cli --session devops.json --export-session devops.md

# Use a specific model and system prompt
chatgpt-cli --prompt "What's new in Python 3.12?" \
  --model gpt-4 \
  --system "You are a Python expert."
```

## 📄 Configuration
Set your OpenAI API key in a `.env` file or your environment:
```
OPENAI_API_KEY=sk-...
```

## 📦 Project Structure
```
chatgpt_cli/
├── __main__.py
├── pyproject.toml
├── README.md
└── requirements.txt
```

## 🧾 License
MIT License
