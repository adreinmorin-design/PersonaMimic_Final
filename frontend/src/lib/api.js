import axios from 'axios';

export const SENTINEL_KEY_STORAGE = 'dre_sentinel_key';

export const sentinelStorage = {
  get() {
    return localStorage.getItem(SENTINEL_KEY_STORAGE) || '';
  },
  set(value) {
    localStorage.setItem(SENTINEL_KEY_STORAGE, value);
  },
  clear() {
    localStorage.removeItem(SENTINEL_KEY_STORAGE);
  },
};

export const api = axios.create({ baseURL: '/api' });

api.interceptors.request.use((config) => {
  const key = sentinelStorage.get();
  if (key) {
    config.headers['X-Security-Key'] = key;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 403 && error.response.data?.detail?.includes('SENTINEL BLOCK')) {
      sentinelStorage.clear();
      window.location.reload();
    }
    return Promise.reject(error);
  },
);

export function buildProductDownloadUrl(productPath) {
  if (!productPath) {
    return null;
  }

  const normalizedPath = productPath.replace(/\\/g, '/');
  const filename = normalizedPath.split('/').pop();
  return filename ? `/api/products/download/${encodeURIComponent(filename)}` : null;
}
