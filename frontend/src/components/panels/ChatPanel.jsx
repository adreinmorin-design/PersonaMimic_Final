import { Loader2, Mic, Play, Send } from 'lucide-react';
import ThoughtProcess from '../ThoughtProcess';
import { parseMessage } from '../../lib/chat';

const ChatPanel = ({
  isRecording,
  messages,
  loading,
  input,
  onInputChange,
  onSendMessage,
  onToggleAutonomousChat,
  chatEndRef,
}) => (
  <div className="flex flex-col h-full">
    <div className="px-6 py-3 border-b border-white/5 flex items-center justify-between bg-white/[0.01]">
      <div className="flex items-center gap-2">
        <Mic size={14} className={isRecording ? 'text-red-500 animate-pulse' : 'text-white/20'} />
        <span className="text-[10px] font-black uppercase tracking-widest opacity-40">Autonomous Intelligence</span>
      </div>
      <button
        className={`px-4 py-1.5 rounded-full text-[9px] font-black uppercase transition-all flex items-center gap-2 ${isRecording ? 'bg-blue-500 text-white shadow-[0_0_15px_rgba(59,130,246,0.5)]' : 'bg-white/5 text-white/40 hover:bg-white/10 border border-white/5'}`}
        onClick={onToggleAutonomousChat}
      >
        {isRecording ? 'Sync Active' : 'Sync Neural Hearing'}
      </button>
    </div>
    <div className="flex-1 overflow-y-auto p-4 space-y-4">
      {messages.map((message, index) => {
        const { text, thought } = parseMessage(message.content);
        return (
          <div
            key={index}
            className={`flex flex-col ${message.role === 'user' ? 'items-end' : 'items-start'}`}
          >
            <div className={`chat-bubble ${message.role === 'user' ? 'user-bubble' : 'bot-bubble'}`}>
              <div className="flex justify-between items-center mb-1">
                <span className="text-[10px] font-black uppercase opacity-40">
                  {message.role === 'user' ? 'Operator' : 'Persona'}
                </span>
                {message.audio && (
                  <Play
                    size={10}
                    className="cursor-pointer hover:text-white"
                    onClick={() => new Audio(message.audio).play()}
                  />
                )}
              </div>
              <p className="whitespace-pre-wrap text-sm">{text}</p>
              {thought && <ThoughtProcess content={thought} />}
            </div>
          </div>
        );
      })}
      {loading && (
        <div className="bot-bubble chat-bubble flex items-center gap-2 opacity-60">
          <Loader2 size={14} className="animate-spin" />
          <span className="text-xs font-medium">Neural Processing...</span>
        </div>
      )}
      <div ref={chatEndRef} />
    </div>

    <div className="p-4 bg-black/20 flex gap-3">
      <input
        id="chat-command"
        name="command"
        type="text"
        placeholder="Enter command..."
        className="flex-1 text-sm bg-black/40"
        value={input}
        onChange={(event) => onInputChange(event.target.value)}
        onKeyDown={(event) => event.key === 'Enter' && onSendMessage()}
      />
      <button className="btn-primary p-3" onClick={onSendMessage} disabled={loading}>
        <Send size={18} />
      </button>
    </div>
  </div>
);

export default ChatPanel;
