from typing import Dict, Any, List
from pathlib import Path

SYSTEM_PROMPT = """You are a local code-generation assistant.
Requirements:
- Produce complete, runnable code with all dependencies indicated.
- Include a TESTS section describing how to test the generated artifacts.
- Include an optional PATCH section (unified diff) if you propose changes.
- Prefer safety-first patterns and explicit confirmations before any system changes.
- Keep outputs deterministic and concise.
- Include entrypoints and usage for CLI/script/service/API.
"""

def _write(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

class CodeGenerator:
    def __init__(self, model_path: str):
        self.model_path = model_path

    def generate_code(self, task: str, context: Dict[str, Any], out_dir: Path) -> (str, List[str]):
        """
        Generate files based on the task keywords: 'cli', 'api', 'data', 'service', 'script'.
        Writes real files into out_dir and returns a markdown summary plus list of created files.
        """
        created = []
        md = []
        md.append("SYSTEM_PROMPT:\n" + SYSTEM_PROMPT.strip())
        md.append("\nTASK:\n" + task.strip())
        md.append("\nCONTEXT_KEYS:\n" + ", ".join(sorted(context.keys())))

        t = task.lower()
        if "api" in t:
            code = """\
from fastapi import FastAPI

app = FastAPI()

@app.get('/hello/{name}')
def hello(name: str):
    return {"message": f"Hello, {name}! (from haven't tool's)"}
"""
            p = out_dir / "api_service.py"
            _write(p, code)
            created.append(str(p))
            md.append("\nOUTPUT: generated/api_service.py\n")
            md.append("Run: uvicorn generated.api_service:app --port 8000\n")
            md.append("\n# TESTS\n- Use HTTP client to GET /hello/Ariyan and expect JSON with message.\n")
            md.append("\n# PATCH (optional)\n- Add /health endpoint if needed.\n")

        elif "data" in t:
            code = """\
import csv

def process_csv(path):
    with open(path) as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    print(f'Total rows: {len(rows)}')
    return rows

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print('Usage: python data_processor.py <csv-file>')
        raise SystemExit(1)
    process_csv(sys.argv[1])
"""
            p = out_dir / "data_processor.py"
            _write(p, code)
            created.append(str(p))
            md.append("\nOUTPUT: generated/data_processor.py\n")
            md.append("Run: python generated/data_processor.py sample.csv\n")
            md.append("\n# TESTS\n- Provide a small CSV and expect row count output.\n")
            md.append("\n# PATCH (optional)\n- Add filters/grouping as needed.\n")

        else:
            # Default to CLI tool
            cli = """\
import sys

def main():
    if len(sys.argv) < 2:
        print('Usage: python cli_greet.py <name>')
        sys.exit(1)
    name = sys.argv[1]
    print(f'Hello, {name}! (from haven\\'t tool\\'s)')

if __name__ == '__main__':
    main()
"""
            p = out_dir / "cli_greet.py"
            _write(p, cli)
            created.append(str(p))
            md.append("\nOUTPUT: generated/cli_greet.py\n")
            md.append("Run: python generated/cli_greet.py Ariyan\n")
            md.append("\n# TESTS\n- See tests/test_cli_greet.py to validate output.\n")
            md.append("\n# PATCH (optional)\n- Add --upper flag to shout the greeting.\n")

        summary = "\n".join(md)
        return summary, created
