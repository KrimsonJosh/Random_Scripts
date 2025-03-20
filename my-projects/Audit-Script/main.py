import requests
import base64
import json

# ------------------------------------------------------
# HELPER DETECTION & PARSE FUNCTIONS (UNCHANGED)
# ------------------------------------------------------
def detect_frameworks(dependencies):
    frameworks = []
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
        "fastapi": "FastAPI"
    }
    for dep in dependencies:
        dep_lower = dep.lower()
        for keyword, fw_name in framework_map.items():
            if keyword in dep_lower and fw_name not in frameworks:
                frameworks.append(fw_name)
    return frameworks if frameworks else ["N/A"]

def detect_database(dependencies):
    db_map = {
        "mysql": "MySQL",
        "psycopg2": "PostgreSQL",
        "pg": "PostgreSQL",
        "sqlalchemy": "SQL-based (generic)",
        "mongoose": "MongoDB",
        "mongodb": "MongoDB",
        "redis": "Redis",
        "sqlite": "SQLite"
    }
    databases = []
    for dep in dependencies:
        dep_lower = dep.lower()
        for keyword, db_name in db_map.items():
            if keyword in dep_lower and db_name not in databases:
                databases.append(db_name)
    return databases if databases else ["N/A"]

def detect_authentication(dependencies):
    auth_map = {
        "passport": "Passport.js",
        "jwt": "JWT",
        "django-auth": "Django Authentication",
        "oauth": "OAuth",
        "flask-login": "Flask-Login",
        "devise": "Devise (Ruby)",
        "omniauth": "OmniAuth (Ruby)"
    }
    auth_systems = []
    for dep in dependencies:
        dep_lower = dep.lower()
        for keyword, auth_name in auth_map.items():
            if keyword in dep_lower and auth_name not in auth_systems:
                auth_systems.append(auth_name)
    return auth_systems if auth_systems else ["N/A"]

def detect_testing(dependencies, file_list):
    test_map = {
        "pytest": "pytest",
        "unittest": "unittest",
        "jest": "Jest",
        "mocha": "Mocha",
        "junit": "JUnit",
        "rspec": "RSpec"
    }
    test_tools = []
    for dep in dependencies:
        dep_lower = dep.lower()
        for keyword, test_name in test_map.items():
            if keyword in dep_lower and test_name not in test_tools:
                test_tools.append(test_name)

    for f in file_list:
        name = f['name'].lower()
        if name in ["tests", "test"] and f['type'] == 'dir':
            if "Folder" not in test_tools:
                test_tools.append("Folder")

    return test_tools if test_tools else ["N/A"]

def detect_deployment(file_list):
    deployment = []
    known_files = {
        "dockerfile": "Docker",
        "docker-compose.yml": "Docker Compose",
        "procfile": "Heroku (Procfile)",
        "vercel.json": "Vercel",
        "app.yaml": "Google App Engine",
        "cloudbuild.yaml": "Google Cloud Build"
    }
    for f in file_list:
        lower_name = f['name'].lower()
        if lower_name in known_files:
            if known_files[lower_name] not in deployment:
                deployment.append(known_files[lower_name])
    return deployment if deployment else ["N/A"]

def parse_requirements_txt(content):
    lines = content.splitlines()
    deps = []
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#'):
            dep_name = line.split('==')[0].split('>=')[0].strip()
            deps.append(dep_name)
    return deps

def parse_package_json(content):
    try:
        data = json.loads(content)
        deps = []
        if 'dependencies' in data:
            deps.extend(list(data['dependencies'].keys()))
        if 'devDependencies' in data:
            deps.extend(list(data['devDependencies'].keys()))
        return deps
    except json.JSONDecodeError:
        return []

def get_file_content(owner, repo, path, headers):
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        file_info = r.json()
        if file_info.get('encoding') == 'base64':
            return base64.b64decode(file_info['content']).decode('utf-8', errors='ignore')
    return None

