// shared app state passed down to every screen and overlay. holds the current
// user, a login gate, the overlay navigation helpers (open a post, a profile, a
// hashtag, a story), tab switching, and a global refresh nonce. App.js builds
// the value; screens read it through the useApp hook.
import { createContext, useContext } from 'react';

export const AppContext = createContext({
  user: null,
  // returns true if a signed in user exists. otherwise opens the login prompt
  // and returns false, so callers can do `if (!requireAuth()) return;`.
  requireAuth: () => false,
  openLogin: () => {},
  openPost: () => {},
  openProfile: () => {},
  openHashtag: () => {},
  openStory: () => {},
  closeTop: () => {},
  goTab: () => {},
  refreshNonce: 0,
  refresh: () => {},
});

export function useApp() {
  return useContext(AppContext);
}
