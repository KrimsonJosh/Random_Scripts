import requests
import base64
import json

# -----------------------------------------------------------------------
# 1) DETECTION / PARSING FUNCTIONS (with some expansions as requested)
# -----------------------------------------------------------------------

def detect_frameworks(dependencies):
    """
    Check for known frameworks in the list of dependencies (case-insensitive).
    If none found, return ["N/A"].
    """
    frameworks_found = []
    # Add more if needed (e.g., "nuxt": "Nuxt", "svelte": "Svelte")
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
    """
    Check for known DB libraries.
    If none found, return ["N/A"].
    """
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
    """
    If we find 'clerk', 'jwt', 'next-auth', 'passport', 'oauth', 'flask-login', 'devise', 'omniauth', etc.
    return them as a list, otherwise ["N/A"].
    """
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

def detect_testing(dependencies, file_list):
    """
    If we find 'pytest', 'unittest', 'jest', 'mocha', 'junit', 'rspec', etc.
    Also check if there's a 'tests' or 'test' folder. 
    Return them as a list, or ["N/A"] if none found.
    """
    test_found = []
    test_map = {
        "pytest": "pytest",
        "unittest": "unittest",
        "jest": "Jest",
        "mocha": "Mocha",
        "junit": "JUnit",
        "rspec": "RSpec"
    }
    for dep in dependencies:
        dep_lower = dep.lower()
        for keyword, name in test_map.items():
            if keyword in dep_lower and name not in test_found:
                test_found.append(name)

    # Check for a "tests" or "test" folder
    for item in file_list:
        if item["type"] == "dir":
            dir_name = item["name"].lower()
            if dir_name in ["tests", "test"] and "Test Folder" not in test_found:
                test_found.append("Test Folder")

    return test_found if test_found else ["N/A"]

def detect_deployment(file_list):
    """
    Check for Dockerfile, docker-compose, procfile, vercel.json, netlify.toml, etc.
    Return them as a list or ["N/A"] if none found.
    """
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
    for f in file_list:
        fname = f["name"].lower()
        if fname in known_files:
            label = known_files[fname]
            if label not in found_deploy:
                found_deploy.append(label)

    return found_deploy if found_deploy else ["N/A"]

