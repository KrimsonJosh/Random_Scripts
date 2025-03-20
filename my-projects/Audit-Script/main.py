import requests
import base64
import json
import time
import os
from dotenv import load_dotenv

load_dotenv()

GithubToken = os.getenv('API_TOKEN')
print("GitHub Token (start):", GithubToken[:10] + "..." if GithubToken else "None")

# -----------------------------------------------------------------------
# 1) UTILITY: RECURSIVE FOLDER FETCH
# -----------------------------------------------------------------------
def list_directory_recursive(owner, repo, path, headers, accumulated=None):
    """
    Recursively list all files & subfolders under `path`.
    Returns a list of file objects (same shape as GitHub /contents response).
    """
    if accumulated is None:
        accumulated = []

    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        return accumulated  # no access or doesn't exist

    items = resp.json()
    # If 'items' is not a list, it's probably a file or an error
    if not isinstance(items, list):
        return accumulated

    for i in items:
        accumulated.append(i)
        if i["type"] == "dir":
            # Recurse into subdir
            subpath = i["path"]  # e.g. "tests/subdir"
            list_directory_recursive(owner, repo, subpath, headers, accumulated)

    return accumulated


# -----------------------------------------------------------------------
# 2) DETECTION / PARSING FUNCTIONS
# -----------------------------------------------------------------------

def detect_frameworks(dependencies):
    frameworks_found = []
    framework_map = {
        "django": "Django",
        "flask": "Flask",
        "react": "React",
        "angular": "Angular",
        "vue": "Vue.js",
        "express": "Express",
        "rails": "Ruby on Rails",
        "laravel": "Laravel",
        "spring-boot": "Spring Boot",
        "fastapi": "FastAPI",
        "next": "Next.js",
        "nuxt": "Nuxt",
        "svelte": "Svelte"
    }
    for dep in dependencies:
        dep_lower = dep.lower()
        for keyword, name in framework_map.items():
            if keyword in dep_lower and name not in frameworks_found:
                frameworks_found.append(name)
    return frameworks_found if frameworks_found else ["N/A"]

def detect_database(dependencies):
    db_found = []
    db_map = {
        "mysql": "MySQL",
        "psycopg2": "PostgreSQL",
        "pg": "PostgreSQL",
        "sqlalchemy": "SQL-based (generic)",
        "mongoose": "MongoDB",
        "mongodb": "MongoDB",
        "redis": "Redis",
        "sqlite": "SQLite",
        "supabase": "Supabase",
        "prisma": "Prisma (ORM)"
    }
    for dep in dependencies:
        dep_lower = dep.lower()
        for keyword, name in db_map.items():
            if keyword in dep_lower and name not in db_found:
                db_found.append(name)
    return db_found if db_found else ["N/A"]

def detect_authentication(dependencies):
    auth_found = []
    auth_map = {
        "clerk": "Clerk",
        "jwt": "JWT",
        "next-auth": "NextAuth",
        "passport": "Passport.js",
        "oauth": "OAuth",
        "flask-login": "Flask-Login",
        "devise": "Devise",
        "omniauth": "OmniAuth"
    }
    for dep in dependencies:
        dep_lower = dep.lower()
        for keyword, name in auth_map.items():
            if keyword in dep_lower and name not in auth_found:
                auth_found.append(name)
    return auth_found if auth_found else ["N/A"]

def parse_requirements_txt(content):
    lines = content.splitlines()
    deps = []
    for line in lines:
        line = line.strip()
        if line and not line.startswith("#"):
            dep_name = line.split("==")[0].split(">=")[0].strip()
            deps.append(dep_name)
    return deps

def parse_package_json(content):
    try:
        data = json.loads(content)
        deps = []
        if "dependencies" in data:
            deps.extend(data["dependencies"].keys())
        if "devDependencies" in data:
            deps.extend(data["devDependencies"].keys())
        return list(deps)
    except:
        return []

