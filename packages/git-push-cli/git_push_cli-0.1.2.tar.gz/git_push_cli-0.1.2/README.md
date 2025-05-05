# GitPush CLI Tool

GitPush is a command-line tool that allows you to execute Git commands by providing natural language prompts. Using the Groq API, it generates and runs Git commands for you.

## Features

- Convert natural language commands into Git commands
- Supports Git operations like `git init`, `git commit`, `git push`, etc.
- Easy to use: simply enter a prompt and the tool executes the corresponding Git command

## Installation

1. **Install GitPush using pip:**

   To install GitPush, simply run the following command:

   ```bash
   pip install git-push-cli
   ```

2. **Verify the installation:**

After installing, verify that GitPush is installed correctly by running:

   ```bash
   gitpush
   ```

This should open the GitPush CLI interface.

## Setting up the Groq API Key

1. **Enter your Groq API key**

The first time you run GitPush, it will ask you to enter your Groq API key. This key is required to generate Git commands from natural language prompts.

When prompted, enter your Groq API key and press **Enter**.


The key will be stored securely, so you only need to enter it once.

## Using the GitPush CLI Tool

Once your Groq API key is set up, you can start using GitPush to generate and execute Git commands.

1. **Enter a natural language prompt**

After setting your Groq API key, you can enter any Git-related prompt, and GitPush will generate and execute the corresponding Git command.

Example prompts:
- "Initialize a Git repository"
- "Commit my changes with the message 'Initial commit'"
- "Push my changes to the remote repository"

GitPush will generate and execute the corresponding Git command.

2. **Exit the tool:**

To exit the GitPush CLI tool, simply type `exit` and press **Enter**.


## Example Workflow

Here’s how a typical session would look:

1. **Install GitPush**: `pip install git-push-cli==0.1.1`


2. **Run GitPush CLI**: `gitpush`


3. **Enter your Groq API key**: `gsk_**********************************`


4. **Generate and let the agent execute Git command by entering a prompt**: `initialize git`


5. **Exit the tool**: `exit`


## Requirements

- Python 3.x or higher
- A Groq API key for generating Git commands
- Git installed on your machine