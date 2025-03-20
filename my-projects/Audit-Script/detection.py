# detection.py

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


def detect_testing(owner, repo, combined_deps, headers):
    """
    Very naive for now:
    - If we see 'pytest', 'jest', etc. in deps, we add it
    - For deeper detection, you'd list files in test folder
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
    for dep in combined_deps:
        dep_lower = dep.lower()
        for k, v in test_map.items():
            if k in dep_lower and v not in test_found:
                test_found.append(v)

    return test_found if test_found else ["N/A"]
