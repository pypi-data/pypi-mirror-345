# AI Execute (aix)

AI-powered console command generator.

## Overview

`aix` is a command-line tool that uses a locally-hosted AI model to generate terminal commands based on user prompts. It provides a convenient way to generate commands while incorporating safety measures to prevent the execution of dangerous or invalid commands.

WARNING: while safety measures in place, it is still important to use this tool carefully. Verify all commands it provides. If you choose to automatically execute commands, do not ask it to do anything dangerous. While there are safety nets in-place, do not rely on them. **TL;DR: use at your own risk.**

## Features

- Generate terminal commands using AI.
- Automatically adapts to your operating system/shell.
- Safety checks for potentially dangerous commands.
- Manual verification prompts for added security.
- Optional `--yes` flag for automatic execution of commands with no found vulnerabilities. _See the above disclaimer._

## Installation

1. Download Ollama at the official site: [https://ollama.com/download](https://ollama.com/download)
2. Download llama3.1 (8 billion parameter version) _This will take approx 5gb_
```shell
$ ollama run llama3.1:8b
```

``shell
$ pip install ai-execute
```

## Usage

Run the `aix` command with a prompt to generate a terminal command

```shell
$ aix "List all files in the current directory"
```

## Options

* `--yes`, `-y`: Automatically execute the generated command if no safety warnings are found. _See the above disclaimer._

Example:
```shell
$ aix "Create a new file called cats.txt"
```
