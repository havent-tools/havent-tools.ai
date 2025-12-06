from typing import Dict, Any
from .executor import propose_and_execute

class Verifier:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.use_docker = bool(config.get("executor", {}).get("use_docker", False))
        self.whitelist = list(config.get("command_whitelist", []))
        self.timeout = int(config.get("safety", {}).get("max_command_runtime_sec", 180))
        self.require_confirm = bool(config.get("safety", {}).get("require_confirm_before_run", True))
        self.log_file = config.get("safety", {}).get("log_commands_to", "")

    def build_sandbox(self) -> int:
        cmd = "docker build -t personal-ai-agent-sandbox -f docker/Dockerfile.sandbox ."
        return propose_and_execute(cmd, self.whitelist, self.require_confirm, self.timeout, self.log_file)

    def run_checks(self) -> int:
        cmds = [
            "pytest",
            "flake8",
            "mypy",
            "bandit -r .",
            "coverage run -m pytest",
            "coverage report -m"
        ]
        rc = 0
        for c in cmds:
            rc = propose_and_execute(c, self.whitelist, self.require_confirm, self.timeout, self.log_file)
            if rc != 0:
                break
        return rc
