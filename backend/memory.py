import json
import os
import time
from typing import List, Dict, Any, Optional
from backend import config

class JSONFallbackDB:
    """A simple JSON-based database for fallback storage if MongoDB is not available."""
    def __init__(self, filepath: str = None):
        if filepath is None:
            default_path = os.getenv("DATABASE_FALLBACK_PATH", os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "db_fallback.json"
            ))
            dir_name = os.path.dirname(default_path)
            try:
                if not os.path.exists(dir_name):
                    os.makedirs(dir_name, exist_ok=True)
            except Exception:
                pass

            is_writable = False
            if os.path.exists(dir_name) and os.access(dir_name, os.W_OK):
                try:
                    test_file = os.path.join(dir_name, ".db_write_test")
                    with open(test_file, "w") as f:
                        f.write("test")
                    os.remove(test_file)
                    is_writable = True
                except Exception:
                    is_writable = False

            if not is_writable:
                import tempfile
                self.filepath = os.path.join(tempfile.gettempdir(), "db_fallback.json")
                print(f"Fallback DB directory {dir_name} not writable. Using temp directory: {self.filepath}")
            else:
                self.filepath = default_path
        else:
            self.filepath = filepath

        # Ensure fallback file exists and has correct structure
        if not os.path.exists(self.filepath):
            self.data = {
                "logs": [],
                "commits": [],
                "simulations": {
                    "slack": [],
                    "email": [],
                    "linkedin": [],
                    "chat": []
                },
                "personality": {
                    "sliders": {
                        "empathy": 60,
                        "urgency": 40,
                        "formality": 80,
                        "sarcasm": 20,
                        "typos": 20
                    },
                    "description": "Professional software engineer clone. Diligent, focused, and polite."
                },
                "agents": [
                    {"id": "main", "name": "Main Agent", "role": "Represents the user's primary identity", "status": "idle", "last_active": time.time()}
                ],
                "issues": [],
                "settings": {
                    "doppelganger_active": False
                }
            }
            self._save()
        else:
            try:
                with open(self.filepath, "r") as f:
                    self.data = json.load(f)
                # Ensure all simulation collections exist
                if "simulations" not in self.data:
                    self.data["simulations"] = {}
                for k in ["slack", "email", "linkedin", "chat"]:
                    if k not in self.data["simulations"]:
                        self.data["simulations"][k] = []
                # Ensure personality sliders exist
                if "personality" not in self.data:
                    self.data["personality"] = {}
                if "sliders" not in self.data["personality"]:
                    self.data["personality"]["sliders"] = {}
                for k, v in [("empathy", 60), ("urgency", 40), ("formality", 80), ("sarcasm", 20), ("typos", 20)]:
                    if k not in self.data["personality"]["sliders"]:
                        self.data["personality"]["sliders"][k] = v
                # Ensure settings exist
                if "settings" not in self.data:
                    self.data["settings"] = {"doppelganger_active": False}
                elif "doppelganger_active" not in self.data["settings"]:
                    self.data["settings"]["doppelganger_active"] = False
                self._save()
            except Exception:
                self.data = {
                    "logs": [],
                    "commits": [],
                    "simulations": {"slack": [], "email": [], "linkedin": [], "chat": []},
                    "personality": {
                        "sliders": {"empathy": 60, "urgency": 40, "formality": 80, "sarcasm": 20, "typos": 20},
                        "description": "Professional software engineer clone. Diligent, focused, and polite."
                    },
                    "agents": [
                        {"id": "main", "name": "Main Agent", "role": "Represents the user's primary identity", "status": "idle", "last_active": time.time()}
                    ],
                    "issues": [],
                    "settings": {"doppelganger_active": False}
                }
                self._save()

    def _save(self):
        try:
            with open(self.filepath, "w") as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            print(f"Error saving JSON DB: {e}")

    def insert_one(self, collection: str, document: Dict[str, Any]) -> Dict[str, Any]:
        if collection not in self.data:
            self.data[collection] = []
        if "_id" not in document:
            document["_id"] = str(time.time_ns())
        if "created_at" not in document:
            document["created_at"] = time.time()
        self.data[collection].append(document)
        self._save()
        return document

    def find(self, collection: str, query: Dict[str, Any] = None, limit: int = 100) -> List[Dict[str, Any]]:
        # Flattened fetch
        items = self.data.get(collection, [])
        if collection == "simulations":
            # Simulations might be nested
            return [items]
        # Return reversed items for logs to show newest first, or preserve order
        # Let's filter slightly (only direct equivalence for simple query)
        filtered = []
        for item in items:
            match = True
            if query:
                for k, v in query.items():
                    if item.get(k) != v:
                        match = False
                        break
            if match:
                filtered.append(item)
        # Sort by created_at desc if available
        filtered.sort(key=lambda x: x.get("created_at", 0), reverse=True)
        return filtered[:limit]

    def update_one(self, collection: str, query: Dict[str, Any], update: Dict[str, Any]) -> bool:
        items = self.data.get(collection, [])
        if collection == "personality":
            # personality is a dict, not list in our structure
            if "sliders" in update:
                self.data["personality"]["sliders"].update(update["sliders"])
            if "description" in update:
                self.data["personality"]["description"] = update["description"]
            self._save()
            return True
            
        for item in items:
            match = True
            for k, v in query.items():
                if item.get(k) != v:
                    match = False
                    break
            if match:
                item.update(update)
                self._save()
                return True
        return False

    def delete_many(self, collection: str, query: Dict[str, Any] = None):
        if collection in self.data:
            if not query:
                self.data[collection] = []
            else:
                self.data[collection] = [
                    item for item in self.data[collection]
                    if not all(item.get(k) == v for k, v in query.items())
                ]
            self._save()

