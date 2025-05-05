import subprocess
import json
from groq import Groq
from gitpush.config import get_api_key, set_api_key_path

def get_git_command_from_model(user_input):
    api_key = get_api_key()

    client = Groq(api_key=api_key)

    prompt = f"""
You are a Git command generator agent. Given a user's request, respond ONLY with a JSON object in the format:
{{"git_command": "<actual_git_command>"}}
Do not include any explanations or formatting.

User request: {user_input}
""".strip()

    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile",
    )

    response_text = chat_completion.choices[0].message.content.strip()
    try:
        command_json = json.loads(response_text)
        return command_json.get("git_command")
    except:
        print("Invalid JSON response from model:", response_text)
        return None

def execute_git_command(command):
    print(f"\nExecuting: {command}")
    result = subprocess.run(command, shell=True, text=True, capture_output=True)
    print(f"\nOutput:\n{result.stdout}")
    if result.stderr:
        print(f"\nError:\n{result.stderr}")

def main():
    set_api_key_path()

    print("Welcome to GitPush CLI")
    while True:
        user_input = input("\nEnter a prompt to execute a Git command (or type 'exit' to quit): ")
        if user_input.lower() == "exit":
            break
        git_command = get_git_command_from_model(user_input)
        if git_command:
            execute_git_command(git_command)
        else:
            print("Error processing request.")