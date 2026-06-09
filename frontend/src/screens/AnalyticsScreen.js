// analytics screen powered by the lab 8 segment tree. range total goes inside
// a gradient-bordered summary card; the 60 day histogram bars use the brand
// gradient so the numbers read at a glance.
import React, { useCallback, useEffect, useMemo, useState } from 'react';
import {
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';

import { api } from '../api/client';
import EmptyState from '../components/EmptyState';
import GradientButton from '../components/GradientButton';
import GradientCardBorder from '../components/GradientCardBorder';
import GradientProgress from '../components/GradientProgress';
import GradientText from '../components/GradientText';
import OutlineButton from '../components/OutlineButton';
import ScreenContainer from '../components/ScreenContainer';
import StatRow from '../components/StatRow';
import {
  colors,
  gradientDir,
  gradientStops,
  radii,
  spacing,
  typography,
} from '../theme';

const BAR_WIDTH = 14;

function formatDate(originIso, offset) {
  if (!originIso) return '';
  const d = new Date(originIso);
  d.setDate(d.getDate() + offset);
  return d.toISOString().slice(0, 10);
}

export default function AnalyticsScreen() {
  const [username, setUsername] = useState('alice');
  const [from, setFrom] = useState('');
  const [to, setTo] = useState('');
  const [series, setSeries] = useState(null);
  const [range, setRange] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const load = useCallback(async () => {
    if (!username) return;
    setLoading(true);
    setError(null);
    try {
      const seriesPayload = await api.likesSeries(username);
      setSeries(seriesPayload);
      const rangePayload = await api.likesRange(username, from, to);
      setRange(rangePayload);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [username, from, to]);

  useEffect(() => {
    load();
  }, [load]);

  const visibleBuckets = useMemo(() => {
    if (!series) return [];
    const tail = series.series.slice(-60);
    return tail.map((value, idx) => ({
      value,
      offset: series.window_days - tail.length + idx,
    }));
  }, [series]);

  const peak = useMemo(() => {
    if (!visibleBuckets.length) return 1;
    return Math.max(1, ...visibleBuckets.map((b) => b.value));
  }, [visibleBuckets]);

  const commentBuckets = useMemo(() => {
    if (!series || !series.comment_series) return [];
    const tail = series.comment_series.slice(-60);
    return tail.map((value, idx) => ({
      value,
      offset: series.window_days - tail.length + idx,
    }));
  }, [series]);

  const commentPeak = useMemo(() => {
    if (!commentBuckets.length) return 1;
    return Math.max(1, ...commentBuckets.map((b) => b.value));
  }, [commentBuckets]);

  return (
    <ScreenContainer>
      <View style={styles.header}>
        <View style={{ flex: 1 }}>
          <Text style={[typography.display, { color: colors.text }]}>insights</Text>
          {/* internal: range queries off the lab 8 segment tree */}
          <Text style={[typography.caption, { color: colors.muted }]}>
            likes and comments over any date range
          </Text>
        </View>
      </View>
      <View style={styles.controlRow}>
        <TextInput
          value={username}
          onChangeText={setUsername}
          placeholder="username"
          placeholderTextColor={colors.muted}
          style={styles.input}
          autoCapitalize="none"
        />
        <GradientButton label="load" onPress={load} size="sm" />
      </View>
      <View style={styles.rangeRow}>
        <TextInput
          value={from}
          onChangeText={setFrom}
          placeholder="from yyyy-mm-dd"
          placeholderTextColor={colors.muted}
          style={[styles.input, { flex: 1 }]}
        />
        <TextInput
          value={to}
          onChangeText={setTo}
          placeholder="to yyyy-mm-dd"
          placeholderTextColor={colors.muted}
          style={[styles.input, { flex: 1 }]}
        />
        <OutlineButton label="apply" onPress={load} size="sm" />
      </View>
      <GradientProgress active={loading} />
      <ScrollView contentContainerStyle={styles.scrollBody}>
      {range ? (
        <View style={styles.summaryWrap}>
          <GradientCardBorder>
            <View style={styles.summary}>
              <View style={styles.summaryNums}>
                <View style={styles.summaryMetric}>
                  <GradientText style={[typography.display, { fontSize: 32 }]}>
                    {range.total_likes}
                  </GradientText>
                  <Text style={[typography.caption, { color: colors.muted }]}>likes</Text>
                </View>
                <View style={styles.summaryMetric}>
                  <GradientText style={[typography.display, { fontSize: 32 }]}>
                    {range.total_comments ?? 0}
                  </GradientText>
                  <Text style={[typography.caption, { color: colors.muted }]}>comments</Text>
                </View>
              </View>
              <Text style={[typography.body, { color: colors.text, marginTop: spacing.sm }]}>
                for @{range.username}
              </Text>
              <Text style={[typography.caption, { color: colors.muted, marginTop: 2 }]}>
                {range.from} . {range.to} . {range.days} days
              </Text>
            </View>
          </GradientCardBorder>
        </View>
      ) : null}
      {visibleBuckets.length ? (
        <View style={styles.chartWrap}>
          <Text style={[typography.label, styles.sectionTitle]}>
            last 60 days
          </Text>
          <ScrollView
            horizontal
            showsHorizontalScrollIndicator={false}
            contentContainerStyle={styles.chart}
          >
            {visibleBuckets.map((b, idx) => {
              const height = 4 + (b.value / peak) * 110;
              return (
                <View key={idx} style={styles.barWrap}>
                  <LinearGradient
                    colors={gradientStops}
                    start={gradientDir.vertical.start}
                    end={gradientDir.vertical.end}
                    style={[styles.bar, { height }]}
                  />
                  {idx % 7 === 0 ? (
                    <Text style={styles.barLabel} numberOfLines={1}>
                      {formatDate(series?.origin, b.offset).slice(5)}
                    </Text>
                  ) : (
                    <Text style={styles.barLabel}> </Text>
                  )}
                </View>
              );
            })}
          </ScrollView>
          <View style={styles.statBar}>
            <StatRow
              size="sm"
              items={[
                { value: series.window_days, label: 'window days' },
                { value: visibleBuckets.reduce((s, b) => s + b.value, 0), label: 'shown likes' },
                { value: peak, label: 'peak day' },
              ]}
            />
          </View>
        </View>
      ) : !loading ? (
        <EmptyState
          glyph="a"
          title="no engagement yet"
          body="no likes in this date range yet. pick a wider range and reload."
        />
      ) : null}
      {commentBuckets.length ? (
        <View style={styles.chartWrap}>
          <Text style={[typography.label, styles.sectionTitle]}>
            comments last 60 days
          </Text>
          <ScrollView
            horizontal
            showsHorizontalScrollIndicator={false}
            contentContainerStyle={styles.chart}
          >
            {commentBuckets.map((b, idx) => {
              const height = 4 + (b.value / commentPeak) * 110;
              return (
                <View key={idx} style={styles.barWrap}>
                  <LinearGradient
                    colors={gradientStops}
                    start={gradientDir.vertical.start}
                    end={gradientDir.vertical.end}
                    style={[styles.bar, { height }]}
                  />
                  {idx % 7 === 0 ? (
                    <Text style={styles.barLabel} numberOfLines={1}>
                      {formatDate(series?.origin, b.offset).slice(5)}
                    </Text>
                  ) : (
                    <Text style={styles.barLabel}> </Text>
                  )}
                </View>
              );
            })}
          </ScrollView>
          <View style={styles.statBar}>
            <StatRow
              size="sm"
              items={[
                { value: commentBuckets.reduce((s, b) => s + b.value, 0), label: 'shown comments' },
                { value: commentPeak, label: 'peak day' },
              ]}
            />
          </View>
        </View>
      ) : null}
      {error ? <Text style={styles.error}>{error}</Text> : null}
      </ScrollView>
    </ScreenContainer>
  );
}

const styles = StyleSheet.create({
  header: {
    paddingHorizontal: spacing.lg,
    paddingTop: spacing.md,
    paddingBottom: spacing.sm,
    flexDirection: 'row',
    alignItems: 'center',
  },
  controlRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: spacing.lg,
    paddingBottom: spacing.sm,
  },
  rangeRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: spacing.lg,
    paddingBottom: spacing.sm,
  },
  input: {
    color: colors.text,
    backgroundColor: colors.inputBackground,
    borderRadius: radii.md,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    minWidth: 120,
    marginRight: spacing.sm,
    flexShrink: 1,
  },
  scrollBody: { paddingBottom: spacing.xxl },
  summaryWrap: { paddingHorizontal: spacing.lg, paddingTop: spacing.md },
  summary: {
    padding: spacing.lg,
    backgroundColor: colors.background,
    borderRadius: radii.md,
  },
  summaryNums: { flexDirection: 'row' },
  summaryMetric: { flex: 1, alignItems: 'flex-start' },
  chartWrap: {
    paddingHorizontal: spacing.lg,
    paddingTop: spacing.lg,
  },
  sectionTitle: {
    color: colors.muted,
    marginBottom: spacing.sm,
    textTransform: 'uppercase',
  },
  chart: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    paddingVertical: spacing.sm,
    minHeight: 140,
  },
  barWrap: { width: BAR_WIDTH, alignItems: 'center', marginRight: 4 },
  bar: { width: BAR_WIDTH - 4, borderRadius: 2 },
  barLabel: { fontSize: 9, color: colors.muted, marginTop: 4 },
  statBar: { marginTop: spacing.sm },
  error: { color: colors.text, padding: spacing.md },
});
