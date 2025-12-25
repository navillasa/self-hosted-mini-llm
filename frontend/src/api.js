import axios from 'axios';

const api = axios.create({
  baseURL: "",
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/';
    }
    return Promise.reject(error);
  }
);

export const auth = {
  getGitHubAuthUrl: () => api.get('/api/auth/github'),
  getCurrentUser: () => api.get('/api/auth/me'),
};

export const llm = {
  generate: (prompt, maxTokens = 512) =>
    api.post('/api/llm/generate', { prompt, max_tokens: maxTokens }),
};

export default api;
