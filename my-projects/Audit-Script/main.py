# main.py

import os
import time
from dotenv import load_dotenv
import requests

# Import functions
from github_api import get_all_repos, get_repo_data, get_file_content
from detection import detect_frameworks, detect_database, detect_authentication, detect_testing
from sheety_api import post_to_sheety
from utils import (
    parse_requirements_txt,
    parse_package_json,
    read_readme_license,
    build_headers,
    list_directory_recursive
)

load_dotenv()  # Loads .env file into environment variables

GITHUB_TOKEN = os.getenv("API_TOKEN")


def process_repo(owner, repo, chapter_name, headers):
    """
    Audit a single repo, returning a dictionary of info to be posted.
    """
    repo_data = get_repo_data(owner, repo, headers)
    if not repo_data:
        print(f"[process_repo] Error: Could not retrieve data for {repo}")
        return None

    # Basic info dictionary
    info = {}

    # 1) Chapter (University)
    info["Chapter (University)"] = chapter_name or "N/A"

    # 2) Project Name
    info["Project Name"] = repo_data.get("name") or "N/A"

    # 3) Creation Date
    info["Creation Date"] = repo_data.get("created_at") or "N/A"

    # 4) Date of Last Activity
    info["Date of Last Activity"] = repo_data.get("pushed_at") or "N/A"

    # 5) Project Type => "N/A"
    info["Project Type"] = "N/A"

    # 6) Repository Link
    info["Repository Link"] = repo_data.get("html_url") or "N/A"

    # 7) Live Link (homepage)
    homepage = repo_data.get("homepage") or ""
    info["Live Link"] = homepage.strip() if homepage.strip() else "N/A"

    # 8) Visibility
    info["Visibility"] = "Private" if repo_data.get("private") else "Public"

    # 9) README => "✅" if found, else "❌"
    readme_resp = get_file_content(owner, repo, "README.md", headers)
    if readme_resp:
        info["README"] = "✅"
    else:
        info["README"] = "❌"

    # 10) LICENSE (MIT, GPLv2, etc)
    #    1) Check GitHub API's license object
    #    2) If not found, parse README for common license
    license_obj = repo_data.get("license")
    if license_obj and (license_obj.get("spdx_id") or license_obj.get("name")):
        spdx = license_obj.get("spdx_id") or license_obj.get("name")
        info["LICENSE (MIT, GPLv2, etc)"] = spdx
    else:
        # Check README text for a possible license
        readme_text = get_file_content(owner, repo, "README.md", headers) or ""
        found_license = read_readme_license(readme_text)
        info["LICENSE (MIT, GPLv2, etc)"] = found_license or "N/A"

    # 11) CONTRIBUTING.md => "✅" or "❌"
    contrib = get_file_content(owner, repo, "CONTRIBUTING.md", headers)
    info["CONTRIBUTING.md"] = "✅" if contrib else "❌"

    # 12) Open Issues (excluding PRs)
    issues_url = f"https://api.github.com/repos/{owner}/{repo}/issues?state=open"
    response = requests.get(issues_url, headers=headers)
    if response.status_code == 200:
        issues = response.json()
        open_issues = [issue for issue in issues if "pull_request" not in issue]
        info["Open Issues"] = len(open_issues)
    else:
        info["Open Issues"] = "N/A"

    # 13) Open PRs
    prs_url = f"https://api.github.com/repos/{owner}/{repo}/pulls?state=open"
    prs_resp = requests.get(prs_url, headers=headers)
    if prs_resp.status_code == 200:
        open_prs = prs_resp.json()
        info["Open PRs"] = len(open_prs)
    else:
        info["Open PRs"] = "N/A"
    issue_template = get_file_content(owner, repo, ".github/ISSUE_TEMPLATE", headers)
    info["Issue Templates"] = "✅" if issue_template else "❌"
    # 15) Labeling System (describe)
    # 16) Tag System (describe)
    # 17) Associated Project Board (link)
    info["Labeling System (describe)"] = "N/A"
    info["Tag System (describe)"] = "N/A"
    info["Associated Project Board (link)"] = "N/A"

    # 18) Languages
    lang_url = repo_data.get("languages_url")
    if lang_url:
        langs_resp = requests.get(lang_url, headers=headers)
        if langs_resp.status_code == 200:
            langs_dict = langs_resp.json()
            if langs_dict:
                info["Languages"] = ", ".join(langs_dict.keys())
            else:
                info["Languages"] = "N/A"
        else:
            info["Languages"] = "N/A"
    else:
        info["Languages"] = "N/A"

    # 19-22) We'll do detection for frameworks, DB, deployment, testing
    #        by reading top-level files + any known config files
    # 1) Gather dependencies from requirements.txt, package.json, etc.
    combined_deps = []
    req_txt = get_file_content(owner, repo, "requirements.txt", headers)
    if req_txt:
        combined_deps.extend(parse_requirements_txt(req_txt))
    pkg_json = get_file_content(owner, repo, "package.json", headers)
    if pkg_json:
        combined_deps.extend(parse_package_json(pkg_json))

    # We'll remove duplicates
    combined_deps = list(set(combined_deps))

    # 19) Frameworks
    fw = detect_frameworks(combined_deps)
    info["Frameworks"] = ", ".join(fw) if fw != ["N/A"] else "N/A"

    # 20) Database
    dbs = detect_database(combined_deps)
    info["Database"] = ", ".join(dbs) if dbs != ["N/A"] else "N/A"

    # 21) Deployment => minimal detection at top-level
    # for example, Dockerfile, etc.
    # We'll just do naive approach or skip
    info["Deployment"] = "N/A"

    # 22) Testing => detect testing from combined deps + test folder
    test_list = detect_testing(owner, repo, combined_deps, headers)
    info["Testing"] = ", ".join(test_list) if test_list != ["N/A"] else "N/A"

    # 23) Dependencies => "N/A"
    info["Dependencies"] = "N/A"

    # 24) Authentication
    auths = detect_authentication(combined_deps)
    info["Authentication"] = ", ".join(auths) if auths != ["N/A"] else "N/A"

    # 25) Documentation => "N/A"
    info["Documentation (link)"] = "N/A"

    return info


def main():
    print("=== GitHub Projects Auditor ===")
    owner = input("Enter GitHub owner (user or org): ").strip()
    chapter_name = input("Enter Chapter (University) name: ").strip()
    sheety_url = input("Enter Sheety POST endpoint URL: ").strip()
    sheety_token = input("Enter Sheety Bearer Token (if any): ").strip() or None
    is_org = input("Is this an organization? (y/n): ").lower().startswith("y")

    # Build GitHub headers
    headers = build_headers(GITHUB_TOKEN)

    # Get all repos
    repos = get_all_repos(owner, headers, is_org=is_org)
    print(f"Found {len(repos)} repos for '{owner}'.")

    for repo_name in repos:
        info = process_repo(owner, repo_name, chapter_name, headers)
        if not info:
            continue

        # Build row payload for Sheety
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

        # Post to Sheety
        resp = post_to_sheety(sheety_url, sheety_token, row_payload)
        if resp.status_code in [200, 201]:
            print(f"✓ Added row for repo '{repo_name}'")
        else:
            print(f"✗ Failed row for '{repo_name}': {resp.status_code} {resp.text}")

        time.sleep(1)  # small delay to avoid rate-limiting

    print("Done!")


if __name__ == "__main__":
    main()
