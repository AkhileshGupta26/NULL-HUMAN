import time
import random
from typing import List, Dict, Any, Optional
from backend import memory

# Initial seed data to make the dashboard look instantly active and rich on boot
INITIAL_SLACK = [
    {
        "channel": "#dev-team",
        "sender": "Sarah (PM)",
        "message": "Hey everyone, do we have an update on the API latency issue in production?",
        "timestamp": time.time() - 3600 * 2,
        "is_agent": False
    },
    {
        "channel": "#dev-team",
        "sender": "John (Dev)",
        "message": "I checked the logs, it seems database connection pool exhaustion might be happening during peak times.",
        "timestamp": time.time() - 3600 * 1.8,
        "is_agent": False
    },
    {
        "channel": "#dev-team",
        "sender": "NULL//HUMAN (Doppelgänger)",
        "message": "I'm looking into it. I will write a script to monitor pool usage and see if we can optimize the cleanup threshold in config.py.",
        "timestamp": time.time() - 3600 * 1.5,
        "is_agent": True
    },
    {
        "channel": "#general",
        "sender": "HR Team",
        "message": "Reminder: Please submit your timesheets by Friday afternoon! 📝",
        "timestamp": time.time() - 3600 * 4,
        "is_agent": False
    }
]

INITIAL_EMAIL = [
    {
        "id": "e1",
        "sender": "Sarah.pm@company.com",
        "subject": "Urgent: Client Review Meeting Tomorrow",
        "body": "Hi, can you make sure the dashboard demo is fully functional for our 10 AM review tomorrow? The client wants to see the live metrics updating.",
        "timestamp": time.time() - 3600 * 5,
        "read": True,
        "replied": True,
        "reply_body": "Hi Sarah, yes, the metrics dashboard is stable. I have double-checked the WebSocket connections and everything is green. I will be present for the meeting."
    },
    {
        "id": "e2",
        "sender": "recruiter@hightechtalent.io",
        "subject": "Opportunities at TechCorp - Lead Role",
        "body": "Hi, I saw your GitHub profile and was extremely impressed by your recent work with autonomous agent architectures. Would you be open to a quick call this Thursday?",
        "timestamp": time.time() - 3600 * 1,
        "read": False,
        "replied": False
    }
]

INITIAL_LINKEDIN = [
    {
        "id": "l1",
        "sender": "Alex Mercer",
        "avatar": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&q=80&w=100",
        "message": "Hey! Loved your post on autonomous agent reflection loops. Let's catch up sometime next week to talk tech.",
        "timestamp": time.time() - 3600 * 24,
        "replied": True,
        "reply_text": "Hey Alex! Thanks for reaching out. Yes, reflection loops are crucial for reliability. Let's schedule a Zoom chat next Wednesday!"
    },
    {
        "id": "l2",
        "sender": "Sophia Chen (Technical Recruiter)",
        "avatar": "https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&q=80&w=100",
        "message": "Hi there! We are currently looking for a Senior AI Agent Engineer at NextGen Systems. Your background in LLM orchestration looks perfect. Let me know if you are open to discuss.",
        "timestamp": time.time() - 3600 * 3,
        "replied": False
    }
]

INITIAL_CHAT = [
    {
        "sender": "NULL//HUMAN (Doppelgänger)",
        "message": "Direct link established. I can answer questions in real-time using my current personality matrix. Send a message to test my responses.",
        "timestamp": time.time(),
        "is_agent": True
    }
]


