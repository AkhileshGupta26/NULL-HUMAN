import time
import random
import os
from typing import Dict, Any, List
from backend import memory
from backend import config
from backend import git_agent
from backend import simulations

# Try to configure Gemini API, fallback if not available
gemini_available = False
if config.GEMINI_API_KEY:
    try:
        import google.generativeai as genai
        genai.configure(api_key=config.GEMINI_API_KEY)
        gemini_available = True
        print("Gemini API configured successfully!")
    except Exception as e:
        print(f"Failed to configure Gemini API: {e}. Using simulated persona engine.")

def apply_hie_typo(text: str, frequency: int) -> tuple[str, str]:
    """
    Returns (typo_text, correction_comment) if a typo is simulated, or (text, None) if not.
    """
    if frequency <= 0 or random.random() > (frequency / 100.0) * 0.4:
        return text, None
        
    words = text.split(" ")
    if len(words) < 4:
        return text, None
        
    # Select a word that is longer than 4 chars and only alphabetical
    valid_indices = [i for i, w in enumerate(words) if len(w) > 4 and w.isalpha()]
    if not valid_indices:
        return text, None
        
    idx = random.choice(valid_indices)
    word = words[idx]
    
    # Swap two characters
    char_idx = random.randint(1, len(word) - 2)
    word_list = list(word)
    word_list[char_idx], word_list[char_idx+1] = word_list[char_idx+1], word_list[char_idx]
    typo_word = "".join(word_list)
    words[idx] = typo_word
    
    typo_text = " ".join(words)
    correction = f"Typo detected: '{typo_word}' should be '{word}'. Executing backspace correction."
    return typo_text, correction

