import { AlertCircle, Mic } from 'lucide-react';
import { motion } from 'framer-motion';

const SentinelOverlay = ({
  securityKey,
  isRecording,
  voiceStatus,
  onSecurityKeyChange,
  onAuthorize,
  onStartSentinelVoiceAuth,
}) => (
  <div className="fixed inset-0 z-[100] bg-black/90 backdrop-blur-3xl flex items-center justify-center p-6 text-center">
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      className="max-w-md w-full glass-panel border-red-500/20 p-12 space-y-8"
    >
      <div className="w-16 h-16 bg-red-500/10 rounded-full flex items-center justify-center mx-auto ring-4 ring-red-500/10 mb-4">
        <AlertCircle size={32} className="text-red-500" />
      </div>
      <div className="space-y-2">
        <h2 className="text-2xl font-black uppercase tracking-tighter">Sentinel Lockdown</h2>
        <p className="text-white/40 text-sm font-medium">
          This interface manages high-value funds and autonomous production. Enter the security key to unlock the Neural Bridge.
        </p>
      </div>
      <div className="space-y-4">
        <input
          type="password"
          placeholder="Enter Security Key..."
          className="w-full text-center bg-black/40 border-red-500/20 text-red-500 font-mono"
          value={securityKey}
          onChange={(event) => onSecurityKeyChange(event.target.value)}
        />
        <div className="flex gap-2">
          <button
            className="flex-1 py-4 bg-red-500/10 hover:bg-red-500/20 text-red-500 font-black uppercase tracking-widest rounded-2xl transition-all border border-red-500/20"
            onClick={onAuthorize}
          >
            Authorize Access
          </button>
          <button
            className={`w-20 flex flex-col items-center justify-center rounded-2xl border transition-all ${isRecording ? 'bg-blue-500/20 border-blue-500/40 text-blue-400 shadow-[0_0_20px_rgba(59,130,246,0.5)]' : 'bg-white/5 border-white/10 text-white/50 hover:bg-white/10'}`}
            onClick={onStartSentinelVoiceAuth}
            disabled={isRecording}
            title="Neural Voice Auth"
          >
            <Mic size={24} className={isRecording ? 'animate-pulse' : ''} />
          </button>
        </div>
        {voiceStatus && (
          <p className="text-xs font-bold text-center text-blue-400 uppercase tracking-widest mt-2 bg-blue-500/10 py-1 rounded border border-blue-500/20 animate-pulse">
            {voiceStatus}
          </p>
        )}
      </div>
    </motion.div>
  </div>
);

export default SentinelOverlay;