# Random simulation prompts for generating incoming events
INCOMING_EVENTS_POOL = [
    {
        "channel": "slack",
        "data": {
            "channel": "#dev-team",
            "sender": "John (Dev)",
            "message": "Should we migrate to the new database cluster this week or wait for the weekend release?",
            "reply_prompt": "Answer that we should wait for the weekend release to minimize risk, but prepare the schema migration script beforehand."
        }
    },
    {
        "channel": "slack",
        "data": {
            "channel": "#general",
            "sender": "Sarah (PM)",
            "message": "Has anyone tested the latest release package on staging? We need a quick sign-off.",
            "reply_prompt": "Respond that you ran the automated smoke tests on staging and everything completed successfully. Sign off on the staging deployment."
        }
    },
    {
        "channel": "email",
        "data": {
            "id": "",
            "sender": "billing@cloudservices.com",
            "subject": "Alert: Monthly Usage Threshold Reached",
            "body": "Dear Customer, your organization's API usage has reached 85% of your allocated monthly tier. Please upgrade or manage your limits to prevent suspension.",
            "reply_prompt": "Write a reply asking to check which sub-agent is consuming excess API usage, and say you will implement rate limits on the backend orchestrator."
        }
    },
    {
        "channel": "email",
        "data": {
            "id": "",
            "sender": "careers@google-tech-recruiting.com",
            "subject": "Software Engineer Role Interview Request",
            "body": "Hello, we reviewed your technical screening and would love to move you to the virtual onsite round. Could you send us your availability for next week?",
            "reply_prompt": "Reply politely expressing enthusiasm, and coordinate with the calendar agent to suggest Monday and Wednesday afternoon between 2 PM and 5 PM EST."
        }
    },
    {
        "channel": "linkedin",
        "data": {
            "sender": "David Miller (Engineering Manager)",
            "message": "Hi, congratulations on launching the new open-source MCP server. Are you planning on adding MongoDB vector search integrations soon?",
            "reply_prompt": "Say thank you, and mention that the MongoDB vector search integration is actually going to be implemented tonight as our memory database layer."
        }
    }
]

def seed_initial_data():
    """Seeds the DB with initial data if empty."""
    # Slack
    slack_msgs = memory.get_simulations("slack")
    if not slack_msgs:
        for msg in INITIAL_SLACK:
            memory.add_simulated_message("slack", msg)
            
    # Email
    email_msgs = memory.get_simulations("email")
    if not email_msgs:
        for msg in INITIAL_EMAIL:
            memory.add_simulated_message("email", msg)
            
    # LinkedIn
    linkedin_msgs = memory.get_simulations("linkedin")
    if not linkedin_msgs:
        for msg in INITIAL_LINKEDIN:
            memory.add_simulated_message("linkedin", msg)
            
    # Chat
    chat_msgs = memory.get_simulations("chat")
    if not chat_msgs:
        for msg in INITIAL_CHAT:
            memory.add_simulated_message("chat", msg)

def get_all_simulated_data() -> Dict[str, List[Dict[str, Any]]]:
    """Retrieves all simulation message logs."""
    return {
        "slack": memory.get_simulations("slack"),
        "email": memory.get_simulations("email"),
        "linkedin": memory.get_simulations("linkedin"),
        "chat": memory.get_simulations("chat")
    }

def simulate_incoming_event() -> Optional[Dict[str, Any]]:
    """Simulates an incoming user communication (Slack, Email, LinkedIn)."""
    # 35% chance to spawn an event when this is run
    if random.random() > 0.4:
        return None
        
    event = random.choice(INCOMING_EVENTS_POOL)
    channel = event["channel"]
    data = event["data"].copy()
    
    if channel == "slack":
        data["timestamp"] = time.time()
        data["is_agent"] = False
        memory.add_simulated_message("slack", data)
        return {"channel": "slack", "message": f"New Slack message in {data['channel']} from {data['sender']}"}
        
    elif channel == "email":
        data["id"] = f"e{int(time.time())}"
        data["timestamp"] = time.time()
        data["read"] = False
        data["replied"] = False
        memory.add_simulated_message("email", data)
        return {"channel": "email", "message": f"New Email from {data['sender']}: {data['subject']}"}
        
    elif channel == "linkedin":
        data["id"] = f"l{int(time.time())}"
        data["timestamp"] = time.time()
        data["replied"] = False
        data["avatar"] = f"https://i.pravatar.cc/100?img={random.randint(1, 70)}"
        memory.add_simulated_message("linkedin", data)
        return {"channel": "linkedin", "message": f"New LinkedIn message from {data['sender']}"}
        
    return None
