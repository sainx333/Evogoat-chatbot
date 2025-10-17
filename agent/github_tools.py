import os, requests, subprocess, tempfile, importlib.util

GITHUB_RAW = "https://raw.githubusercontent.com"

def get_github_file(user, repo, branch, path):
    url = f"{GITHUB_RAW}/{user}/{repo}/{branch}/{path}"
    r = requests.get(url)
    r.raise_for_status()
    return r.text

def install_package(pkg_name):
    """Limited installer: only for simple, known packages."""
    if pkg_name.isidentifier():
        subprocess.run(["pip", "install", pkg_name, "--quiet"], check=True)

def load_module_from_code(name, code):
    """Load a module from source text safely into memory."""
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".py")
    tmp.write(code.encode())
    tmp.close()
    spec = importlib.util.spec_from_file_location(name, tmp.name)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    os.unlink(tmp.name)
    return mod
