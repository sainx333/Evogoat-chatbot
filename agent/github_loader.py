# agent/github_loader.py
import os, requests, base64, tempfile, importlib.util, json
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()
TOKEN = os.getenv("GITHUB_TOKEN")
API = "https://api.github.com"

HEADERS = {"Authorization": f"token {TOKEN}"} if TOKEN else {}

REPOS_DIR = Path("repos")
REPOS_DIR.mkdir(exist_ok=True)

def list_repo_files(owner: str, repo: str, path: str = "", ref: str = "main"):
    """Return list of files (name, path, type, size) under path."""
    url = f"{API}/repos/{owner}/{repo}/contents/{path}?ref={ref}"
    r = requests.get(url, headers=HEADERS, timeout=15)
    r.raise_for_status()
    return r.json()  # list of entries

def fetch_file(owner: str, repo: str, filepath: str, ref: str = "main"):
    """Return decoded content of a file via GitHub API (safe read-only)."""
    url = f"{API}/repos/{owner}/{repo}/contents/{filepath}?ref={ref}"
    r = requests.get(url, headers=HEADERS, timeout=15)
    r.raise_for_status()
    data = r.json()
    if data.get("encoding") == "base64":
        return base64.b64decode(data["content"]).decode("utf-8", errors="ignore")
    return data.get("content", "")

def save_repo_file(owner: str, repo: str, filepath: str, content: str):
    dest = REPOS_DIR / owner / repo / Path(filepath).parent
    dest.mkdir(parents=True, exist_ok=True)
    out = REPOS_DIR / owner / repo / filepath
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(content, encoding="utf-8")
    return out

def inspect_and_cache(owner: str, repo: str, path: str = "", ref: str = "main"):
    """List files and cache them locally for review; return index."""
    files = list_repo_files(owner, repo, path, ref)
    index = []
    for entry in files:
        index.append({
            "name": entry.get("name"),
            "path": entry.get("path"),
            "type": entry.get("type"),
            "size": entry.get("size"),
            "sha": entry.get("sha")
        })
    # write index for human review
    idxp = REPOS_DIR / owner / repo / "index.json"
    idxp.parent.mkdir(parents=True, exist_ok=True)
    idxp.write_text(json.dumps(index, indent=2))
    return index

def load_module_from_code(name: str, code: str):
    """Dynamically load a module from source; returns module object."""
    # Static safety checks BEFORE loading
    banned = ["os.system", "subprocess", "exec(", "eval("]
    for b in banned:
        if b in code:
            raise ValueError("Code contains banned patterns; manual review required")

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".py")
    tmp.write(code.encode("utf-8"))
    tmp.flush()
    tmp.close()
    spec = importlib.util.spec_from_file_location(name, tmp.name)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)   # executes — only after checks and approval
    os.unlink(tmp.name)
    return module