# We won't parse dependencies in detail (your request). 
# But let's keep these functions so we can do minimal detection of frameworks/auth/etc.
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
# 2) REPO AUDIT FUNCTION (with the EXACT columns & new rules)
# -----------------------------------------------------------------------
def audit_repo(owner, repo, chapter, token=None):
    """
    Returns a dict with the columns you requested, following your new rules:
      - Chapter (University): always the user’s input
      - Project Name
      - Creation Date
      - Date of Last Activity
      - Project Type => "N/A" (unless you want to guess from topics)
      - Repository Link
      - Live Link => if homepage is set, else "N/A"
      - Visibility
      - README => "Checkmark" if found, else "No checkmark"
      - LICENSE (MIT, GPLv2, etc) => if found, else "N/A"
      - CONTRIBUTING.md => "Checkmark" or "No checkmark"
      - Open Issues => 0 if none or if error
      - Open PRs => 0 if none or if error
      - Issue Templates => "Checkmark" or "N/A"
      - Labeling System (describe) => "Checkmark" if any labels, else "N/A"
      - Tag System (describe) => always "N/A"
      - Associated Project Board (link) => always "N/A"
      - Languages => from the GH API if any, else "N/A"
      - Frameworks => from naive detection, else "N/A"
      - Database => from naive detection, else "N/A"
      - Deployment => from naive detection, else "N/A"
      - Testing => from naive detection, else "N/A"
      - Dependencies => always "N/A"
      - Authentication => from naive detection, else "N/A"
      - Documentation (link) => always "N/A"
    """
    headers = {}
    if token:
        headers["Authorization"] = f"token {token}"

    base_url = f"https://api.github.com/repos/{owner}/{repo}"
    r = requests.get(base_url, headers=headers)
    if r.status_code != 200:
        print(f"Error fetching repo {owner}/{repo} -> {r.status_code}")
        return None

    data = r.json()
    info = {}

    # Populate defaults
    info["Chapter (University)"] = chapter
    info["Project Name"] = data.get("name", "N/A")
    info["Creation Date"] = data.get("created_at", "N/A")
    info["Date of Last Activity"] = data.get("pushed_at", "N/A")
    info["Project Type"] = "N/A"
    info["Repository Link"] = data.get("html_url", "N/A")

    # "Live Link": only set if 'homepage' is not empty
    homepage = data.get("homepage") or ""
    info["Live Link"] = homepage if homepage.strip() else "N/A"

    # Visibility
    info["Visibility"] = "Private" if data.get("private") else "Public"

    # README => check if readme endpoint returns 200
    readme_url = f"{base_url}/readme"
    rr = requests.get(readme_url, headers=headers)
    info["README"] = "Checkmark" if rr.status_code == 200 else "No checkmark"

    # LICENSE
    license_obj = data.get("license")
    if license_obj and (license_obj.get("spdx_id") or license_obj.get("name")):
        spdx = license_obj.get("spdx_id") or license_obj.get("name")
        info["LICENSE (MIT, GPLv2, etc)"] = spdx
    else:
        info["LICENSE (MIT, GPLv2, etc)"] = "N/A"

    # CONTRIBUTING.md => check if it exists
    contrib_url = f"{base_url}/contents/CONTRIBUTING.md"
    rc = requests.get(contrib_url, headers=headers)
    info["CONTRIBUTING.md"] = "Checkmark" if rc.status_code == 200 else "No checkmark"

    # Open Issues (excluding PRs)
    issues_url = f"{base_url}/issues"
    r_issues = requests.get(issues_url, headers=headers, params={"state": "open", "filter": "all"})
    if r_issues.status_code == 200:
        issues_data = r_issues.json()
        open_issues = [i for i in issues_data if "pull_request" not in i]
        info["Open Issues"] = len(open_issues)
    else:
        info["Open Issues"] = 0

    # Open PRs
    prs_url = f"{base_url}/pulls"
    r_prs = requests.get(prs_url, headers=headers, params={"state": "open"})
    if r_prs.status_code == 200:
        info["Open PRs"] = len(r_prs.json())
    else:
        info["Open PRs"] = 0

    # Issue Templates => "Checkmark" if .github/ISSUE_TEMPLATE exists
    issue_templ_url = f"{base_url}/contents/.github/ISSUE_TEMPLATE"
    rt = requests.get(issue_templ_url, headers=headers)
    if rt.status_code == 200:
        info["Issue Templates"] = "Checkmark"
    else:
        info["Issue Templates"] = "N/A"

    # Labeling System => "Checkmark" if any labels, else "N/A"
    labels_url = f"{base_url}/labels"
    rl = requests.get(labels_url, headers=headers)
    if rl.status_code == 200:
        label_list = rl.json()
        if label_list:  # non-empty
            info["Labeling System (describe)"] = "Checkmark"
        else:
            info["Labeling System (describe)"] = "N/A"
    else:
        info["Labeling System (describe)"] = "N/A"

    # Tag System => always "N/A"
    info["Tag System (describe)"] = "N/A"

    # Associated Project Board => always "N/A"
    info["Associated Project Board (link)"] = "N/A"

    # Languages
    lang_url = data.get("languages_url")
    if lang_url:
        r_lang = requests.get(lang_url, headers=headers)
        if r_lang.status_code == 200:
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

    # We still need to read top-level files to detect deployment or testing
    default_branch = data.get("default_branch", "main")
    contents_url = f"{base_url}/contents"
    rc_list = requests.get(contents_url, headers=headers, params={"ref": default_branch})
    file_list = rc_list.json() if rc_list.status_code == 200 else []

    # Gather minimal dependencies to detect frameworks/auth/etc. 
    # But final "Dependencies" = "N/A" per your request.
    combined_deps = []

    # Check requirements.txt
    req_txt = get_file_content(owner, repo, "requirements.txt", headers)
    if req_txt:
        combined_deps.extend(parse_requirements_txt(req_txt))

    # Check Pipfile
    pipfile_txt = get_file_content(owner, repo, "Pipfile", headers)
    if pipfile_txt:
        for line in pipfile_txt.splitlines():
            line = line.strip()
            if "=" in line and not line.startswith("[") and not line.startswith("#"):
                dep_name = line.split("=")[0].strip()
                combined_deps.append(dep_name)

    # Check package.json
    package_json_txt = get_file_content(owner, repo, "package.json", headers)
    if package_json_txt:
        combined_deps.extend(parse_package_json(package_json_txt))

    # De-dupe
    combined_deps = list(set(combined_deps))

    # Frameworks
    fw = detect_frameworks(combined_deps)
    info["Frameworks"] = ", ".join(fw) if fw != ["N/A"] else "N/A"

    # DB
    dbs = detect_database(combined_deps)
    info["Database"] = ", ".join(dbs) if dbs != ["N/A"] else "N/A"

    # Deployment
    dep_list = detect_deployment(file_list)
    info["Deployment"] = ", ".join(dep_list) if dep_list != ["N/A"] else "N/A"

    # Testing
    test_list = detect_testing(combined_deps, file_list)
    info["Testing"] = ", ".join(test_list) if test_list != ["N/A"] else "N/A"

    # Dependencies => always "N/A"
    info["Dependencies"] = "N/A"

    # Authentication
    auth_list = detect_authentication(combined_deps)
    info["Authentication"] = ", ".join(auth_list) if auth_list != ["N/A"] else "N/A"

    # Documentation => always "N/A"
    info["Documentation (link)"] = "N/A"

    return info

