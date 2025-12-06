import subprocess
import shlex
import time
from pathlib import Path
from typing import List, Optional

def _log_path(cfg_log: str) -> Path:
    p = Path(cfg_log)
    p.parent.mkdir(parents=True, exist_ok=True)
    return p

def propose_and_execute(cmd: str, whitelist: Optional[List[str]] = None, require_confirm: bool = True, timeout_sec: int = 180, log_file: Optional[str] = None) -> int:
    print(f"[PROPOSED CMD] {cmd}")
    allowed = True
    if whitelist:
        allowed = any(cmd.strip().startswith(w) for w in whitelist)
    if not allowed:
        print("Command not in whitelist. Aborting.")
        return 1

    if require_confirm:
        ans = input("Run this command? [y/N] ").strip().lower()
        if ans not in ("y", "yes"):
            print("Aborted by user.")
            return 1

    start = time.time()
    rc = 0
    try:
        proc = subprocess.run(shlex.split(cmd), timeout=timeout_sec)
        rc = proc.returncode
    except subprocess.TimeoutExpired:
        print("Command timed out.")
        rc = 124
    except Exception as e:
        print(f"Error running command: {e}")
        rc = 1
    finally:
        elapsed = time.time() - start
        print(f"[EXIT CODE] {rc} (elapsed {elapsed:.2f}s)")
        if log_file:
            lp = _log_path(log_file)
            with lp.open("a", encoding="utf-8") as f:
                f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} | rc={rc} | {cmd}\n")
    return rc

def load_config(config_path: Path, example_path: Path) -> dict:
    import json
    if config_path.exists():
        try:
            return json.loads(config_path.read_text(encoding="utf-8"))
        except Exception:
            pass
    try:
        return json.loads(example_path.read_text(encoding="utf-8"))
    except Exception:
        return {
            "agent_name": "haven't tool's",
            "allowed_fetch_domains": ["api.github.com", "raw.githubusercontent.com", "github.com"],
            "local_model_path": "",
            "executor": {"use_docker": False},
            "command_whitelist": ["pytest", "flake8", "mypy", "bandit -r .", "coverage run", "coverage report", "ls", "echo", "cat", "tmux", "screen"],
            "safety": {"require_confirm_before_run": True, "max_command_runtime_sec": 180, "log_commands_to": "logs/commands.log"},
            "generator": {"enable_plugins": True, "default_output_dir": "generated", "output_types": ["cli", "script", "service", "api", "data"]}
        }
