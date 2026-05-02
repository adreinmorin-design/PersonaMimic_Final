import React, { useEffect, useMemo, useState } from 'react';
import { api } from '../../lib/api';

const isPageVisible = () => typeof document === 'undefined' || !document.hidden;

const SynthesisVault = () => {
  const [tools, setTools] = useState([]);
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchVault = async () => {
      try {
        const [toolsResponse, jobsResponse] = await Promise.all([
          api.get('/reverse-engineering/tools'),
          api.get('/reverse-engineering/history'),
        ]);
        setTools(toolsResponse.data || []);
        setJobs(jobsResponse.data || []);
      } catch (error) {
        console.error('Failed to fetch reverse-engineering vault:', error);
      } finally {
        setLoading(false);
      }
    };

    const refreshWhenVisible = () => {
      if (isPageVisible()) {
        fetchVault();
      }
    };

    refreshWhenVisible();
    const interval = setInterval(refreshWhenVisible, 5000);
    const handleVisibilityChange = () => {
      if (!document.hidden) {
        fetchVault();
      }
    };
    document.addEventListener('visibilitychange', handleVisibilityChange);
    return () => {
      clearInterval(interval);
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, []);

  const jobsById = useMemo(() => {
    const index = {};
    for (const job of jobs || []) {
      index[job.id] = job;
    }
    return index;
  }, [jobs]);

  const formatTime = (dateStr) => {
    if (!dateStr) return 'Unknown';
    try {
      return new Date(dateStr).toLocaleTimeString();
    } catch {
      return 'Invalid Date';
    }
  };

  const renderSteps = (title, steps = []) => (
    <div className="mt-2">
      <p className="text-[10px] uppercase tracking-wider text-cyan-400">{title}</p>
      {steps.length === 0 ? (
        <p className="text-[10px] text-slate-400">No entries provided.</p>
      ) : (
        <ul className="mt-1 space-y-1">
          {steps.map((item, index) => (
            <li key={`${title}-${index}`} className="text-[11px] text-slate-200/90">
              {index + 1}. {item}
            </li>
          ))}
        </ul>
      )}
    </div>
  );

  if (loading && tools.length === 0) {
    return (
      <div className="p-6 bg-slate-900/50 rounded-xl border border-slate-800 animate-pulse">
        <div className="h-4 w-44 bg-slate-800 rounded mb-4"></div>
        <div className="space-y-3">
          <div className="h-24 bg-slate-800/50 rounded"></div>
          <div className="h-24 bg-slate-800/50 rounded"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 bg-slate-900/80 backdrop-blur-md rounded-xl border border-slate-700/50 shadow-2xl relative overflow-hidden">
      <div className="absolute -top-24 -right-24 w-48 h-48 bg-cyan-500/10 blur-3xl rounded-full"></div>

      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-xl font-bold bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">
            REPLICATED TOOLS VAULT
          </h2>
          <p className="text-xs text-slate-400 font-mono mt-1 uppercase tracking-tighter">
            Open-Source Agent Reverse Engineering
          </p>
        </div>
      </div>

      <div className="space-y-3 max-h-[420px] overflow-y-auto pr-2 custom-scrollbar">
        {tools.length === 0 ? (
          <div className="text-center py-10 border border-dashed border-slate-800 rounded-lg">
            <span className="text-slate-500 text-sm italic">
              No replicated tools yet. Trigger a synthesis run to populate this vault.
            </span>
          </div>
        ) : (
          tools.map((tool) => {
            const linkedJob = jobsById[tool.job_id];
            return (
              <div
                key={tool.id}
                className="p-4 bg-slate-800/40 border border-slate-700/50 rounded-lg hover:border-cyan-500/30 transition-all duration-300"
              >
                <div className="flex justify-between items-start gap-4">
                  <div>
                    <p className="text-[10px] text-cyan-400 font-mono uppercase tracking-widest">
                      TARGET: {tool.target_name || tool.target_id}
                    </p>
                    <h3 className="text-sm font-semibold text-slate-100 mt-1">{tool.tool_name}</h3>
                    <p className="text-xs text-slate-300 mt-2">{tool.purpose_summary || tool.explanation}</p>
                    {tool.source_repo_url && (
                      <a
                        className="text-[11px] text-cyan-400 hover:text-cyan-300 mt-2 inline-block"
                        href={tool.source_repo_url}
                        target="_blank"
                        rel="noreferrer"
                      >
                        Source Repository
                      </a>
                    )}
                  </div>
                  <div className="text-right">
                    <span className="block text-[10px] text-slate-500 font-mono">
                      {formatTime(tool.created_at)}
                    </span>
                    <div
                      className={`mt-1 text-[10px] font-bold px-2 py-0.5 rounded uppercase ${
                        tool.status === 'completed'
                          ? 'text-green-400 bg-green-400/10'
                          : tool.status === 'partial'
                            ? 'text-amber-400 bg-amber-400/10'
                            : 'text-red-400 bg-red-400/10'
                      }`}
                    >
                      {tool.status}
                    </div>
                    {linkedJob && (
                      <p className="text-[10px] text-slate-400 mt-1">
                        Job #{tool.job_id}: {linkedJob.status}
                      </p>
                    )}
                  </div>
                </div>

                <details className="mt-3 group/code">
                  <summary className="text-[10px] font-bold text-slate-500 cursor-pointer hover:text-cyan-400 transition-colors uppercase tracking-widest list-none flex items-center gap-2">
                    <span className="group-open/code:rotate-90 transition-transform">▶</span>
                    How To Use
                  </summary>
                  <div className="mt-3 p-3 bg-black/40 rounded border border-slate-700/50">
                    <p className="text-[11px] text-slate-200/90">{tool.explanation || 'No explanation provided.'}</p>
                    {renderSteps('Prerequisites', tool.prerequisites)}
                    {renderSteps('Setup Steps', tool.setup_steps)}
                    {renderSteps('Run Steps', tool.run_steps)}
                    {renderSteps('Integration Steps', tool.integration_steps)}
                    {renderSteps('Limitations', tool.limitations)}
                  </div>
                </details>

                {tool.replicated_code && (
                  <details className="mt-3 group/source">
                    <summary className="text-[10px] font-bold text-slate-500 cursor-pointer hover:text-cyan-400 transition-colors uppercase tracking-widest list-none flex items-center gap-2">
                      <span className="group-open/source:rotate-90 transition-transform">▶</span>
                      View Replicated Source
                    </summary>
                    <pre className="mt-3 p-3 bg-black/60 rounded border border-slate-700/50 text-[10px] font-mono text-cyan-100/80 overflow-x-auto whitespace-pre-wrap max-h-48 custom-scrollbar">
                      {tool.replicated_code}
                    </pre>
                  </details>
                )}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};

export default SynthesisVault;
