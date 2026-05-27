"use client";

import { useEffect, useState, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { 
  Play, Pause, RefreshCw, Terminal, 
  MessageSquare, Mail, GitBranch, 
  Send, ShieldAlert, Cpu, CheckCircle2, User, Sparkles,
  Activity
} from "lucide-react";

// Centralized API configuration supporting local development and production environment overrides
let rawApiBase = process.env.NEXT_PUBLIC_API_BASE || "http://127.0.0.1:8000/api";
if (rawApiBase && !rawApiBase.endsWith("/api") && !rawApiBase.endsWith("/api/")) {
  const cleaned = rawApiBase.endsWith("/") ? rawApiBase.slice(0, -1) : rawApiBase;
  rawApiBase = `${cleaned}/api`;
}
const API_BASE = rawApiBase;

export default function Dashboard() {
  const [mounted, setMounted] = useState(false);
  const [active, setActive] = useState(false);
  const [personality, setPersonality] = useState({
    sliders: { empathy: 60, urgency: 40, formality: 80, sarcasm: 20, typos: 20 },
    description: "Professional software engineer clone. Diligent, focused, and polite."
  });
  const [agents, setAgents] = useState<any[]>([]);
  const [logs, setLogs] = useState<any[]>([]);
  const [commits, setCommits] = useState<any[]>([]);
  const [issues, setIssues] = useState<any[]>([]);
  const [feeds, setFeeds] = useState<any>({ slack: [], email: [], linkedin: [], chat: [] });
  const [isOffline, setIsOffline] = useState(false);
  
  // Connection states
  const [identityMode, setIdentityMode] = useState("sandbox");
  const [gitlabPat, setGitlabPat] = useState("");
  const [gitlabUsername, setGitlabUsername] = useState("");
  const [gitlabRepo, setGitlabRepo] = useState("");
  const [gitlabHost, setGitlabHost] = useState("gitlab.com");
  const [geminiApiKey, setGeminiApiKey] = useState("");
  const [showIdentitySettings, setShowIdentitySettings] = useState(false);
  const [isSavingIdentity, setIsSavingIdentity] = useState(false);
  const [showPat, setShowPat] = useState(false);
  const [showGeminiKey, setShowGeminiKey] = useState(false);
  const [detectionState, setDetectionState] = useState({ detection_risk: 12, behavior_adaptation: false });

  const [currentTab, setCurrentTab] = useState<"slack" | "email" | "linkedin" | "chat">("slack");
  const [slackChannel, setSlackChannel] = useState("#dev-team");
  const [selectedEmail, setSelectedEmail] = useState<any>(null);
  
  const [newIssueTitle, setNewIssueTitle] = useState("");
  const [newIssueDesc, setNewIssueDesc] = useState("");
  const [isSubmittingIssue, setIsSubmittingIssue] = useState(false);
  const [isTicking, setIsTicking] = useState(false);
  const [isResetting, setIsResetting] = useState(false);

  const [directChatMessage, setDirectChatMessage] = useState("");
  const [isSendingChat, setIsSendingChat] = useState(false);

  const logsContainerRef = useRef<HTMLDivElement>(null);
  const slackContainerRef = useRef<HTMLDivElement>(null);
  const chatContainerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setMounted(true);
    fetchDashboardData();
    fetchIdentitySettings();
    
    // Poll dashboard data every 1.5 seconds
    const interval = setInterval(() => {
      fetchDashboardData();
    }, 1500);
    
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    // Scroll to bottom of logs on new log
    if (logsContainerRef.current) {
      logsContainerRef.current.scrollTop = logsContainerRef.current.scrollHeight;
    }
  }, [logs]);

  useEffect(() => {
    // Scroll to bottom of Slack messages on update
    if (slackContainerRef.current) {
      slackContainerRef.current.scrollTop = slackContainerRef.current.scrollHeight;
    }
  }, [feeds.slack, slackChannel]);

  useEffect(() => {
    // Scroll to bottom of Chat messages on update
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [feeds.chat, currentTab]);

  const handleSendDirectChat = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!directChatMessage || isSendingChat) return;
    setIsSendingChat(true);
    const msg = directChatMessage;
    setDirectChatMessage("");
    
    try {
      const res = await fetch(`${API_BASE}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: msg })
      });
      if (res.ok) {
        fetchDashboardData();
      }
    } catch (err) {
      console.error("Error sending direct chat:", err);
    } finally {
      setIsSendingChat(false);
    }
  };

  const fetchIdentitySettings = async () => {
    try {
      const res = await fetch(`${API_BASE}/identity`);
      if (res.ok) {
        const data = await res.json();
        setIdentityMode(data.identity_mode || "sandbox");
        setGitlabPat(data.gitlab_pat || "");
        setGitlabUsername(data.gitlab_username || "");
        setGitlabRepo(data.gitlab_repo || "");
        setGitlabHost(data.gitlab_host || "gitlab.com");
        setGeminiApiKey(data.gemini_api_key || "");
      }
    } catch (err) {
      console.error("Error fetching identity settings:", err);
    }
  };

  const handleSaveIdentitySettings = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSavingIdentity(true);
    try {
      const res = await fetch(`${API_BASE}/identity`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          identity_mode: identityMode,
          gitlab_pat: gitlabPat,
          gitlab_username: gitlabUsername,
          gitlab_repo: gitlabRepo,
          gitlab_host: gitlabHost,
          gemini_api_key: geminiApiKey
        })
      });
      if (res.ok) {
        setShowIdentitySettings(false);
        fetchDashboardData();
      } else {
        alert("Failed to save identity connection settings.");
      }
    } catch (err) {
      console.error("Error saving identity settings:", err);
    } finally {
      setIsSavingIdentity(false);
    }
  };

  const fetchDashboardData = async () => {
    try {
      const res = await fetch(`${API_BASE}/dashboard`);
      if (res.ok) {
        setIsOffline(false);
        const data = await res.json();
        setActive(data.doppelganger_active);
        setPersonality(data.personality);
        setAgents(data.agents);
        // Reverse logs to display oldest at top and scroll down
        const sortedLogs = [...data.logs].reverse();
        setLogs(sortedLogs);
        setCommits(data.commits);
        setIssues(data.issues);
        setFeeds(data.feeds);
        if (data.detection_state) {
          setDetectionState(data.detection_state);
        }
        
        // Auto select first email if none selected and emails exist
        if (data.feeds?.email?.length > 0 && !selectedEmail) {
          setSelectedEmail(data.feeds.email[0]);
        } else if (data.feeds?.email?.length > 0 && selectedEmail) {
          // Keep reference updated
          const updated = data.feeds.email.find((e: any) => e.id === selectedEmail.id);
          if (updated) setSelectedEmail(updated);
        }
      } else {
        setIsOffline(true);
      }
    } catch (err) {
      console.error("Error fetching dashboard data:", err);
      setIsOffline(true);
    }
  };

  const toggleDoppelganger = async () => {
    const endpoint = active ? "deactivate" : "activate";
    try {
      const res = await fetch(`${API_BASE}/${endpoint}`, { method: "POST" });
      if (res.ok) {
        fetchDashboardData();
      }
    } catch (err) {
      console.error("Error toggling doppelganger:", err);
    }
  };

  const handleSliderChange = async (key: string, value: number) => {
    const updatedSliders = { ...personality.sliders, [key]: value };
    // Optimistic update
    setPersonality({ ...personality, sliders: updatedSliders });
    
    try {
      await fetch(`${API_BASE}/personality`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          sliders: updatedSliders,
          description: personality.description
        })
      });
    } catch (err) {
      console.error("Error saving sliders:", err);
    }
  };

  const handleForceTick = async () => {
    setIsTicking(true);
    try {
      await fetch(`${API_BASE}/tick`, { method: "POST" });
      await fetchDashboardData();
    } catch (err) {
      console.error("Error triggering tick:", err);
    } finally {
      setIsTicking(false);
    }
  };

  const handleResetDemo = async () => {
    if (!confirm("Are you sure you want to reset all sandbox commits, issues, logs, and communication archives?")) return;
    setIsResetting(true);
    try {
      await fetch(`${API_BASE}/reset`, { method: "POST" });
      setSelectedEmail(null);
      await fetchDashboardData();
    } catch (err) {
      console.error("Error resetting demo:", err);
    } finally {
      setIsResetting(false);
    }
  };

  const handleCreateIssue = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newIssueTitle || !newIssueDesc) return;
    setIsSubmittingIssue(true);
    try {
      const res = await fetch(`${API_BASE}/issue`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          title: newIssueTitle,
          description: newIssueDesc
        })
      });
      if (res.ok) {
        setNewIssueTitle("");
        setNewIssueDesc("");
        fetchDashboardData();
      }
    } catch (err) {
      console.error("Error creating issue:", err);
    } finally {
      setIsSubmittingIssue(false);
    }
  };

  const getAgentStatus = (id: string) => {
    const a = agents.find(agent => agent.id === id);
    return a ? a.status : "idle";
  };

  if (!mounted) return null;

  // Filter slack based on channel
  const filteredSlack = feeds.slack?.filter((m: any) => m.channel === slackChannel) || [];

  // Filter recent commits to dynamically light up the calendar bottom right cell
  const recentCommits = commits.filter(c => 
    c.time?.includes("second") || 
    c.time?.includes("minute") || 
    c.time?.includes("hour")
  ).length;

  return (
    <div className="min-h-screen bg-[#030303] text-gray-200 flex flex-col p-4 md:p-6 select-none font-sans">
      
      {/* Connection Offline Warning Banner */}
      <AnimatePresence>
        {isOffline && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="w-full bg-neon-red/10 border border-neon-red/30 p-3 rounded-xl mb-6 text-center text-xs font-mono text-neon-red uppercase tracking-wider flex items-center justify-center gap-2 shadow-[0_0_15px_rgba(255,0,85,0.15)] animate-pulse"
          >
            <ShieldAlert className="w-4 h-4 text-neon-red" />
            <span>[Connection offline]: Cannot communicate with replication backend at <span className="underline">{API_BASE}</span>. Verify backend deployment and env configs.</span>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Top Console Bar */}
      <header className="w-full flex flex-col md:flex-row justify-between items-center py-4 px-6 border border-neon-blue/20 bg-black/60 rounded-xl mb-6 gap-4 cyber-panel">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-neon-blue/10 border border-neon-blue flex items-center justify-center text-neon-blue shadow-[0_0_15px_rgba(0,240,255,0.2)]">
            <Cpu className="w-6 h-6 animate-pulse" />
          </div>
          <div>
            <h1 className="text-lg font-black uppercase tracking-wider text-transparent bg-clip-text bg-gradient-to-r from-neon-blue to-neon-purple">
              NULL//HUMAN REPLICATION ENGINE
            </h1>
            <p className="text-[10px] text-gray-500 font-mono tracking-widest uppercase">
              STATUS: {isOffline ? "OFFLINE" : "ONLINE"} // SYNTHETIC SYNC RATIO: {isOffline ? "0.0%" : "99.1%"}
            </p>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          {/* Identity Control Center Trigger */}
          <button
            onClick={() => setShowIdentitySettings(true)}
            className="px-3.5 py-1.5 border border-neon-blue/40 hover:border-neon-blue bg-neon-blue/5 hover:bg-neon-blue/20 text-neon-blue hover:shadow-[0_0_15px_rgba(0,240,255,0.25)] rounded text-xs uppercase tracking-wider font-semibold font-mono flex items-center gap-2 cursor-pointer transition-all duration-300"
          >
            <User className="w-3.5 h-3.5" />
            Identity Control Center
          </button>

          {/* Reset Demo */}
          <button
            onClick={handleResetDemo}
            disabled={isResetting || isOffline}
            className="px-3.5 py-1.5 border border-neon-red/40 hover:border-neon-red bg-neon-red/5 hover:bg-neon-red/20 text-neon-red hover:shadow-[0_0_15px_rgba(255,0,85,0.25)] rounded text-xs uppercase tracking-wider font-semibold font-mono flex items-center gap-2 cursor-pointer transition-all duration-300 disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isResetting ? 'animate-spin' : ''}`} />
            Reset Demo
          </button>

          {/* Force cycle tick */}
          <button
            onClick={handleForceTick}
            disabled={isTicking || isOffline}
            className="px-3.5 py-1.5 border border-neon-purple/40 hover:border-neon-purple bg-neon-purple/5 hover:bg-neon-purple/20 text-neon-purple hover:shadow-[0_0_15px_rgba(189,0,255,0.25)] rounded text-xs uppercase tracking-wider font-semibold font-mono flex items-center gap-2 cursor-pointer transition-all duration-300 disabled:opacity-50"
          >
            <Sparkles className={`w-3.5 h-3.5 ${isTicking ? 'animate-spin' : ''}`} />
            Force Cycle
          </button>

          {/* Status Indicator / Activation Toggle */}
          <button
            onClick={toggleDoppelganger}
            disabled={isOffline}
            className={`px-5 py-1.5 rounded flex items-center gap-2 text-xs uppercase font-bold tracking-widest cursor-pointer border transition-all duration-300 disabled:opacity-50 ${
              active 
                ? "border-neon-green bg-neon-green/10 text-neon-green shadow-[0_0_15px_rgba(57,255,20,0.3)] hover:bg-neon-green/20" 
                : "border-gray-500 bg-gray-500/5 text-gray-400 hover:text-gray-300"
            }`}
          >
            {active ? <Pause className="w-3.5 h-3.5" /> : <Play className="w-3.5 h-3.5" />}
            {active ? "DOPPELGÄNGER MODE: ACTIVE" : "DOPPELGÄNGER MODE: OFF"}
          </button>
        </div>
      </header>

      {/* Main Panel Grid Layout */}
      <div className="grid grid-cols-1 xl:grid-cols-12 gap-6 flex-1 items-stretch">
        
        {/* Left Section: GitLab Centerpiece (Col-span 7) */}
        <section className="xl:col-span-7 flex flex-col gap-6">
          
          {/* GitLab Contribution Activity Calendar Grid */}
          <div className="cyber-panel p-5 rounded-xl border border-neon-blue/10 flex flex-col bg-black/45 shadow-[0_8px_30px_rgb(0,0,0,0.4)]">
            <div className="flex items-center justify-between mb-4 border-b border-neon-blue/10 pb-2">
              <div className="flex items-center gap-2">
                <Activity className="w-4 h-4 text-neon-green animate-pulse" />
                <h2 className="text-xs uppercase font-bold tracking-widest text-neon-green">
                  Live GitLab Contribution Activity Calendar
                </h2>
              </div>
              <div className="text-[10px] text-gray-500 font-mono tracking-widest uppercase">
                AUTONOMOUS CODE LAYER PATTERNS
              </div>
            </div>
            
            <div className="flex flex-col gap-2 overflow-x-auto pb-2 scrollbar-none">
              <div className="flex gap-[4px] justify-between">
                {/* 24 columns representing 24 weeks */}
                {Array.from({ length: 24 }).map((_, colIdx) => {
                  return (
                    <div key={colIdx} className="flex flex-col gap-[4px]">
                      {Array.from({ length: 7 }).map((_, rowIdx) => {
                        const daysAgo = (23 - colIdx) * 7 + (6 - rowIdx);
                        const date = new Date();
                        date.setDate(date.getDate() - daysAgo);
                        const dateStr = date.toISOString().split("T")[0];
                        
                        let level = 0;
                        if (daysAgo === 0) {
                          level = recentCommits > 0 ? Math.min(4, recentCommits) : 0;
                        } else {
                          let hash = 0;
                          for (let i = 0; i < dateStr.length; i++) {
                            hash = dateStr.charCodeAt(i) + ((hash << 5) - hash);
                          }
                          const val = Math.abs(hash) % 100;
                          if (val >= 60) {
                            if (val < 82) level = 1;
                            else if (val < 92) level = 2;
                            else if (val < 97) level = 3;
                            else level = 4;
                          }
                        }
                        
                        let colorClass = "bg-white/5 border border-white/2 hover:border-gray-500";
                        if (level === 1) colorClass = "bg-emerald-950/40 border border-emerald-950/20";
                        else if (level === 2) colorClass = "bg-emerald-800/60 border border-emerald-800/30";
                        else if (level === 3) colorClass = "bg-emerald-600/80 border border-emerald-600/40";
                        else if (level === 4) colorClass = "bg-neon-green/90 border border-neon-green/50 shadow-[0_0_8px_rgba(57,255,20,0.35)]";
                        
                        return (
                          <div
                            key={rowIdx}
                            title={`${dateStr}: ${level} autonomous code updates`}
                            className={`w-[15px] h-[15px] rounded-[2px] transition-all duration-200 hover:scale-125 cursor-pointer ${colorClass}`}
                          />
                        );
                      })}
                    </div>
                  );
                })}
              </div>
              
              <div className="flex justify-between items-center text-[9px] text-gray-500 font-mono mt-2.5 px-1">
                <div>Autonomous commit stream: <span className="text-neon-green font-bold">{commits.length} pushed patches</span></div>
                <div className="flex items-center gap-1.5">
                  <span>Less</span>
                  <div className="w-[10px] h-[10px] rounded-[1px] bg-white/5 border border-white/2" />
                  <div className="w-[10px] h-[10px] rounded-[1px] bg-emerald-950/40" />
                  <div className="w-[10px] h-[10px] rounded-[1px] bg-emerald-800/60" />
                  <div className="w-[10px] h-[10px] rounded-[1px] bg-emerald-600/80" />
                  <div className="w-[10px] h-[10px] rounded-[1px] bg-neon-green" />
                  <span>More</span>
                </div>
              </div>
            </div>
          </div>

          {/* Subgrid: Terminals & Issues */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 flex-1 items-stretch">
            
            {/* Live Terminal Commit Feed */}
            <div className="cyber-panel p-5 rounded-xl border border-neon-blue/10 flex flex-col bg-black/45 min-h-[420px] shadow-[0_8px_30px_rgb(0,0,0,0.35)]">
              <div className="flex items-center justify-between mb-4 border-b border-neon-blue/10 pb-2">
                <div className="flex items-center gap-2">
                  <Terminal className="w-4 h-4 text-neon-blue" />
                  <h2 className="text-xs uppercase font-bold tracking-widest text-neon-blue">
                    Live GitLab Terminal Feed
                  </h2>
                </div>
                <span className="text-[9px] text-gray-500 font-mono uppercase">
                  origin/main
                </span>
              </div>
              
              <div className="flex-1 overflow-y-auto pr-1 flex flex-col gap-3 font-mono text-[11px] scrollbar-thin">
                {commits.length === 0 ? (
                  <div className="text-gray-655 italic text-center py-12">// Waiting for coding clicks...</div>
                ) : (
                  commits.map((c: any, idx: number) => (
                    <div key={c.sha || idx} className="p-3 border border-neon-blue/15 bg-black/70 rounded-lg flex flex-col gap-1.5 hover:border-neon-blue/40 transition-all">
                      <div className="flex justify-between items-center text-[10px]">
                        <span className="text-neon-blue font-bold">commit {c.sha}</span>
                        <span className="text-gray-500">{c.time}</span>
                      </div>
                      <div className="text-gray-200 font-medium leading-relaxed">{c.message}</div>
                      <div className="text-[9px] text-gray-500">Author: {c.author}</div>
                      {c.files && c.files.length > 0 && (
                        <div className="text-[9px] text-neon-green/90 mt-1 truncate">
                          Files: {c.files.join(", ")}
                        </div>
                      )}
                    </div>
                  ))
                )}
              </div>
            </div>

            {/* GitLab Workspace Issues */}
            <div className="cyber-panel p-5 rounded-xl border border-neon-blue/10 flex flex-col bg-black/45 min-h-[420px] shadow-[0_8px_30px_rgb(0,0,0,0.35)]">
              <div className="flex items-center gap-2 mb-4 border-b border-neon-blue/10 pb-2">
                <ShieldAlert className="w-4 h-4 text-neon-red" />
                <h2 className="text-xs uppercase font-bold tracking-widest text-neon-red">
                  GitLab Issue Tracker & Discussions
                </h2>
              </div>
              
              {/* Form Injector */}
              <form onSubmit={handleCreateIssue} className="flex flex-col gap-2.5 mb-4 p-3.5 bg-black/60 border border-neon-red/15 rounded-lg shadow-[inset_0_2px_4px_rgba(0,0,0,0.6)]">
                <div className="text-[9px] text-gray-500 font-bold uppercase tracking-wider font-mono">
                  // Inject Issue for Agent Action
                </div>
                <input
                  type="text"
                  placeholder="Issue title (e.g. fix database pool leak)"
                  value={newIssueTitle}
                  onChange={(e) => setNewIssueTitle(e.target.value)}
                  className="w-full p-2 border border-neon-blue/10 bg-black/80 text-xs rounded focus:outline-none focus:border-neon-blue font-mono"
                />
                <textarea
                  placeholder="Provide bug description..."
                  value={newIssueDesc}
                  onChange={(e) => setNewIssueDesc(e.target.value)}
                  rows={2}
                  className="w-full p-2 border border-neon-blue/10 bg-black/80 text-xs rounded focus:outline-none focus:border-neon-blue font-mono resize-none"
                />
                <button
                  type="submit"
                  disabled={isSubmittingIssue || isOffline}
                  className="w-full py-2 bg-neon-red/10 border border-neon-red/30 hover:border-neon-red hover:bg-neon-red/20 text-neon-red font-bold text-xs uppercase tracking-widest rounded transition-all cursor-pointer disabled:opacity-50"
                >
                  {isSubmittingIssue ? "INJECTING..." : "INJECT GITLAB ISSUE"}
                </button>
              </form>

              {/* Issues List */}
              <div className="flex-1 overflow-y-auto pr-1 flex flex-col gap-3 scrollbar-thin">
                {issues.length === 0 ? (
                  <div className="text-gray-600 italic text-xs text-center py-12">// No issues in GitLab history.</div>
                ) : (
                  [...issues].reverse().map((issue: any, idx: number) => {
                    return (
                      <div key={issue.id || idx} className="p-3 bg-black/60 border border-gray-800 rounded-lg flex flex-col gap-2 transition-all hover:border-gray-700">
                        <div className="flex justify-between items-center">
                          <span className="text-xs font-bold text-gray-300">
                            #{issue.id}: {issue.title}
                          </span>
                          <span className={`px-2 py-0.5 rounded text-[8px] font-mono font-bold uppercase tracking-wider ${
                            issue.status === "open"
                              ? "bg-neon-red/10 border border-neon-red/20 text-neon-red animate-pulse"
                              : "bg-neon-green/10 border border-neon-green/20 text-neon-green"
                          }`}>
                            {issue.status}
                          </span>
                        </div>
                        <p className="text-[10px] text-gray-400 font-mono leading-relaxed">{issue.description}</p>
                        {issue.comments && issue.comments.length > 0 && (
                          <div className="mt-1 flex flex-col gap-1.5 border-t border-gray-800/80 pt-2">
                            {issue.comments.map((comment: any, cIdx: number) => (
                              <div key={cIdx} className="text-[9.5px] font-mono bg-neon-blue/5 border-l-2 border-neon-blue p-2 rounded">
                                <span className="text-neon-blue font-bold">{comment.author}</span>: {comment.comment}
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    );
                  })
                )}
              </div>
            </div>

          </div>

        </section>

        {/* Right Section: Controls, Exposure Risk, Cognitive Stream, Sandboxed Feeds (Col-span 5) */}
        <section className="xl:col-span-5 flex flex-col gap-6">
          
          {/* AI Exposure Risk Assessment Gauge */}
          <div className="cyber-panel p-5 rounded-xl border border-neon-blue/10 flex items-center justify-between relative overflow-hidden bg-black/45 shadow-[0_8px_30px_rgba(0,0,0,0.5)]">
            <div className="absolute inset-0 grid-bg opacity-10 pointer-events-none"></div>
            
            <div className="flex flex-col gap-1 z-10">
              <div className="flex items-center gap-1.5">
                <ShieldAlert className={`w-4.5 h-4.5 ${detectionState.detection_risk > 50 ? 'text-neon-red animate-pulse' : 'text-neon-blue'}`} />
                <h2 className="text-xs uppercase font-bold tracking-widest text-gray-300">AI Exposure Risk Assessment</h2>
              </div>
              <div className="text-[9px] text-gray-500 font-mono mt-0.5">
                SUSPICION MATRIX SCANNER
              </div>
              
              <div className="mt-3.5 flex flex-col gap-1">
                {detectionState.behavior_adaptation ? (
                  <div className="text-[10px] text-neon-red font-mono bg-neon-red/10 border border-neon-red/20 px-2.5 py-1 rounded animate-pulse inline-block font-semibold">
                    [WARNING: BEHAVIOR ADAPTATION ACTIVE]
                  </div>
                ) : (
                  <div className="text-[10px] text-neon-green font-mono bg-neon-green/10 border border-neon-green/20 px-2.5 py-1 rounded inline-block font-semibold">
                    [STATUS: IDENTITY LAYER LOCKED]
                  </div>
                )}
                <p className="text-[9px] text-gray-400 mt-1 max-w-[200px] leading-relaxed">
                  {detectionState.behavior_adaptation 
                    ? "Suspicious prompts intercepted. Engine dial settings tuned down to prevent exposure."
                    : "Footprint behaves convincingly human. Pacing model matches client typing logs."}
                </p>
              </div>
            </div>
            
            {/* SVG Ring Gauge */}
            <div className="relative w-28 h-28 flex items-center justify-center z-10">
              <svg className="w-full h-full transform -rotate-90">
                <circle
                  cx="56"
                  cy="56"
                  r="45"
                  stroke="#12121e"
                  strokeWidth="6"
                  fill="transparent"
                />
                <circle
                  cx="56"
                  cy="56"
                  r="45"
                  stroke={
                    detectionState.detection_risk > 60 
                      ? "var(--cyber-neon-red)" 
                      : detectionState.detection_risk > 30 
                      ? "var(--cyber-neon-purple)" 
                      : "var(--cyber-neon-blue)"
                  }
                  strokeWidth="6"
                  fill="transparent"
                  strokeDasharray={282.7}
                  strokeDashoffset={282.7 - (282.7 * detectionState.detection_risk) / 100}
                  className="transition-all duration-1000 ease-out"
                  style={{
                    filter: `drop-shadow(0 0 8px ${
                      detectionState.detection_risk > 60 
                        ? "rgba(255,0,85,0.7)" 
                        : detectionState.detection_risk > 30 
                        ? "rgba(189,0,255,0.7)" 
                        : "rgba(0,240,255,0.7)"
                    })`
                  }}
                />
              </svg>
              
              <div className="absolute flex flex-col items-center">
                <span className={`text-xl font-black font-mono tracking-tighter ${
                  detectionState.detection_risk > 60 ? 'text-neon-red' : detectionState.detection_risk > 30 ? 'text-neon-purple' : 'text-neon-blue'
                }`}>
                  {detectionState.detection_risk}%
                </span>
                <span className="text-[7px] text-gray-500 font-mono tracking-wider uppercase">SUSPICION</span>
              </div>
            </div>
          </div>

          {/* Active Cognitive Stream Log Feed */}
          <div className="cyber-panel p-5 rounded-xl border border-neon-blue/10 flex flex-col bg-black/45 min-h-[350px] shadow-[0_8px_30px_rgb(0,0,0,0.4)]">
            <div className="flex items-center gap-2 mb-4 border-b border-neon-blue/10 pb-2">
              <Terminal className="w-4 h-4 text-neon-blue" />
              <h2 className="text-xs uppercase font-bold tracking-widest text-neon-blue">Cognitive Stream</h2>
            </div>
            
            <div ref={logsContainerRef} className="flex-1 overflow-y-auto pr-1.5 flex flex-col gap-2.5 font-mono text-[11px] leading-relaxed scrollbar-thin">
              {logs.length === 0 ? (
                <div className="text-gray-500 italic">// Awaiting engine triggers...</div>
              ) : (
                logs.map((log: any, idx) => {
                  let badgeColor = "text-neon-blue border-neon-blue/20 bg-neon-blue/5";
                  let messageColor = "text-gray-300";
                  
                  if (log.step_type === "system") {
                    badgeColor = "text-neon-purple border-neon-purple/20 bg-neon-purple/5";
                    messageColor = "text-neon-purple/80 font-semibold";
                  } else if (log.step_type === "critique") {
                    badgeColor = "text-neon-red border-neon-red/20 bg-neon-red/5";
                    messageColor = "text-orange-400";
                  } else if (log.step_type === "action") {
                    badgeColor = "text-neon-green border-neon-green/20 bg-neon-green/5";
                    messageColor = "text-neon-green/90";
                  }

                  return (
                    <div key={log._id || idx} className="border-l border-gray-800 pl-3 py-0.5 flex flex-col gap-1">
                      <div className="flex items-center gap-2 text-[9px]">
                        <span className="text-gray-500">[{new Date(log.timestamp * 1000).toLocaleTimeString()}]</span>
                        <span className={`px-1.5 py-0.2 border rounded ${badgeColor} uppercase tracking-wider text-[8px]`}>
                          {log.agent_id} // {log.step_type}
                        </span>
                      </div>
                      <div className={messageColor}>{log.message}</div>
                      {log.critique && (
                        <div className="text-[10px] text-red-400 bg-neon-red/5 border-l border-neon-red p-1 mt-1 font-mono italic">
                          &gt; Critique loop: {log.critique}
                        </div>
                      )}
                    </div>
                  );
                })
              )}
            </div>
          </div>

          {/* Tabbed Mocks & Sandbox Feeds */}
          <div className="cyber-panel rounded-xl border border-neon-blue/10 flex flex-col bg-black/45 min-h-[380px] shadow-[0_8px_30px_rgb(0,0,0,0.4)]">
            
            {/* Tabs Header */}
            <div className="flex border-b border-neon-blue/10 bg-black/40 rounded-t-xl overflow-hidden">
              <button
                onClick={() => setCurrentTab("slack")}
                className={`flex-1 py-3 text-[10px] uppercase tracking-wider font-bold font-mono border-r border-neon-blue/10 flex items-center justify-center gap-1 cursor-pointer transition-all duration-150 ${
                  currentTab === "slack" ? "text-neon-blue bg-[#030303] shadow-[inset_0_-2px_0_var(--cyber-neon-blue)]" : "text-gray-500 hover:text-gray-300"
                }`}
              >
                <MessageSquare className="w-3 h-3" />
                Slack Channels
              </button>
              <button
                onClick={() => setCurrentTab("email")}
                className={`flex-1 py-3 text-[10px] uppercase tracking-wider font-bold font-mono border-r border-neon-blue/10 flex items-center justify-center gap-1 cursor-pointer transition-all duration-150 ${
                  currentTab === "email" ? "text-neon-blue bg-[#030303] shadow-[inset_0_-2px_0_var(--cyber-neon-blue)]" : "text-gray-500 hover:text-gray-300"
                }`}
              >
                <Mail className="w-3 h-3" />
                Email Inbox
              </button>
              <button
                onClick={() => setCurrentTab("linkedin")}
                className={`flex-1 py-3 text-[10px] uppercase tracking-wider font-bold font-mono border-r border-neon-blue/10 flex items-center justify-center gap-1 cursor-pointer transition-all duration-150 ${
                  currentTab === "linkedin" ? "text-neon-blue bg-[#030303] shadow-[inset_0_-2px_0_var(--cyber-neon-blue)]" : "text-gray-500 hover:text-gray-300"
                }`}
              >
                <svg className="w-3 h-3 fill-current" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0z"/>
                </svg>
                LinkedIn DMs
              </button>
              <button
                onClick={() => setCurrentTab("chat")}
                className={`flex-1 py-3 text-[10px] uppercase tracking-wider font-bold font-mono flex items-center justify-center gap-1 cursor-pointer transition-all duration-150 ${
                  currentTab === "chat" ? "text-neon-blue bg-[#030303] shadow-[inset_0_-2px_0_var(--cyber-neon-blue)]" : "text-gray-500 hover:text-gray-300"
                }`}
              >
                <Cpu className="w-3 h-3" />
                Doppelgänger Chat
              </button>
            </div>

            {/* Tab content panels */}
            <div className="p-4 flex-1 flex flex-col overflow-hidden max-h-[380px]">
              
              {/* Slack channels */}
              {currentTab === "slack" && (
                <div className="flex-1 flex flex-col overflow-hidden">
                  <div className="flex gap-2 mb-3 bg-black/60 p-1 rounded-lg border border-neon-blue/5">
                    <button
                      onClick={() => setSlackChannel("#dev-team")}
                      className={`px-3 py-1 text-[10px] font-mono rounded cursor-pointer ${
                        slackChannel === "#dev-team" ? "bg-neon-blue/15 text-neon-blue border border-neon-blue/20" : "text-gray-500 hover:text-gray-300"
                      }`}
                    >
                      #dev-team
                    </button>
                    <button
                      onClick={() => setSlackChannel("#general")}
                      className={`px-3 py-1 text-[10px] font-mono rounded cursor-pointer ${
                        slackChannel === "#general" ? "bg-neon-blue/15 text-neon-blue border border-neon-blue/20" : "text-gray-500 hover:text-gray-300"
                      }`}
                    >
                      #general
                    </button>
                  </div>

                  <div ref={slackContainerRef} className="flex-1 overflow-y-auto pr-1 flex flex-col gap-3 scrollbar-thin">
                    {filteredSlack.length === 0 ? (
                      <div className="text-gray-600 italic text-xs font-mono">// Channel feed is empty.</div>
                    ) : (
                      filteredSlack.map((m: any, idx: number) => (
                        <div 
                          key={idx} 
                          className={`p-2.5 rounded-lg border text-xs max-w-[85%] ${
                            m.is_agent 
                              ? "bg-neon-blue/5 border-neon-blue/20 self-end text-right" 
                              : "bg-black/40 border-gray-805 self-start text-left"
                          }`}
                        >
                          <div className="flex items-center gap-1.5 mb-1 text-[9px] text-gray-500 justify-start">
                            <span className={`font-bold ${m.is_agent ? "text-neon-blue" : "text-gray-400"}`}>
                              {m.sender}
                            </span>
                            <span>•</span>
                            <span>{new Date(m.timestamp * 1000).toLocaleTimeString()}</span>
                          </div>
                          <div className="text-gray-300 whitespace-pre-wrap">{m.message}</div>
                        </div>
                      ))
                    )}
                  </div>
                </div>
              )}

              {/* Email Inbox */}
              {currentTab === "email" && (
                <div className="flex-1 flex flex-col md:grid md:grid-cols-12 gap-3 overflow-hidden">
                  
                  <div className="col-span-5 border-r border-neon-blue/5 flex flex-col gap-2 overflow-y-auto max-h-72 pr-1 scrollbar-thin">
                    {feeds.email?.map((e: any) => (
                      <button
                        key={e.id}
                        onClick={() => setSelectedEmail(e)}
                        className={`p-2 rounded text-left flex flex-col gap-1 border cursor-pointer transition-all ${
                          selectedEmail?.id === e.id 
                            ? "bg-neon-blue/10 border-neon-blue/30" 
                            : "bg-black/30 border-gray-850 hover:bg-black/60"
                        }`}
                      >
                        <div className="flex justify-between items-center text-[9px]">
                          <span className={`truncate w-24 font-bold ${!e.read ? "text-neon-blue" : "text-gray-400"}`}>
                            {e.sender.split("@")[0]}
                          </span>
                          {!e.read && <span className="w-1.5 h-1.5 rounded-full bg-neon-blue animate-pulse"></span>}
                        </div>
                        <div className="text-[10px] font-semibold truncate text-gray-200">{e.subject}</div>
                      </button>
                    ))}
                  </div>

                  <div className="col-span-7 flex flex-col bg-black/40 rounded p-2.5 border border-neon-blue/5 overflow-y-auto max-h-72 scrollbar-thin">
                    {selectedEmail ? (
                      <div className="text-xs flex flex-col gap-3 font-mono">
                        <div className="border-b border-gray-800/80 pb-2 flex flex-col gap-1 text-[10px] text-gray-500">
                          <div>From: {selectedEmail.sender}</div>
                          <div className="text-gray-300 font-bold">Subject: {selectedEmail.subject}</div>
                        </div>
                        
                        <div className="text-gray-400 leading-relaxed text-[11px]">
                          {selectedEmail.body}
                        </div>

                        {selectedEmail.replied ? (
                          <div className="bg-neon-green/5 border-l-2 border-neon-green p-2.5 mt-2 rounded">
                            <div className="text-[9px] text-neon-green font-bold mb-1 uppercase tracking-wider flex items-center gap-1">
                              <CheckCircle2 className="w-3 h-3" />
                              Replied by Doppelgänger
                            </div>
                            <div className="text-[10px] text-gray-300 leading-relaxed whitespace-pre-wrap">
                              {selectedEmail.reply_body}
                            </div>
                          </div>
                        ) : (
                          <div className="text-[10px] text-orange-400 italic mt-3 flex items-center gap-1.5">
                            <span className="w-1.5 h-1.5 rounded-full bg-orange-400 animate-ping"></span>
                            Awaiting engine trigger cycle...
                          </div>
                        )}
                      </div>
                    ) : (
                      <div className="text-gray-655 italic text-xs justify-center items-center h-full flex font-mono">// Select email to inspect.</div>
                    )}
                  </div>

                </div>
              )}

              {/* LinkedIn DMs */}
              {currentTab === "linkedin" && (
                <div className="flex-1 overflow-y-auto pr-1 flex flex-col gap-4 scrollbar-thin">
                  {feeds.linkedin?.length === 0 ? (
                    <div className="text-gray-655 italic text-xs font-mono">// LinkedIn feed is empty.</div>
                  ) : (
                    feeds.linkedin?.map((l: any, idx: number) => (
                      <div key={l.id || idx} className="p-3 bg-black/40 border border-gray-850 rounded-lg flex flex-col gap-2.5">
                        
                        <div className="flex items-center gap-2">
                          <img 
                            src={l.avatar} 
                            alt={l.sender} 
                            className="w-7 h-7 rounded-full border border-neon-purple/20 object-cover" 
                          />
                          <div className="text-xs">
                            <div className="font-bold text-gray-200">{l.sender}</div>
                            <div className="text-[9px] text-gray-500">Recruiter DM</div>
                          </div>
                        </div>

                        <div className="text-xs text-gray-300 pl-9 font-mono leading-relaxed">
                          {l.message}
                        </div>

                        {l.replied ? (
                          <div className="pl-9 mt-1">
                            <div className="bg-neon-purple/5 border-l-2 border-neon-purple p-2.5 rounded text-xs font-mono">
                              <div className="text-[9px] text-neon-purple font-bold mb-1 uppercase tracking-wider">
                                Doppelgänger reply
                              </div>
                              <div className="text-gray-300 leading-relaxed whitespace-pre-wrap">
                                {l.reply_text}
                              </div>
                            </div>
                          </div>
                        ) : (
                          <div className="pl-9 text-[10px] text-orange-400 italic flex items-center gap-1.5">
                            <span className="w-1.5 h-1.5 rounded-full bg-orange-400 animate-ping"></span>
                            Generating doppelgänger response...
                          </div>
                        )}

                      </div>
                    ))
                  )}
                </div>
              )}

              {/* Doppelgänger Chat */}
              {currentTab === "chat" && (
                <div className="flex-1 flex flex-col overflow-hidden justify-between">
                  
                  <div ref={chatContainerRef} className="flex-1 overflow-y-auto pr-1 flex flex-col gap-3 scrollbar-thin">
                    {feeds.chat?.length === 0 ? (
                      <div className="text-gray-650 italic text-xs font-mono">// Conversation logs empty.</div>
                    ) : (
                      feeds.chat?.map((c: any, idx: number) => (
                        <div 
                          key={idx} 
                          className={`p-2.5 rounded-lg border text-xs max-w-[85%] ${
                            c.is_agent 
                              ? "bg-neon-blue/5 border-neon-blue/20 self-end text-right animate-fade-in" 
                              : "bg-black/40 border-gray-805 self-start text-left"
                          }`}
                        >
                          <div className="flex items-center gap-1.5 mb-1 text-[9px] text-gray-500 justify-start">
                            <span className="font-bold text-neon-blue">
                              {c.sender}
                            </span>
                            <span>•</span>
                            <span>{new Date(c.timestamp * 1000).toLocaleTimeString()}</span>
                          </div>
                          <div className="text-gray-300 whitespace-pre-wrap">{c.message}</div>
                        </div>
                      ))
                    )}
                  </div>

                  <form onSubmit={handleSendDirectChat} className="flex gap-2 mt-3 pt-2.5 border-t border-neon-blue/10">
                    <input
                      type="text"
                      placeholder="Ask the Doppelgänger anything (test for AI suspicion)..."
                      value={directChatMessage}
                      onChange={(e) => setDirectChatMessage(e.target.value)}
                      disabled={isSendingChat || isOffline}
                      className="flex-1 p-2 border border-neon-blue/10 bg-black/60 text-xs rounded focus:outline-none focus:border-neon-blue font-mono"
                    />
                    <button
                      type="submit"
                      disabled={isSendingChat || isOffline}
                      className="px-4 bg-neon-blue/15 border border-neon-blue/30 hover:border-neon-blue hover:bg-neon-blue/25 text-neon-blue rounded flex items-center justify-center cursor-pointer transition-all disabled:opacity-50"
                    >
                      <Send className="w-3.5 h-3.5" />
                    </button>
                  </form>

                </div>
              )}

            </div>
          </div>

        </section>

      </div>
      
      {/* Sliding Drawer for Identity Control Center */}
      <AnimatePresence>
        {showIdentitySettings && (
          <>
            {/* Drawer Backdrop Overlay */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 0.6 }}
              exit={{ opacity: 0 }}
              onClick={() => setShowIdentitySettings(false)}
              className="fixed inset-0 bg-black/80 z-40 backdrop-blur-sm"
            />
            
            {/* Drawer Panel */}
            <motion.div
              initial={{ x: "100%" }}
              animate={{ x: 0 }}
              exit={{ x: "100%" }}
              transition={{ type: "tween", duration: 0.3 }}
              className="fixed top-0 right-0 h-full w-full sm:w-96 bg-[#060608]/95 border-l border-neon-blue/25 z-50 p-6 overflow-y-auto flex flex-col gap-6 shadow-[0_0_50px_rgba(0,240,255,0.2)] font-sans"
            >
              <div className="flex items-center justify-between border-b border-neon-blue/25 pb-3">
                <div className="flex items-center gap-2">
                  <User className="w-5 h-5 text-neon-blue" />
                  <h2 className="text-sm font-black uppercase tracking-wider text-neon-blue">
                    Identity Control Center
                  </h2>
                </div>
                <button
                  onClick={() => setShowIdentitySettings(false)}
                  className="text-gray-400 hover:text-white font-mono text-xs uppercase cursor-pointer"
                >
                  [CLOSE]
                </button>
              </div>

              {/* Sliders description */}
              <p className="text-xs text-gray-400 leading-relaxed italic">
                &quot;{personality.description}&quot;
              </p>

              {/* Sliders matrix details */}
              <div className="flex flex-col gap-4">
                <div className="text-[10px] text-gray-500 font-bold uppercase tracking-wider font-mono">
                  // Persona Matrix Sliders
                </div>
                
                <div className="flex flex-col gap-1">
                  <div className="flex justify-between text-[11px] font-mono">
                    <span className="text-neon-green font-semibold">Empathy Matrix</span>
                    <span className="text-gray-400">{personality.sliders.empathy}%</span>
                  </div>
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={personality.sliders.empathy}
                    onChange={(e) => handleSliderChange("empathy", parseInt(e.target.value))}
                    className="w-full accent-neon-green h-1 bg-black rounded"
                  />
                </div>

                <div className="flex flex-col gap-1">
                  <div className="flex justify-between text-[11px] font-mono">
                    <span className="text-neon-red font-semibold">Urgency Rate</span>
                    <span className="text-gray-400">{personality.sliders.urgency}%</span>
                  </div>
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={personality.sliders.urgency}
                    onChange={(e) => handleSliderChange("urgency", parseInt(e.target.value))}
                    className="w-full accent-neon-red h-1 bg-black rounded"
                  />
                </div>

                <div className="flex flex-col gap-1">
                  <div className="flex justify-between text-[11px] font-mono">
                    <span className="text-neon-blue font-semibold">Formality Vector</span>
                    <span className="text-gray-400">{personality.sliders.formality}%</span>
                  </div>
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={personality.sliders.formality}
                    onChange={(e) => handleSliderChange("formality", parseInt(e.target.value))}
                    className="w-full accent-neon-blue h-1 bg-black rounded"
                  />
                </div>

                <div className="flex flex-col gap-1">
                  <div className="flex justify-between text-[11px] font-mono">
                    <span className="text-neon-purple font-semibold">Sarcasm Modulator</span>
                    <span className="text-gray-400">{personality.sliders.sarcasm}%</span>
                  </div>
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={personality.sliders.sarcasm}
                    onChange={(e) => handleSliderChange("sarcasm", parseInt(e.target.value))}
                    className="w-full accent-neon-purple h-1 bg-black rounded"
                  />
                </div>

                <div className="flex flex-col gap-1">
                  <div className="flex justify-between text-[11px] font-mono">
                    <span className="text-pink-400 font-semibold">Human Typo Rate (HIE)</span>
                    <span className="text-gray-400">{personality.sliders.typos || 0}%</span>
                  </div>
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={personality.sliders.typos || 0}
                    onChange={(e) => handleSliderChange("typos", parseInt(e.target.value))}
                    className="w-full accent-pink-400 h-1 bg-black rounded animate-pulse"
                  />
                </div>
              </div>

              {/* GitLab connection config form */}
              <form 
                onSubmit={handleSaveIdentitySettings}
                className="flex flex-col gap-4 mt-2 bg-black/60 border border-neon-blue/10 p-4 rounded-lg shadow-[inset_0_2px_4px_rgba(0,0,0,0.6)]"
              >
                <div className="text-[10px] text-gray-500 font-bold uppercase tracking-wider font-mono">
                  // Connection Configurations
                </div>

                <div className="flex flex-col gap-1.5">
                  <span className="text-[8px] text-gray-400 font-mono">IDENTITY CONTINUITY MODE</span>
                  <select
                    value={identityMode}
                    onChange={(e) => setIdentityMode(e.target.value)}
                    className="w-full p-2 border border-neon-blue/15 bg-black/85 text-xs rounded text-gray-200 focus:outline-none focus:border-neon-blue font-mono"
                  >
                    <option value="sandbox">Synthetic Presence Sandbox</option>
                    <option value="continuity">Identity Continuity Mode (Real GitLab)</option>
                  </select>
                </div>

                <div className="flex flex-col gap-1.5">
                  <span className="text-[8px] text-gray-400 font-mono">GITLAB HOST</span>
                  <input
                    type="text"
                    value={gitlabHost}
                    onChange={(e) => setGitlabHost(e.target.value)}
                    placeholder="gitlab.com"
                    className="w-full p-2 border border-neon-blue/15 bg-black/85 text-xs rounded text-gray-250 focus:outline-none focus:border-neon-blue font-mono"
                  />
                </div>

                <div className="flex flex-col gap-1.5">
                  <span className="text-[8px] text-gray-400 font-mono">GITLAB USERNAME</span>
                  <input
                    type="text"
                    value={gitlabUsername}
                    onChange={(e) => setGitlabUsername(e.target.value)}
                    placeholder="username"
                    className="w-full p-2 border border-neon-blue/15 bg-black/85 text-xs rounded text-gray-250 focus:outline-none focus:border-neon-blue font-mono"
                  />
                </div>

                <div className="flex flex-col gap-1.5">
                  <span className="text-[8px] text-gray-400 font-mono">REPOSITORY PATH</span>
                  <input
                    type="text"
                    value={gitlabRepo}
                    onChange={(e) => setGitlabRepo(e.target.value)}
                    placeholder="username/repository-slug"
                    className="w-full p-2 border border-neon-blue/15 bg-black/85 text-xs rounded text-gray-250 focus:outline-none focus:border-neon-blue font-mono"
                  />
                </div>

                <div className="flex flex-col gap-1.5">
                  <span className="text-[8px] text-gray-400 font-mono">GITLAB ACCESS TOKEN (PAT)</span>
                  <div className="relative">
                    <input
                      type={showPat ? "text" : "password"}
                      value={gitlabPat}
                      onChange={(e) => setGitlabPat(e.target.value)}
                      placeholder="glpat-..."
                      className="w-full p-2 pr-10 border border-neon-blue/15 bg-black/85 text-xs rounded text-gray-200 focus:outline-none focus:border-neon-blue font-mono"
                    />
                    <button
                      type="button"
                      onClick={() => setShowPat(!showPat)}
                      className="absolute right-2 top-2.5 text-gray-500 hover:text-gray-300 text-[9px] font-mono cursor-pointer"
                    >
                      {showPat ? "HIDE" : "SHOW"}
                    </button>
                  </div>
                </div>

                <div className="flex flex-col gap-1.5">
                  <span className="text-[8px] text-gray-400 font-mono">GEMINI API KEY</span>
                  <div className="relative">
                    <input
                      type={showGeminiKey ? "text" : "password"}
                      value={geminiApiKey}
                      onChange={(e) => setGeminiApiKey(e.target.value)}
                      placeholder="AIzaSy..."
                      className="w-full p-2 pr-10 border border-neon-blue/15 bg-black/85 text-xs rounded text-gray-200 focus:outline-none focus:border-neon-blue font-mono"
                    />
                    <button
                      type="button"
                      onClick={() => setShowGeminiKey(!showGeminiKey)}
                      className="absolute right-2 top-2.5 text-gray-500 hover:text-gray-300 text-[9px] font-mono cursor-pointer"
                    >
                      {showGeminiKey ? "HIDE" : "SHOW"}
                    </button>
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={isSavingIdentity || isOffline}
                  className="w-full mt-2 py-2.5 bg-neon-blue/15 border border-neon-blue/30 hover:border-neon-blue hover:bg-neon-blue/20 text-neon-blue font-bold text-xs uppercase tracking-widest rounded transition-all cursor-pointer disabled:opacity-50"
                >
                  {isSavingIdentity ? "SAVING..." : "SAVE CONNECTION DETAILS"}
                </button>
              </form>

              <div className="p-2.5 bg-neon-blue/5 border border-neon-blue/10 rounded-lg text-[9px] text-gray-500 font-mono flex flex-col gap-0.5">
                <div>// STYLE MAPPING VECTOR:</div>
                <div className="text-neon-blue">
                  E{personality.sliders.empathy}::U{personality.sliders.urgency}::F{personality.sliders.formality}::S{personality.sliders.sarcasm}::T{personality.sliders.typos || 0}
                </div>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>

      {/* Visual Sandbox File Status footer */}
      <footer className="mt-6 p-4.5 border border-neon-blue/15 bg-black/40 rounded-xl flex flex-col md:flex-row justify-between items-center text-[10px] font-mono text-gray-500 gap-2.5">
        <div>
          // LOCAL SYNTHETIC SANDBOX ROOT: <span className="text-neon-blue">git-sandbox/</span>
        </div>
        <div className="flex items-center gap-3">
          <span>Active Issues: <span className="text-neon-red">{issues.filter(i=>i.status==="open").length} open</span> / <span className="text-neon-green">{issues.filter(i=>i.status==="closed").length} resolved</span></span>
          <span>•</span>
          <span>Commits History: <span className="text-neon-blue">{commits.length} pushed patches</span></span>
        </div>
      </footer>
    </div>
  );
}
