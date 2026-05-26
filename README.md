# NULL//HUMAN
### *The Autonomous Digital Doppelgänger Agent*

> **“Disappear from the internet. Your AI won't.”**

This is not a chatbot. This is a fully autonomous AI identity replication system that mimics your online activity, coding footprint, and professional communication patterns. 

---

## 🖤 The Story (The Hackathon Hook)

The internet is already becoming autonomous. What happens when AI can fully replace your digital existence? 

**The Experiment:** You go offline for 7 days. Your doppelgänger takes over:
- It replies to emails from your inbox.
- It chats with colleagues in Slack channels.
- It commits code and closes bugs in your Git repositories.
- It maintains your recruiter dialogues on LinkedIn.

**The Reveal:** *Nobody noticed the human disappeared.*

---

## 🛠 System Architecture

```
                   ┌────────────────────┐
                   │    USER PROFILE    │
                   │ (style, inputs,    │
                   │  sliders, sliders) │
                   └─────────┬──────────┘
                             │
                             ▼
                 ┌─────────────────────┐
                 │ PERSONA ENGINE      │
                 │ (behavior modeling) │
                 └─────────┬───────────┘
                           │
         ┌─────────────────┼─────────────────┐
         ▼                 ▼                 ▼
┌────────────────┐ ┌────────────────┐ ┌────────────────┐
│ COMMUNICATION  │ │   DEV AGENT    │ │ DECISION AGENT │
│ (Email/LinkedIn│ │ (Git Sandboxing│ │  (Reflection   │
│  Slack Mocks)  │ │   Commits)     │ │   & Critique)  │
└────────────────┘ └────────────────┘ └────────────────┘
         │                 │                 │
         └─────────────────┼─────────────────┘
                           ▼
                ┌────────────────────┐
                │   MEMORY ENGINE    │
                │ (MongoDB / JSON)   │
                └────────────────────┘
```

---

## ✨ Features Built For The Demo

### 1. Persona Engine
Uses a **Personality Matrix** to align agent responses with your current vibe. Slide controls in real-time to adjust:
- **Empathy** (determines sensitivity to interpersonal context)
- **Urgency** (affects action priority and response speed)
- **Formality** (adjusts syntax styling between casual chat and email)
- **Sarcasm** (injects wit and humor into communication streams)

### 2. Git & Workspace Autonomy
A custom **Coding Sub-agent** interacts with a local Git sandbox (`git-sandbox`). Injecting an issue in the console triggers the agent to:
- Write real Python files solving the issue.
- Run local git commands (`add`, `commit`) with your custom digital signature (`NULL//HUMAN <agent@nullhuman.ai>`).
- Comment on and close the workspace ticket automatically.

### 3. Agent Orchestration Graph
A live SVG network map showing communication nodes spawning in real-time:
- **Main Agent**: Listens to workspace events and coordinates tasks.
- **Coding Agent**: Handles code generation, file edits, and git commits.
- **Social Agent**: Formulates simulated chat responses.
- **Scheduler Agent**: Syncs calendar slots and meeting requests.
- **Reputation Agent**: A critiquing loop that inspects drafts for safety before publishing.

### 4. Self-Critique & Reflection Loops
Watch the agent think in the **Reasoning Log Stream**. The agent writes its initial thoughts, critiques them against your sliders, refactors its draft, and logs its output.

### 5. High-Fidelity Simulation Hub
Tabs to inspect the agent's digital life:
- **Slack Channels** (`#dev-team` / `#general`)
- **Email Client** (threads from clients, PMs, and recruiters)
- **LinkedIn DM Center** (recruiter outreach handling)
- **Git Logs** (inspecting live repository hashes and diff files)

---

## 🚀 Getting Started

### 1. Prerequisites
- **Node.js** (v18+)
- **Python** (v3.10+)
- **Git** (locally configured)

### 2. Clone and Setup Workspace
```bash
git clone https://github.com/your-username/dead-internet-agent.git
cd dead-internet-agent
```

### 3. Start Backend (FastAPI)
```bash
cd backend
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
python main.py
```
*The FastAPI server will start on [http://localhost:8000](http://localhost:8000).*

### 4. Start Frontend (Next.js)
In a new terminal window:
```bash
cd frontend
npm install
npm run dev
```
*The frontend will run on [http://localhost:3000](http://localhost:3000).*

---

## 🔒 Configuration (Optional)
Create a `.env` file in the `backend/` folder to run with live MongoDB Atlas or Gemini models:
```env
MONGODB_URI=your_mongodb_atlas_connection_string
GEMINI_API_KEY=your_gemini_api_key
RUN_INTERVAL_SECONDS=5
```
*If left empty, the system automatically runs on local memory databases and built-in template-based persona generation, ensuring 100% functionality offline.*

---

## ⚖️ License
NULL//HUMAN © 2026. Made with existential dread for the hackathon.
