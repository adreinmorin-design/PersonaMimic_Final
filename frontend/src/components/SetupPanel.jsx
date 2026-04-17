import { Bot, Mic } from 'lucide-react';
import { motion } from 'framer-motion';

const SetupPanel = ({
  name,
  isRegistering,
  isRecording,
  trainingScript,
  voiceStatus,
  onNameChange,
  onRegister,
  onStartVoiceRegistration,
}) => (
  <div className="flex-1 flex flex-col items-center justify-center p-12 text-center space-y-8">
    <motion.div initial={{ scale: 0.9, opacity: 0 }} animate={{ scale: 1, opacity: 1 }}>
      <div className="w-20 h-20 bg-blue-500/10 rounded-3xl flex items-center justify-center mx-auto mb-6">
        <Bot size={32} className="text-blue-400" />
      </div>
      <h1 className="text-3xl font-black mb-2 tracking-tighter uppercase">Initialize Dre Interface</h1>
      <p className="text-white/40 max-w-sm mx-auto mb-8 font-medium">Neural mimicry active. Secure connection re-established.</p>

      <div className="w-full max-w-md space-y-4">
        <input
          id="identity-name"
          name="username"
          type="text"
          placeholder="Identity: Dre"
          className="w-full text-center"
          value={name}
          onChange={(event) => onNameChange(event.target.value)}
        />

        <div className="flex gap-2 mt-4">
          <button className="btn-primary flex-1" onClick={onRegister} disabled={isRegistering}>
            {isRegistering ? 'Authorizing...' : 'Authorize Secure Connection'}
          </button>
          <button
            className={`flex items-center justify-center p-4 rounded-xl border transition-all ${isRecording ? 'bg-red-500/20 border-red-500/40 text-red-500 shadow-[0_0_20px_rgba(239,68,68,0.4)]' : 'bg-blue-500/10 border-blue-500/20 text-blue-400 hover:bg-blue-500/20'}`}
            onClick={onStartVoiceRegistration}
            title={isRecording ? 'Stop Recording' : 'Record Master Voice'}
          >
            <Mic size={20} className={isRecording ? 'animate-pulse' : ''} />
          </button>
        </div>
        {trainingScript && (
          <div className="mt-4 p-4 bg-blue-500/10 border border-blue-500/20 rounded-xl">
            <span className="text-[10px] font-black uppercase tracking-widest text-blue-400 opacity-60 mb-2 block">
              Read This Script
            </span>
            <p className="text-sm font-bold italic text-white/90">
              "
              {trainingScript}
              "
            </p>
          </div>
        )}
        {voiceStatus && <p className="text-xs font-bold text-center text-blue-400 mt-2">{voiceStatus}</p>}
      </div>
    </motion.div>
  </div>
);

export default SetupPanel;
