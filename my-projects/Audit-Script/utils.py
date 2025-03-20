# utils.py

import base64
import requests

def parse_requirements_txt(content):
    """
    content is a *decoded* string of requirements.txt
    """
    lines = content.splitlines()
    deps = []
    for line in lines:
        line = line.strip()
        if line and not line.startswith("#"):
            dep_name = line.split("==")[0].split(">=")[0].strip()
            deps.append(dep_name)
    return deps

def parse_package_json(content):
    """
    content is the decoded string of package.json
    """
    import json
    try:
        data = json.loads(content)
        all_deps = []
        if "dependencies" in data:
            all_deps.extend(list(data["dependencies"].keys()))
        if "devDependencies" in data:
            all_deps.extend(list(data["devDependencies"].keys()))
        return all_deps
    except:
        return []

def read_readme_license(readme_text):
    """
    Check for license keywords in the readme text.
    Return "MIT", "GPL", "Apache", or "BSD" if found, else None.
    """
    possible = ["MIT", "GPL", "Apache", "BSD"]
    lower_text = readme_text.lower()
    for pl in possible:
        if pl.lower() in lower_text:
            return pl
    return None

def build_headers(token):
    """
    Build the standard GitHub headers, including your token if present.
    """
    headers = {
        "Accept": "application/vnd.github+json"
    }
    if token:
        headers["Authorization"] = f"token {token}"
    return headers

def list_directory_recursive(owner, repo, path, headers):
    """
    Example for a deeper listing of all subfolders in a directory.
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        return []
    items = resp.json()
    if not isinstance(items, list):
        return []

    out = []
    for i in items:
        out.append(i)
        if i["type"] == "dir":
            subpath = i["path"]
            out.extend(list_directory_recursive(owner, repo, subpath, headers))
    return out
