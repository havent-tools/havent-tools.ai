# personal-ai-agent — “haven’t tool’s”

A local-first, advanced AI agent that takes your idea (prompt) and generates ready-to-run tools/software code with tests. It runs entirely without elevated permissions and can use a separate terminal session.

## Features
- No sudo required; user-level only.
- Agent name: “haven’t tool’s”.
- Generator produces runnable code with TESTS and optional PATCH.
- Verifier runs pytest, flake8, mypy, bandit, and coverage.
- Executor prints [PROPOSED CMD] and asks for confirmation before running.
- Optional Docker sandbox (you can skip it).

## Quick start (Linux)
1. `python3 -m venv .venv && source .venv/bin/activate`
2. `pip install -r requirements.txt`
3. `chmod +x ai_launcher.sh`
4. `./ai_launcher.sh` or `./ai_launcher.sh tmux` for a separate tmux session
5. Provide your prompt; the agent will generate code and propose verification steps.

## Structure
- `src/main.py`: Entry flow (ask task → optional context → generate → verify).
- `src/agent/fetchers.py`: GitHub tree + local folder reader (whitelisted).
- `src/agent/generator.py`: Local LLM wrapper, SYSTEM_PROMPT, templates for CLI/API/Data.
- `src/agent/verifier.py`: pytest, flake8, mypy, bandit, coverage (Docker optional).
- `src/agent/executor.py`: propose-and-execute with confirmation and logging.