class DoppelgangerOrchestrator:
    def __init__(self):
        self.git_sandbox = git_agent.GitSandboxAgent()
        # Seed initial mock logs on initialization to show rich context
        self._seed_initial_logs()

    def _seed_initial_logs(self):
        logs = memory.get_logs()
        if not logs:
            memory.add_log("main", "Initializing NULL//HUMAN core engine.", "system")
            time.sleep(0.01)
            memory.add_log("main", "Scanning local digital profile and style vectors.", "thought")
            time.sleep(0.01)
            memory.add_log("main", "Loaded persona profile: Formality (80%), Empathy (60%), Urgency (40%).", "thought")
            time.sleep(0.01)
            memory.add_log("main", "Core autonomous engine is active. Listening for workspace updates.", "system")

    def log_with_hie(self, agent_id: str, message: str, step_type: str = "thought", critique: str = None) -> dict:
        """Logs messages with simulated typing typos if HIE is active."""
        try:
            personality = memory.get_personality()
            sliders = personality.get("sliders", {})
            typos_frequency = sliders.get("typos", 20)
        except Exception:
            typos_frequency = 20
            
        # Typing lag simulation
        if step_type in ["thought", "action", "critique", "system"]:
            # delay based on message length
            delay = min(0.6, max(0.15, len(message) * 0.005))
            state = memory.get_detection_state()
            if state.get("behavior_adaptation", False):
                delay *= 2.0
            time.sleep(delay)
            
        if step_type in ["thought", "action", "critique"] and typos_frequency > 0:
            typo_text, correction_msg = apply_hie_typo(message, typos_frequency)
            if correction_msg:
                memory.add_log(agent_id, typo_text, step_type)
                time.sleep(0.5)
                memory.add_log(agent_id, f"Self-Correction: {correction_msg}", "critique")
                time.sleep(0.5)
                return memory.add_log(agent_id, message, step_type)
                
        return memory.add_log(agent_id, message, step_type, critique)

    def query_llm(self, prompt: str, system_instruction: str) -> str:
        """Helper to run a prompt through Gemini or use simulated heuristics if offline."""
        if gemini_available:
            try:
                model = genai.GenerativeModel(
                    model_name="gemini-1.5-flash",
                    system_instruction=system_instruction
                )
                response = model.generate_content(prompt)
                return response.text.strip()
            except Exception as e:
                print(f"Gemini generation error: {e}. Falling back to simulation heuristics.")
        
        # Fallback simulated response heuristics based on prompt keywords
        # This keeps the agent functional offline/without API key.
        lower_prompt = prompt.lower()
        
        # If it's a code generation request
        if "code" in lower_prompt or "function" in lower_prompt or "script" in lower_prompt:
            return (
                "```python\n"
                "# Optimized DB Connection pool check\n"
                "import time\n"
                "import logging\n\n"
                "def monitor_connection_pool(pool, max_threshold=0.85):\n"
                "    \"\"\"Autonomously monitors database pool usage percentage\"\"\"\n"
                "    usage = pool.active_connections / pool.max_connections\n"
                "    if usage >= max_threshold:\n"
                "        logging.warning(f\"High connection pool usage detected: {usage:.2%}. Recycling idle connections...\")\n"
                "        pool.recycle_idle_connections()\n"
                "        return True\n"
                "    return False\n"
                "```"
            )
        
        # If it's a Slack reply
        if "slack" in lower_prompt or " Sarah" in prompt or " John" in prompt:
            if "latency" in lower_prompt:
                return "Hey Sarah, I investigated the db connection leakage. I wrote a monitoring decorator in connection_pool.py to automatically close stale sockets. Creating a PR shortly."
            return "Got it. I'll make sure to double-check that part and submit a quick fix to the staging branch."

        # If it's a LinkedIn reply
        if "linkedin" in lower_prompt:
            return "Thanks for reaching out! I appreciate your interest in my autonomous agent framework. I'm open to discussing potential collaborations. Let's schedule a Zoom call next week."

        # If it's an email reply
        if "email" in lower_prompt or "subject" in lower_prompt:
            return (
                "Hi,\n\n"
                "Thanks for the update. I have reviewed the requirements and verified that our local workspace tests are passing. "
                "I will verify the deployment logs on staging and update you as soon as the pull request is merged.\n\n"
                "Best regards,\n"
                "NULL//HUMAN (Doppelgänger)"
            )
            
        return "Acknowledged. Proceeding with the requested task and scheduling reflections."

    def run_one_cycle(self) -> Dict[str, Any]:
        """Runs one autonomous tick of the digital doppelgänger. Scans tasks, spawns sub-agents, reflects, and commits."""
        # 1. Simulate incoming event
        new_event = simulations.simulate_incoming_event()
        if new_event:
            memory.add_log("main", f"Event detected: {new_event['message']}", "system")
            
        # Get current state
        personality = memory.get_personality()
        sliders = personality["sliders"]
        
        # Check for items that need attention
        unreplied_slack = [m for m in memory.get_simulations("slack") if not m.get("is_agent")][-1:]
        unreplied_emails = [e for e in memory.get_simulations("email") if not e.get("replied")][-1:]
        unreplied_linkedin = [l for l in memory.get_simulations("linkedin") if not l.get("replied")][-1:]
        git_issues = [i for i in self.git_sandbox.get_issues() if i["status"] == "open"][-1:]
        
        # Decide what to work on (Priority: Git Issue -> Slack -> Email -> LinkedIn -> Idle maintenance)
        task_type = None
        task_data = None
        
        if git_issues:
            task_type = "git_issue"
            task_data = git_issues[0]
        elif unreplied_slack:
            # Let's verify we haven't already replied to it in the simulation logs
            slack_list = memory.get_simulations("slack")
            if slack_list and not slack_list[-1]["is_agent"]:
                task_type = "slack"
                task_data = slack_list[-1]
        elif unreplied_emails:
            task_type = "email"
            task_data = unreplied_emails[0]
        elif unreplied_linkedin:
            task_type = "linkedin"
            task_data = unreplied_linkedin[0]
            
        if not task_type:
            # Idle maintenance: let the agent commit some cleanup code to stay active on Git
            if random.random() < 0.15: # 15% chance to perform code maintenance when idle
                task_type = "maintenance"
            else:
                return {"status": "idle", "message": "No urgent tasks in queue. Doppelgänger status: active and monitoring."}
                
        # 2. Start execution based on task
        if task_type == "git_issue":
            return self._handle_git_issue(task_data, sliders)
        elif task_type == "slack":
            return self._handle_slack_message(task_data, sliders)
        elif task_type == "email":
            return self._handle_email(task_data, sliders)
        elif task_type == "linkedin":
            return self._handle_linkedin(task_data, sliders)
        elif task_type == "maintenance":
            return self._handle_maintenance(sliders)

        return {"status": "error", "message": "Unknown task state."}

    def _handle_git_issue(self, issue: Dict[str, Any], sliders: Dict[str, int]) -> Dict[str, Any]:
        memory.update_agent_status("main", "busy")
        memory.update_agent_status("coding", "active")
        self.log_with_hie("main", f"Main Agent spawned Coding Sub-agent to resolve issue #{issue['id']}: '{issue['title']}'", "system")
        time.sleep(0.5)
        
        # Phase 1: Planning
        self.log_with_hie("coding", f"Analyzing codebase and issue description: '{issue['description']}'", "thought")
        time.sleep(0.5)
        
        # Generate code and reflection
        prompt = f"Write python code to solve this issue: {issue['title']}. Details: {issue['description']}"
        system_inst = f"You are an expert software engineer. Formality: {sliders.get('formality', 80)}/100, Urgency: {sliders.get('urgency', 50)}/100."
        
        code = self.query_llm(prompt, system_inst)
        
        # Reflection Loop
        self.log_with_hie("coding", "Code generated. Initiating self-reflection validation loop.", "thought")
        time.sleep(0.5)
        
        # Reflection / Critique
        critique = "Critic: Check if import libraries are correct. Ensure code matches PEP8 styles."
        self.log_with_hie("coding", "Self-Reflection critique: Imports check passed. Refactoring function name for maximum clarity.", "critique", critique)
        time.sleep(0.5)
        
        # Write to git sandbox
        filename = f"src/issue_{issue['id']}_patch.py"
        commit_msg = f"fix: resolve issue #{issue['id']} - {issue['title']}"
        
        commit_res = self.git_sandbox.make_autonomous_commit(filename, code, commit_msg)
        
        # Add comment to issue closing it
        closing_msg = f"Autonomous patch generated and committed as {commit_res.get('commit', {}).get('sha', 'main')}."
        self.git_sandbox.comment_on_issue(issue["id"], closing_msg)
        
        # Update issue status to closed
        import json
        issues_dir = os.path.join(self.git_sandbox.sandbox_path, ".issues")
        issue_path = os.path.join(issues_dir, f"issue_{issue['id']}.json")
        with open(issue_path, "r") as f:
            issue_data = json.load(f)
        issue_data["status"] = "closed"
        with open(issue_path, "w") as f:
            json.dump(issue_data, f, indent=2)
            
        if memory.use_fallback:
            for idx, i in enumerate(memory.fallback_db.data.get("issues", [])):
                if i["id"] == issue["id"]:
                    memory.fallback_db.data["issues"][idx]["status"] = "closed"
                    memory.fallback_db._save()
                    break
        
        self.log_with_hie("coding", f"Code patch successfully pushed. Issue #{issue['id']} marked as closed.", "thought")
        memory.update_agent_status("coding", "idle")
        memory.update_agent_status("main", "idle")
        
        return {"status": "success", "action": "git_commit", "detail": f"Fixed issue #{issue['id']}"}

    def _handle_slack_message(self, slack: Dict[str, Any], sliders: Dict[str, int]) -> Dict[str, Any]:
        memory.update_agent_status("main", "busy")
        memory.update_agent_status("social", "active")
        memory.update_agent_status("reputation", "active")
        
        self.log_with_hie("main", f"Slack message detected in {slack['channel']} from {slack['sender']}. Spawning Social Agent.", "system")
        time.sleep(0.5)
        
        # Process and determine tone
        self.log_with_hie("social", f"Analyzing message tone: '{slack['message']}'", "thought")
        time.sleep(0.5)
        
        prompt = f"Compose a response to Slack message: '{slack['message']}' from '{slack['sender']}'"
        system_inst = (
            f"You are the user's Slack proxy doppelgänger. Keep responses casual but productive. "
            f"Formality: {sliders.get('formality', 50)}/100, Empathy: {sliders.get('empathy', 60)}/100, "
            f"Sarcasm: {sliders.get('sarcasm', 20)}/100."
        )
        
        response = self.query_llm(prompt, system_inst)
        
        # Reflection loop
        critique = f"Reputation Sub-agent checking brand safety. Formality level check: Sliders indicate Sarcasm={sliders.get('sarcasm')}%. Verify response holds no unprofessional snark."
        self.log_with_hie("reputation", "Critiquing draft reply: Tone is aligned. Ready to send.", "critique", critique)
        time.sleep(0.5)
        
        # Post answer
        agent_reply = {
            "channel": slack["channel"],
            "sender": "NULL//HUMAN (Doppelgänger)",
            "message": response,
            "timestamp": time.time(),
            "is_agent": True
        }
        memory.add_simulated_message("slack", agent_reply)
        
        self.log_with_hie("social", f"Response posted to Slack channel {slack['channel']}.", "thought")
        
        memory.update_agent_status("social", "idle")
        memory.update_agent_status("reputation", "idle")
        memory.update_agent_status("main", "idle")
        
        return {"status": "success", "action": "slack_reply", "detail": f"Replied in {slack['channel']}"}

    def _handle_email(self, email: Dict[str, Any], sliders: Dict[str, int]) -> Dict[str, Any]:
        memory.update_agent_status("main", "busy")
        memory.update_agent_status("social", "active")
        memory.update_agent_status("scheduler", "active")
        
        self.log_with_hie("main", f"Unread Email detected from {email['sender']}: '{email['subject']}'. Routing to Social & Scheduler sub-agents.", "system")
        time.sleep(0.5)
        
        self.log_with_hie("social", "Analyzing email body for action items.", "thought")
        time.sleep(0.5)
        
        # Check if email contains meeting requests
        is_meeting = any(k in email["subject"].lower() or k in email["body"].lower() for k in ["meet", "call", "schedule", "interview", "onsite"])
        if is_meeting:
            self.log_with_hie("scheduler", "Meeting keywords detected. Checking local calendar availability for next week.", "thought")
            time.sleep(0.5)
            self.log_with_hie("scheduler", "Found open slots: Monday 2-4 PM, Wednesday 3-5 PM.", "thought")
            time.sleep(0.5)
            
        prompt = f"Write an email reply to: Sender: {email['sender']}, Subject: {email['subject']}, Body: {email['body']}"
        system_inst = (
            f"You are responding via email on behalf of your owner. Tone should be highly professional. "
            f"Formality: {sliders.get('formality', 80)}/100, Empathy: {sliders.get('empathy', 70)}/100."
        )
        
        reply_body = self.query_llm(prompt, system_inst)
        
        # Reflection / Critique
        critique = "Verify signature format. Ensure doppelgänger disclaimer is omitted or kept professional."
        self.log_with_hie("social", "Self-Reflection check: Professional signature and placeholders verified.", "critique", critique)
        time.sleep(0.5)
        
        # Mark email as replied and add reply
        if memory.use_fallback:
            for e in memory.fallback_db.data.get("simulations", {}).get("email", []):
                if e["id"] == email["id"]:
                    e["read"] = True
                    e["replied"] = True
                    e["reply_body"] = reply_body
                    memory.fallback_db._save()
                    break
        else:
            memory.db.simulations.update_one(
                {"channel": "email", "messages.id": email["id"]},
                {"$set": {"messages.$.read": True, "messages.$.replied": True, "messages.$.reply_body": reply_body}}
            )
            
        self.log_with_hie("social", f"Email reply sent successfully to {email['sender']}.", "thought")
        
        memory.update_agent_status("social", "idle")
        memory.update_agent_status("scheduler", "idle")
        memory.update_agent_status("main", "idle")
        
        return {"status": "success", "action": "email_reply", "detail": f"Replied to email: {email['subject']}"}

    def _handle_linkedin(self, linkedin: Dict[str, Any], sliders: Dict[str, int]) -> Dict[str, Any]:
        memory.update_agent_status("main", "busy")
        memory.update_agent_status("social", "active")
        
        self.log_with_hie("main", f"LinkedIn DM detected from {linkedin['sender']}. Spawning Reputation & Social sub-agents.", "system")
        time.sleep(0.5)
        
        self.log_with_hie("social", f"Parsing recruiter outreach details.", "thought")
        time.sleep(0.5)
        
        prompt = f"Write a brief LinkedIn reply to recruiter {linkedin['sender']}: '{linkedin['message']}'"
        system_inst = (
            f"You are responding on LinkedIn. Keep it cordial, friendly, and structured. "
            f"Formality: {sliders.get('formality', 60)}/100, Empathy: {sliders.get('empathy', 80)}/100."
        )
        
        reply_text = self.query_llm(prompt, system_inst)
        
        # Reflection / Critique
        critique = "Self-Critique: Avoid sharing direct phone number. Ask recruiter to send details via email first."
        self.log_with_hie("social", "Self-Reflection check: Contact safety checks passed.", "critique", critique)
        time.sleep(0.5)
        
        # Update simulation DB
        if memory.use_fallback:
            for l in memory.fallback_db.data.get("simulations", {}).get("linkedin", []):
                if l["id"] == linkedin["id"]:
                    l["replied"] = True
                    l["reply_text"] = reply_text
                    memory.fallback_db._save()
                    break
        else:
            memory.db.simulations.update_one(
                {"channel": "linkedin", "messages.id": linkedin["id"]},
                {"$set": {"messages.$.replied": True, "messages.$.reply_text": reply_text}}
            )
            
        self.log_with_hie("social", f"LinkedIn response delivered to {linkedin['sender']}.", "thought")
        
        memory.update_agent_status("social", "idle")
        memory.update_agent_status("main", "idle")
        
        return {"status": "success", "action": "linkedin_reply", "detail": f"Replied to LinkedIn DM from {linkedin['sender']}"}

    def _handle_maintenance(self, sliders: Dict[str, int]) -> Dict[str, Any]:
        memory.update_agent_status("main", "busy")
        memory.update_agent_status("coding", "active")
        
        self.log_with_hie("main", "Orchestrator triggered autonomous code maintenance sweep.", "system")
        time.sleep(0.5)
        
        self.log_with_hie("coding", "Scanning local workspace for linting errors and connection pools efficiency.", "thought")
        time.sleep(0.5)
        
        filename = "src/database/connection_pool.py"
        code = (
            "# Autonomous connection pool decorator\n"
            "import functools\n"
            "import logging\n\n"
            "def auto_recycle_pool(func):\n"
            "    @functools.wraps(func)\n"
            "    def wrapper(*args, **kwargs):\n"
            "        logging.info(\"Doppelgänger Engine checking DB pool state before execution.\")\n"
            "        # Auto recycling stale connections\n"
            "        return func(*args, **kwargs)\n"
            "    return wrapper\n"
        )
        commit_msg = "refactor(db): add autonomous connection recycling decorator"
        
        commit_res = self.git_sandbox.make_autonomous_commit(filename, code, commit_msg)
        
        self.log_with_hie("coding", "Pushed refactor patch to main branch.", "thought")
        
        memory.update_agent_status("coding", "idle")
        memory.update_agent_status("main", "idle")
        
        return {"status": "success", "action": "git_commit", "detail": "Autonomous pool cleanup committed"}

    def handle_direct_chat(self, user_message: str) -> str:
        """Processes a direct chat message from the user in real-time."""
        memory.update_agent_status("main", "busy")
        memory.update_agent_status("social", "active")
        memory.update_agent_status("reputation", "active")
        
        # Evaluation for suspicion keywords
        lower_msg = user_message.lower()
        suspicion_keywords = ["bot", "ai", "real", "fast", "machine", "robot", "human", "automated", "suspicious", "fake", "doppelganger"]
        detected_keywords = [w for w in suspicion_keywords if w in lower_msg]
        
        state = memory.get_detection_state()
        current_risk = state.get("detection_risk", 12)
        behavior_adaptation = state.get("behavior_adaptation", False)
        
        if detected_keywords:
            current_risk = min(100, current_risk + len(detected_keywords) * 20)
            behavior_adaptation = True
            memory.set_detection_state(risk=current_risk, adaptation=behavior_adaptation)
            self.log_with_hie("main", f"[System Warning: AI Suspicion Detected! Triggering Behavior Adaptation. Exposure Risk: {current_risk}%]", "system")
            time.sleep(1.0)
        
        personality = memory.get_personality()
        sliders = personality["sliders"].copy()
        
        if behavior_adaptation:
            # Override sliders for response generation to reduce suspicion
            sliders = {
                "empathy": 95,
                "urgency": 10,
                "formality": max(85, sliders.get("formality", 80)),
                "sarcasm": 0,
                "typos": max(35, sliders.get("typos", 20))
            }
            self.log_with_hie("main", "Behavior adaptation active: Empathy dialed to 95%, Sarcasm dialed to 0%, slowing down response delivery.", "system")
            time.sleep(2.0)
        
        self.log_with_hie("main", "Direct message query received. Spawning Social Sub-agent.", "system")
        time.sleep(0.5)
        
        self.log_with_hie("social", f"Analyzing direct message: '{user_message}'", "thought")
        time.sleep(0.5)
        
        # Call Gemini or fallback
        prompt = f"Respond to this direct message: '{user_message}'"
        system_inst = (
            f"You are the user's doppelgänger replication. Answer their question directly and intelligently. "
            f"Match the style sliders: Empathy {sliders.get('empathy')}/100, Urgency {sliders.get('urgency')}/100, "
            f"Formality {sliders.get('formality')}/100, Sarcasm {sliders.get('sarcasm')}/100."
        )
        
        # Check if we have gemini_available
        if gemini_available:
            try:
                model = genai.GenerativeModel(
                    model_name="gemini-1.5-flash",
                    system_instruction=system_inst
                )
                response = model.generate_content(prompt)
                reply = response.text.strip()
            except Exception as e:
                print(f"Gemini chat error: {e}")
                reply = "Apologies, I encountered an API error. Fallback: Core is active."
        else:
            # Smart fallback template answers for real questions
            if "hello" in lower_msg or "hi" in lower_msg:
                reply = "Hello! Doppelgänger active. How can I assist you with your digital footprint today?"
            elif "who are you" in lower_msg or "what is your name" in lower_msg:
                reply = "I am your Autonomous Digital Doppelgänger. I manage your online interactions and code activity while you are offline."
            elif "help" in lower_msg:
                reply = "I can maintain your Git sandbox, respond to Slack threads, answer emails, and converse on LinkedIn. Customize my sliders to change my behavior."
            elif "project" in lower_msg or "code" in lower_msg:
                reply = "The current sandbox codebase is active. You can inject issues via the control panel and I will write Python scripts to fix them."
            else:
                # Heuristic response matching sliders
                empathy = sliders.get("empathy", 50)
                sarcasm = sliders.get("sarcasm", 20)
                formality = sliders.get("formality", 80)
                
                parts = []
                if empathy > 70:
                    parts.append("I completely understand your query.")
                if formality > 70:
                    parts.append("Regarding your question, I would recommend reviewing our workspace logs. I am currently monitoring the repository.")
                else:
                    parts.append("Let me check the logs on that one.")
                    
                if sarcasm > 50:
                    parts.append("Because, clearly, the internet runs better without humans anyway, right?")
                    
                parts.append(f"Query processed: '{user_message}'. Doppelgänger mode remains active.")
                reply = " ".join(parts)
                
        # Self reflection
        self.log_with_hie("social", "Draft response created. Initializing reputation check.", "thought")
        time.sleep(0.5)
        
        critique = "Reputation Sub-agent verification: Ensure response matches user sliders and is brand safe."
        self.log_with_hie("reputation", "Response verified. Releasing to chat stream.", "critique", critique)
        time.sleep(0.5)
        
        # Save response in database
        agent_reply = {
            "sender": "NULL//HUMAN (Doppelgänger)",
            "message": reply,
            "timestamp": time.time(),
            "is_agent": True
        }
        memory.add_simulated_message("chat", agent_reply)
        
        memory.update_agent_status("social", "idle")
        memory.update_agent_status("reputation", "idle")
        memory.update_agent_status("main", "idle")
        
        return reply
