// app entry. the chrome lives in RootShell so any bottom navigator drop in
// later is a one prop change here.
import React, { useState } from 'react';
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

export default function App() {
  const [tab, setTab] = useState('home');
  const ActiveScreen = SCREENS[tab];
  return (
    <SafeAreaProvider>
      <RootShell topBar={<TabBar tabs={TABS} active={tab} onChange={setTab} />}>
        <ActiveScreen />
      </RootShell>
      <StatusBar style="dark" />
    </SafeAreaProvider>
  );
}
