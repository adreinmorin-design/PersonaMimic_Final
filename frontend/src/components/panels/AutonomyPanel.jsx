import React, { useState } from 'react';
import { Activity, AlertCircle, BarChart3, Bot, Terminal, Zap, Send, Target, Trash2 } from 'lucide-react';
import SwarmGraph from '../SwarmGraph';
import StatusLog from '../StatusLog';
import ReverseEngineeringAdminPanel from './ReverseEngineeringAdminPanel';
import SynthesisVault from './SynthesisVault';
import { api } from '../../lib/api';

const AutonomyPanel = ({ autonomyLog, swarmStatus, onDeployBrain, onSpawnBrain, onStopBrain }) => {
  const [directive, setDirective] = useState('');
  const [isUpdating, setIsUpdating] = useState(false);

  const handleSetDirective = async () => {
    if (!directive.trim()) return;
    try {
      setIsUpdating(true);
      await api.post('/swarm/directive', { directive });
      // Notification or UI feedback could go here
    } catch (e) {
      console.error("Failed to set directive", e);
    } finally {
      setIsUpdating(false);
    }
  };

  const handleClearDirective = async () => {
    try {
      setIsUpdating(true);
      await api.post('/swarm/directive', { directive: null });
      setDirective('');
    } catch (e) {
      console.error("Failed to clear directive", e);
    } finally {
      setIsUpdating(false);
    }
  };

  return (
    <div className="flex flex-col h-full p-8 space-y-8 overflow-y-auto no-scrollbar">
      <div className="flex items-center justify-between border-b border-white/5 pb-6">
        <div className="flex items-center gap-4">
          <div className="p-3 bg-blue-500/10 border border-blue-500/20 rounded-xl relative">
            <BarChart3 className="text-blue-400" size={24} />
            <div className="absolute -top-1 -right-1 w-2 h-2 bg-blue-500 rounded-full animate-ping" />
          </div>
          <div>
            <h2 className="text-xl font-black tracking-tight uppercase text-white/90">
              Industrial <span className="text-blue-400">Forge</span>
            </h2>
            <p className="text-[10px] font-mono text-slate-500 uppercase tracking-widest mt-1">Multi-Agent Industrial Orchestration // Operational</p>
          </div>
        </div>
        <button className="btn-primary flex items-center gap-3 px-6 py-3" onClick={onDeployBrain}>
          <Bot size={16} />
          <span className="text-[10px] font-black tracking-[0.2em]">Deploy Neural Node</span>
        </button>
      </div>

      {/* --- SWARM DIRECTIVE INTERFACE --- */}
      <div className="glass-panel p-8 border-blue-500/30 bg-blue-500/[0.05] shadow-[0_0_50px_rgba(59,130,246,0.1)]">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-4">
             <div className="p-2 bg-blue-500/20 rounded-lg">
                <Target size={18} className="text-blue-400" />
             </div>
             <div>
                <h3 className="text-sm font-black uppercase tracking-[0.3em] text-white">Autonomous Directive</h3>
                <p className="text-[9px] font-mono text-blue-400/50 uppercase mt-1">System-Wide Objective Override</p>
             </div>
          </div>
          <div className="px-3 py-1 bg-blue-500/10 border border-blue-500/20 rounded text-[9px] font-black text-blue-400 uppercase tracking-tighter">
            Level 6 Priority
          </div>
        </div>
        
        <div className="flex gap-4">
          <div className="flex-1 relative">
            <input 
              id="autonomy-directive"
              name="directive"
              type="text" 
              value={directive}
              onChange={(e) => setDirective(e.target.value)}
              placeholder="Inject a global objective for the autonomous swarm (e.g. 'Build a SaaS for real estate analytics')..."
              className="w-full bg-[#020617] border border-white/20 rounded-xl px-6 py-4 text-sm font-mono text-blue-100 placeholder:text-slate-600 focus:outline-none focus:border-blue-500 transition-all shadow-inner"
            />
            {directive && (
              <button 
                onClick={handleClearDirective}
                className="absolute right-4 top-1/2 -translate-y-1/2 text-slate-500 hover:text-red-400 transition-colors p-2"
              >
                <Trash2 size={16} />
              </button>
            )}
          </div>
          <button 
            onClick={handleSetDirective}
            disabled={isUpdating || !directive.trim()}
            className="px-8 py-4 bg-blue-600 hover:bg-blue-500 disabled:opacity-30 disabled:hover:bg-blue-600 rounded-xl flex items-center gap-3 transition-all shadow-[0_0_20px_rgba(37,99,235,0.3)]"
          >
            {isUpdating ? <RefreshCw size={16} className="animate-spin" /> : <Send size={16} />}
            <span className="text-xs font-black uppercase tracking-widest">Inject Goal</span>
          </button>
        </div>
        <p className="mt-4 text-[10px] text-slate-400 font-medium italic flex items-center gap-2">
          <AlertCircle size={12} className="text-amber-500" />
          Directives bypass standard niche discovery. All active brains will converge on this objective until cleared.
        </p>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6 relative">
        {Object.entries(swarmStatus || {}).map(([brainName, data]) => {
          const isHealing = data.last_log?.some(
            (log) => (typeof log === 'string' ? log : log.content || '').includes('[HEALING]') || (typeof log === 'string' ? log : log.content || '').includes('[VAULT ERROR]'),
          );

          const isReverse = data.last_log?.some(
            (log) => (typeof log === 'string' ? log : log.content || '').includes('Reverse Engineering') || (typeof log === 'string' ? log : log.content || '').includes('Synthesis target:')
          ) || data.last_tool === 'reverse_engineering_sweep';

          return (
            <div key={brainName} className={`glass-panel p-6 space-y-5 relative transition-all duration-700 ${
              isReverse ? 'border-cyan-500/30' : 
              isHealing ? 'border-amber-500/30' : 
              'border-white/5'
            }`}>
              
              {/* Status Header */}
              <div className="flex justify-between items-start">
                <div className="flex items-center gap-4">
                  <div className={`w-1 h-8 rounded-full transition-colors duration-1000 ${data.running ? 'bg-green-500' : 'bg-red-500/40'}`} />
                  <div>
                     <h3 className="text-sm font-black text-white/90 uppercase tracking-[0.2em] flex items-center gap-2">
                      {brainName}
                      <div className={`w-1.5 h-1.5 rounded-full ${data.running ? 'bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.6)] animate-pulse' : 'bg-red-500/20'}`} />
                    </h3>
                    <div className="text-[9px] font-mono text-slate-500 mt-1 uppercase">
                      ID: {brainName.toUpperCase()}_NODE_{data.tasks}
                    </div>
                  </div>
                </div>
                <div className="px-2 py-1 bg-white/5 border border-white/5 rounded text-[8px] font-bold text-slate-400 font-mono">
                  {data.model?.replace(':latest', '')}
                </div>
              </div>

              {/* Engine Monitor */}
              <div className="bg-[#020617] rounded-xl border border-white/5 p-4 h-44 flex flex-col relative overflow-hidden group">
                 <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/[0.02] to-transparent opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none" />
                 <div className="flex justify-between items-center mb-3 border-b border-white/5 pb-2">
                    <div className="flex items-center gap-2">
                      <Activity size={10} className="text-cyan-500 animate-pulse" />
                      <span className="text-[8px] font-black text-slate-500 uppercase tracking-widest">Neural Stream</span>
                    </div>
                    <div className={`px-2 py-0.5 rounded text-[8px] font-black uppercase tracking-tighter ${
                      isReverse ? 'text-cyan-400 bg-cyan-500/10' : 'text-slate-400'
                    }`}>
                      PHASE::{data.phase || 'IDLE'}
                    </div>
                 </div>
                 
                 <div className="flex-1 overflow-y-auto no-scrollbar space-y-1.5">
                    {data.last_log?.length > 0 ? (
                      data.last_log.map((log, idx) => (
                        <div key={idx} className="flex gap-3 text-[10px] font-mono leading-relaxed">
                          <span className="text-slate-600 font-black shrink-0">[{new Date(data.updated_at).toLocaleTimeString([], { hour12: false })}]</span>
                          <span className={`break-words ${isReverse ? 'text-cyan-100/80 font-medium' : 'text-slate-400'}`}>
                            {typeof log === 'string' ? log : log?.content}
                          </span>
                        </div>
                      ))
                    ) : (
                      <div className="h-full flex flex-col items-center justify-center opacity-20 text-[10px] uppercase font-black tracking-[0.2em] gap-2">
                         <Zap size={16} />
                         Standby Mode
                      </div>
                    )}
                 </div>
              </div>

              {/* Actions */}
              <div className="flex gap-3">
                 <button 
                    className={`flex-1 flex items-center justify-center gap-2 py-2.5 rounded-lg text-[9px] font-black transition-all border ${
                      data.running 
                      ? 'bg-red-500/10 border-red-500/20 text-red-400 hover:bg-red-500/20' 
                      : 'bg-green-500/10 border-green-500/20 text-green-400 hover:bg-green-500/20'
                    }`}
                    onClick={() => data.running ? onStopBrain(brainName) : onSpawnBrain(brainName)}
                  >
                    {data.running ? <Zap size={12} /> : <Activity size={12} />}
                    {data.running ? 'TERMINATE NODE' : 'INITIATE SYNAPSE'}
                 </button>
              </div>

              {/* Meta Overlay for Active States */}
              {isReverse && (
                <div className="absolute top-0 right-0 p-4">
                   <div className="flex items-center gap-2 px-3 py-1 bg-cyan-500/20 border border-cyan-500/30 rounded-full shadow-[0_0_15px_rgba(34,211,238,0.2)]">
                      <div className="w-1.5 h-1.5 bg-cyan-400 rounded-full animate-ping" />
                      <span className="text-[7px] font-black text-cyan-400 uppercase tracking-widest">Reverse Engineering Cycle Active</span>
                   </div>
                </div>
              )}
            </div>
          );
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <SynthesisVault />
        </div>
        <div className="lg:col-span-1">
          <ReverseEngineeringAdminPanel />
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-5 gap-8">
        <div className="lg:col-span-3 glass-panel p-6 border-white/5">
          <div className="flex items-center justify-between mb-6">
             <h3 className="text-[10px] font-black uppercase tracking-[0.3em] text-white/50">Neural Topography</h3>
             <div className="px-3 py-1 bg-white/5 rounded text-[8px] font-black text-slate-500 uppercase">Real-Time Visualization</div>
          </div>
          <SwarmGraph swarmStatus={swarmStatus} />
        </div>

        <div className="lg:col-span-2 glass-panel p-6 border-white/5 flex flex-col h-[400px]">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3 text-[10px] font-black uppercase tracking-widest text-[#10b981]">
              <Terminal size={14} className="animate-pulse" />
              Central Telemetry
            </div>
            <div className="text-[8px] font-mono text-slate-600">SYSTEM_LOG_v1.0.2</div>
          </div>
          <div className="flex-1 overflow-hidden">
             <StatusLog logs={autonomyLog} />
          </div>
        </div>
      </div>
    </div>
  );
};

export default AutonomyPanel;
