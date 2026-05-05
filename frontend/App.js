// app shell. wraps the active screen in a phone-shaped container on web and
// renders the gradient tabbar above it. each screen owns its own padding so
// the shell only handles outer chrome.
import React, { useState } from 'react';
import { Platform, StyleSheet, View } from 'react-native';
import { StatusBar } from 'expo-status-bar';
import { SafeAreaProvider, SafeAreaView } from 'react-native-safe-area-context';

import HomeScreen from './src/screens/HomeScreen';
import TrendingScreen from './src/screens/TrendingScreen';
import SearchScreen from './src/screens/SearchScreen';
import ReelsScreen from './src/screens/ReelsScreen';
import NotificationsScreen from './src/screens/NotificationsScreen';
import ThreadScreen from './src/screens/ThreadScreen';
import NearbyScreen from './src/screens/NearbyScreen';
import AnalyticsScreen from './src/screens/AnalyticsScreen';
import CommunitiesScreen from './src/screens/CommunitiesScreen';
import TabBar from './src/components/TabBar';
import { colors, layout } from './src/theme';

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

const isWeb = Platform.OS === 'web';

export default function App() {
  const [tab, setTab] = useState('home');
  const ActiveScreen = SCREENS[tab];

  return (
    <SafeAreaProvider>
      <View style={styles.outer}>
        <View style={styles.shell}>
          <SafeAreaView style={styles.safe} edges={['top']}>
            <TabBar tabs={TABS} active={tab} onChange={setTab} />
            <View style={styles.body}>
              <ActiveScreen />
            </View>
            <StatusBar style="dark" />
          </SafeAreaView>
        </View>
      </View>
    </SafeAreaProvider>
  );
}

const styles = StyleSheet.create({
  outer: {
    flex: 1,
    backgroundColor: isWeb ? '#ececef' : colors.background,
    alignItems: 'center',
    justifyContent: 'center',
  },
  shell: {
    flex: 1,
    width: '100%',
    maxWidth: layout.maxAppWidth,
    backgroundColor: colors.background,
    ...(isWeb && {
      shadowColor: '#000',
      shadowOpacity: 0.12,
      shadowRadius: 28,
      shadowOffset: { width: 0, height: 6 },
    }),
  },
  safe: { flex: 1, backgroundColor: colors.background },
  body: { flex: 1, backgroundColor: colors.background },
});
