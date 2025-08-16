
import os
import subprocess
import pathlib
import shutil

# =========================
# CONFIGURATION
# =========================
CONFIG_NAME = "api"                             # Must use IBM default 'api'
GRAPHQL_FILE = "schema/index.graphql"          # Path to your GraphQL schema
# =========================

# === CONFIGURATION ===
API_NAME = "GQL/my_first_stepzen"
REST_ENDPOINT = "https://fake-json-api.mock.beeceptor.com/users" #ANY REST ENDPOINT
HEADERS = {
    "Authorization": "Bearer DUMMY_TOKEN"
}


# === CONFIGURATION ===
STEPZEN_DOMAIN = "us-east-a.ibm.stepzen.net"   # 🔹 Replace with your IBM StepZen domain
STEPZEN_ACCOUNT = ""            # 🔹 IBM account name
STEPZEN_ADMINKEY = ""              # 🔹 IBM admin key
GRAPHQL_SOURCE = "schema/index.graphql"        # Path to your GraphQL schema
GRAPHQL_DEST = "index.graphql"  
BASE_FOLDER = "YOUR_WORKSPACE_FOLDER"
# ======================


def ensure_graphql():
    """Ensure index.graphql exists at StepZen root."""
    source = pathlib.Path(GRAPHQL_SOURCE)
    dest = pathlib.Path(GRAPHQL_DEST)
    if not source.exists():
        raise FileNotFoundError(f"[ERROR] GraphQL schema not found at {GRAPHQL_SOURCE}")
    shutil.copy(source, dest)
    print(f"[INFO] Copied {GRAPHQL_SOURCE} to {GRAPHQL_DEST}")

def clean_cache():
    """Delete old StepZen cache to prevent stale configurations."""
    stepzen_cache = pathlib.Path(".stepzen")
    if stepzen_cache.exists():
        shutil.rmtree(stepzen_cache)
        print("[INFO] Cleared old StepZen cache")

def stepzen_login():
    """Login for IBM-managed StepZen by writing credentials directly."""
    creds_path = pathlib.Path.home() / ".stepzen" / "credentials"
    creds_path.parent.mkdir(parents=True, exist_ok=True)

    if creds_path.exists():
        print("[INFO] StepZen already logged in (credentials file exists).")
        return

    print("[INFO] Writing IBM StepZen credentials...")
    creds_content = f"""
account: {STEPZEN_ACCOUNT}
adminkey: {STEPZEN_ADMINKEY}
domain: {STEPZEN_DOMAIN}
"""
    with open(creds_path, "w") as f:
        f.write(creds_content.strip())

    print(f"[INFO] Credentials saved to {creds_path}")

    # Verify login
    subprocess.run(["stepzen", "whoami"], check=True)


def write_config():
    """Write IBM-compliant config.yaml in the requested nested format."""
    config_content = (
        "configurationset:\n"
        "  - configuration:\n"
        "      name: api\n"
        "      configuration: rest_backend\n"
    )
    with open("config.yaml", "w", encoding="utf-8") as f:
        f.write(config_content)
    print("[INFO] IBM-compliant nested config.yaml written")


def write_graphql_schema(rest_url):
    with open('user.txt', 'r') as file:
        content = file.read()

    """Create StepZen GraphQL schema mapping REST endpoint."""
    graphql_content =  content + f"""
    

type Query {{
  users: [User] @rest(endpoint: "{rest_url}", configuration: "api")
}}
"""
    os.makedirs("schema", exist_ok=True)
    with open("schema/index.graphql", "w") as f:
        f.write(graphql_content.strip())
    print("[INFO] Created schema/index.graphql")

def deploy_stepzen():
    """Deploy API to IBM StepZen."""
    print(f"[INFO] Deploying {API_NAME} to IBM StepZen...")
    subprocess.run(["stepzen", "deploy", API_NAME], check=True)
    print("[INFO] Deployment finished.")


def init_stepzen():
    """Initialize StepZen workspace if missing."""
    if not os.path.exists(".stepzen"):
        print("[INFO] Initializing StepZen workspace...")
        subprocess.run(["stepzen", "init"], check=True)
    else:
        print("[INFO] StepZen workspace already exists.")


import subprocess
import os

def start_stepzen():
    """Start StepZen API locally."""
    print("[INFO] Starting StepZen API locally in current directory...")
    subprocess.run(["stepzen", "start"], check=True)



def main():
    clean_cache()         # Remove old workspace metadata
    init_stepzen()       # Initialize StepZen workspace
    stepzen_login()       # Write IBM credentials
    write_config()        # Create config.yaml with default 'api'
    write_graphql_schema(REST_ENDPOINT)  # Create GraphQL schema
    ensure_graphql()      # Ensure index.graphql exists
    deploy_stepzen()      # Deploy API
    start_stepzen()       # Start API locally

if __name__ == "__main__":
    main()
