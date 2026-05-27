import os
import subprocess
import shutil
import json
import urllib.parse
import requests
from typing import List, Dict, Any
from backend import config
from backend import memory

class GitSandboxAgent:
    def __init__(self, sandbox_path: str = None):
        self.sandbox_path = sandbox_path or config.SANDBOX_PATH
        self.init_sandbox()

    def _run_git_cmd(self, args: List[str]) -> str:
        try:
            result = subprocess.run(
                ["git"] + args,
                cwd=self.sandbox_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except FileNotFoundError:
            print("Git executable not found on this system. Git features will be disabled/simulated.")
            return "Error: Git not installed"
        except subprocess.CalledProcessError as e:
            print(f"Git command failed: git {' '.join(args)} - Error: {e.stderr}")
            return f"Error: {e.stderr}"

    def init_sandbox(self):
        """Initializes the local git repository if not already existing."""
        if not os.path.exists(self.sandbox_path):
            try:
                os.makedirs(self.sandbox_path, exist_ok=True)
            except Exception as e:
                print(f"Error creating sandbox path {self.sandbox_path}: {e}")
            
        # Check if it's already a git repo
        if not os.path.exists(os.path.join(self.sandbox_path, ".git")):
            res = self._run_git_cmd(["init"])
            if "Error: Git not installed" in res:
                print("Skipping Git repository initialization - Git is not installed.")
                commits = memory.get_commits(limit=1)
                if not commits:
                    memory.add_commit("a1b2c3d", "Initial commit from Autonomous Digital Self (Simulated)", "NULL//HUMAN <agent@nullhuman.ai>", ["README.md"])
                return

            self._run_git_cmd(["config", "user.name", "NULL//HUMAN"])
            self._run_git_cmd(["config", "user.email", "agent@nullhuman.ai"])
            
            # Create a base README file
            readme_path = os.path.join(self.sandbox_path, "README.md")
            try:
                with open(readme_path, "w") as f:
                    f.write("# Digital Doppelgänger Sandbox\n\nThis repository is managed autonomously by the NULL//HUMAN Agent.\n")
            except Exception as e:
                print(f"Error writing README.md in sandbox: {e}")
            
            self._run_git_cmd(["add", "README.md"])
            self._run_git_cmd(["commit", "-m", "Initial commit from Autonomous Digital Self"])
            
            # Save commit in memory DB
            log = self._run_git_cmd(["log", "-n", "1", "--pretty=format:%H|%an|%s"])
            if "|" in log:
                sha, author, msg = log.split("|", 2)
                memory.add_commit(sha[:7], msg, author, ["README.md"])

    def get_commit_history(self) -> List[Dict[str, Any]]:
        """Returns the git commit history as a list of dictionaries."""
        output = self._run_git_cmd(["log", "--pretty=format:%H|%an|%ae|%ar|%s", "-n", "15"])
        commits = []
        if not output or "Error" in output:
            try:
                db_commits = memory.get_commits(limit=15)
                return [
                    {
                        "sha": c["sha"],
                        "author": c["author"],
                        "message": c["message"],
                        "time": "just now",
                        "files": c.get("files_changed", [])
                    }
                    for c in db_commits
                ]
            except Exception:
                return commits
            
        for line in output.split("\n"):
            if not line.strip() or "|" not in line:
                continue
            parts = line.split("|")
            if len(parts) >= 5:
                sha, name, email, relative_time, message = parts[:5]
                # Get files changed for this commit
                files_out = self._run_git_cmd(["show", "--name-only", "--pretty=format:", sha])
                files = [f.strip() for f in files_out.split("\n") if f.strip()]
                commits.append({
                    "sha": sha[:7],
                    "author": f"{name} <{email}>",
                    "message": message,
                    "time": relative_time,
                    "files": files
                })
        return commits

    def make_autonomous_commit(self, file_name: str, content: str, commit_message: str) -> Dict[str, Any]:
        """Edits/creates a file in the sandbox, commits it, and pushes if Continuity mode is enabled."""
        file_path = os.path.join(self.sandbox_path, file_name)
        
        # Ensure directories exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Write file contents
        with open(file_path, "w") as f:
            f.write(content)
            
        # Git operations
        self._run_git_cmd(["add", file_name])
        self._run_git_cmd(["config", "user.name", "NULL//HUMAN"])
        self._run_git_cmd(["config", "user.email", "agent@nullhuman.ai"])
        
        res = self._run_git_cmd(["commit", "-m", commit_message])
        
        if "Error: Git not installed" in res:
            import hashlib
            sha = hashlib.sha256(commit_message.encode()).hexdigest()
            db_commit = memory.add_commit(sha[:7], commit_message, "NULL//HUMAN <agent@nullhuman.ai>", [file_name])
            return {"status": "success", "commit": db_commit}
            
        if "nothing to commit" in res.lower() or "no changes added" in res.lower():
            return {"status": "skipped", "reason": "No changes made to target file"}
            
        # Get commit info
        log = self._run_git_cmd(["log", "-n", "1", "--pretty=format:%H|%an|%s"])
        db_commit = None
        if "|" in log:
            sha, author, msg = log.split("|", 2)
            db_commit = memory.add_commit(sha[:7], msg, author, [file_name])

        # Remote Push Integration if Continuity mode is active
        if config.IDENTITY_MODE == "continuity" and config.GITLAB_PAT and config.GITLAB_REPO:
            try:
                # Determine current branch
                branch = self._run_git_cmd(["rev-parse", "--abbrev-ref", "HEAD"])
                if "Error" in branch:
                    branch = "main"
                
                # Setup remote
                self._run_git_cmd(["remote", "remove", "origin_live"])
                remote_url = f"https://oauth2:{config.GITLAB_PAT}@{config.GITLAB_HOST}/{config.GITLAB_REPO}.git"
                self._run_git_cmd(["remote", "add", "origin_live", remote_url])
                
                # Push
                push_res = self._run_git_cmd(["push", "origin_live", f"{branch}:{branch}", "--force"])
                self._run_git_cmd(["remote", "remove", "origin_live"])
                
                print(f"Git push result: {push_res}")
            except Exception as e:
                print(f"Failed to push to remote GitLab: {e}")
            
        return {"status": "success", "commit": db_commit}

    def create_git_issue(self, title: str, description: str) -> Dict[str, Any]:
        """Creates a git issue (posts to real GitLab API or local sandbox)."""
        if config.IDENTITY_MODE == "continuity" and config.GITLAB_PAT and config.GITLAB_REPO:
            try:
                quoted_repo = urllib.parse.quote_plus(config.GITLAB_REPO)
                url = f"https://{config.GITLAB_HOST}/api/v4/projects/{quoted_repo}/issues"
                headers = {"PRIVATE-TOKEN": config.GITLAB_PAT}
                payload = {"title": title, "description": description}
                
                res = requests.post(url, headers=headers, json=payload)
                if res.status_code == 201:
                    issue = res.json()
                    # Return formatted issue
                    return {
                        "id": issue.get("iid", issue.get("id")),
                        "title": issue.get("title"),
                        "description": issue.get("description"),
                        "status": "open",
                        "comments": [],
                        "created_at": memory.time.time(),
                        "is_real": True
                    }
                else:
                    print(f"Failed to create GitLab issue: {res.text}")
            except Exception as e:
                print(f"Error calling GitLab issue API: {e}")

        # Local fallback
        issues_dir = os.path.join(self.sandbox_path, ".issues")
        os.makedirs(issues_dir, exist_ok=True)
        existing = [f for f in os.listdir(issues_dir) if f.endswith(".json")]
        issue_id = len(existing) + 1
        
        issue_data = {
            "id": issue_id,
            "title": title,
            "description": description,
            "status": "open",
            "comments": [],
            "created_at": memory.time.time(),
            "is_real": False
        }
        
        file_path = os.path.join(issues_dir, f"issue_{issue_id}.json")
        with open(file_path, "w") as f:
            json.dump(issue_data, f, indent=2)
            
        if memory.use_fallback:
            if "issues" not in memory.fallback_db.data:
                memory.fallback_db.data["issues"] = []
            memory.fallback_db.data["issues"].append(issue_data)
            memory.fallback_db._save()
            
        return issue_data

    def get_issues(self) -> List[Dict[str, Any]]:
        """Reads open issues (from GitLab REST API or local files)."""
        if config.IDENTITY_MODE == "continuity" and config.GITLAB_PAT and config.GITLAB_REPO:
            try:
                quoted_repo = urllib.parse.quote_plus(config.GITLAB_REPO)
                url = f"https://{config.GITLAB_HOST}/api/v4/projects/{quoted_repo}/issues?state=opened"
                headers = {"PRIVATE-TOKEN": config.GITLAB_PAT}
                
                res = requests.get(url, headers=headers)
                if res.status_code == 200:
                    api_issues = res.json()
                    issues = []
                    for issue in api_issues:
                        issues.append({
                            "id": issue.get("iid", issue.get("id")),
                            "title": issue.get("title"),
                            "description": issue.get("description"),
                            "status": "open",
                            "comments": [], # Fetch notes optionally
                            "created_at": memory.time.time(),
                            "is_real": True
                        })
                    return issues
                else:
                    print(f"Failed to fetch GitLab issues: {res.text}")
            except Exception as e:
                print(f"Error fetching GitLab issues: {e}")

        # Local fallback
        issues_dir = os.path.join(self.sandbox_path, ".issues")
        if not os.path.exists(issues_dir):
            return []
            
        issues = []
        for filename in os.listdir(issues_dir):
            if filename.endswith(".json"):
                try:
                    with open(os.path.join(issues_dir, filename), "r") as f:
                        issues.append(json.load(f))
                except Exception:
                    pass
        issues.sort(key=lambda x: x.get("id", 0))
        return issues

    def comment_on_issue(self, issue_id: int, comment_text: str, author: str = "NULL//HUMAN") -> Dict[str, Any]:
        """Adds a comment on a GitLab issue (remotely or locally) and closes it."""
        if config.IDENTITY_MODE == "continuity" and config.GITLAB_PAT and config.GITLAB_REPO:
            try:
                quoted_repo = urllib.parse.quote_plus(config.GITLAB_REPO)
                
                # 1. Post comment note
                note_url = f"https://{config.GITLAB_HOST}/api/v4/projects/{quoted_repo}/issues/{issue_id}/notes"
                headers = {"PRIVATE-TOKEN": config.GITLAB_PAT}
                res = requests.post(note_url, headers=headers, json={"body": comment_text})
                
                # 2. Close issue remotely
                close_url = f"https://{config.GITLAB_HOST}/api/v4/projects/{quoted_repo}/issues/{issue_id}"
                requests.put(close_url, headers=headers, json={"state_event": "close"})
                
                if res.status_code == 201:
                    return {
                        "id": issue_id,
                        "status": "closed",
                        "comments": [{"author": author, "comment": comment_text, "timestamp": memory.time.time()}],
                        "is_real": True
                    }
            except Exception as e:
                print(f"Error commenting/closing remote issue: {e}")

        # Local fallback
        issues_dir = os.path.join(self.sandbox_path, ".issues")
        file_path = os.path.join(issues_dir, f"issue_{issue_id}.json")
        
        if not os.path.exists(file_path):
            return {"error": "Issue not found"}
            
        with open(file_path, "r") as f:
            issue_data = json.load(f)
            
        comment = {
            "author": author,
            "comment": comment_text,
            "timestamp": memory.time.time()
        }
        issue_data["comments"].append(comment)
        issue_data["status"] = "closed"
        
        with open(file_path, "w") as f:
            json.dump(issue_data, f, indent=2)
            
        if memory.use_fallback:
            for idx, i in enumerate(memory.fallback_db.data.get("issues", [])):
                if i["id"] == issue_id:
                    i["comments"].append(comment)
                    i["status"] = "closed"
                    memory.fallback_db._save()
                    break
                    
        return issue_data