# Instantiate Database Manager
db_client = None
db = None
use_fallback = True

if config.MONGODB_URI:
    try:
        from pymongo import MongoClient
        db_client = MongoClient(config.MONGODB_URI, serverSelectionTimeoutMS=2000)
        # Trigger connection check
        db_client.server_info()
        db = db_client[config.DB_NAME]
        use_fallback = False
        print("Connected to MongoDB successfully!")
    except Exception as e:
        print(f"MongoDB connection failed: {e}. Falling back to local JSON database.")
        use_fallback = True
else:
    print("No MongoDB URI configured. Using local JSON database fallback.")
    use_fallback = True

fallback_db = JSONFallbackDB()

def add_log(agent_id: str, message: str, step_type: str = "thought", critique: str = None) -> Dict[str, Any]:
    log_entry = {
        "agent_id": agent_id,
        "message": message,
        "step_type": step_type, # thought, action, critique, system
        "critique": critique,
        "timestamp": time.time(),
        "created_at": time.time()
    }
    if use_fallback:
        return fallback_db.insert_one("logs", log_entry)
    else:
        log_entry["_id"] = str(time.time_ns())
        db.logs.insert_one(log_entry)
        return log_entry

def get_logs(limit: int = 50) -> List[Dict[str, Any]]:
    if use_fallback:
        return fallback_db.find("logs", limit=limit)
    else:
        cursor = db.logs.find().sort("timestamp", -1).limit(limit)
        return [dict(doc, _id=str(doc["_id"])) for doc in cursor]

def add_commit(sha: str, message: str, author: str, files_changed: List[str]) -> Dict[str, Any]:
    commit_entry = {
        "sha": sha,
        "message": message,
        "author": author,
        "files_changed": files_changed,
        "timestamp": time.time(),
        "created_at": time.time()
    }
    if use_fallback:
        return fallback_db.insert_one("commits", commit_entry)
    else:
        commit_entry["_id"] = str(time.time_ns())
        db.commits.insert_one(commit_entry)
        return commit_entry

def get_commits(limit: int = 20) -> List[Dict[str, Any]]:
    if use_fallback:
        return fallback_db.find("commits", limit=limit)
    else:
        cursor = db.commits.find().sort("timestamp", -1).limit(limit)
        return [dict(doc, _id=str(doc["_id"])) for doc in cursor]

def get_personality() -> Dict[str, Any]:
    if use_fallback:
        return fallback_db.data["personality"]
    else:
        doc = db.personality.find_one()
        if not doc:
            # Insert default
            default_p = {
                "sliders": {"empathy": 60, "urgency": 40, "formality": 80, "sarcasm": 20, "typos": 20},
                "description": "Professional software engineer clone. Diligent, focused, and polite."
            }
            db.personality.insert_one(default_p)
            return default_p
        return dict(doc, _id=str(doc["_id"]))

def update_personality(sliders: Dict[str, int], description: str = None) -> bool:
    if use_fallback:
        update_data = {"sliders": sliders}
        if description:
            update_data["description"] = description
        return fallback_db.update_one("personality", {}, update_data)
    else:
        update_data = {"sliders": sliders}
        if description:
            update_data["description"] = description
        res = db.personality.update_one({}, {"$set": update_data}, upsert=True)
        return res.modified_count > 0 or res.upserted_id is not None

