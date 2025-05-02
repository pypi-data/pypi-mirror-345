from . import prompt
from . import cmd

import argparse
import subprocess

import colorama
from colorama import Fore


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="AI Execute (aix)",
        description="Use a locally-hosted AI model to generate terminal commands"
    )
    
    parser.add_argument(
        "prompt",
        help="The command to request the AI to generate"
    )
    
    parser.add_argument(
        "--yes", "-y",
        action="store_true",
        help="Run the command without manual verification. Commands considered potentially dangerous will still require"
             " manual verification (e.g., rm, dd). WARNING: even with safety precautions, this may allow the AI to run "
             "dangerous commands without approval. Use at your own risk."
    )
    
    return parser.parse_args()


def main():
    colorama.init()
    
    args = get_args()
    
    response = prompt.get_cmd(args.prompt)
    if response.invalid_input:
        print(f"{Fore.RED}Your input was flagged as invalid. Please try a different prompt.{Fore.RESET}")
        return
    
    if response.invalid_output:
        print(f"{Fore.RED}AI provided invalid output. Please try a different prompt.{Fore.RESET}")
        return
    
    if response.dangerous:
        print(f"{Fore.RED}The command you requested was flagged as dangerous and will not be executed.{Fore.RESET}")
        return
    
    potentially_dangerous = cmd.is_potentially_dangerous(response.command)
    
    if args.yes and not potentially_dangerous:
        print(f"Running: {response.command}")
        subprocess.run(response.command, shell=True)
        return
    
    for warning in potentially_dangerous:
        print(f"{Fore.RED}WARNING: {warning}{Fore.RESET}")
    
    print(f"Suggested command: {response.command}")
    
    run_cmd = input("Run command? (y/n): ")
    while run_cmd.lower() not in ["y", "yes", "n", "no"]:
        print("Please provide y or n.")
        run_cmd = input("Run command? (y/n): ")
    
    if run_cmd.lower() in ["y", "yes"]:
        subprocess.run(response.command, shell=True)


if __name__ == "__main__":
    main()