def get_file_content(owner, repo, path, headers):
    """
    Return the text content of path if it exists/base64-encoded, else None.
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    resp = requests.get(url, headers=headers)
    if resp.status_code == 200:
        j = resp.json()
        if j.get("encoding") == "base64":
            return base64.b64decode(j["content"]).decode("utf-8", errors="ignore")
    return None


# -----------------------------------------------------------------------
# 3) TEST DETECTION (INCL. RECURSION INTO `test/` or `tests/`)
# -----------------------------------------------------------------------
def detect_testing(owner, repo, combined_deps, file_list_top, headers):
    """
    - Checks known test deps in `combined_deps` (pytest, jest, etc.)
    - Checks top-level "test"/"tests" folder, recurses inside to find known test files
      or jest.config, etc.
    - Returns a list (or ["N/A"] if none found).
    """
    test_found = set()

    # Basic map from dependencies
    test_map = {
        "pytest": "pytest",
        "unittest": "unittest",
        "jest": "Jest",
        "mocha": "Mocha",
        "junit": "JUnit",
        "rspec": "RSpec"
    }
    for dep in combined_deps:
        dep_lower = dep.lower()
        for keyword, name in test_map.items():
            if keyword in dep_lower:
                test_found.add(name)

    # Check top-level for "test" or "tests" folder
    test_dir_paths = []
    for f_obj in file_list_top:
        if f_obj["type"] == "dir":
            dname = f_obj["name"].lower()
            if dname in ["test", "tests"]:
                test_dir_paths.append(f_obj["path"])

    # Recurse each test folder and see what we find
    for tpath in test_dir_paths:
        all_files = list_directory_recursive(owner, repo, tpath, headers)
        for f_obj in all_files:
            if f_obj["type"] == "file":
                fname_lower = f_obj["name"].lower()
                # If we see a jest.config.* => add "Jest"
                if fname_lower.startswith("jest.config"):
                    test_found.add("Jest")
                # Another example: "test_something.py" => might indicate python test => "pytest" or "unittest"
                # You can add more logic here if you want deeper detection.

        # If we found a test folder, let's label it
        if "Test Folder" not in test_found:
            test_found.add("Test Folder")

    return list(test_found) if test_found else ["N/A"]


# -----------------------------------------------------------------------
# 4) REPO AUDIT FUNCTION
# -----------------------------------------------------------------------
def audit_repo(owner, repo, chapter, token=None):
    """
    - Everything default => "N/A" if not found
    - Deeper test detection, etc.
    """
    headers = {
        "Accept": "application/vnd.github+json"
    }
    if token:
        headers["Authorization"] = f"token {token}"

    base_url = f"https://api.github.com/repos/{owner}/{repo}"
    r = requests.get(base_url, headers=headers)
    if r.status_code != 200:
        print(f"Error fetching repo {owner}/{repo} -> {r.status_code}")
        return None

    data = r.json()
    info = {}

    # 1) Chapter (University)
    info["Chapter (University)"] = chapter or "N/A"

    # 2) Project Name
    info["Project Name"] = data.get("name") or "N/A"

    # 3) Creation Date
    info["Creation Date"] = data.get("created_at") or "N/A"

    # 4) Date of Last Activity
    info["Date of Last Activity"] = data.get("pushed_at") or "N/A"

    # 5) Project Type => "N/A"
    info["Project Type"] = "N/A"

    # 6) Repository Link
    info["Repository Link"] = data.get("html_url") or "N/A"

    # 7) Live Link
    homepage = data.get("homepage") or ""
    info["Live Link"] = homepage.strip() if homepage.strip() else "N/A"

    # 8) Visibility
    info["Visibility"] = "Private" if data.get("private") else "Public"

    # 9) README => "✅" if found, else "❌"
    readme_url = f"{base_url}/readme"
    rr = requests.get(readme_url, headers=headers)
    readme_found = (rr.status_code == 200)
    info["README"] = "✅" if readme_found else "❌"

    # Grab README text if found (for license check)
    readme_text = ""
    if readme_found:
        rd = rr.json()
        if rd.get("content"):
            try:
                readme_text = base64.b64decode(rd["content"]).decode("utf-8", errors="ignore")
            except:
                pass

    # 10) LICENSE
    license_obj = data.get("license")
    if license_obj and (license_obj.get("spdx_id") or license_obj.get("name")):
        spdx = license_obj.get("spdx_id") or license_obj.get("name")
        info["LICENSE (MIT, GPLv2, etc)"] = spdx
    else:
        # Check readme text for MIT, GPL, Apache, BSD
        possible_licenses = ["MIT", "GPL", "Apache", "BSD"]
        found_lic = None
        for plc in possible_licenses:
            if plc.lower() in readme_text.lower():
                found_lic = plc
                break
        info["LICENSE (MIT, GPLv2, etc)"] = found_lic if found_lic else "N/A"

    # 11) CONTRIBUTING.md => "✅" or "❌"
    contrib_url = f"{base_url}/contents/CONTRIBUTING.md"
    rc = requests.get(contrib_url, headers=headers)
    info["CONTRIBUTING.md"] = "✅" if rc.status_code == 200 else "❌"

    # 12) Open Issues (excluding PRs)
    issues_url = f"{base_url}/issues"
    r_issues = requests.get(issues_url, headers=headers, params={"state": "open", "filter": "all"})
    open_issues_count = 0
    if r_issues.status_code == 200:
        issues_data = r_issues.json()
        actual_issues = [i for i in issues_data if "pull_request" not in i]
        open_issues_count = len(actual_issues)
    info["Open Issues"] = open_issues_count or "N/A"  # If 0 => "N/A"

    # 13) Open PRs => if 0 => "N/A"
    prs_url = f"{base_url}/pulls"
    r_prs = requests.get(prs_url, headers=headers, params={"state": "open"})
    if r_prs.status_code == 200:
        open_pr_count = len(r_prs.json())
        info["Open PRs"] = open_pr_count if open_pr_count > 0 else "N/A"
    else:
        info["Open PRs"] = "N/A"

    # 14) Issue Templates => "✅" or "❌"
    issue_templ_url = f"{base_url}/contents/.github/ISSUE_TEMPLATE"
    rt = requests.get(issue_templ_url, headers=headers)
    info["Issue Templates"] = "✅" if rt.status_code == 200 else "❌"

    # 15) Labeling System (describe) => see if we have any labels
    labels_url = base_url + "/labels"
    r_labels = requests.get(labels_url, headers=headers)
    if r_labels.status_code == 200:
        labels_data = r_labels.json()
        if labels_data:
            info["Labeling System (describe)"] = ", ".join([lbl["name"] for lbl in labels_data])
        else:
            info["Labeling System (describe)"] = "N/A"
    else:
        info["Labeling System (describe)"] = "N/A"

    # 16) Tag System (describe) => see if we have any tags
    tags_url = base_url + "/tags"
    r_tags = requests.get(tags_url, headers=headers)
    if r_tags.status_code == 200:
        tags_data = r_tags.json()
        if tags_data:
            info["Tag System (describe)"] = ", ".join([tg["name"] for tg in tags_data])
        else:
            info["Tag System (describe)"] = "N/A"
    else:
        info["Tag System (describe)"] = "N/A"

    # 17) Associated Project Board => "N/A" (we aren't enumerating project boards)
    info["Associated Project Board (link)"] = "N/A"

    # 18) Languages
    lang_url = data.get("languages_url", "")
    if lang_url:
        r_lang = requests.get(lang_url, headers=headers)
        if r_lang.status_code == 200 and isinstance(r_lang.json(), dict):
            lang_dict = r_lang.json()
            if lang_dict:
                all_langs = list(lang_dict.keys())
                info["Languages"] = ", ".join(all_langs)
            else:
                info["Languages"] = "N/A"
        else:
            info["Languages"] = "N/A"
    else:
        info["Languages"] = "N/A"

    # 19-22) We read top-level files to detect deployment & partial testing
    default_branch = data.get("default_branch", "main")
    contents_url = f"{base_url}/contents"
    rc_list = requests.get(contents_url, headers=headers, params={"ref": default_branch})
    file_list_top = []
    if rc_list.status_code == 200 and isinstance(rc_list.json(), list):
        file_list_top = rc_list.json()

    # Gather minimal dependencies from requirements/Pipfile/package.json
    combined_deps = []

    # requirements.txt
    rtxt = get_file_content(owner, repo, "requirements.txt", headers)
    if rtxt:
        combined_deps.extend(parse_requirements_txt(rtxt))

    # Pipfile
    pfile = get_file_content(owner, repo, "Pipfile", headers)
    if pfile:
        for line in pfile.splitlines():
            line = line.strip()
            if "=" in line and not line.startswith("[") and not line.startswith("#"):
                dep_name = line.split("=")[0].strip()
                combined_deps.append(dep_name)

    # package.json
    pkgjson = get_file_content(owner, repo, "package.json", headers)
    if pkgjson:
        combined_deps.extend(parse_package_json(pkgjson))

    combined_deps = list(set(combined_deps))

    # 19) Frameworks
    fw = detect_frameworks(combined_deps)
    info["Frameworks"] = ", ".join(fw) if fw != ["N/A"] else "N/A"

    # 20) Database
    dbs = detect_database(combined_deps)
    info["Database"] = ", ".join(dbs) if dbs != ["N/A"] else "N/A"

    # 21) Deployment
    # Let's just check top-level for now
    found_deploy = []
    known_files = {
        "dockerfile": "Docker",
        "docker-compose.yml": "Docker Compose",
        "procfile": "Heroku (Procfile)",
        "vercel.json": "Vercel",
        "netlify.toml": "Netlify",
        "app.yaml": "Google App Engine",
        "cloudbuild.yaml": "Google Cloud Build"
    }
    for f_obj in file_list_top:
        fname = f_obj["name"].lower()
        if fname in known_files:
            if known_files[fname] not in found_deploy:
                found_deploy.append(known_files[fname])
    info["Deployment"] = ", ".join(found_deploy) if found_deploy else "N/A"

    # 22) Testing => deeper detection
    test_list = detect_testing(owner, repo, combined_deps, file_list_top, headers)
    if test_list == ["N/A"]:
        info["Testing"] = "N/A"
    else:
        info["Testing"] = ", ".join(test_list)

    # 23) Dependencies => always "N/A"
    info["Dependencies"] = "N/A"

    # 24) Authentication
    auth_list = detect_authentication(combined_deps)
    info["Authentication"] = ", ".join(auth_list) if auth_list != ["N/A"] else "N/A"

    # 25) Documentation => "N/A"
    info["Documentation (link)"] = "N/A"

    return info


# -----------------------------------------------------------------------
# 5) GET ALL REPOS + POST TO SHEETY
# -----------------------------------------------------------------------
def get_all_repos(owner, token=None, is_org=False):
    headers = {
        "Accept": "application/vnd.github+json"
    }
    if token:
        headers["Authorization"] = f"token {token}"

    all_repos = []
    page = 1
    while True:
        if is_org:
            url = f"https://api.github.com/orgs/{owner}/repos"
        else:
            url = f"https://api.github.com/users/{owner}/repos"

        resp = requests.get(url, headers=headers, params={"per_page": 100, "page": page})
        if resp.status_code != 200:
            print(f"Error fetching repos for {owner}. Status code: {resp.status_code}")
            print("Response text:", resp.text)
            break

        data = resp.json()
        if not data:
            break

        for repo_obj in data:
            all_repos.append(repo_obj["name"])
        page += 1

    return all_repos

def post_to_sheety(sheety_url, sheety_token, row_data):
    headers = {
        "Content-Type": "application/json"
    }
    if sheety_token:
        headers["Authorization"] = f"Bearer {sheety_token}"

    body = {
        "sheet1": row_data
    }
    r = requests.post(sheety_url, headers=headers, json=body)
    if r.status_code not in [200, 201]:
        print("Error posting to Sheety:", r.status_code, r.text)
    return r

def main():
    print("=== GitHub Projects Auditor (Sheety) ===")

    owner = input("Enter GitHub owner (user or org): ").strip()
    token = GithubToken  # from .env
    is_org = input("Is this an organization? (y/n): ").lower().startswith("y")

    chapter_name = input("Enter Chapter (University) name: ").strip()

    sheety_url = input("Enter Sheety POST endpoint URL: ").strip()
    sheety_token = input("Enter Sheety Bearer Token (if any): ").strip() or None

    repos = get_all_repos(owner, token=token, is_org=is_org)
    print(f"Found {len(repos)} repositories for '{owner}'.")

    for repo_name in repos:
        info = audit_repo(owner, repo_name, chapter=chapter_name, token=token)
        time.sleep(1)  # small delay to avoid rate limit
        if not info:
            continue

        # Build row payload
        row_payload = {
            "chapterUniversity": info["Chapter (University)"],
            "projectName": info["Project Name"],
            "creationDate": info["Creation Date"],
            "dateOfLastActivity": info["Date of Last Activity"],
            "projectType": info["Project Type"],
            "repositoryLink": info["Repository Link"],
            "liveLink": info["Live Link"],
            "visibility": info["Visibility"],
            "readme": info["README"],
            "licenseMitGplv2Etc": info["LICENSE (MIT, GPLv2, etc)"],
            "contributingMd": info["CONTRIBUTING.md"],
            "openIssues": info["Open Issues"],
            "openPrs": info["Open PRs"],
            "issueTemplates": info["Issue Templates"],
            "labelingSystemDescribe": info["Labeling System (describe)"],
            "tagSystemDescribe": info["Tag System (describe)"],
            "associatedProjectBoardLink": info["Associated Project Board (link)"],
            "languages": info["Languages"],
            "frameworks": info["Frameworks"],
            "database": info["Database"],
            "deployment": info["Deployment"],
            "testing": info["Testing"],
            "dependencies": info["Dependencies"],
            "authentication": info["Authentication"],
            "documentationLink": info["Documentation (link)"]
        }

        # Print for debug so you see final data going to Sheety
        print(f"\nPosting row for '{repo_name}':")
        for k,v in row_payload.items():
            print(f"  {k}: {v}")

        resp = post_to_sheety(sheety_url, sheety_token, row_payload)
        if resp.status_code in [200, 201]:
            print(f"✓ Successfully added row for repo '{repo_name}'")
        else:
            print(f"✗ Failed to add row for repo '{repo_name}'")

    print("Done!")

if __name__ == "__main__":
    main()