# ------------------------------------------------------
# CORE REPO AUDIT FUNCTION
# ------------------------------------------------------
def get_repo_info(owner, repo, token=None):
    """
    Gather details about a single repo. Returns a dict with the keys:
    - "Chapter (University)"
    - "Project Name"
    - "Creation Date"
    - "Date of Last Activity"
    - "Project Type"
    - "Repository Link"
    - "Live Link"
    - "Visibility"
    - "README"
    - "LICENSE (MIT, GPLv2, etc)"
    - "CONTRIBUTING.md"
    - "Open Issues"
    - "Open PRs"
    - "Issue Templates"
    - "Labeling System (describe)"
    - "Tag System (describe)"
    - "Associated Project Board (link)"
    - "Languages"
    - "Frameworks"
    - "Database"
    - "Deployment"
    - "Testing"
    - "Dependencies"
    - "Authentication"
    - "Documentation (link)"
    """
    headers = {}
    if token:
        headers['Authorization'] = f"token {token}"

    base_url = f"https://api.github.com/repos/{owner}/{repo}"
    r = requests.get(base_url, headers=headers)
    if r.status_code != 200:
        print(f"Error fetching repo info for {owner}/{repo}. Status Code:", r.status_code)
        return None

    repo_data = r.json()
    info = {}

    # Fill default "N/A" for all columns to ensure they exist
    columns = [
        "Chapter (University)", "Project Name", "Creation Date", "Date of Last Activity", "Project Type",
        "Repository Link", "Live Link", "Visibility", "README", "LICENSE (MIT, GPLv2, etc)",
        "CONTRIBUTING.md", "Open Issues", "Open PRs", "Issue Templates",
        "Labeling System (describe)", "Tag System (describe)", "Associated Project Board (link)",
        "Languages", "Frameworks", "Database", "Deployment", "Testing", "Dependencies",
        "Authentication", "Documentation (link)"
    ]
    for col in columns:
        info[col] = "N/A"

    # Basic info
    info["Project Name"] = repo_data.get("name", "N/A")
    info["Creation Date"] = repo_data.get("created_at", "N/A")
    info["Date of Last Activity"] = repo_data.get("pushed_at", "N/A")
    info["Repository Link"] = repo_data.get("html_url", "N/A")
    info["Live Link"] = repo_data.get("homepage") or "N/A"
    info["Visibility"] = "Private" if repo_data.get("private") else "Public"

    # LICENSE
    license_obj = repo_data.get("license")
    if license_obj:
        spdx = license_obj.get("spdx_id") or license_obj.get("name")
        info["LICENSE (MIT, GPLv2, etc)"] = spdx if spdx else "N/A"

    # CONTRIBUTING.md
    contrib_url = f"{base_url}/contents/CONTRIBUTING.md"
    rc = requests.get(contrib_url, headers=headers)
    if rc.status_code == 200:
        info["CONTRIBUTING.md"] = "Yes"

    # Open Issues (excluding PRs)
    issues_url = f"{base_url}/issues"
    r_issues = requests.get(issues_url, headers=headers, params={"state": "open", "filter": "all"})
    if r_issues.status_code == 200:
        issues = r_issues.json()
        open_issues = [i for i in issues if 'pull_request' not in i]
        info["Open Issues"] = len(open_issues)

    # Open PRs
    prs_url = f"{base_url}/pulls"
    r_prs = requests.get(prs_url, headers=headers, params={"state": "open"})
    if r_prs.status_code == 200:
        prs = r_prs.json()
        info["Open PRs"] = len(prs)

    # README (first 200 chars)
    readme_url = f"{base_url}/readme"
    r_readme = requests.get(readme_url, headers=headers)
    if r_readme.status_code == 200:
        readme_data = r_readme.json()
        content = readme_data.get("content")
        encoding = readme_data.get("encoding")
        if content and encoding == "base64":
            decoded = base64.b64decode(content).decode("utf-8", errors="ignore")
            info["README"] = (decoded[:200] + "...") if len(decoded) > 200 else decoded
        else:
            info["README"] = "Available"

    # Issue Templates
    issue_template_url = f"{base_url}/contents/.github/ISSUE_TEMPLATE"
    rit = requests.get(issue_template_url, headers=headers)
    if rit.status_code == 200:
        data_it = rit.json()
        if isinstance(data_it, list):
            templates = [item["name"] for item in data_it]
            info["Issue Templates"] = ", ".join(templates) if templates else "N/A"

    # Labeling System
    labels_url = f"{base_url}/labels"
    r_labels = requests.get(labels_url, headers=headers)
    if r_labels.status_code == 200:
        label_list = [lb["name"] for lb in r_labels.json()]
        info["Labeling System (describe)"] = ", ".join(label_list) if label_list else "N/A"

    # Tag System
    tags_url = f"{base_url}/tags"
    r_tags = requests.get(tags_url, headers=headers)
    if r_tags.status_code == 200:
        tag_list = [tg["name"] for tg in r_tags.json()]
        info["Tag System (describe)"] = ", ".join(tag_list) if tag_list else "N/A"

    # Associated Project Board (link) - Not trivial via REST; so "N/A" or custom logic
    info["Associated Project Board (link)"] = "N/A"

    # Languages
    lang_url = repo_data.get("languages_url")
    if lang_url:
        r_lang = requests.get(lang_url, headers=headers)
        if r_lang.status_code == 200:
            lang_list = list(r_lang.json().keys())
            info["Languages"] = ", ".join(lang_list) if lang_list else "N/A"

    # Now get top-level files for further detection
    default_branch = repo_data.get("default_branch", "main")
    contents_url = f"https://api.github.com/repos/{owner}/{repo}/contents"
    rcnt = requests.get(contents_url, headers=headers, params={"ref": default_branch})
    file_list = []
    if rcnt.status_code == 200 and isinstance(rcnt.json(), list):
        file_list = rcnt.json()

    # Gather Dependencies
    combined_deps = []
    # requirements.txt
    req_txt = get_file_content(owner, repo, "requirements.txt", headers)
    if req_txt:
        combined_deps.extend(parse_requirements_txt(req_txt))
    # Pipfile
    pip_content = get_file_content(owner, repo, "Pipfile", headers)
    if pip_content:
        lines = pip_content.splitlines()
        for line in lines:
            line = line.strip()
            if "=" in line and not line.startswith("[") and not line.startswith("#"):
                dep_name = line.split("=")[0].strip()
                combined_deps.append(dep_name)
    # package.json
    pkg_json = get_file_content(owner, repo, "package.json", headers)
    if pkg_json:
        combined_deps.extend(parse_package_json(pkg_json))

    # remove duplicates
    combined_deps = list(set(combined_deps))
    if combined_deps:
        info["Dependencies"] = ", ".join(combined_deps)

    # Detect frameworks
    fw = detect_frameworks(combined_deps)
    if fw != ["N/A"]:
        info["Frameworks"] = ", ".join(fw)

    # Detect DB
    dbs = detect_database(combined_deps)
    if dbs != ["N/A"]:
        info["Database"] = ", ".join(dbs)

    # Detect auth
    auth = detect_authentication(combined_deps)
    if auth != ["N/A"]:
        info["Authentication"] = ", ".join(auth)

    # Deployment
    dep_info = detect_deployment(file_list)
    if dep_info != ["N/A"]:
        info["Deployment"] = ", ".join(dep_info)

    # Testing
    test_info = detect_testing(combined_deps, file_list)
    if test_info != ["N/A"]:
        info["Testing"] = ", ".join(test_info)

    # Documentation (link)
    if repo_data.get("has_wiki"):
        info["Documentation (link)"] = repo_data.get("html_url", "") + "/wiki"
    else:
        docs_url = f"https://api.github.com/repos/{owner}/{repo}/contents/docs"
        rd = requests.get(docs_url, headers=headers)
        if rd.status_code == 200 and isinstance(rd.json(), list):
            info["Documentation (link)"] = f"{repo_data.get('html_url', '')}/tree/{default_branch}/docs"

    # Topics: Chapter (University) + Project Type
    topics_url = f"{base_url}/topics"
    custom_headers = {**headers}
    custom_headers["Accept"] = "application/vnd.github.mercy-preview+json"
    rt = requests.get(topics_url, headers=custom_headers)
    if rt.status_code == 200:
        topic_list = rt.json().get("names", [])
        # Chapter (University)
        chapter = [t for t in topic_list if ("chapter" in t.lower() or "university" in t.lower())]
        if chapter:
            info["Chapter (University)"] = chapter[0]
        # Project Type
        project_types = ["web", "mobile", "api", "library", "cli"]
        pt = [t for t in topic_list if t.lower() in project_types]
        if pt:
            info["Project Type"] = pt[0]

    return info

