import { Terminal } from 'lucide-react';

const VaultPanel = ({ vaultSettings, vaultDraft, onVaultDraftChange, onVaultSave }) => (
  <div className="h-full p-6 flex flex-col">
    <div className="flex items-center justify-between mb-8">
      <h2 className="text-xl font-bold flex items-center gap-2">
        <Terminal className="text-red-400" />
        {' '}
        Neural Vault: Secure Storage
      </h2>
      <div className="bg-red-500/10 border border-red-500/20 px-4 py-1.5 rounded-xl text-[10px] font-black text-red-500 uppercase tracking-widest">
        Entropy Level: High-Secure
      </div>
    </div>

    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 overflow-y-auto">
      {vaultSettings.map((setting) => (
        <div key={setting.key} className="glass-panel p-6 border-white/5 space-y-4">
          <div className="flex justify-between items-center">
            <span className="text-[10px] font-black uppercase text-white/30 tracking-widest">{setting.key}</span>
            <span className={`text-[8px] font-black uppercase px-2 py-0.5 rounded ${setting.is_encrypted ? 'bg-blue-500/10 text-blue-400' : 'bg-yellow-500/10 text-yellow-400'}`}>
              {setting.is_encrypted ? 'ENCRYPTED' : 'PLAIN-TEXT'}
            </span>
          </div>
          <div className="text-sm font-mono break-all opacity-80 bg-black/40 p-3 rounded-lg border border-white/5">
            {setting.value}
          </div>
        </div>
      ))}

      <div className="glass-panel p-6 border-blue-500/20 bg-blue-500/5 space-y-4">
        <h3 className="text-sm font-black uppercase tracking-widest opacity-40">Inject New Secret</h3>
        <div className="space-y-3">
          <input
            type="text"
            placeholder="Key (e.g. WHOP_API_KEY)"
            className="w-full text-xs"
            value={vaultDraft.key}
            onChange={(event) => onVaultDraftChange({ ...vaultDraft, key: event.target.value })}
          />
          <input
            type="password"
            placeholder="Secret Value"
            className="w-full text-xs"
            value={vaultDraft.value}
            onChange={(event) => onVaultDraftChange({ ...vaultDraft, value: event.target.value })}
          />
          <button className="w-full btn-primary py-3 text-xs" onClick={onVaultSave}>
            Seal in Vault
          </button>
        </div>
      </div>
    </div>
  </div>
);

export default VaultPanel;
