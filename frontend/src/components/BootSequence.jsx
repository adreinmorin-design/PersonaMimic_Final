import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Terminal, Shield, Cpu, Activity, Database, Zap } from 'lucide-react';
import { api } from '../lib/api';

const BootSequence = ({ onComplete }) => {
  const [logs, setLogs] = useState([]);
  const [progress, setProgress] = useState(0);
  const [complete, setComplete] = useState(false);
  const [intelligence, setIntelligence] = useState(null);

  const bootSteps = [
    { id: 'auth', label: 'Verifying Neural Gateway Security...', icon: Shield, delay: 800 },
    { id: 'db', label: 'Synchronizing Forensic Database...', icon: Database, delay: 1200 },
    { id: 'redis', label: 'Initializing High-Speed Cache...', icon: Zap, delay: 1000 },
    { id: 'swarm', label: 'Enumerating Swarm Nodes...', icon: Cpu, delay: 1500 },
    { id: 'intel', label: 'Assessing Core Intelligence Tier...', icon: Activity, delay: 1200 },
  ];

  useEffect(() => {
    let currentStep = 0;
    
    const runStep = async () => {
      if (currentStep >= bootSteps.length) {
        setComplete(true);
        setTimeout(onComplete, 1000);
        return;
      }

      const step = bootSteps[currentStep];
      setLogs(prev => [...prev, { ...step, status: 'processing', timestamp: new Date().toLocaleTimeString() }]);

      // Artificial Delay + Real API Check
      await new Promise(r => setTimeout(r, step.delay));

      try {
        if (step.id === 'intel') {
          const res = await api.get('/system/intelligence');
          setIntelligence(res.data);
          setLogs(prev => prev.map(l => l.id === step.id ? { ...l, status: 'success', detail: `Tier ${res.data.tier}: ${res.data.assessment}` } : l));
        } else if (step.id === 'db' || step.id === 'redis') {
          const res = await api.get('/system/health');
          const status = res.data[step.id === 'db' ? 'database' : 'redis'];
          setLogs(prev => prev.map(l => l.id === step.id ? { ...l, status: status === 'online' ? 'success' : 'warning', detail: status.toUpperCase() } : l));
        } else {
          setLogs(prev => prev.map(l => l.id === step.id ? { ...l, status: 'success' } : l));
        }
      } catch (err) {
          setLogs(prev => prev.map(l => l.id === step.id ? { ...l, status: 'error', detail: 'TIMEOUT' } : l));
      }

      setProgress(((currentStep + 1) / bootSteps.length) * 100);
      currentStep++;
      runStep();
    };

    runStep();
  }, []);

  return (
    <div className="fixed inset-0 z-[100] bg-[#020617] flex flex-col items-center justify-center p-8 overflow-hidden">
      {/* Background Ambience */}
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,rgba(14,165,233,0.05)_0%,transparent_70%)]"></div>
      
      <div className="w-full max-w-2xl relative z-10">
        <div className="flex items-center gap-4 mb-8">
          <div className="p-3 bg-cyan-500/10 border border-cyan-500/20 rounded-xl">
            <Terminal className="text-cyan-400 animate-pulse" size={24} />
          </div>
          <div>
            <h1 className="text-xl font-black tracking-[0.3em] uppercase text-white/90">System Initialization</h1>
            <p className="text-[10px] font-mono text-cyan-500/50 uppercase tracking-widest mt-1">PersonaMimic Neutral Flow v2.4.0</p>
          </div>
        </div>

        <div className="glass-panel p-6 border-white/5 space-y-4 mb-8 h-80 overflow-y-auto no-scrollbar scroll-smooth">
          <AnimatePresence>
            {logs.map((log, idx) => (
              <motion.div 
                key={idx}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                className="flex items-start gap-4 text-[11px] font-mono"
              >
                <div className={`mt-0.5 p-1 rounded-sm ${
                  log.status === 'success' ? 'bg-green-500/10 text-green-400' : 
                  log.status === 'error' ? 'bg-red-500/10 text-red-400' :
                  log.status === 'warning' ? 'bg-amber-500/10 text-amber-400' :
                  'bg-white/5 text-white/40'
                }`}>
                  <log.icon size={12} />
                </div>
                <div className="flex-1">
                  <div className="flex justify-between items-center">
                    <span className={log.status === 'processing' ? 'text-cyan-400 animate-pulse' : 'text-white/70'}>
                      {log.label}
                    </span>
                    <span className="text-white/20 text-[9px]">{log.timestamp}</span>
                  </div>
                  {log.detail && (
                    <motion.div 
                      initial={{ opacity: 0 }} 
                      animate={{ opacity: 1 }}
                      className={`mt-1 text-[9px] font-bold uppercase tracking-tighter ${
                        log.status === 'warning' ? 'text-amber-500/70' : 'text-cyan-500/70'
                      }`}
                    >
                      {'>'} {log.detail}
                    </motion.div>
                  )}
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
          {complete && (
             <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="mt-6 pt-4 border-t border-white/5 text-center"
             >
                <span className="text-[10px] font-black text-green-400 tracking-[0.5em] uppercase animate-pulse">
                    Access Granted
                </span>
             </motion.div>
          )}
        </div>

        <div className="space-y-2">
           <div className="flex justify-between text-[10px] font-black text-white/30 uppercase tracking-widest">
              <span>Overall Link Stability</span>
              <span>{Math.round(progress)}%</span>
           </div>
           <div className="h-1 bg-white/5 rounded-full overflow-hidden">
              <motion.div 
                className="h-full bg-gradient-to-r from-blue-600 to-cyan-400 shadow-[0_0_10px_rgba(14,165,233,0.5)]"
                animate={{ width: `${progress}%` }}
                transition={{ duration: 0.5 }}
              />
           </div>
        </div>
      </div>

      <div className="fixed bottom-8 left-0 right-0 text-center opacity-20 pointer-events-none">
        <span className="text-[10px] font-mono uppercase tracking-[0.8em]">Neural Core: {intelligence?.tier || '0'} // Authorized Session</span>
      </div>
    </div>
  );
};

export default BootSequence;
