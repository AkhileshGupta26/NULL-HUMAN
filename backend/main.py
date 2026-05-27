import os
import shutil
import threading
import time
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional

from backend import config
from backend import memory
from backend import simulations
from backend import orchestrator

app = FastAPI(title="NULL//HUMAN API", version="1.0.0")

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for state
background_thread = None
background_thread_lock = threading.Lock()
orchestrator_engine = None

class PersonalityUpdate(BaseModel):
    sliders: Dict[str, int]
    description: Optional[str] = None

class IdentityUpdate(BaseModel):
    identity_mode: str
    gitlab_pat: Optional[str] = ""
    gitlab_username: Optional[str] = ""
    gitlab_repo: Optional[str] = ""
    gitlab_host: Optional[str] = "gitlab.com"
    gemini_api_key: Optional[str] = ""

class IssueCreate(BaseModel):
    title: str
    description: str

class ChatInput(BaseModel):
    message: str

def ensure_background_loop():
    global background_thread
    if memory.get_doppelganger_active():
        with background_thread_lock:
            if background_thread is None or not background_thread.is_alive():
                print("Restoring background autonomous loop from persisted database state...")
                background_thread = threading.Thread(target=autonomous_loop, daemon=True)
                background_thread.start()

@app.on_event("startup")
def startup_event():
    global orchestrator_engine
    # Initialize components
    orchestrator_engine = orchestrator.DoppelgangerOrchestrator()
    simulations.seed_initial_data()
    ensure_background_loop()
    print("NULL//HUMAN Backend started.")

def autonomous_loop():
    """Background loop that runs when Doppelgänger mode is active."""
    global orchestrator_engine
    while memory.get_doppelganger_active():
        try:
            print("Autonomous tick cycle running...")
            orchestrator_engine.run_one_cycle()
        except Exception as e:
            print(f"Error in autonomous background cycle: {e}")
        time.sleep(config.RUN_INTERVAL_SECONDS)

@app.get("/api/status")
def get_status():
    ensure_background_loop()
    return {
        "status": "online",
        "doppelganger_active": memory.get_doppelganger_active(),
        "run_interval": config.RUN_INTERVAL_SECONDS
    }

@app.post("/api/activate")
def activate_doppelganger(background_tasks: BackgroundTasks):
    global background_thread
    if memory.get_doppelganger_active():
        ensure_background_loop()
        return {"status": "already_active", "message": "Doppelgänger mode is already active."}
        
    memory.set_doppelganger_active(True)
    memory.add_log("main", "Doppelgänger Mode ACTIVATED. Commencing offline hand-off.", "system")
    
    with background_thread_lock:
        if background_thread is None or not background_thread.is_alive():
            background_thread = threading.Thread(target=autonomous_loop, daemon=True)
            background_thread.start()
    
    return {"status": "activated", "message": "Autonomous Doppelgänger loop started."}

@app.post("/api/deactivate")
def deactivate_doppelganger():
    if not memory.get_doppelganger_active():
        return {"status": "already_inactive", "message": "Doppelgänger mode is already inactive."}
        
    memory.set_doppelganger_active(False)
    memory.add_log("main", "Doppelgänger Mode DEACTIVATED. Returning control to human.", "system")
    return {"status": "deactivated", "message": "Autonomous Doppelgänger loop stopped."}

@app.post("/api/tick")
def trigger_tick():
    """Runs exactly one cycle of the agent loop synchronously."""
    global orchestrator_engine
    if not orchestrator_engine:
        raise HTTPException(status_code=500, detail="Orchestrator engine not initialized")
    res = orchestrator_engine.run_one_cycle()
    return res

