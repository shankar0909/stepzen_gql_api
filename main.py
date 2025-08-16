
import os
import subprocess
import pathlib
import shutil
import yaml

# =========================
# CONFIGURATION
# =========================
CONFIG_NAME = "api"                             # Must use IBM default 'api'
GRAPHQL_FILE = "schema/index.graphql"          # Path to your GraphQL schema
# =========================

# === CONFIGURATION ===
API_NAME = "GQL/my_first_stepzen"
REST_ENDPOINT = "https://fake-json-api.mock.beeceptor.com/users"
HEADERS = {
    "Authorization": "Bearer DUMMY_TOKEN"
}


# === CONFIGURATION ===
STEPZEN_DOMAIN = "us-east-a.ibm.stepzen.net"   # 🔹 Replace with your IBM StepZen domain
STEPZEN_ACCOUNT = ""            # 🔹 IBM account name
STEPZEN_ADMINKEY = ""              # 🔹 IBM admin key
GRAPHQL_SOURCE = "schema/index.graphql"        # Path to your GraphQL schema
GRAPHQL_DEST = "index.graphql"  
BASE_FOLDER = "{YOUR BASE DIR}"
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
    if os.path.exists(os.path.join(BASE_FOLDER, ".stepzen")):
        print("[INFO] Initializing StepZen workspace...")
        subprocess.run(["stepzen", "init"], check=True)
    else:
        print("[INFO] StepZen workspace already exists.")



def start_stepzen():
    """Start StepZen API locally."""
    print("[INFO] Starting StepZen API locally in current directory...")
    subprocess.run(["stepzen", "start"], check=True)



def write_config(source_type, connection, output_dir=None, query_name=None, query_type=None, name=None):
    """
    Dynamically run StepZen import for REST or DB/GraphQL sources
    and write IBM-compliant config.yaml in the workspace root.
    """
    if output_dir is None:
        output_dir = os.getcwd()  # default to current dir as workspace root
    subprocess.run(["stepzen", "init", output_dir], check=True)
    # Ensure workspace exists
   # ensure_workspace(output_dir)

    # Build StepZen import command
    # if source_type.lower() == "rest":
    #     cmd = ["stepzen", "import", f"curl {connection}", "--dir", output_dir]
    # else:
    #     cmd = ["stepzen", "import", source_type, connection, "--dir", output_dir]

    cmd = ["stepzen", "import"]
    if source_type.lower() == "rest":
        if not query_name or not query_type or not name:
            raise ValueError("For REST imports, 'query_name', 'query_type', and 'name' are required")
        
        # Build StepZen import command
    cmd = ["stepzen", "import"]

    if source_type.lower() == "rest":
        if not query_name or not query_type or not name:
            raise ValueError("For REST imports, 'query_name', 'query_type', and 'name' are required")
        url = connection.strip()  # remove leading/trailing whitespace
        # Properly quote the URL for StepZen CLI
        cmd += [
            "curl",
            url,
            "--query-name", query_name,
            "--query-type", query_type,
            "--name", name
        ]
    else:
        cmd += [source_type, connection]

    print(f"[INFO] Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        raise RuntimeError(f"[ERROR] StepZen import failed:\n{result.stderr}")

    print(result.stdout)

    # Collect all .graphql files generated
    schema_files = [f for f in os.listdir(output_dir) if f.endswith(".graphql")]
    if not schema_files:
        raise RuntimeError("[ERROR] No .graphql files generated by stepzen import")


    config = {
    "configurationset": [
        {
            "configuration": {
                "name": "api",
                "configuration": "rest_backend"
            
        }
        }
       
    ]  # optional, for your tracking
    }

    config_path = os.path.join(output_dir, "config.yaml")
    with open(config_path, "w", encoding="utf-8") as f:
        yaml.dump(config, f, sort_keys=False)

    print(f"[INFO] IBM-compliant config.yaml written at {config_path}")
    return schema_files


def ensure_workspace(output_dir):
    """Ensure the StepZen workspace exists; create it if missing."""
    if not os.path.isdir(os.path.join(output_dir, ".stepzen")):
        print(f"[INFO] StepZen workspace not found in {output_dir}, initializing...")
        subprocess.run(["stepzen", "init", output_dir], check=True)
        print(f"[INFO] Workspace initialized at {output_dir}")

def main():
    clean_cache()         # Remove old workspace metadata
    init_stepzen()       # Initialize StepZen workspace
    stepzen_login()       # Write IBM credentials
    write_config(
    source_type="rest",
    connection=REST_ENDPOINT,
    output_dir=BASE_FOLDER,
    query_name="users",
    query_type="User",
    name="schema"
)
    #write_config()        # Create config.yaml with default 'api'
    #write_graphql_schema(REST_ENDPOINT)  # Create GraphQL schema
    ensure_graphql()      # Ensure index.graphql exists
    deploy_stepzen()      # Deploy API
    start_stepzen()       # Start API locally

if __name__ == "__main__":
    main()
