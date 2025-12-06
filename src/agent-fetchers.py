from pathlib import Path
from typing import List, Dict, Any, Optional

try:
    import requests
except Exception:
    requests = None

ALLOWED_EXTS = {'.py', '.js', '.sh', '.md', '.go'}

class GitHubFetcher:
    def __init__(self, allowed_domains: Optional[List[str]] = None, token: Optional[str] = None):
        self.allowed_domains = allowed_domains or []
        self.token = token

    def _check_domain(self, url: str) -> bool:
        return any(d in url for d in self.allowed_domains)

    def fetch_tree(self, repo: str, ref: str = "main") -> List[Dict[str, Any]]:
        base = "https://api.github.com"
        url = f"{base}/repos/{repo}/git/trees/{ref}?recursive=1"
        if not self._check_domain(base):
            raise RuntimeError("Domain not allowed for fetch.")
        if requests is None:
            raise RuntimeError("requests not available.")
        headers = {"Accept": "application/vnd.github+json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        r = requests.get(url, headers=headers, timeout=30)
        r.raise_for_status()
        data = r.json()
        result = []
        for node in data.get("tree", []):
            path = node.get("path", "")
            typ = node.get("type", "")
            if typ == "blob":
                ext = Path(path).suffix.lower()
                if ext in ALLOWED_EXTS:
                    raw_url = f"https://raw.githubusercontent.com/{repo}/{ref}/{path}"
                    result.append({"path": path, "type": "file", "url": raw_url})
            elif typ == "tree":
                result.append({"path": path, "type": "dir", "url": None})
        return result

class LocalFolderReader:
    def __init__(self, root: Path):
        self.root = Path(root)

    def list_files(self) -> List[Path]:
        files = []
        for p in self.root.rglob("*"):
            if p.is_file() and p.suffix.lower() in ALLOWED_EXTS:
                files.append(p)
        return files

    def read_files(self) -> Dict[str, str]:
        out = {}
        for f in self.list_files():
            try:
                out[str(f.relative_to(self.root))] = f.read_text(encoding='utf-8', errors='ignore')
            except Exception:
                out[str(f.relative_to(self.root))] = "<ERROR READING FILE>"
        return out
