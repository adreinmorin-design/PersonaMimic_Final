import { Bot } from 'lucide-react';

const AppHeader = ({
  useCloud,
  isConfigured,
  name,
  role,
  revenue,
  selectedModel,
  models,
  onModelChange,
  onCloudToggle,
  intelligence
}) => (
  <div className="px-8 py-5 border-b border-white/5 flex items-center justify-between z-10 relative bg-slate-900/40">
    <div className="flex items-center gap-6">
      <div className="relative">
        <div className="p-3 bg-cyan-500/10 rounded-xl relative ring-1 ring-cyan-500/20 group">
          <Bot className="text-cyan-400 group-hover:scale-110 transition-transform" size={24} />
          <div className="absolute -top-1 -right-1 w-2.5 h-2.5 bg-green-500 rounded-full border-2 border-[#020617] animate-pulse" />
        </div>
      </div>
      <div>
        <div className="flex items-center gap-3">
          <h1 className="text-lg font-black tracking-tight uppercase leading-none text-white/90">
            PersonaMimic <span className="text-cyan-400">Sentinel</span>
          </h1>
          <div className="px-2 py-0.5 bg-cyan-500/10 border border-cyan-500/20 rounded text-[8px] font-black text-cyan-400 uppercase tracking-widest">
            v2.4
          </div>
        </div>
        <div className="flex items-center gap-3 text-[10px] uppercase font-bold mt-1.5 font-mono">
          <span className="text-cyan-500/50">OPERATOR:</span>
          <span className={isConfigured ? 'text-white' : 'text-yellow-400'}>{isConfigured ? name : 'GUEST'}</span>
          <span className="opacity-10">|</span>
          <span className="text-blue-400/60 tracking-wider">SEC_LEVEL_{role?.toUpperCase() || '0'}</span>
        </div>
      </div>
    </div>

    {isConfigured && (
      <div className="flex items-center gap-8">
        {/* Intelligence / Capability Meter */}
        <div className="flex flex-col items-end gap-1.5">
          <div className="flex items-center gap-2">
            <span className="text-[8px] font-black text-cyan-500/50 uppercase tracking-[0.2em]">Neural Intelligence Level</span>
            <span className="text-[10px] font-black text-cyan-400">TIER {intelligence?.tier || 1}</span>
          </div>
          <div className="w-48 h-1.5 bg-white/5 rounded-full overflow-hidden flex gap-0.5 p-0.5 border border-white/5">
            {[...Array(10)].map((_, i) => (
              <div 
                key={i} 
                className={`flex-1 rounded-sm transition-all duration-500 ${
                  i < (intelligence?.tier || 1) ? 'bg-cyan-500 shadow-[0_0_5px_rgba(34,211,238,0.5)]' : 'bg-white/5'
                }`}
              />
            ))}
          </div>
          <div className="text-[8px] font-bold text-slate-500 uppercase tracking-tighter truncate w-48 text-right">
             ARCHETYPES: {intelligence?.capabilities?.join(', ') || 'NONE DETECTED'}
          </div>
        </div>

        <div className="h-10 w-px bg-white/5" />

        <div className="hidden xl:flex items-center gap-6 px-6 py-2.5 bg-white/[0.02] border border-white/5 rounded-2xl">
          <div className="flex flex-col items-end">
            <span className="text-[7px] font-black uppercase opacity-40 tracking-widest text-[#10b981]">Total Revenue</span>
            <span className="text-sm font-black text-[#10b981] tracking-tighter leading-none">$ {(revenue?.total || 0).toLocaleString()}</span>
          </div>
          <div className="flex flex-col items-end">
            <span className="text-[7px] font-black uppercase opacity-40 tracking-widest text-cyan-500">Stability</span>
            <span className="text-sm font-black text-cyan-500 tracking-tighter leading-none">{revenue?.growth || '+0%'}</span>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <select 
            id="model-selector"
            name="model"
            className="text-[10px] font-black p-2 bg-slate-800/50 border-slate-700/50 uppercase focus:border-cyan-500 transition-colors" 
            value={selectedModel} 
            onChange={(e) => onModelChange(e.target.value)}
          >
            {models && models.length > 0 ? (
              models.map((m) => (
                <option key={m} value={m} className="bg-slate-900 text-white">
                  {m}
                </option>
              ))
            ) : (
              <option className="bg-slate-900 text-white">Loading Models...</option>
            )}
          </select>

          <div className="flex items-center gap-2 bg-slate-800/50 p-1 rounded-xl border border-slate-700/50">
            <button
              className={`px-3 py-1.5 rounded-lg text-[9px] font-black uppercase transition-all ${!useCloud ? 'bg-cyan-500 text-white' : 'opacity-30 hover:opacity-100'}`}
              onClick={() => useCloud && onCloudToggle()}
            >
              LOC
            </button>
            <button
              className={`px-3 py-1.5 rounded-lg text-[9px] font-black uppercase transition-all ${useCloud ? 'bg-purple-600 text-white' : 'opacity-30 hover:opacity-100'}`}
              onClick={() => !useCloud && onCloudToggle()}
            >
              CLD
            </button>
          </div>
        </div>
      </div>
    )}
  </div>
);

export default AppHeader;
