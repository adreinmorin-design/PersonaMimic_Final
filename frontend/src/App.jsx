import React, { useEffect, useRef, useState } from 'react';
import {
  MessageSquare,
  Terminal,
  BarChart3,
  Package,
  RefreshCw,
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import AppHeader from './components/AppHeader';
import SentinelOverlay from './components/SentinelOverlay';
import SetupPanel from './components/SetupPanel';
import Sidebar from './components/Sidebar';
import BootSequence from './components/BootSequence';
import ChatPanel from './components/panels/ChatPanel';
import AutonomyPanel from './components/panels/AutonomyPanel';
import AuditPanel from './components/panels/AuditPanel';
import WorkspacePanel from './components/panels/WorkspacePanel';
import VaultPanel from './components/panels/VaultPanel';
import { api, sentinelStorage } from './lib/api';
import { toChatHistory } from './lib/chat';
import { useDashboardData } from './hooks/useDashboardData';
import { useVoiceControls } from './hooks/useVoiceControls';

const App = () => {
  const [activeTab, setActiveTab] = useState('chat');
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [name, setName] = useState('Dre');
  const [isConfigured, setIsConfigured] = useState(false);
  const [securityKey, setSecurityKey] = useState(sentinelStorage.get());
  const [showSentinel, setShowSentinel] = useState(!sentinelStorage.get());
  const [role, setRole] = useState('owner');
  const [loading, setLoading] = useState(false);
  const [isRegistering, setIsRegistering] = useState(false);
  const [isBooting, setIsBooting] = useState(false);
  const [hasBooted, setHasBooted] = useState(false);
  const [intelligence, setIntelligence] = useState({ tier: 1, capabilities: [], assessment: 'Initializing...' });
  const [showTerminal, setShowTerminal] = useState(false);
  const [vaultDraft, setVaultDraft] = useState({ key: '', value: '' });
  const chatEndRef = useRef(null);

  useEffect(() => {
    const fetchIntel = async () => {
      try {
        const res = await api.get('/system/intelligence');
        setIntelligence(res.data);
      } catch (e) {
        console.error("Intel fetch failed", e);
      }
    };
    if (isConfigured) {
      fetchIntel();
      const interval = setInterval(fetchIntel, 10000);
      return () => clearInterval(interval);
    }
  }, [isConfigured]);

  const dashboardData = useDashboardData({ activeTab, showSentinel });
  const sanitizedDashboardData = dashboardData || {};
  const {
    autonomyLog = [],
    swarmStatus = {},
    vaultSettings = [],
    products = [],
    models = [],
    selectedModel = '',
    useCloud = false,
    revenue = { total: 0, growth: '+0%', customers: 0 },
    refreshProducts = () => {},
    saveVaultEntry = () => {},
    changeModel = () => {},
    toggleCloud = () => {},
    spawnBrain = () => {},
    stopBrain = () => {},
  } = sanitizedDashboardData;

  const {
    isRecording,
    voiceStatus,
    trainingScript,
    startVoiceRegistration,
    startSentinelVoiceAuth,
    toggleAutonomousChat,
  } = useVoiceControls({
    username: name,
    onAutonomousReply: ({ text, response, audioUrl }) => {
      setMessages((previousMessages) => [
        ...previousMessages,
        { role: 'user', content: text },
        { role: 'bot', content: response, audio: audioUrl },
      ]);
    },
    onSentinelUnlock: (nextSecurityKey) => {
      sentinelStorage.set(nextSecurityKey);
      setSecurityKey(nextSecurityKey);
      setShowSentinel(false);
      setIsBooting(true);
    },
  });

  useEffect(() => {
    if (activeTab === 'chat' && chatEndRef.current instanceof Element) {
      try {
        chatEndRef.current.scrollIntoView({ behavior: 'smooth' });
      } catch (e) {
        console.warn("[SCROLL-ERROR] Failed to scroll chat into view:", e);
      }
    }
  }, [messages, activeTab]);

  const handleRegister = async () => {
    const trimmedName = name.trim();
    if (!trimmedName) return;
    try {
      setIsRegistering(true);
      const response = await api.post('/auth/register', { username: trimmedName, consent_given: true });
      setName(trimmedName);
      setRole(response.data.role);
      setIsConfigured(true);
      setIsBooting(true);
      setMessages([{ role: 'bot', content: `Identity verified. Role: **${response.data.role.toUpperCase()}**. System online.` }]);
    } catch {
      alert('Registration failed.');
    } finally {
      setIsRegistering(false);
    }
  };

  const sendMessage = async () => {
    const trimmedInput = input.trim();
    if (!trimmedInput || loading) return;
    const userMessage = { role: 'user', content: trimmedInput };
    const nextMessages = [...messages, userMessage];
    setMessages(nextMessages);
    setInput('');
    setLoading(true);
    try {
      const response = await api.post('/chat', { message: trimmedInput, history: toChatHistory(nextMessages) });
      const botMessage = { role: 'bot', content: response.data.response, audio: response.data.audio_url };
      setMessages((prev) => [...prev, botMessage]);
      if (response.data.audio_url) new Audio(response.data.audio_url).play();
    } catch {
      setMessages((prev) => [...prev, { role: 'bot', content: '[ERR] System offline.' }]);
    } finally {
      setLoading(false);
    }
  };

  const currentTabContent = () => {
    switch(activeTab) {
      case 'chat': return <ChatPanel isRecording={isRecording} messages={messages} loading={loading} input={input} onInputChange={setInput} onSendMessage={sendMessage} onToggleAutonomousChat={toggleAutonomousChat} chatEndRef={chatEndRef} />;
      case 'forge': return <AutonomyPanel autonomyLog={autonomyLog} swarmStatus={swarmStatus} onDeployBrain={() => {}} onSpawnBrain={spawnBrain} onStopBrain={stopBrain} />;
      case 'audit': return <AuditPanel />;
      case 'inventory': return <WorkspacePanel products={products} onRefreshProducts={refreshProducts} />;
      case 'vault': return <VaultPanel vaultSettings={vaultSettings} vaultDraft={vaultDraft} onVaultDraftChange={setVaultDraft} onVaultSave={() => {}} />;
      default: return null;
    }
  };

  return (
    <div className="w-full h-screen flex items-center justify-center p-4">
      <AnimatePresence>
        {showSentinel && (
          <SentinelOverlay
            securityKey={securityKey}
            isRecording={isRecording}
            voiceStatus={voiceStatus}
            onSecurityKeyChange={setSecurityKey}
            onAuthorize={() => { sentinelStorage.set(securityKey); setShowSentinel(false); setIsBooting(true); }}
            onStartSentinelVoiceAuth={startSentinelVoiceAuth}
          />
        )}
      </AnimatePresence>

      <AnimatePresence>
        {isBooting && (
          <BootSequence onComplete={() => { setIsBooting(false); setHasBooted(true); }} />
        )}
      </AnimatePresence>

      <div className="w-full max-w-6xl h-[92vh] glass-panel flex flex-col overflow-hidden relative">
        <AppHeader 
          useCloud={useCloud} 
          isConfigured={isConfigured} 
          name={name} 
          role={role} 
          revenue={revenue} 
          selectedModel={selectedModel} 
          models={models} 
          onModelChange={changeModel} 
          onCloudToggle={toggleCloud} 
          intelligence={intelligence}
        />

        {!isConfigured ? (
          <SetupPanel name={name} isRegistering={isRegistering} isRecording={isRecording} trainingScript={trainingScript} voiceStatus={voiceStatus} onNameChange={setName} onRegister={handleRegister} onStartVoiceRegistration={startVoiceRegistration} />
        ) : (
          <div className="flex-1 flex flex-col overflow-hidden">
            <div className="px-8 py-4 z-10 flex gap-4 border-b border-white/5">
              {['chat', 'forge', 'audit', 'inventory', 'vault'].map(tab => (
                <button key={tab} onClick={() => setActiveTab(tab)} className={`px-4 py-2 text-[10px] font-black uppercase tracking-widest transition-all ${activeTab === tab ? 'text-blue-400 bg-blue-500/10 rounded-lg' : 'opacity-40 hover:opacity-100'}`}>
                  {tab}
                </button>
              ))}
            </div>

            <div className="flex-1 overflow-hidden z-10">
              <AnimatePresence mode="wait">
                <motion.div key={activeTab} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }} className="h-full">
                  {currentTabContent()}
                </motion.div>
              </AnimatePresence>
            </div>

            {isConfigured && <Sidebar autonomyLog={autonomyLog} />}
          </div>
        )}

        <AnimatePresence>
          {showTerminal && (
            <motion.div 
              initial={{ y: '100%' }}
              animate={{ y: 0 }}
              exit={{ y: '100%' }}
              transition={{ type: 'spring', damping: 25, stiffness: 200 }}
              className="absolute bottom-20 left-6 right-6 h-64 glass-panel border border-blue-500/30 bg-[#020617]/95 z-[60] flex flex-col shadow-[0_-20px_50px_rgba(0,0,0,0.5)]"
            >
              <div className="flex items-center justify-between px-6 py-3 border-b border-white/5 bg-white/[0.02]">
                <div className="flex items-center gap-3">
                  <Terminal size={14} className="text-blue-400" />
                  <span className="text-[10px] font-black uppercase tracking-[0.3em] text-white/50">System Terminal</span>
                </div>
                <button onClick={() => setShowTerminal(false)} className="text-[10px] font-black uppercase text-white/20 hover:text-white/50 transition-colors">Close</button>
              </div>
              <div className="flex-1 overflow-y-auto p-6 font-mono text-[10px] space-y-2 no-scrollbar">
                {autonomyLog.length > 0 ? (
                  autonomyLog.map((log, idx) => (
                    <div key={idx} className="flex gap-4">
                      <span className="text-blue-500/50 shrink-0">[{new Date().toLocaleTimeString([], { hour12: false })}]</span>
                      <span className="text-blue-100/70 select-text selection:bg-blue-500/30">
                         {typeof log === 'string' ? log : log?.content}
                      </span>
                    </div>
                  ))
                ) : (
                  <div className="h-full flex flex-col items-center justify-center opacity-20 uppercase font-black tracking-[0.2em] gap-2">
                     <span className="animate-pulse">No terminal input detected...</span>
                  </div>
                )}
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        <button 
          className="fixed bottom-6 right-6 w-12 h-12 bg-blue-500 rounded-full flex items-center justify-center shadow-2xl z-[70] hover:scale-110 active:scale-95 transition-transform" 
          onClick={() => setShowTerminal(!showTerminal)}
        >
          <Terminal size={20} className="text-white" />
        </button>
      </div>
    </div>
  );
};

export default App;
