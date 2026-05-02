import React, { useEffect, useState } from 'react';
import { ShieldCheck, ShieldAlert, Clock, RefreshCw, MessageSquare } from 'lucide-react';
import { api } from '../../lib/api';

const AuditPanel = () => {
  const [reviews, setReviews] = useState([]);
  const [loading, setLoading] = useState(false);

  const fetchReviews = async () => {
    try {
      setLoading(true);
      const res = await api.get('/swarm/reviews');
      setReviews(res.data);
    } catch (e) {
      console.error("Failed to fetch reviews", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReviews();
    const interval = setInterval(fetchReviews, 15000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="h-full p-8 flex flex-col space-y-8 overflow-y-auto no-scrollbar">
      <div className="flex items-center justify-between border-b border-white/5 pb-6">
        <div className="flex items-center gap-4">
          <div className="p-3 bg-blue-500/10 border border-blue-500/20 rounded-xl">
            <ShieldCheck className="text-blue-400" size={24} />
          </div>
          <div>
            <h2 className="text-xl font-black tracking-tight uppercase text-white/90">
              Adversary <span className="text-blue-400">Audit</span>
            </h2>
            <p className="text-[10px] font-mono text-slate-500 uppercase tracking-widest mt-1">Industrial Quality Gate // Security & Compliance</p>
          </div>
        </div>
        <button 
          onClick={fetchReviews} 
          disabled={loading}
          className="text-xs opacity-50 hover:opacity-100 flex items-center gap-2 transition-all"
        >
          <RefreshCw size={12} className={loading ? 'animate-spin' : ''} />
          Sync Audits
        </button>
      </div>

      <div className="grid grid-cols-1 gap-4">
        {reviews.length > 0 ? (
          reviews.map((review) => (
            <div key={review.id} className={`glass-panel p-6 border-l-4 ${
              review.status === 'approved' ? 'border-l-green-500/50' : 
              review.status === 'rejected' ? 'border-l-red-500/50' : 
              'border-l-amber-500/50'
            }`}>
              <div className="flex justify-between items-start mb-4">
                <div className="space-y-1">
                  <div className="flex items-center gap-3">
                    <h3 className="text-lg font-black text-white/90">{review.product_name}</h3>
                    <span className={`px-2 py-0.5 rounded text-[8px] font-black uppercase tracking-widest ${
                      review.status === 'approved' ? 'bg-green-500/10 text-green-400' :
                      review.status === 'rejected' ? 'bg-red-500/10 text-red-400' :
                      'bg-amber-500/10 text-amber-400'
                    }`}>
                      {review.status}
                    </span>
                  </div>
                  <div className="flex items-center gap-3 text-[10px] font-mono text-slate-500">
                    <span className="flex items-center gap-1"><Clock size={10} /> {new Date(review.timestamp).toLocaleString()}</span>
                    <span className="flex items-center gap-1"><ShieldCheck size={10} /> Auditor: {review.reviewer_brain}</span>
                  </div>
                </div>
                <div className="text-[10px] font-mono text-slate-600 uppercase">Iteration #{review.iteration}</div>
              </div>

              <div className="bg-[#020617] rounded-xl border border-white/5 p-4 flex gap-4">
                <MessageSquare size={14} className="text-blue-500/50 shrink-0 mt-1" />
                <div className="text-[11px] font-mono text-blue-100/70 leading-relaxed whitespace-pre-wrap">
                  {review.critique || "No critique provided by adversary brain."}
                </div>
              </div>
            </div>
          ))
        ) : (
          <div className="border-2 border-dashed border-white/5 rounded-3xl p-16 text-center opacity-20">
            <ShieldAlert size={48} className="mx-auto mb-4" />
            <p className="font-black uppercase tracking-widest text-sm italic">No audits recorded in current cycle.</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default AuditPanel;