# ------------------------------------------------------
# GET ALL REPOS + POST TO SHEETY
# ------------------------------------------------------
def get_all_repos(owner, token=None, is_org=False):
    """
    Retrieves all repositories for a user (default) or org (if is_org=True).
    """
    headers = {}
    if token:
        headers["Authorization"] = f"token {token}"

    repos = []
    page = 1
    while True:
        if is_org:
            url = f"https://api.github.com/orgs/{owner}/repos"
        else:
            url = f"https://api.github.com/users/{owner}/repos"

        resp = requests.get(url, headers=headers, params={"per_page": 100, "page": page})
        if resp.status_code != 200:
            print(f"Error fetching repos from {url}, status = {resp.status_code}")
            break

        data = resp.json()
        if not data:
            break  # no more repos

        for repo_obj in data:
            repos.append(repo_obj["name"])

        page += 1

    return repos

def post_to_sheety(sheety_url, sheety_token, row_data):
    """
    row_data => dictionary that matches your Sheety column names.
    """
    headers = {
        "Content-Type": "application/json"
    }
    if sheety_token:
        headers["Authorization"] = f"Bearer {sheety_token}"

    # Sheety expects something like { "sheet1": { ...fields... } }
    body = {"sheet1": row_data}
    r = requests.post(sheety_url, headers=headers, json=body)
    if r.status_code not in [200, 201]:
        print("Error posting to Sheety:", r.status_code, r.text)
    return r

