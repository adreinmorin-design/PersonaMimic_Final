import React from 'react';
import { motion } from 'framer-motion';

const Sidebar = ({ autonomyLog = [] }) => {
  return (
    <div className="absolute top-24 right-8 w-64 pointer-events-none z-20 space-y-4">
      {/* Neural Production Line */}
      <div className="glass-panel p-4 border-blue-500/10 bg-blue-500/[0.02]">
        <div className="flex justify-between items-center mb-3">
          <span className="text-[8px] font-black uppercase text-blue-400 tracking-widest">Neural Production Line</span>
          <div className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-ping" />
        </div>
        <div className="space-y-3">
          {[
            { step: 'Inception', status: 'Done', level: 100 },
            { step: 'Asset Coding', status: 'Active', level: 65 },
            { step: 'Functional Validation', status: 'Wait', level: 0 },
            { step: 'Market Launch', status: 'Wait', level: 0 },
          ].map((item, index) => (
            <div key={item.step} className="space-y-1">
              <div className="flex justify-between text-[7px] font-black uppercase">
                <span className="opacity-40">{item.step}</span>
                <span className={item.status === 'Active' ? 'text-blue-400' : 'opacity-20'}>{item.status}</span>
              </div>
              <div className="w-full h-0.5 bg-white/5 rounded-full overflow-hidden">
                <motion.div 
                  initial={{ width: 0 }} 
                  animate={{ width: `${item.level}%` }} 
                  className="h-full bg-blue-500" 
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
