import os
import argparse
import json
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime
from colorama import init, Fore, Style

# Load environment variables from a .env file if present
load_dotenv()

# Initialize colorama
init(autoreset=True)

# Load the API key from the environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Default log file name
LOG_FILE = "chatgpt_cli_log.jsonl"
DEFAULT_SESSION_FILE = "chat_session.json"

def query_chatgpt(messages, model="gpt-4o"):
    if not OPENAI_API_KEY:
        print(Fore.RED + "OpenAI API key not found. Please set OPENAI_API_KEY in your environment or .env file.")
        return None

    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        chat_completion = client.chat.completions.create(
            messages=messages,
            model=model,
        )
        return chat_completion
    except Exception as e:
        print(Fore.RED + f"An error occurred: {e}")
        return None

def log_interaction(prompt, response):
    try:
        with open(LOG_FILE, "a") as f:
            log_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "prompt": prompt,
                "response": response
            }
            f.write(json.dumps(log_entry) + "\n")
    except Exception as e:
        print(Fore.RED + f"Failed to write log entry: {e}")

def filter_logs(keyword):
    try:
        with open(LOG_FILE, "r") as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    if keyword.lower() in entry["prompt"].lower() or keyword.lower() in entry["response"].lower():
                        print(json.dumps(entry, indent=2))
                except json.JSONDecodeError:
                    continue
    except FileNotFoundError:
        print(Fore.YELLOW + "Log file not found.")

def list_sessions():
    print(Fore.CYAN + "Available session files:")
    for file in os.listdir("."):
        if file.endswith(".json"):
            print("-", file)

def export_session(file_path, output_path):
    try:
        with open(file_path, "r") as f:
            messages = json.load(f)
        with open(output_path, "w") as out:
            if output_path.endswith(".md"):
                out.write("---\n")
                out.write(f"title: ChatGPT Session\n")
                out.write(f"date: {datetime.utcnow().isoformat()}\n")
                out.write("layout: post\n")
                out.write("---\n\n")
                for msg in messages:
                    role = msg.get("role", "unknown").capitalize()
                    content = msg.get("content", "").strip()
                    out.write(f"**{role}:** {content}  \n\n")
            else:
                for msg in messages:
                    role = msg.get("role", "unknown").capitalize()
                    content = msg.get("content", "").strip()
                    out.write(f"{role}: {content}\n\n")
        print(Fore.GREEN + f"Session exported to {output_path}")
    except Exception as e:
        print(Fore.RED + f"Failed to export session: {e}")

def load_session(file_path, new_session=False):
    if new_session:
        return []
    if os.path.exists(file_path):
        try:
            with open(file_path, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(Fore.YELLOW + "Warning: Session file is not valid JSON. Starting fresh.")
    return []

def save_session(file_path, messages):
    try:
        with open(file_path, "w") as f:
            json.dump(messages, f, indent=2)
    except Exception as e:
        print(Fore.RED + f"Failed to save session: {e}")

def main():
    parser = argparse.ArgumentParser(description="ChatGPT CLI Tool")
    parser.add_argument("--prompt", type=str, help="Prompt to send to ChatGPT")
    parser.add_argument("--output", choices=["text", "json", "raw"], default="text", help="Output format: text (default), json, or raw")
    parser.add_argument("--log", action="store_true", help="Log the prompt and response to a file")
    parser.add_argument("--filter", type=str, help="Keyword to filter logs")
    parser.add_argument("--session", type=str, default=DEFAULT_SESSION_FILE, help="Path to session file to maintain chat history")
    parser.add_argument("--new-session", action="store_true", help="Start a new session, ignoring previous conversation history")
    parser.add_argument("--model", type=str, default="gpt-4o", help="OpenAI model to use (default: gpt-4o)")
    parser.add_argument("--system", type=str, help="System message to set assistant behavior")
    parser.add_argument("--quiet", action="store_true", help="Suppress console output")
    parser.add_argument("--list-sessions", action="store_true", help="List available session files")
    parser.add_argument("--export-session", type=str, help="Export a session to plain text or Markdown format (.txt or .md)")
    args = parser.parse_args()

    if args.list_sessions:
        list_sessions()
        return

    if args.export_session:
        export_session(args.session, args.export_session)
        return

    if args.filter:
        filter_logs(args.filter)
        return

    if not args.prompt:
        print(Fore.YELLOW + "Please provide a prompt with --prompt")
        return

    session_messages = load_session(args.session, args.new_session)

    if args.system and all(msg['role'] != 'system' for msg in session_messages):
        session_messages.insert(0, {"role": "system", "content": args.system})

    session_messages.append({"role": "user", "content": args.prompt})

    result = query_chatgpt(session_messages, model=args.model)
    if result:
        content = result.choices[0].message.content.strip()
        session_messages.append({"role": "assistant", "content": content})

        if not args.quiet:
            if args.output == "text":
                print("\n" + Fore.GREEN + content)
            elif args.output == "json":
                print(Fore.CYAN + json.dumps({
                    "prompt": args.prompt,
                    "response": content
                }, indent=2))
            elif args.output == "raw":
                print(result)

        if args.log:
            log_interaction(args.prompt, content)

        save_session(args.session, session_messages)

if __name__ == "__main__":
    main()