def main():
    print("=== GitHub Projects Auditor (Sheety) ===")
    owner = input("Enter GitHub owner (user or org): ").strip()
    token = input("Enter your GitHub Token (or leave blank for public only): ").strip() or None
    org_choice = input("Is this an organization? (y/n): ").lower().startswith('y')

    sheety_url = input("Enter Sheety POST endpoint URL: ").strip()
    sheety_token = input("Enter Sheety Bearer Token (if any): ").strip() or None

    # Fetch all repos
    repos = get_all_repos(owner, token, is_org=org_choice)
    if not repos:
        print("No repositories found or error occurred.")
        return

    print(f"Found {len(repos)} repositories. Gathering info and posting to Sheety...")

    for repo_name in repos:
        info = get_repo_info(owner, repo_name, token=token)
        if not info:
            continue

        # Convert the "info" dict to Sheety JSON fields.
        # The user wants these columns in the final spreadsheet:
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

        # CHECK Sheety's "API Docs" to see EXACT JSON keys for these columns.
        # Example guess below:

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

        # POST to Sheety to add a new row
        resp = post_to_sheety(sheety_url, sheety_token, row_payload)
        if resp.status_code in [200, 201]:
            print(f"Successfully added row for repo '{repo_name}'.")
        else:
            print(f"Failed to add row for repo '{repo_name}'. See error above.")

    print("Done!")

if __name__ == "__main__":
    main()
