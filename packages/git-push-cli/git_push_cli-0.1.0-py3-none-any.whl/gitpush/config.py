import os
import pathlib

CONFIG_FILE = os.path.join(pathlib.Path.home(), ".gitpush_config")

def set_api_key_path():
    if not os.path.exists(CONFIG_FILE):
        api_key = input("Enter your Groq API key (only once): ").strip()
        with open(CONFIG_FILE, "w") as f:
            f.write(api_key)

def get_api_key():
    with open(CONFIG_FILE, "r") as f:
        return f.read().strip()
