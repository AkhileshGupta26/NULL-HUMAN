"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { Shield, Server, Terminal, Radio } from "lucide-react";

export default function Home() {
  const router = useRouter();
  const [mounted, setMounted] = useState(false);
  const [bootLog, setBootLog] = useState<string[]>([]);
  const [isBooting, setIsBooting] = useState(false);

  const logs = [
    "Loading memory vectors...",
    "Synchronizing GitLab repository profile...",
    "Profiling communication syntax patterns (Formality: 80%)...",
    "Persona model loaded. Emulating response cadence...",
    "Activating sub-agent orchestration threads...",
    "Main Agent: ONLINE",
    "Coding Agent: ONLINE",
    "Social Agent: ONLINE",
    "Scheduler Agent: ONLINE",
    "Reputation Agent: ONLINE",
    "NULL//HUMAN is ready for autonomous hand-off."
  ];

  useEffect(() => {
    setMounted(true);
  }, []);

  const handleActivate = () => {
    setIsBooting(true);
    let index = 0;
    const interval = setInterval(() => {
      if (index < logs.length) {
        setBootLog((prev) => [...prev, logs[index]]);
        index++;
      } else {
        clearInterval(interval);
        setTimeout(() => {
          router.push("/dashboard");
        }, 1200);
      }
    }, 250);
  };

  if (!mounted) return null;

  return (
    <div className="min-h-screen flex flex-col justify-center items-center px-4 relative overflow-hidden bg-black text-white font-sans selection:bg-neon-blue selection:text-black">
      {/* Background neon glows */}
      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-neon-blue/10 rounded-full blur-[120px] pointer-events-none" />
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-neon-purple/10 rounded-full blur-[120px] pointer-events-none" />

      <div className="max-w-4xl w-full z-10 flex flex-col items-center text-center">
        
        {/* Logo/Tag */}
        <motion.div 
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="flex items-center gap-2 px-3 py-1.5 border border-neon-blue/30 bg-neon-blue/5 rounded-full mb-8"
        >
          <Radio className="w-4 h-4 text-neon-blue animate-pulse" />
          <span className="text-xs uppercase tracking-[0.2em] text-neon-blue font-semibold">NULL//HUMAN V1.0.0</span>
        </motion.div>

        {/* Title */}
        <motion.h1 
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.8, delay: 0.1 }}
          className="text-5xl md:text-7xl font-extrabold uppercase tracking-tight mb-4"
        >
          What if you <br className="md:hidden"/>
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-neon-blue via-neon-purple to-neon-red neon-text-blue">
            disappeared
          </span> tomorrow?
        </motion.h1>

        {/* Subtitle */}
        <motion.h2 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.8, delay: 0.3 }}
          className="text-xl md:text-2xl font-light text-gray-400 tracking-wide mb-8 max-w-2xl"
        >
          “Your online identity won&apos;t. Your AI is ready.”
        </motion.h2>

        {/* Bullet description */}
        <motion.div 
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.4 }}
          className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-12 max-w-3xl w-full text-left"
        >
          <div className="p-5 cyber-panel rounded-lg border border-neon-blue/10 flex flex-col gap-3">
            <Shield className="w-6 h-6 text-neon-blue" />
            <h3 className="text-sm font-semibold uppercase tracking-wider text-neon-blue">Autonomous Replication</h3>
            <p className="text-xs text-gray-400 leading-relaxed">It mimics your tone, response speed, and behavioral cadence across communication nodes.</p>
          </div>
          <div className="p-5 cyber-panel rounded-lg border border-neon-purple/10 flex flex-col gap-3">
            <Server className="w-6 h-6 text-neon-purple" />
            <h3 className="text-sm font-semibold uppercase tracking-wider text-neon-purple">GitLab Autonomy</h3>
            <p className="text-xs text-gray-400 leading-relaxed">Automatically solves workspace tickets, generates pull requests, and commits real code.</p>
          </div>
          <div className="p-5 cyber-panel rounded-lg border border-neon-red/10 flex flex-col gap-3">
            <Terminal className="w-6 h-6 text-neon-red" />
            <h3 className="text-sm font-semibold uppercase tracking-wider text-neon-red">Reflection Cycles</h3>
            <p className="text-xs text-gray-400 leading-relaxed">The agent analyzes its own outputs, critiquing grammar, mood alignment, and logic before publishing.</p>
          </div>
        </motion.div>

        {/* Control Button Area */}
        <div className="h-44 w-full flex flex-col items-center justify-start">
          <AnimatePresence mode="wait">
            {!isBooting ? (
              <motion.button
                key="activate-btn"
                exit={{ opacity: 0, scale: 0.9 }}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.98 }}
                onClick={handleActivate}
                className="relative px-8 py-4 bg-transparent border-2 border-neon-blue text-neon-blue uppercase tracking-widest text-sm font-bold rounded-lg cursor-pointer overflow-hidden transition-all duration-300 hover:bg-neon-blue hover:text-black hover:shadow-[0_0_30px_rgba(0,240,255,0.6)]"
              >
                Activate Doppelgänger Mode
              </motion.button>
            ) : (
              <motion.div
                key="booting-log"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="w-full max-w-lg p-4 rounded-lg bg-black border border-neon-blue/30 font-mono text-left text-xs leading-relaxed max-h-40 overflow-y-auto scrollbar-thin shadow-[0_0_20px_rgba(0,240,255,0.15)]"
              >
                <div className="flex items-center gap-2 text-neon-blue mb-2 animate-pulse">
                  <span className="inline-block w-2 h-2 rounded-full bg-neon-blue"></span>
                  <span>BOOTING REPLICATION INSTANCE...</span>
                </div>
                {bootLog.map((log, idx) => (
                  <div key={idx} className="text-gray-400">
                    <span className="text-neon-purple">&gt; </span>
                    {log}
                  </div>
                ))}
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Small disclaimer */}
        <motion.p 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.8, delay: 0.6 }}
          className="text-[10px] uppercase tracking-widest text-gray-600 mt-8"
        >
          Warning: This creates a fully active digital signature. Nobody will notice you left.
        </motion.p>

      </div>
    </div>
  );
}