@app.get("/api/dashboard")
def get_dashboard_data():
    """Fetches all metrics, feeds, logs, and agent states for the UI."""
    global orchestrator_engine
    if not orchestrator_engine:
        raise HTTPException(status_code=500, detail="Engine not ready")
        
    ensure_background_loop()
    return {
        "doppelganger_active": memory.get_doppelganger_active(),
        "personality": memory.get_personality(),
        "agents": memory.get_agents(),
        "logs": memory.get_logs(limit=40),
        "commits": orchestrator_engine.git_sandbox.get_commit_history(),
        "issues": orchestrator_engine.git_sandbox.get_issues(),
        "feeds": simulations.get_all_simulated_data(),
        "detection_state": memory.get_detection_state()
    }

@app.get("/api/identity")
def get_identity():
    return {
        "identity_mode": config.IDENTITY_MODE,
        "gitlab_pat": config.GITLAB_PAT,
        "gitlab_username": config.GITLAB_USERNAME,
        "gitlab_repo": config.GITLAB_REPO,
        "gitlab_host": config.GITLAB_HOST,
        "gemini_api_key": config.GEMINI_API_KEY
    }

@app.post("/api/identity")
def update_identity(data: IdentityUpdate):
    global orchestrator_engine
    success = config.save_identity_credentials(data.dict())
    if success:
        # Re-initialize Gemini if API Key changed
        if data.gemini_api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=data.gemini_api_key)
                orchestrator.gemini_available = True
                print("Gemini API re-configured successfully via Identity Control Center!")
            except Exception as e:
                print(f"Failed to configure Gemini API: {e}")
                orchestrator.gemini_available = False
        else:
            orchestrator.gemini_available = False
        
        memory.add_log("main", f"Identity Control Center settings updated: Mode={data.identity_mode}", "system")
        return {"status": "success", "message": "Identity configurations updated successfully."}
    raise HTTPException(status_code=500, detail="Failed to save identity credentials")

@app.post("/api/personality")
def save_personality(data: PersonalityUpdate):
    success = memory.update_personality(data.sliders, data.description)
    if success:
        memory.add_log("main", f"System profile updated: sliders={data.sliders}", "system")
        return {"status": "success", "personality": memory.get_personality()}
    raise HTTPException(status_code=500, detail="Failed to update personality")

@app.post("/api/issue")
def create_issue(issue: IssueCreate):
    global orchestrator_engine
    if not orchestrator_engine:
        raise HTTPException(status_code=500, detail="Engine not ready")
    new_issue = orchestrator_engine.git_sandbox.create_git_issue(issue.title, issue.description)
    memory.add_log("main", f"New workspace issue submitted: '{issue.title}'", "system")
    return {"status": "success", "issue": new_issue}

@app.post("/api/chat")
def handle_chat_message(chat: ChatInput):
    global orchestrator_engine
    if not orchestrator_engine:
        raise HTTPException(status_code=500, detail="Engine not ready")
        
    user_msg = {
        "sender": "Human (Owner)",
        "message": chat.message,
        "timestamp": time.time(),
        "is_agent": False
    }
    memory.add_simulated_message("chat", user_msg)
    
    reply = orchestrator_engine.handle_direct_chat(chat.message)
    return {"status": "success", "reply": reply}

@app.post("/api/reset")
def reset_demo():
    global orchestrator_engine
    # Deactivate loop if active
    memory.set_doppelganger_active(False)
    time.sleep(0.5) # allow loop to exit
    
    # Clear databases
    memory.clear_db()
    
    # Reinit git sandbox
    if os.path.exists(config.SANDBOX_PATH):
        try:
            shutil.rmtree(config.SANDBOX_PATH)
        except Exception as e:
            print(f"Error removing sandbox folder: {e}")
            
    orchestrator_engine = orchestrator.DoppelgangerOrchestrator()
    simulations.seed_initial_data()
    
    return {"status": "success", "message": "Demo database and git repository reset complete."}

if __name__ == "__main__":
    import uvicorn
    # Dynamically select import path based on running directory
    app_import = "main:app"
    try:
        if os.path.exists("backend") and os.path.isdir("backend"):
            app_import = "backend.main:app"
    except Exception:
        pass
    uvicorn.run(app_import, host=config.HOST, port=config.PORT, reload=True)
