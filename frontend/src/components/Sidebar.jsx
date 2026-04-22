import React from 'react';
import { motion } from 'framer-motion';

const Sidebar = ({ autonomyLog = [], swarmStatus = {} }) => {
  const brains = Object.values(swarmStatus);
  const activeBrain = brains.find(b => b.running) || {};
  const currentPhase = activeBrain.phase || 'idle';

  const getStatus = (step) => {
    switch(step) {
      case 'Inception':
        if (['task_init', 'hunting'].includes(currentPhase)) return { status: 'Active', level: 40 };
        if (['generating', 'coding', 'reverse_engineering', 'auditing', 'finalizing', 'completed'].includes(currentPhase)) return { status: 'Done', level: 100 };
        return { status: 'Wait', level: 0 };
      case 'Asset Coding':
        if (['generating', 'coding', 'reverse_engineering'].includes(currentPhase)) return { status: 'Active', level: 65 };
        if (['auditing', 'finalizing', 'completed'].includes(currentPhase)) return { status: 'Done', level: 100 };
        return { status: 'Wait', level: 0 };
      case 'Functional Validation':
        if (['auditing', 'fault_detected', 'repaired'].includes(currentPhase)) return { status: 'Active', level: 50 };
        if (['finalizing', 'completed'].includes(currentPhase)) return { status: 'Done', level: 100 };
        return { status: 'Wait', level: 0 };
      case 'Market Launch':
        if (currentPhase === 'finalizing') return { status: 'Active', level: 80 };
        if (currentPhase === 'completed') return { status: 'Done', level: 100 };
        return { status: 'Wait', level: 0 };
      default: return { status: 'Wait', level: 0 };
    }
  };

  const steps = [
    { step: 'Inception', ...getStatus('Inception') },
    { step: 'Asset Coding', ...getStatus('Asset Coding') },
    { step: 'Functional Validation', ...getStatus('Functional Validation') },
    { step: 'Market Launch', ...getStatus('Market Launch') },
  ];

  return (
    <div className="absolute top-24 right-8 w-64 pointer-events-none z-20 space-y-4">
      {/* Neural Production Line */}
      <div className="glass-panel p-4 border-blue-500/10 bg-blue-500/[0.02]">
        <div className="flex justify-between items-center mb-3">
          <span className="text-[8px] font-black uppercase text-blue-400 tracking-widest">Neural Production Line</span>
          <div className={`w-1.5 h-1.5 rounded-full ${brains.some(b => b.running) ? 'bg-blue-500 animate-ping' : 'bg-white/10'}`} />
        </div>
        <div className="space-y-3">
          {steps.map((item, index) => (
            <div key={item.step} className="space-y-1">
              <div className="flex justify-between text-[7px] font-black uppercase">
                <span className={item.level > 0 ? 'opacity-100' : 'opacity-40'}>{item.step}</span>
                <span className={item.status === 'Active' ? 'text-blue-400' : item.status === 'Done' ? 'text-green-400 opacity-60' : 'opacity-20'}>
                  {item.status}
                </span>
              </div>
              <div className="w-full h-0.5 bg-white/5 rounded-full overflow-hidden">
                <motion.div 
                  initial={false}
                  animate={{ width: `${item.level}%` }} 
                  className={`h-full ${item.status === 'Done' ? 'bg-green-500/50' : 'bg-blue-500'}`}
                />
              </div>
            </div>
          ))}
        </div>
      </div>

    </div>
  );
};

export default Sidebar;
