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

const isPageVisible = () => typeof document === 'undefined' || !document.hidden;

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
  const [uiNotice, setUiNotice] = useState('');
  const chatEndRef = useRef(null);

  useEffect(() => {
    const fetchIntel = async () => {
      if (!isPageVisible()) {
        return;
      }
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
      const handleVisibilityChange = () => {
        if (!document.hidden) {
          fetchIntel();
        }
      };
      document.addEventListener('visibilitychange', handleVisibilityChange);
      return () => {
        clearInterval(interval);
        document.removeEventListener('visibilitychange', handleVisibilityChange);
      };
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

  const handleDeployBrain = async () => {
    try {
      await spawnBrain(name);
      setUiNotice(`Node ${name} deployed.`);
    } catch {
      setUiNotice(`Unable to deploy ${name}.`);
    }
  };

  const handleVaultSave = async () => {
    const key = vaultDraft.key.trim();
    const value = vaultDraft.value;
    if (!key || !value) {
      setUiNotice('Vault entry needs both key and value.');
      return;
    }

    try {
      await saveVaultEntry({ key, value, encrypt: true });
      setVaultDraft({ key: '', value: '' });
      setUiNotice(`Vault entry ${key} saved.`);
    } catch {
      setUiNotice(`Unable to save vault entry ${key}.`);
    }
  };

  useEffect(() => {
    if (!uiNotice) {
      return undefined;
    }
    const timeoutId = window.setTimeout(() => setUiNotice(''), 3000);
    return () => window.clearTimeout(timeoutId);
  }, [uiNotice]);

  const currentTabContent = () => {
    switch(activeTab) {
      case 'chat': return <ChatPanel isRecording={isRecording} messages={messages} loading={loading} input={input} onInputChange={setInput} onSendMessage={sendMessage} onToggleAutonomousChat={toggleAutonomousChat} chatEndRef={chatEndRef} />;
      case 'forge': return <AutonomyPanel autonomyLog={autonomyLog} swarmStatus={swarmStatus} onDeployBrain={handleDeployBrain} onSpawnBrain={spawnBrain} onStopBrain={stopBrain} />;
      case 'audit': return <AuditPanel />;
      case 'inventory': return <WorkspacePanel products={products} onRefreshProducts={refreshProducts} />;
      case 'vault': return <VaultPanel vaultSettings={vaultSettings} vaultDraft={vaultDraft} onVaultDraftChange={setVaultDraft} onVaultSave={handleVaultSave} />;
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
            onAuthorize={() => {
              sentinelStorage.set(securityKey);
              setShowSentinel(false);
              setIsBooting(true);
            }}
            onStartSentinelVoiceAuth={startSentinelVoiceAuth}
          />
        )}
      </AnimatePresence>

      <AnimatePresence>
        {isBooting && (
          <BootSequence
            onComplete={() => {
              setIsBooting(false);
              setHasBooted(true);
            }}
          />
        )}
      </AnimatePresence>

      {!isConfigured && !showSentinel && !isBooting && (
        <SetupPanel
          name={name}
          isRegistering={isRegistering}
          isRecording={isRecording}
          trainingScript={trainingScript}
          voiceStatus={voiceStatus}
          onNameChange={setName}
          onRegister={handleRegister}
          onStartVoiceRegistration={startVoiceRegistration}
        />
      )}

      {isConfigured && hasBooted && (
        <div className="flex w-full h-full gap-4 relative overflow-hidden">
          {/* Sidebar Navigation */}
          <div className="w-20 flex flex-col items-center py-8 glass-panel border border-white/5 bg-slate-900/40 gap-8 z-10">
            <button
              onClick={() => setActiveTab('chat')}
              className={`p-3 rounded-xl transition-all ${activeTab === 'chat' ? 'bg-blue-500 text-white shadow-[0_0_20px_rgba(59,130,246,0.5)]' : 'text-white/20 hover:text-white/50'}`}
            >
              <MessageSquare size={22} />
            </button>
            <button
              onClick={() => setActiveTab('forge')}
              className={`p-3 rounded-xl transition-all ${activeTab === 'forge' ? 'bg-blue-500 text-white shadow-[0_0_20px_rgba(59,130,246,0.5)]' : 'text-white/20 hover:text-white/50'}`}
            >
              <RefreshCw size={22} />
            </button>
            <button
              onClick={() => setActiveTab('inventory')}
              className={`p-3 rounded-xl transition-all ${activeTab === 'inventory' ? 'bg-blue-500 text-white shadow-[0_0_20px_rgba(59,130,246,0.5)]' : 'text-white/20 hover:text-white/50'}`}
            >
              <Package size={22} />
            </button>
            <button
              onClick={() => setActiveTab('audit')}
              className={`p-3 rounded-xl transition-all ${activeTab === 'audit' ? 'bg-blue-500 text-white shadow-[0_0_20px_rgba(59,130,246,0.5)]' : 'text-white/20 hover:text-white/50'}`}
            >
              <BarChart3 size={22} />
            </button>
            <button
              onClick={() => setActiveTab('vault')}
              className={`p-3 rounded-xl transition-all ${activeTab === 'vault' ? 'bg-blue-500 text-white shadow-[0_0_20px_rgba(59,130,246,0.5)]' : 'text-white/20 hover:text-white/50'}`}
            >
              <Terminal size={22} />
            </button>
          </div>

          {/* Main Content Area */}
          <div className="flex-1 flex flex-col glass-panel border border-white/5 bg-slate-900/40 overflow-hidden relative">
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
            {uiNotice && (
              <div className="px-8 py-2 border-b border-white/5 text-[10px] font-mono uppercase tracking-wider text-cyan-300 bg-cyan-500/5">
                {uiNotice}
              </div>
            )}
            <div className="flex-1 overflow-hidden">
              {currentTabContent()}
            </div>
          </div>

          {/* Status Overlay */}
          <Sidebar autonomyLog={autonomyLog} swarmStatus={swarmStatus} />
        </div>
      )}

      <AnimatePresence>
        {showTerminal && (
          <motion.div
            initial={{ y: '100%', opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            exit={{ y: '100%', opacity: 0 }}
            transition={{ type: 'spring', damping: 25, stiffness: 200 }}
            className="absolute bottom-24 left-32 right-12 h-64 glass-panel border border-blue-500/30 bg-[#020617]/95 z-[60] flex flex-col shadow-[0_-20px_50px_rgba(0,0,0,0.5)]"
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
  );
};

export default App;
