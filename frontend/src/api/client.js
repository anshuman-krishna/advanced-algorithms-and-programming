// thin fetch wrapper. all api urls flow through here so the base can
// swap between local dev, lan, or hosted backends via env at build time.

const DEFAULT_BASE = 'http://127.0.0.1:8000';

let token = null;

export function setToken(value) {
  token = value;
}

async function request(path, options = {}) {
  const base = process.env.EXPO_PUBLIC_API_BASE || DEFAULT_BASE;
  const headers = { 'Content-Type': 'application/json', ...(options.headers || {}) };
  if (token) headers.Authorization = `Token ${token}`;
  const res = await fetch(`${base}${path}`, { ...options, headers });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`api ${res.status}: ${text}`);
  }
  if (res.status === 204) return null;
  return res.json();
}

export const api = {
  listPosts: () => request('/api/posts/posts/'),
  getPost: (id) => request(`/api/posts/posts/${id}/`),
  listComments: (postId) => request(`/api/posts/posts/${postId}/comments/`),
  likePost: (id) => request(`/api/posts/posts/${id}/like/`, { method: 'POST' }),
  unlikePost: (id) => request(`/api/posts/posts/${id}/unlike/`, { method: 'POST' }),
  listUsers: () => request('/api/accounts/users/'),
  me: () => request('/api/accounts/users/me/'),
  login: (username, password) =>
    request('/api/auth/token/', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    }),
};
