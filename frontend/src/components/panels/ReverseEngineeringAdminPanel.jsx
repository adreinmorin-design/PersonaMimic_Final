import React, { useEffect, useMemo, useState } from 'react';
import { api } from '../../lib/api';

const initialForm = {
  target_id: '',
  name: '',
  description: '',
  source_repo_url: '',
  aliases: '',
};

const ReverseEngineeringAdminPanel = () => {
  const [targets, setTargets] = useState([]);
  const [form, setForm] = useState(initialForm);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');

  const refreshTargets = async () => {
    const response = await api.get('/reverse-engineering/targets');
    setTargets(response.data || []);
  };

  useEffect(() => {
    let mounted = true;
    const load = async () => {
      try {
        await refreshTargets();
      } catch (err) {
        if (mounted) setError('Failed to load target catalog.');
      } finally {
        if (mounted) setLoading(false);
      }
    };
    load();
    return () => {
      mounted = false;
    };
  }, []);

  const summary = useMemo(() => {
    const builtIn = targets.filter((target) => target.is_builtin).length;
    const custom = targets.filter((target) => !target.is_builtin).length;
    return { builtIn, custom };
  }, [targets]);

  const handleChange = (field, value) => {
    setForm((previous) => ({ ...previous, [field]: value }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setSaving(true);
    setError('');
    setNotice('');
    try {
      const aliases = form.aliases
        .split(',')
        .map((item) => item.trim())
        .filter(Boolean);
      await api.post('/reverse-engineering/targets', {
        target_id: form.target_id.trim(),
        name: form.name.trim(),
        description: form.description.trim() || null,
        source_repo_url: form.source_repo_url.trim() || null,
        aliases,
      });
      await refreshTargets();
      setForm(initialForm);
      setNotice('Custom target added.');
    } catch (err) {
      setError(err?.response?.data?.detail || 'Failed to create target.');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="glass-panel p-6 border-white/5 space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-[10px] font-black uppercase tracking-[0.25em] text-white/70">Target Admin</h3>
          <p className="text-[10px] text-slate-500 mt-1">Manage open-source reverse-engineering targets.</p>
        </div>
        <div className="text-right text-[10px] font-mono text-slate-400">
          <div>Built-in: {summary.builtIn}</div>
          <div>Custom: {summary.custom}</div>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-3">
        <input
          id="target-id"
          name="target_id"
          className="bg-black/30 border border-white/10 rounded px-3 py-2 text-xs text-white placeholder:text-slate-500"
          placeholder="target_id (e.g. agentforge-lite)"
          value={form.target_id}
          onChange={(e) => handleChange('target_id', e.target.value)}
          required
        />
        <input
          id="target-name"
          name="name"
          className="bg-black/30 border border-white/10 rounded px-3 py-2 text-xs text-white placeholder:text-slate-500"
          placeholder="Name"
          value={form.name}
          onChange={(e) => handleChange('name', e.target.value)}
          required
        />
        <input
          id="target-url"
          name="source_repo_url"
          className="md:col-span-2 bg-black/30 border border-white/10 rounded px-3 py-2 text-xs text-white placeholder:text-slate-500"
          placeholder="Source Repo URL"
          value={form.source_repo_url}
          onChange={(e) => handleChange('source_repo_url', e.target.value)}
        />
        <input
          id="target-aliases"
          name="aliases"
          className="md:col-span-2 bg-black/30 border border-white/10 rounded px-3 py-2 text-xs text-white placeholder:text-slate-500"
          placeholder="Aliases (comma-separated)"
          value={form.aliases}
          onChange={(e) => handleChange('aliases', e.target.value)}
        />
        <textarea
          id="target-description"
          name="description"
          className="md:col-span-2 bg-black/30 border border-white/10 rounded px-3 py-2 text-xs text-white placeholder:text-slate-500 min-h-16"
          placeholder="Description"
          value={form.description}
          onChange={(e) => handleChange('description', e.target.value)}
        />
        <div className="md:col-span-2 flex items-center justify-between">
          <button
            type="submit"
            disabled={saving}
            className="px-4 py-2 bg-blue-500/20 border border-blue-500/30 rounded text-[10px] font-black uppercase tracking-wider text-blue-300 hover:bg-blue-500/30 disabled:opacity-50"
          >
            {saving ? 'Saving...' : 'Add Target'}
          </button>
          {loading && <span className="text-[10px] text-slate-500">Loading catalog...</span>}
        </div>
      </form>

      {notice && <p className="text-[10px] text-green-400">{notice}</p>}
      {error && <p className="text-[10px] text-red-400">{error}</p>}

      <div className="max-h-40 overflow-y-auto custom-scrollbar space-y-2 border-t border-white/5 pt-3">
        {targets.map((target) => (
          <div key={target.id} className="flex items-center justify-between bg-black/20 border border-white/5 rounded px-3 py-2">
            <div>
              <p className="text-[11px] text-white/90 font-medium">{target.name}</p>
              <p className="text-[10px] text-slate-500 font-mono">{target.target_id}</p>
            </div>
            <span className={`text-[9px] uppercase font-black px-2 py-1 rounded ${target.is_builtin ? 'text-cyan-300 bg-cyan-500/15' : 'text-amber-300 bg-amber-500/15'}`}>
              {target.is_builtin ? 'built-in' : 'custom'}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ReverseEngineeringAdminPanel;

