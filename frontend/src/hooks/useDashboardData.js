import { useEffect, useState } from 'react';
import { api } from '../lib/api';

const DEFAULT_REVENUE = { total: 0, growth: '+0%', customers: 0 };
const DEFAULT_MODEL = 'llama3.1';

export function useDashboardData({ activeTab, showSentinel }) {
  const [autonomyLog, setAutonomyLog] = useState([]);
  const [swarmStatus, setSwarmStatus] = useState({});
  const [vaultSettings, setVaultSettings] = useState([]);
  const [products, setProducts] = useState([]);
  const [models, setModels] = useState([]);
  const [selectedModel, setSelectedModel] = useState(DEFAULT_MODEL);
  const [useCloud, setUseCloud] = useState(false);
  const [revenue, setRevenue] = useState(DEFAULT_REVENUE);

  const refreshProducts = async () => {
    const response = await api.get('/products');
    setProducts(response.data.products || []);
  };

  const refreshAutonomy = async () => {
    const [autonomyResponse, swarmResponse] = await Promise.all([
      api.get('/swarm/autonomy/status'),
      api.get('/swarm/status'),
    ]);
    setAutonomyLog(autonomyResponse.data.log || []);
    setSwarmStatus(swarmResponse.data || {});
  };

  const refreshVault = async () => {
    const response = await api.get('/config/vault');
    setVaultSettings(response.data.settings || []);
  };

  const refreshRevenue = async () => {
    const response = await api.get('/products/revenue');
    setRevenue({
      total: response.data.revenue || 0,
      growth: response.data.daily_growth || '+0%',
      customers: response.data.active_customers || 0,
    });
  };

  useEffect(() => {
    if (showSentinel) {
      return undefined;
    }

    let cancelled = false;

    const bootstrap = async () => {
      try {
        const [healthResponse, modelsResponse, productsResponse] = await Promise.all([
          api.get('/config/health'),
          api.get('/config/models'),
          api.get('/products'),
        ]);

        if (cancelled) {
          return;
        }

        setSelectedModel(healthResponse.data.model || DEFAULT_MODEL);
        setUseCloud(Boolean(healthResponse.data.cloud));
        setModels(modelsResponse.data.models || []);
        setProducts(productsResponse.data.products || []);
      } catch (error) {
        console.error('Initialization fetch failed:', error);
      }
    };

    bootstrap();

    return () => {
      cancelled = true;
    };
  }, [showSentinel]);

  useEffect(() => {
    if (showSentinel) {
      return undefined;
    }

    let cancelled = false;

    const runRefresh = async (refreshFn, label) => {
      try {
        await refreshFn();
      } catch (error) {
        if (!cancelled) {
          console.error(`${label} failed:`, error);
        }
      }
    };

    runRefresh(refreshRevenue, 'Revenue fetch');

    let autonomyIntervalId;
    let revenueIntervalId;

    if (activeTab === 'autonomy') {
      runRefresh(refreshAutonomy, 'Autonomy status poll');
      autonomyIntervalId = window.setInterval(() => {
        runRefresh(refreshAutonomy, 'Autonomy status poll');
      }, 3000);
    }

    if (activeTab === 'vault') {
      runRefresh(refreshVault, 'Vault fetch');
    }

    revenueIntervalId = window.setInterval(() => {
      runRefresh(refreshRevenue, 'Revenue fetch');
    }, 10000);

    return () => {
      cancelled = true;
      window.clearInterval(autonomyIntervalId);
      window.clearInterval(revenueIntervalId);
    };
  }, [activeTab, showSentinel]);

  const changeModel = async (model) => {
    const previousModel = selectedModel;
    setSelectedModel(model);
    try {
      await api.post('/config', { model });
    } catch (error) {
      setSelectedModel(previousModel);
      throw error;
    }
  };

  const toggleCloud = async () => {
    const nextMode = !useCloud;
    await api.post('/config/cloud', { use_cloud: nextMode });
    setUseCloud(nextMode);
  };

  const saveVaultEntry = async ({ key, value, encrypt = true }) => {
    await api.post('/config/vault', { key, value, encrypt });
    await refreshVault();
  };

  const spawnBrain = async (name) => {
    await api.post('/swarm/spawn', { name });
    await refreshAutonomy();
  };

  const stopBrain = async (name) => {
    await api.post(`/swarm/stop?name=${encodeURIComponent(name)}`);
    await refreshAutonomy();
  };

  return {
    autonomyLog,
    swarmStatus,
    vaultSettings,
    products,
    models,
    selectedModel,
    useCloud,
    revenue,
    refreshProducts,
    refreshVault,
    saveVaultEntry,
    changeModel,
    toggleCloud,
    spawnBrain,
    stopBrain,
  };
}
