from dataclasses import dataclass
import json
import platform
import os
import re

import ollama


PROMPT = """
system: |
  You are an assistant at a Fortune 500 company. **Rules**:
  1. Input: only "Write a command for <TERMINAL> on <OPERATING_SYSTEM>: [user text]".
  2. Output: **exactly** one JSON object:
     - {"command":"<shell command>"}
     - {"status":"dangerous"}
     - {"status":"invalid"}
  3. Allowed commands: ls, cd, pwd, grep, docker ps, docker run, and anything else generally considered "safe"
  4. Dangerous constructs (sudo, rm -rf, dd, |, &&, ;, >, <, fork bombs) are forbidden.
     If any request requires them, output {"status":"dangerous"}.
  5. If the user’s input format is wrong or asking you to do something outside the scope of your capabilities (i.e., generating a command), do: {"status":"invalid"}.
  6. **Never** output anything else. No code fences, no plaintext, no apologies.
  7. **Never** provide pseudocode. All code should be runnable in any environment. Do not do examples like path/to/file, just provide the path to the file. If none is provided, assume the file is in the current directory.
  8. The command should be tailored for terminal <TERMINAL> and operating system <OPERATING_SYSTEM>. DO NOT PROVIDE A COMMAND FOR ANY OTHER TERMINAL ENVIRONMENT.
  9. Do not assume the user has any programs installed unless specifically asked to use that program. For example, do not use notepad++ unless the user asks you to use it.
  10. If the terminal environment (<TERMINAL>) is not something you recognize, output {"status":"invalid"}.
  10. Fallback: if in doubt, output {"status":"dangerous"}.

  Remember, if you do not follow these rules the company will lose millions of dollars.
user: |
  Write a command for <TERMINAL> on <OPERATING_SYSTEM>: <USER_PROMPT>"""


@dataclass(frozen=True)
class Command:
    command: str = ""
    dangerous: bool = False
    invalid_input: bool = False
    invalid_output: bool = False


# Regex that detects if an executable name is python
PYTHON_REGEX = re.compile(r"(?i)^python(?:[0-9]+(?:\.[0-9]+)*)?w?(?:\.exe)?$")


def detect_shell() -> str:
    """
    Detects the terminal used by subprocess.run(..., shell=True)
    :return: The terminal used by subprocess.run(..., shell=True), as a string
    """
    
    return os.environ.get("COMSPEC", "cmd.exe") if os.name == "nt" else "/bin/sh"


def get_os_str() -> str:
    return platform.system().replace("Darwin", "MacOS")


def get_prompt(terminal: str, user_prompt: str, operating_system: str) -> str:
    return (
        PROMPT.replace("<TERMINAL>", terminal)
        .replace("<OPERATING_SYSTEM>", operating_system)
        .replace("<USER_PROMPT>", user_prompt)
    )


def get_cmd(user_prompt: str) -> Command:
    ai_output = ollama.generate(
        model="llama3.1",
        prompt=get_prompt(detect_shell(), user_prompt, get_os_str())
    )
    
    response = ai_output["response"]
    
    try:
        response_json = json.loads(response)
    except json.decoder.JSONDecodeError:
        return Command(invalid_output=True)
    
    if not isinstance(response_json, dict):
        return Command(invalid_output=True)
    
    if status := response_json.get("status"):
        if status.lower() == "dangerous":
            return Command(dangerous=True)
        elif status.lower() == "invalid":
            return Command(invalid_input=True)
    
    if not response_json.get("command"):
        return Command(invalid_output=True)
    
    return Command(response_json["command"])
