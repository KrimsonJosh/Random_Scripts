# GitHub Auditor

A simple tool that scans one or more GitHub repositories, gathers metadata (like README presence, LICENSE, frameworks, etc.), and logs the results into a Google Sheet via [Sheety](https://sheety.co/).

## Setup

### 1. Clone & Install
```bash
git clone https://github.com/YourOrg/github-auditor.git
cd github-auditor
pip install -r requirements.txt
```

### 2. GitHub Token
Create a `.env` file in the root:
```
API_TOKEN=ghp_YourGitHubTokenHere
```
- Needed for private repos or higher rate limits (LIMIT IS 60 IF NO API KEY).

### 3. Sheety Setup
- Go to [Sheety](https://sheety.co/) and create a project.
- Get your POST endpoint URL (e.g., `https://api.sheety.co/xxxx/yourSheet/sheet1`).
- If the sheet is private, get your **Bearer Token**.

## Usage
Run the script:
```bash
python main.py
```
Answer prompts:
- GitHub owner (or org)
- Chapter (University) name
- Sheety POST URL
- Sheety Token (if any)
- Is it an organization? (y/n)

Each repo will be audited and results added to your Google Sheet.

## What It Detects
- README & LICENSE
- Open Issues & PRs
- Languages, Frameworks, Databases
- Testing tools (e.g., Jest, pytest)
- Deployment tools (e.g., Docker, Vercel)
- Authentication (JWT, Clerk, etc.)

## Notes
- Customize detection logic in `detection.py`


## TODO:
- Need to add better detection logic and more items to map