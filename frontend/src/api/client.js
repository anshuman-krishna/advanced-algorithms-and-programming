// thin fetch wrapper. all api urls flow through here so the base can
// swap between local dev, lan, or hosted backends via env at build time.

const DEFAULT_BASE = 'http://127.0.0.1:8000';

let token = null;

export function setToken(value) {
  token = value;
}

// the app registers a handler here so any auth gated call that comes back 401
// opens the login prompt instead of surfacing a raw error to the user.
let onUnauthorized = null;
export function setUnauthorizedHandler(fn) {
  onUnauthorized = fn;
}

// error carrying the http status so callers can tell "needs login" apart from
// a real failure
export class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
  }
}

async function request(path, options = {}) {
  const base = process.env.EXPO_PUBLIC_API_BASE || DEFAULT_BASE;
  const headers = { 'Content-Type': 'application/json', ...(options.headers || {}) };
  if (token) headers.Authorization = `Token ${token}`;
  const res = await fetch(`${base}${path}`, { ...options, headers });
  if (res.status === 401 || res.status === 403) {
    // not logged in (or token expired). nudge the app to show the login prompt
    // and report a friendly message rather than the raw server text.
    if (onUnauthorized) onUnauthorized();
    throw new ApiError('please log in to continue', res.status);
  }
  if (!res.ok) {
    const text = await res.text();
    throw new ApiError(`api ${res.status}: ${text}`, res.status);
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

  // phase 5: comment threads (lab 4)
  thread: (postId, prune = true) =>
    request(`/api/posts/posts/${postId}/thread/?prune=${prune ? 1 : 0}`),
  threadStats: (postId) => request(`/api/posts/posts/${postId}/thread-stats/`),
  threadDepth: (postId) => request(`/api/posts/posts/${postId}/thread-depth/`),
  threadSearch: (postId, q, userId) => {
    const qs = new URLSearchParams();
    if (q) qs.set('q', q);
    if (userId) qs.set('user_id', String(userId));
    return request(`/api/posts/posts/${postId}/thread-search/?${qs.toString()}`);
  },
  createComment: (postId, content, parentId = null) =>
    request('/api/posts/comments/', {
      method: 'POST',
      body: JSON.stringify({ post: postId, parent: parentId, content }),
    }),
  deleteComment: (id) => request(`/api/posts/comments/${id}/`, { method: 'DELETE' }),
  likeComment: (id) => request(`/api/posts/comments/${id}/like/`, { method: 'POST' }),
  unlikeComment: (id) => request(`/api/posts/comments/${id}/unlike/`, { method: 'POST' }),

  // phase 5: notifications (lab 3 ex 2)
  listNotifications: () => request('/api/notifications/'),
  unreadCount: () => request('/api/notifications/unread-count/'),
  markNotificationsRead: () =>
    request('/api/notifications/mark_all_read/', { method: 'POST' }),
  notificationsQueueStats: () => request('/api/notifications/queue/stats/'),
  drainNotifications: () =>
    request('/api/notifications/queue/stats/', { method: 'POST' }),

  // phase 5: reels (lab 3 ex 1 dll)
  reelsPage: (cursor, direction = 'next', limit = 5) => {
    const qs = new URLSearchParams({ direction, limit: String(limit) });
    if (cursor != null) qs.set('cursor', String(cursor));
    return request(`/api/reels/page/?${qs.toString()}`);
  },
  reelsAround: (postId, k = 3) => request(`/api/reels/around/${postId}/?k=${k}`),
  reelsMarkViewed: (postId) =>
    request(`/api/reels/${postId}/view/`, { method: 'POST' }),
  reelsMostViewed: () => request('/api/reels/most-viewed/'),
  reelsStats: () => request('/api/reels/stats/'),

  // phase 6: analytics (lab 8 ex 3 segment tree)
  likesRange: (identifier, from, to) => {
    const qs = new URLSearchParams();
    if (from) qs.set('from', from);
    if (to) qs.set('to', to);
    return request(`/api/analytics/users/${identifier}/likes-range/?${qs.toString()}`);
  },
  likesSeries: (identifier) =>
    request(`/api/analytics/users/${identifier}/likes-series/`),
  analyticsStats: () => request('/api/analytics/stats/'),

  // phase 6: geo (lab 7 ex 1 quadtree)
  geoNearby: (lat, lng, radius = 5, limit = 25) =>
    request(
      `/api/geo/nearby/?lat=${lat}&lng=${lng}&radius=${radius}&limit=${limit}`,
    ),
  geoBbox: (minLat, minLng, maxLat, maxLng, limit = 100) =>
    request(
      `/api/geo/bbox/?min_lat=${minLat}&min_lng=${minLng}` +
        `&max_lat=${maxLat}&max_lng=${maxLng}&limit=${limit}`,
    ),
  geoNearest: (lat, lng, k = 5) =>
    request(`/api/geo/nearest/?lat=${lat}&lng=${lng}&k=${k}`),
  geoStats: () => request('/api/geo/stats/'),

  // phase 6: social graph traversals (lab 6 ex 2 + ex 3)
  communities: () => request('/api/social/communities/'),
  communityOf: (identifier) =>
    request(`/api/social/users/${identifier}/community/`),
  shortestChain: (fromId, toId) =>
    request(
      `/api/social/shortest-chain/?from=${encodeURIComponent(fromId)}` +
        `&to=${encodeURIComponent(toId)}`,
    ),
  nichePosts: (identifier, limit = 20) =>
    request(`/api/social/users/${identifier}/niche-posts/?limit=${limit}`),
  reach: (identifier, maxDepth) => {
    const qs = maxDepth != null ? `?max_depth=${maxDepth}` : '';
    return request(`/api/social/users/${identifier}/reach/${qs}`);
  },

  // phase 7 follow-ups
  threadCount: (postId) => request(`/api/posts/posts/${postId}/thread-count/`),
  threadEngagement: (postId, score = 'likes') =>
    request(`/api/posts/posts/${postId}/thread-engagement/?score=${score}`),
  hashtagRelated: (name, limit = 10) =>
    request(`/api/search/hashtag/${encodeURIComponent(name)}/related/?limit=${limit}`),
  exploreFeed: (categoryId, k = 10) =>
    request(`/api/feed/explore/?category=${categoryId}&k=${k}`),
  geoDense: (threshold = 1, minSize = 5) =>
    request(`/api/geo/dense/?threshold=${threshold}&min_size=${minSize}`),
  trendingHashtags: (limit = 10) =>
    request(`/api/search/hashtags/trending/?limit=${limit}`),
};
