import shlex
import os

DANGEROUS = {"rm", "dd", "del", "mkfs", "chmod"}
DANGEROUS_GIT = {"reset", "clean"}


def is_potentially_dangerous(cmd: str) -> list[str]:
    # sourcery skip: use-named-expression
    warnings = []
    
    # 1) Normalize & tokenize
    try:
        tokens = shlex.split(cmd)
    except ValueError:
        return ["Could not parse command safely"]
    if not tokens:
        return warnings
    
    # 2) If it starts with sudo, skip sudo and any sudo flags
    idx = 0
    if os.path.basename(tokens[0]).lower() == "sudo":
        warnings.append("Potentially dangerous command: sudo")
        idx = 1
        # skip over sudo flags like -u, -H, etc.
        while idx < len(tokens) and tokens[idx].startswith("-"):
            idx += 1
        if idx >= len(tokens):
            return ["`sudo` with no command detected"]
    
    # 3) Identify the real program
    program = os.path.basename(tokens[idx]).lower()
    
    # 4) Check against dangerous binaries
    if program in DANGEROUS:
        warnings.append(f"Potentially dangerous command: {program}")
    
    # 5) Scan for any recursive-style flags (-r anywhere in the group) or --recursive
    recursive_flags = [
        t for t in tokens[idx + 1:]
        if (t.startswith("-") and "r" in t[1:].lower()) or t.lower() == "--recursive"
    ]
    if recursive_flags:
        warnings.append(f"Recursive flag detected: {' '.join(recursive_flags)}")
    
    # 6) Special handling for git subcommands
    if program == "git" and idx + 1 < len(tokens):
        sub = tokens[idx + 1].lower()
        if sub in DANGEROUS_GIT:
            warnings.append(f"Potentially dangerous git operation: git {sub}")
    
    return warnings
