#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
from pathlib import Path
from textwrap import dedent

from agent.executor import propose_and_execute, load_config
from agent.fetchers import GitHubFetcher, LocalFolderReader
from agent.generator import CodeGenerator
from agent.verifier import Verifier

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = PROJECT_ROOT / "config.json"
CONFIG_EXAMPLE_PATH = PROJECT_ROOT / "config.example.json"
LOGS_DIR = PROJECT_ROOT / "logs"
GENERATED_DIR = PROJECT_ROOT / "generated"
TESTS_DIR = PROJECT_ROOT / "tests"

def ask(question: str, default: str = "") -> str:
    prompt = f" [{default}] " if default else " "
    val = input(question + prompt).strip()
    return val if val else default

def ask_yes_no(q: str, default="no") -> bool:
    prompt = " [y/N] " if default.lower() in ("no", "n", "") else " [Y/n] "
    ans = input(q + prompt).strip().lower()
    if ans == "" and default:
        ans = default
    return ans in ("y", "yes")

def ensure_dirs():
    for d in (PROJECT_ROOT, LOGS_DIR, GENERATED_DIR, TESTS_DIR):
        Path(d).mkdir(parents=True, exist_ok=True)

def bootstrap_tests():
    # Minimal test to make verifier happy
    tf = TESTS_DIR / "test_cli_greet.py"
    if not tf.exists():
        tf.write_text(dedent("""\
            from subprocess import run, PIPE
            def test_cli_greet():
                p = run(['python', 'generated/cli_greet.py', 'Ariyan'], stdout=PIPE, text=True)
                assert 'Hello, Ariyan!' in p.stdout
        """), encoding="utf-8")

def run_flow():
    print("=== Advanced personal-ai-agent — 'haven't tool's' ===")
    ensure_dirs()

    cfg = load_config(CONFIG_PATH, CONFIG_EXAMPLE_PATH)
    agent_name = cfg.get("agent_name", "haven't tool's")
    whitelist = cfg.get("command_whitelist", [])
    require_confirm = bool(cfg.get("safety", {}).get("require_confirm_before_run", True))
    timeout = int(cfg.get("safety", {}).get("max_command_runtime_sec", 180))
    log_file = cfg.get("safety", {}).get("log_commands_to", "")

    # Agent prompt
    task = ask("Describe your idea/prompt for the agent:", default="Build a CLI that greets by name.")
    print(f"\n[Agent: {agent_name}] Task:\n- {task}\n")

    # Optional context
    ctx_choice = ask("Context source [none/local/github]?", default="none").lower()
    context = {}
    if ctx_choice == "local":
        root = ask("Local folder path:", default=str(PROJECT_ROOT))
        reader = LocalFolderReader(Path(root))
        context["local_files"] = reader.read_files()
    elif ctx_choice == "github":
        repo = ask("GitHub repo (owner/name):", default="octocat/Hello-World")
        ref = ask("Ref (branch/sha):", default="main")
        token = os.environ.get("GITHUB_TOKEN", "")
        fetcher = GitHubFetcher(cfg.get("allowed_fetch_domains", []), token)
        try:
            context["github_tree"] = fetcher.fetch_tree(repo, ref)
        except Exception as e:
            print(f"GitHub fetch failed: {e}")

    # Generate code
    gen = CodeGenerator(model_path=cfg.get("local_model_path", ""))
    output_md, created_files = gen.generate_code(task, context, GENERATED_DIR)
    out_file = GENERATED_DIR / "output.md"
    out_file.write_text(output_md, encoding="utf-8")
    print(f"Generated output saved: {out_file.relative_to(PROJECT_ROOT)}")
    for rel in created_files:
        print(f"Wrote: {Path(rel).relative_to(PROJECT_ROOT)}")

    # Bootstrap a basic test (if not present)
    bootstrap_tests()

    # Verification
    verifier = Verifier(cfg)
    if ask_yes_no("Run verification (pytest/flake8/mypy/bandit/coverage)?", default="yes"):
        verifier.run_checks()

    # Optional Docker sandbox build
    if ask_yes_no("Build Docker sandbox image?", default="no"):
        verifier.build_sandbox()

    print("\n=== Summary ===")
    print(f"- Agent: {agent_name}")
    print(f"- Prompt: {task}")
    print(f"- Generated: {out_file.relative_to(PROJECT_ROOT)} and files under generated/")
    print("- Tests: tests/")
    print("- All commands require confirmation and are logged if configured.")

if __name__ == "__main__":
    run_flow()
