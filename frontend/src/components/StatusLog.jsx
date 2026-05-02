import { useEffect, useRef, useState } from 'react';
import { Scroll, Lock, Unlock } from 'lucide-react';

const StatusLog = ({ logs }) => {
  const logEndRef = useRef(null);
  const containerRef = useRef(null);
  const [autoScroll, setAutoScroll] = useState(true);

  // Auto-scroll logic: only scroll if enabled and ref is valid
  useEffect(() => {
    if (autoScroll && containerRef.current instanceof Element) {
      try {
        containerRef.current.scrollTop = containerRef.current.scrollHeight;
      } catch (e) {
        console.warn("[SCROLL-ERROR] Failed to scroll telemetry:", e);
      }
    }
  }, [logs, autoScroll]);

  // Handle manual scroll to toggle auto-scroll
  const onScroll = () => {
    if (!(containerRef.current instanceof Element)) return;
    
    const { scrollTop, scrollHeight, clientHeight } = containerRef.current;
    const isAtBottom = scrollHeight - scrollTop - clientHeight < 50;
    
    // If the user manually scrolls up, disable auto-scroll
    if (!isAtBottom && autoScroll) {
      setAutoScroll(false);
    }
    // If the user scrolls back to bottom, re-enable auto-scroll
    if (isAtBottom && !autoScroll) {
      setAutoScroll(true);
    }
  };

  return (
    <div className="flex flex-col h-full bg-[#020617]/40 rounded-xl border border-white/5 overflow-hidden">
      {/* Mini Header / Controls */}
      <div className="flex justify-between items-center px-4 py-2 border-b border-white/5 bg-white/[0.02]">
        <div className="flex items-center gap-2">
          <div className={`w-1 h-1 rounded-full ${autoScroll ? 'bg-blue-400 animate-pulse' : 'bg-slate-600'}`} />
          <span className="text-[8px] font-black uppercase tracking-[0.2em] text-slate-500">
            {autoScroll ? 'Streaming Live' : 'Log Paused'}
          </span>
        </div>
        <button 
          id="toggle-autoscroll"
          name="autoscroll"
          onClick={() => setAutoScroll(!autoScroll)}
          className={`flex items-center gap-2 px-2 py-1 rounded transition-all ${
            autoScroll 
            ? 'text-blue-400 hover:text-blue-300' 
            : 'text-slate-500 hover:text-slate-300'
          }`}
          title={autoScroll ? "Lock Scroll (Sticky)" : "Unlock Scroll (Manual)"}
        >
          {autoScroll ? <Lock size={10} /> : <Unlock size={10} />}
          <span className="text-[8px] font-black uppercase tracking-widest">{autoScroll ? 'STICKY' : 'FREE'}</span>
        </button>
      </div>

      {/* Log Stream */}
      <div 
        ref={containerRef}
        onScroll={onScroll}
        className="flex-1 overflow-y-auto p-4 no-scrollbar selection:bg-blue-500/30 space-y-2"
      >
        {logs.length > 0 ? (
          logs.map((log, index) => {
            const content = typeof log === 'string' ? log : log.content;
            const role = typeof log === 'string' ? 'system' : log.role;
            
            return (
              <div
                key={index}
                className="flex gap-4 text-[10px] font-mono leading-relaxed group"
              >
                <span className="text-slate-600 font-black shrink-0 tabular-nums opacity-40">
                  {new Date().toLocaleTimeString([], { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                </span>
                <span className={`break-words ${
                  role === 'system' ? 'text-blue-300/90' : 
                  role === 'user' ? 'text-emerald-400/90' : 
                  'text-slate-400'
                }`}>
                  <span className="font-black uppercase tracking-tighter mr-2 opacity-40">{role}:</span>
                  {content}
                </span>
              </div>
            );
          })
        ) : (
          <div className="h-full flex flex-col items-center justify-center opacity-10 text-[10px] uppercase font-black tracking-[0.3em] gap-2">
            Waiting for neural telemetry...
          </div>
        )}
        <div ref={logEndRef} />
      </div>
    </div>
  );
};

export default StatusLog;
