// trending feed. each row carries the lab 8 max heap rank, the lab 3
// priority queue score visualised as a gradient progress bar, and the
// engagement number rendered in the brand gradient so it pops at a glance.
import React, { useCallback, useEffect, useMemo, useState } from 'react';
import {
  FlatList,
  Pressable,
  StyleSheet,
  Text,
  View,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';

import { api } from '../api/client';
import { useApp } from '../context/AppContext';
import AvatarRing from '../components/AvatarRing';
import EmptyState from '../components/EmptyState';
import GradientProgress from '../components/GradientProgress';
import RankBadge from '../components/RankBadge';
import ScreenContainer from '../components/ScreenContainer';
import SectionDivider from '../components/SectionDivider';
import StatRow from '../components/StatRow';
import {
  colors,
  gradientDir,
  gradientStops,
  radii,
  spacing,
  typography,
} from '../theme';

export default function TrendingScreen() {
  const { openPost, openProfile } = useApp();
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const base = process.env.EXPO_PUBLIC_API_BASE || 'http://127.0.0.1:8000';
      // wide window so the ranked list stays full even when posts are spread
      // across the last few weeks rather than the last few hours
      const res = await fetch(`${base}/api/feed/trending/?k=20&window_hours=720`);
      if (!res.ok) throw new Error(`api ${res.status}`);
      const json = await res.json();
      setItems(json.results || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const peakScore = useMemo(() => {
    return items.reduce((m, it) => Math.max(m, it.score || 0), 0.0001);
  }, [items]);

  return (
    <ScreenContainer>
      <View style={styles.header}>
        <Text style={[typography.display, styles.title]}>trending</Text>
        {/* internal: ranked by the lab 8 max heap, scored by the lab 3 priority queue */}
        <Text style={[typography.caption, styles.subtitle]}>
          the posts everyone is on right now
        </Text>
      </View>
      <GradientProgress active={loading} />
      <FlatList
        data={items}
        keyExtractor={(item) => String(item.post_id)}
        ItemSeparatorComponent={() => <SectionDivider inset={spacing.lg} />}
        contentContainerStyle={styles.list}
        renderItem={({ item, index }) => (
          <Pressable style={styles.row} onPress={() => openPost(item.post_id)}>
            <Pressable onPress={() => openProfile(item.author_username)} hitSlop={4}>
              <AvatarRing username={item.author_username || ''} size={42} />
            </Pressable>
            <View style={styles.body}>
              <View style={styles.headRow}>
                <RankBadge rank={index + 1} />
                <Text
                  style={[typography.bodyStrong, styles.author]}
                  onPress={() => openProfile(item.author_username)}
                >
                  @{item.author_username}
                </Text>
              </View>
              <Text style={[typography.body, styles.caption]} numberOfLines={2}>
                {item.caption || 'no caption'}
              </Text>
              <View style={styles.scoreTrack}>
                <LinearGradient
                  colors={gradientStops}
                  start={gradientDir.horizontal.start}
                  end={gradientDir.horizontal.end}
                  style={[
                    styles.scoreFill,
                    { width: `${Math.min(100, ((item.score || 0) / peakScore) * 100)}%` },
                  ]}
                />
              </View>
              <View style={styles.statsLine}>
                <StatRow
                  size="sm"
                  items={[
                    { value: item.likes || 0, label: 'likes' },
                    { value: Number((item.score || 0).toFixed(2)), label: 'score' },
                  ]}
                />
              </View>
            </View>
          </Pressable>
        )}
        ListEmptyComponent={
          !loading ? (
            <EmptyState
              glyph="t"
              title="no trending posts yet"
              body="trending fills in as posts collect likes. check back in a bit."
            />
          ) : null
        }
      />
      {error ? <Text style={styles.error}>{error}</Text> : null}
    </ScreenContainer>
  );
}

const styles = StyleSheet.create({
  header: { paddingHorizontal: spacing.lg, paddingTop: spacing.md, paddingBottom: spacing.sm },
  title: { color: colors.text },
  subtitle: { color: colors.muted, marginTop: 2 },
  list: { paddingTop: spacing.sm, paddingBottom: spacing.xxl, flexGrow: 1 },
  row: {
    flexDirection: 'row',
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
  },
  body: { flex: 1, marginLeft: spacing.md },
  headRow: { flexDirection: 'row', alignItems: 'center', marginBottom: spacing.xs },
  author: { color: colors.text, marginLeft: spacing.sm },
  caption: { color: colors.text },
  scoreTrack: {
    marginTop: spacing.sm,
    height: 4,
    width: '100%',
    backgroundColor: colors.surfaceMuted,
    borderRadius: radii.sm,
    overflow: 'hidden',
  },
  scoreFill: { height: 4, borderRadius: radii.sm },
  statsLine: { marginTop: spacing.sm },
  error: { color: colors.text, padding: spacing.md },
});