# -----------------------------------------------------------------------
# 3) GET ALL REPOS + POST TO SHEETY
# -----------------------------------------------------------------------
def get_all_repos(owner, token=None, is_org=False):
    """
    Gets all repos for a user (or org if is_org=True), paginating if needed.
    """
    headers = {}
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
            break

        data = resp.json()
        if not data:
            break

        for repo_obj in data:
            all_repos.append(repo_obj["name"])
        page += 1

    return all_repos

def post_to_sheety(sheety_url, sheety_token, row_data):
    """
    POST one row to Sheety.
    row_data is a dict with keys matching your Sheety column names.
    """
    headers = {"Content-Type": "application/json"}
    if sheety_token:
        headers["Authorization"] = f"Bearer {sheety_token}"

    body = {
        # "sheet1": {...} or whatever the sheet name is as recognized by Sheety
        "sheet1": row_data
    }
    r = requests.post(sheety_url, headers=headers, json=body)
    if r.status_code not in [200, 201]:
        print("Error posting to Sheety:", r.status_code, r.text)
    return r

def main():
    print("=== GitHub Projects Auditor (Sheety) ===")

    owner = input("Enter GitHub owner (user or org): ").strip()
    token = input("Enter your GitHub token (or leave blank): ").strip() or None
    is_org_input = input("Is this an organization? (y/n): ").lower()
    is_org = (is_org_input.startswith("y"))

    # CHAPTER/UNIVERSITY is a single user-provided string.
    chapter_name = input("Enter Chapter (University) name: ").strip()

    # Sheety
    sheety_url = input("Enter Sheety POST endpoint URL: ").strip()
    sheety_token = input("Enter Sheety Bearer Token (if any): ").strip() or None

    # Get all repos
    repos = get_all_repos(owner, token=token, is_org=is_org)
    print(f"Found {len(repos)} repositories for '{owner}'.")

    for repo_name in repos:
        audited = audit_repo(owner, repo_name, chapter=chapter_name, token=token)
        if not audited:
            # Some error occurred
            continue

        # Now we must map these columns to the Sheety JSON fields exactly:
        # 
        #  1  Chapter (University)
        #  2  Project Name
        #  3  Creation Date
        #  4  Date of Last Activity
        #  5  Project Type
        #  6  Repository Link
        #  7  Live Link
        #  8  Visibility
        #  9  README
        # 10 LICENSE (MIT, GPLv2, etc)
        # 11 CONTRIBUTING.md
        # 12 Open Issues
        # 13 Open PRs
        # 14 Issue Templates
        # 15 Labeling System (describe)
        # 16 Tag System (describe)
        # 17 Associated Project Board (link)
        # 18 Languages
        # 19 Frameworks
        # 20 Database
        # 21 Deployment
        # 22 Testing
        # 23 Dependencies
        # 24 Authentication
        # 25 Documentation (link)
        #
        # Check your Sheety "API Docs" for the EXACT JSON field names it expects.  
        # If the column is "LICENSE (MIT, GPLv2, etc)", Sheety might transform that into "licenseMitGplv2Etc", etc.

        row_payload = {
            "chapterUniversity": audited["Chapter (University)"],
            "projectName": audited["Project Name"],
            "creationDate": audited["Creation Date"],
            "dateOfLastActivity": audited["Date of Last Activity"],
            "projectType": audited["Project Type"],
            "repositoryLink": audited["Repository Link"],
            "liveLink": audited["Live Link"],
            "visibility": audited["Visibility"],
            "readme": audited["README"],
            "licenseMitGplv2Etc": audited["LICENSE (MIT, GPLv2, etc)"],
            "contributingMd": audited["CONTRIBUTING.md"],
            "openIssues": audited["Open Issues"],
            "openPrs": audited["Open PRs"],
            "issueTemplates": audited["Issue Templates"],
            "labelingSystemDescribe": audited["Labeling System (describe)"],
            "tagSystemDescribe": audited["Tag System (describe)"],
            "associatedProjectBoardLink": audited["Associated Project Board (link)"],
            "languages": audited["Languages"],
            "frameworks": audited["Frameworks"],
            "database": audited["Database"],
            "deployment": audited["Deployment"],
            "testing": audited["Testing"],
            "dependencies": audited["Dependencies"],
            "authentication": audited["Authentication"],
            "documentationLink": audited["Documentation (link)"]
        }

        # POST to Sheety
        resp = post_to_sheety(sheety_url, sheety_token, row_payload)
        if resp.status_code in [200, 201]:
            print(f"✓ Added row for repo '{repo_name}'")
        else:
            print(f"✗ Failed to add row for repo '{repo_name}'")

    print("Done!")

if __name__ == "__main__":
    main()
