// app entry. holds the lightweight auth state (token + current user) and shows
// a login prompt whenever an action needs a signed in user. the chrome lives in
// RootShell so any bottom navigator drop in later is a one prop change here.
import React, { useCallback, useEffect, useState } from 'react';
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
import GradientText from './src/components/GradientText';
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

function AuthBar({ user, onLogin, onLogout }) {
  return (
    <View style={styles.authBar}>
      <GradientText style={[typography.label, styles.brand]}>petgram</GradientText>
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
  );
}

export default function App() {
  const [tab, setTab] = useState('home');
  const [user, setUser] = useState(null);
  const [loginVisible, setLoginVisible] = useState(false);
  const [loginBusy, setLoginBusy] = useState(false);
  const [loginError, setLoginError] = useState(null);

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

  const ActiveScreen = SCREENS[tab];
  const topBar = (
    <View>
      <AuthBar user={user} onLogin={openLogin} onLogout={handleLogout} />
      <TabBar tabs={TABS} active={tab} onChange={setTab} />
    </View>
  );

  return (
    <SafeAreaProvider>
      <RootShell topBar={topBar}>
        {/* remount screens on login/logout so they refetch with the new token */}
        <ActiveScreen key={user ? user.id : 'anon'} />
      </RootShell>
      <LoginModal
        visible={loginVisible}
        busy={loginBusy}
        error={loginError}
        onSubmit={handleLogin}
        onClose={() => setLoginVisible(false)}
      />
      <StatusBar style="dark" />
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
  brand: { color: colors.text, letterSpacing: 0.5 },
  authAction: { ...typography.label, color: colors.primary },
});
