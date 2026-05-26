import os
import json
from dotenv import load_dotenv

load_dotenv()

# MongoDB Configuration
MONGODB_URI = os.getenv("MONGODB_URI", "")
DB_NAME = os.getenv("DB_NAME", "dead_internet_agent")

# Git Sandbox Settings
SANDBOX_PATH = os.getenv("SANDBOX_PATH", os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "git-sandbox"))

# Agent Orchestrator Settings
RUN_INTERVAL_SECONDS = int(os.getenv("RUN_INTERVAL_SECONDS", "5"))
PORT = int(os.getenv("PORT", "8000"))
HOST = os.getenv("HOST", "0.0.0.0")

# Credentials file path
CREDENTIALS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "credentials.json")

# Default Connection settings
IDENTITY_MODE = "sandbox" # sandbox or continuity
GITLAB_PAT = ""
GITLAB_USERNAME = ""
GITLAB_REPO = ""
GITLAB_HOST = "gitlab.com"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

def load_identity_credentials():
    global IDENTITY_MODE, GITLAB_PAT, GITLAB_USERNAME, GITLAB_REPO, GITLAB_HOST, GEMINI_API_KEY
    if os.path.exists(CREDENTIALS_PATH):
        try:
            with open(CREDENTIALS_PATH, "r") as f:
                creds = json.load(f)
                IDENTITY_MODE = creds.get("identity_mode", "sandbox")
                GITLAB_PAT = creds.get("gitlab_pat", "")
                GITLAB_USERNAME = creds.get("gitlab_username", "")
                GITLAB_REPO = creds.get("gitlab_repo", "")
                GITLAB_HOST = creds.get("gitlab_host", "gitlab.com")
                GEMINI_API_KEY = creds.get("gemini_api_key", os.getenv("GEMINI_API_KEY", ""))
                print("Identity Credentials loaded successfully.")
        except Exception as e:
            print(f"Error loading credentials.json: {e}")

def save_identity_credentials(creds: dict):
    global IDENTITY_MODE, GITLAB_PAT, GITLAB_USERNAME, GITLAB_REPO, GITLAB_HOST, GEMINI_API_KEY
    try:
        # Load existing first
        existing = {}
        if os.path.exists(CREDENTIALS_PATH):
            with open(CREDENTIALS_PATH, "r") as f:
                existing = json.load(f)
                
        existing.update(creds)
        
        with open(CREDENTIALS_PATH, "w") as f:
            json.dump(existing, f, indent=2)
            
        IDENTITY_MODE = existing.get("identity_mode", "sandbox")
        GITLAB_PAT = existing.get("gitlab_pat", "")
        GITLAB_USERNAME = existing.get("gitlab_username", "")
        GITLAB_REPO = existing.get("gitlab_repo", "")
        GITLAB_HOST = existing.get("gitlab_host", "gitlab.com")
        GEMINI_API_KEY = existing.get("gemini_api_key", "")
        return True
    except Exception as e:
        print(f"Error saving credentials: {e}")
        return False

# Initialize credentials on load
load_identity_credentials()
