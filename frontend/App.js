import React, { useState } from 'react';
import { StatusBar } from 'expo-status-bar';
import { SafeAreaProvider, SafeAreaView } from 'react-native-safe-area-context';
import { Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';

import HomeScreen from './src/screens/HomeScreen';
import TrendingScreen from './src/screens/TrendingScreen';
import SearchScreen from './src/screens/SearchScreen';
import ReelsScreen from './src/screens/ReelsScreen';
import NotificationsScreen from './src/screens/NotificationsScreen';
import ThreadScreen from './src/screens/ThreadScreen';
import NearbyScreen from './src/screens/NearbyScreen';
import AnalyticsScreen from './src/screens/AnalyticsScreen';
import CommunitiesScreen from './src/screens/CommunitiesScreen';
import { colors } from './src/theme/colors';

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

export default function App() {
  const [tab, setTab] = useState('home');
  return (
    <SafeAreaProvider>
      <SafeAreaView style={styles.root}>
        <ScrollView
          horizontal
          showsHorizontalScrollIndicator={false}
          contentContainerStyle={styles.tabbar}
        >
          {TABS.map((name) => (
            <Pressable
              key={name}
              onPress={() => setTab(name)}
              style={[styles.tab, tab === name && styles.tabActive]}
            >
              <Text style={[styles.tabText, tab === name && styles.tabTextActive]}>
                {name}
              </Text>
            </Pressable>
          ))}
        </ScrollView>
        {tab === 'home' && <HomeScreen />}
        {tab === 'reels' && <ReelsScreen />}
        {tab === 'trending' && <TrendingScreen />}
        {tab === 'search' && <SearchScreen />}
        {tab === 'notifs' && <NotificationsScreen />}
        {tab === 'thread' && <ThreadScreen />}
        {tab === 'nearby' && <NearbyScreen />}
        {tab === 'stats' && <AnalyticsScreen />}
        {tab === 'graph' && <CommunitiesScreen />}
        <StatusBar style="dark" />
      </SafeAreaView>
    </SafeAreaProvider>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: colors.background },
  tabbar: {
    flexDirection: 'row',
    borderBottomColor: colors.border,
    borderBottomWidth: 1,
  },
  tab: { paddingVertical: 12, paddingHorizontal: 18, alignItems: 'center' },
  tabActive: { borderBottomColor: colors.primary, borderBottomWidth: 2 },
  tabText: { color: colors.muted },
  tabTextActive: { color: colors.text, fontWeight: '600' },
});
