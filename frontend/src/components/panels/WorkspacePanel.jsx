import { Download, Package, RefreshCw } from 'lucide-react';
import { buildProductDownloadUrl } from '../../lib/api';

const WorkspacePanel = ({ products, onRefreshProducts }) => (
  <div className="h-full p-6 overflow-y-auto">
    <div className="flex items-center justify-between mb-8">
      <h2 className="text-xl font-bold flex items-center gap-2">
        <Package className="text-blue-400" />
        {' '}
        Digital Assets
      </h2>
      <button
        className="text-xs opacity-50 hover:opacity-100 flex items-center gap-1"
        onClick={onRefreshProducts}
      >
        <RefreshCw size={12} />
        {' '}
        Sync Inventory
      </button>
    </div>

    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      {products.map((product) => {
        const downloadUrl = buildProductDownloadUrl(product.path);
        return (
          <div key={product.id} className="product-card flex flex-col justify-between">
            <div>
              <div className="flex justify-between items-start mb-2">
                <span className="text-[10px] font-black bg-blue-500/10 text-blue-400 px-2 py-0.5 rounded-full uppercase">
                  {product.status}
                </span>
                <span className="text-[10px] opacity-30 font-mono">{product.created_at}</span>
              </div>
              <h3 className="font-bold text-lg mb-1">{product.name}</h3>
              <p className="text-xs opacity-50 mb-4 font-mono truncate">{product.path}</p>
            </div>
            <button
              className="w-full bg-white/5 hover:bg-white/10 p-3 rounded-xl flex items-center justify-center gap-2 transition-colors text-sm font-bold"
              onClick={() => downloadUrl && window.open(downloadUrl)}
              disabled={!downloadUrl || (product.status !== 'packaged' && product.status !== 'published')}
            >
              <Download size={16} />
              {' '}
              Download ZIP
            </button>
          </div>
        );
      })}
      {products.length === 0 && (
        <div className="col-span-full border-2 border-dashed border-white/5 rounded-3xl p-12 text-center opacity-30">
          <Package size={48} className="mx-auto mb-4" />
          <p className="font-bold italic">No assets generated yet.</p>
        </div>
      )}
    </div>
  </div>
);

export default WorkspacePanel;
