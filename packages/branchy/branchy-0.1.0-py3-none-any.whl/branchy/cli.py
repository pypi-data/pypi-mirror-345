#!/usr/bin/env python3

import subprocess
import os
import sys
from datetime import datetime
from rich.console import Console
from rich.table import Table

console = Console()

def run_git_command(args):
    result = subprocess.run(["git"] + args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return result.stdout.strip()

def get_branches():
    local_raw = run_git_command(["branch"]).split('\n')
    remote_raw = run_git_command(["branch", "-r"]).split('\n')

    local_branches = []
    remote_branches = []
    current_branch = ""

    for line in local_raw:
        name = line.strip()
        is_current = name.startswith("*")
        name = name.lstrip("* ").strip()
        if is_current:
            current_branch = name
        local_branches.append((name, is_current))

    for line in remote_raw:
        name = line.strip()
        if "->" not in name:
            remote_branches.append(name)

    return current_branch, local_branches, remote_branches

def get_branch_info(branch):
    first_commit = run_git_command(["log", "--reverse", "--format=%at", branch])
    last_commit = run_git_command(["log", "-1", "--format=%at", branch])
    last_msg = run_git_command(["log", "-1", "--format=%s", branch])
    author = run_git_command(["log", "-1", "--format=%an", branch])
    commit_count = run_git_command(["rev-list", "--count", branch])

    def format_time(ts):
        return datetime.fromtimestamp(int(ts)).strftime("%Y-%m-%d %H:%M:%S") if ts else "Unknown"

    return {
        "created": format_time(first_commit.splitlines()[0]) if first_commit else "Unknown",
        "last_commit": format_time(last_commit) if last_commit else "Unknown",
        "last_msg": last_msg if last_msg else "N/A",
        "author": author if author else "N/A",
        "commits": commit_count if commit_count else "0"
    }

def print_branches_table(branches, branch_type="Local", current_branch=""):
    table = Table(title=f"{branch_type} Branches", show_lines=True)

    table.add_column("Branch", style="bold cyan")
    table.add_column("Current", justify="center")
    table.add_column("Created At")
    table.add_column("Last Commit At")
    table.add_column("Commits", justify="right")
    table.add_column("Author")
    table.add_column("Last Message", style="italic")

    for name, *rest in branches:
        is_current = rest[0] if rest else False
        info = get_branch_info(name)
        table.add_row(
            name,
            "✅" if is_current else "",
            info["created"],
            info["last_commit"],
            info["commits"],
            info["author"],
            info["last_msg"]
        )

    console.print(table)

def print_help():
    console.print("""
    [bold cyan]Git Branch Viewer[/]
    [bold]Usage:[/]
        branchy [options]

    [bold]Options:[/]
        --help, -h          Show this help message
        -c, --creator       Show creator details
    """)

def print_creator():
    console.print("""


                                      .___    __                                                                            
    _____  ___  ___ _____ _____     __| _/   |__| ____   ____   ___________  ___  ______  ______________  _______  __ ____  
    \__  \ \  \/  //     \\__  \   / __ |    |  |/  _ \ /    \ / ____/\__  \ \  \/  /\  \/  /  _ \_  __ \/  _ \  \/ // ___\ 
     / __ \_>    <|  Y Y  \/ __ \_/ /_/ |    |  (  <_> )   |  < <_|  | / __ \_>    <  >    <  <_> )  | \(  <_> )   /\  \___ 
    (____  /__/\_ \__|_|  (____  /\____ |/\__|  |\____/|___|  /\__   |(____  /__/\_ \/__/\_ \____/|__|   \____/ \_/  \___  >
         \/      \/     \/     \/      \/\______|           \/    |__|     \/      \/      \/                            \/ 
        
    👨‍💻 Created by: Axmadjon Qaxxorov
    🛠 Command name: branchy
    🔗 Taplink: https://taplink.cc/itsqaxxorov
    """)

def main():
    if len(sys.argv) > 1:
        if sys.argv[1] in ['--help', '-h']:
            print_help()
            return
        elif sys.argv[1] in ['-c', '--creator']:
            print_creator()
            return
        else:
            console.print("[bold red]❌ Invalid option! Use --help or -h for available options.[/]")
            return

    if not os.path.isdir(".git"):
        console.print("[bold red]❌ This is not a Git repository.[/]")
        return

    current_branch, local_branches, remote_branches = get_branches()
    print_branches_table(local_branches, "Local", current_branch)

    remote_branch_tuples = [(name,) for name in remote_branches]
    print_branches_table(remote_branch_tuples, "Remote")

if __name__ == "__main__":
    main()
