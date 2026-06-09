// app entry. holds the auth state (token + current user), the overlay
// navigation stack (post detail, profile, hashtag, story), and a global refresh
// nonce. everything is handed to screens and overlays through AppContext so any
// tap can open the right surface or gate behind login. the chrome lives in
// RootShell so a real bottom navigator drop in later is a one prop change.
import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { Pressable, StyleSheet, Text, View } from 'react-native';
import { StatusBar } from 'expo-status-bar';
import { SafeAreaProvider } from 'react-native-safe-area-context';

import HomeScreen from './src/screens/HomeScreen';
import TrendingScreen from './src/screens/TrendingScreen';
import SearchScreen from './src/screens/SearchScreen';
import ReelsScreen from './src/screens/ReelsScreen';
import NotificationsScreen from './src/screens/NotificationsScreen';
import ThreadScreen from './src/screens/ThreadScreen';
import NearbyScreen from './src/screens/NearbyScreen';
import AnalyticsScreen from './src/screens/AnalyticsScreen';
import CommunitiesScreen from './src/screens/CommunitiesScreen';
import RootShell from './src/components/RootShell';
import TabBar from './src/components/TabBar';
import LoginModal from './src/components/LoginModal';
import OverlayHost from './src/components/OverlayHost';
import GradientText from './src/components/GradientText';
import RefreshGlyph from './src/components/RefreshGlyph';
import { AppContext } from './src/context/AppContext';
import { api, setToken, setUnauthorizedHandler } from './src/api/client';
import { colors, spacing, typography } from './src/theme';

const TABS = [
  'home',
  'reels',
  'trending',
  'search',
  'notifs',
  'thread',
  'nearby',
  'stats',
  'graph',
];

const SCREENS = {
  home: HomeScreen,
  reels: ReelsScreen,
  trending: TrendingScreen,
  search: SearchScreen,
  notifs: NotificationsScreen,
  thread: ThreadScreen,
  nearby: NearbyScreen,
  stats: AnalyticsScreen,
  graph: CommunitiesScreen,
};

function AuthBar({ user, onLogin, onLogout, onRefresh }) {
  return (
    <View style={styles.authBar}>
      <GradientText style={[typography.label, styles.brand]}>petgram</GradientText>
      <View style={styles.authRight}>
        <Pressable onPress={onRefresh} hitSlop={10} style={styles.refreshBtn}>
          <RefreshGlyph size={18} color={colors.primary} />
        </Pressable>
        {user ? (
          <Pressable onPress={onLogout} hitSlop={8}>
            <Text style={styles.authAction}>@{user.username} · log out</Text>
          </Pressable>
        ) : (
          <Pressable onPress={onLogin} hitSlop={8}>
            <Text style={styles.authAction}>log in</Text>
          </Pressable>
        )}
      </View>
    </View>
  );
}

export default function App() {
  const [tab, setTab] = useState('home');
  const [user, setUser] = useState(null);
  const [loginVisible, setLoginVisible] = useState(false);
  const [loginBusy, setLoginBusy] = useState(false);
  const [loginError, setLoginError] = useState(null);
  const [stack, setStack] = useState([]);
  const [refreshNonce, setRefreshNonce] = useState(0);
  const [threadPostId, setThreadPostId] = useState(null);
  const idRef = useRef(0);

  // any 401 from the api opens the login prompt instead of erroring out
  useEffect(() => {
    setUnauthorizedHandler(() => setLoginVisible(true));
    return () => setUnauthorizedHandler(null);
  }, []);

  const handleLogin = useCallback(async (username, password) => {
    setLoginBusy(true);
    setLoginError(null);
    try {
      const res = await api.login(username, password);
      setToken(res.token);
      const me = await api.me();
      setUser(me);
      setLoginVisible(false);
    } catch (e) {
      setLoginError('that did not work. check the username and password.');
    } finally {
      setLoginBusy(false);
    }
  }, []);

  const handleLogout = useCallback(() => {
    setToken(null);
    setUser(null);
  }, []);

  const openLogin = useCallback(() => {
    setLoginError(null);
    setLoginVisible(true);
  }, []);

  const requireAuth = useCallback(
    (action) => {
      if (user) {
        if (typeof action === 'function') action();
        return true;
      }
      openLogin();
      return false;
    },
    [user, openLogin],
  );

  const push = useCallback((overlay) => {
    idRef.current += 1;
    setStack((s) => [...s, { id: idRef.current, ...overlay }]);
  }, []);

  const closeTop = useCallback(() => setStack((s) => s.slice(0, -1)), []);

  const openPost = useCallback((postId, post) => push({ type: 'post', postId, post }), [push]);
  const openProfile = useCallback(
    (identifier) => {
      if (!identifier) return;
      push({ type: 'profile', identifier: String(identifier) });
    },
    [push],
  );
  const openHashtag = useCallback((tag) => push({ type: 'hashtag', tag }), [push]);
  const openStory = useCallback((users, index = 0) => push({ type: 'story', users, index }), [push]);

  const goTab = useCallback((nextTab, params = {}) => {
    if (params.postId != null) setThreadPostId(params.postId);
    setStack([]);
    setTab(nextTab);
  }, []);

  const refresh = useCallback(() => setRefreshNonce((n) => n + 1), []);

  const ctx = useMemo(
    () => ({
      user,
      requireAuth,
      openLogin,
      openPost,
      openProfile,
      openHashtag,
      openStory,
      closeTop,
      goTab,
      refreshNonce,
      refresh,
    }),
    [user, requireAuth, openLogin, openPost, openProfile, openHashtag, openStory, closeTop, goTab, refreshNonce, refresh],
  );

  const ActiveScreen = SCREENS[tab];
  const topBar = (
    <View>
      <AuthBar user={user} onLogin={openLogin} onLogout={handleLogout} onRefresh={refresh} />
      <TabBar tabs={TABS} active={tab} onChange={(t) => goTab(t)} />
    </View>
  );

  // the thread tab takes an initial post id when a notification routes to it
  const screenProps = tab === 'thread' && threadPostId ? { postId: threadPostId } : {};

  return (
    <SafeAreaProvider>
      <AppContext.Provider value={ctx}>
        <RootShell topBar={topBar} overlay={stack.length ? <OverlayHost stack={stack} /> : null}>
          {/* remount screens on login/logout and on a refresh tap so they refetch */}
          <ActiveScreen key={`${user ? user.id : 'anon'}-${refreshNonce}`} {...screenProps} />
        </RootShell>
        <LoginModal
          visible={loginVisible}
          busy={loginBusy}
          error={loginError}
          onSubmit={handleLogin}
          onClose={() => setLoginVisible(false)}
        />
        <StatusBar style="dark" />
      </AppContext.Provider>
    </SafeAreaProvider>
  );
}

const styles = StyleSheet.create({
  authBar: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: spacing.lg,
    paddingTop: spacing.sm,
    paddingBottom: spacing.xs,
  },
  authRight: { flexDirection: 'row', alignItems: 'center' },
  refreshBtn: { marginRight: spacing.md, padding: 2 },
  brand: { color: colors.text, letterSpacing: 0.5 },
  authAction: { ...typography.label, color: colors.primary },
});
