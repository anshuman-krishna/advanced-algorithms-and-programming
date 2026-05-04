import React, { useState } from 'react';
import { StatusBar } from 'expo-status-bar';
import { SafeAreaProvider, SafeAreaView } from 'react-native-safe-area-context';
import { Pressable, StyleSheet, Text, View } from 'react-native';

import HomeScreen from './src/screens/HomeScreen';
import TrendingScreen from './src/screens/TrendingScreen';
import SearchScreen from './src/screens/SearchScreen';
import { colors } from './src/theme/colors';

const TABS = ['home', 'trending', 'search'];

export default function App() {
  const [tab, setTab] = useState('home');
  return (
    <SafeAreaProvider>
      <SafeAreaView style={styles.root}>
        <View style={styles.tabbar}>
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
        </View>
        {tab === 'home' && <HomeScreen />}
        {tab === 'trending' && <TrendingScreen />}
        {tab === 'search' && <SearchScreen />}
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
  tab: { flex: 1, paddingVertical: 12, alignItems: 'center' },
  tabActive: { borderBottomColor: colors.primary, borderBottomWidth: 2 },
  tabText: { color: colors.muted },
  tabTextActive: { color: colors.text, fontWeight: '600' },
});