def get_agents() -> List[Dict[str, Any]]:
    if use_fallback:
        return fallback_db.data["agents"]
    else:
        cursor = db.agents.find()
        return [dict(doc, _id=str(doc["_id"])) for doc in cursor]

def update_agent_status(agent_id: str, status: str) -> bool:
    if use_fallback:
        for a in fallback_db.data["agents"]:
            if a["id"] == agent_id:
                a["status"] = status
                a["last_active"] = time.time()
                fallback_db._save()
                return True
        # If not found, add it
        new_agent = {
            "id": agent_id,
            "name": f"{agent_id.capitalize()} Agent",
            "role": f"Subagent for {agent_id} tasks",
            "status": status,
            "last_active": time.time()
        }
        fallback_db.data["agents"].append(new_agent)
        fallback_db._save()
        return True
    else:
        res = db.agents.update_one(
            {"id": agent_id},
            {"$set": {"status": status, "last_active": time.time()}},
            upsert=True
        )
        return True

def get_simulations(channel: str) -> List[Dict[str, Any]]:
    if use_fallback:
        return fallback_db.data["simulations"].get(channel, [])
    else:
        # Get simulated messages for a specific channel (slack, email, linkedin)
        doc = db.simulations.find_one({"channel": channel})
        return doc.get("messages", []) if doc else []

def add_simulated_message(channel: str, message: Dict[str, Any]) -> bool:
    if "timestamp" not in message:
        message["timestamp"] = time.time()
    if use_fallback:
        fallback_db.data["simulations"][channel].append(message)
        # Keep last 50
        fallback_db.data["simulations"][channel] = fallback_db.data["simulations"][channel][-50:]
        fallback_db._save()
        return True
    else:
        db.simulations.update_one(
            {"channel": channel},
            {"$push": {"messages": {"$each": [message], "$slice": -50}}},
            upsert=True
        )
        return True

def clear_db():
    if use_fallback:
        fallback_db.delete_many("logs")
        fallback_db.delete_many("commits")
        fallback_db.data["simulations"] = {"slack": [], "email": [], "linkedin": [], "chat": []}
        fallback_db.data["agents"] = [
            {"id": "main", "name": "Main Agent", "role": "Represents the user's primary identity", "status": "idle", "last_active": time.time()}
        ]
        fallback_db.data["issues"] = []
        if "settings" not in fallback_db.data:
            fallback_db.data["settings"] = {}
        fallback_db.data["settings"]["doppelganger_active"] = False
        fallback_db._save()
    else:
        db.logs.delete_many({})
        db.commits.delete_many({})
        db.simulations.delete_many({})
        db.agents.delete_many({})
        db.agents.insert_one({"id": "main", "name": "Main Agent", "role": "Represents the user's primary identity", "status": "idle", "last_active": time.time()})
        db.settings.update_one(
            {"key": "doppelganger_active"},
            {"$set": {"value": False}},
            upsert=True
        )
    
    global detection_risk, behavior_adaptation
    detection_risk = 12
    behavior_adaptation = False

# Global Risk State
detection_risk = 12
behavior_adaptation = False

def get_detection_state():
    return {
        "detection_risk": detection_risk,
        "behavior_adaptation": behavior_adaptation
    }

def set_detection_state(risk: int = None, adaptation: bool = None):
    global detection_risk, behavior_adaptation
    if risk is not None:
        # Clamp between 0 and 100
        detection_risk = max(0, min(100, risk))
    if adaptation is not None:
        behavior_adaptation = adaptation

def get_doppelganger_active() -> bool:
    if use_fallback:
        if "settings" not in fallback_db.data:
            fallback_db.data["settings"] = {"doppelganger_active": False}
            fallback_db._save()
        return fallback_db.data["settings"].get("doppelganger_active", False)
    else:
        try:
            doc = db.settings.find_one({"key": "doppelganger_active"})
            if not doc:
                db.settings.insert_one({"key": "doppelganger_active", "value": False})
                return False
            return doc.get("value", False)
        except Exception:
            return False

def set_doppelganger_active(active: bool):
    if use_fallback:
        if "settings" not in fallback_db.data:
            fallback_db.data["settings"] = {}
        fallback_db.data["settings"]["doppelganger_active"] = active
        fallback_db._save()
    else:
        try:
            db.settings.update_one(
                {"key": "doppelganger_active"},
                {"$set": {"value": active}},
                upsert=True
            )
        except Exception as e:
            print(f"Error updating doppelganger active in MongoDB settings: {e}")

