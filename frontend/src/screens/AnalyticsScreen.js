// ref: claude.md phase 6. lab 8 ex 3 segment tree exposed via /api/analytics.
// the screen accepts a username, asks for the daily series, and renders an
// ascii style bar chart so we don't need a charting library to demo it.

import React, { useCallback, useEffect, useMemo, useState } from 'react';
import {
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View,
} from 'react-native';

import { api } from '../api/client';
import { colors } from '../theme/colors';

const BAR_WIDTH = 24;

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
    // only show the last 60 days so the bar chart fits on a phone
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

  return (
    <View style={styles.container}>
      <View style={styles.topBar}>
        <Text style={styles.title}>analytics</Text>
        <TextInput
          value={username}
          onChangeText={setUsername}
          placeholder="username"
          placeholderTextColor={colors.muted}
          style={styles.input}
        />
        <Pressable onPress={load} style={[styles.btn, styles.btnPrimary]}>
          <Text style={[styles.btnText, styles.btnTextPrimary]}>load</Text>
        </Pressable>
      </View>
      <View style={styles.rangeRow}>
        <TextInput
          value={from}
          onChangeText={setFrom}
          placeholder="from YYYY-MM-DD"
          placeholderTextColor={colors.muted}
          style={[styles.input, { flex: 1 }]}
        />
        <TextInput
          value={to}
          onChangeText={setTo}
          placeholder="to YYYY-MM-DD"
          placeholderTextColor={colors.muted}
          style={[styles.input, { flex: 1 }]}
        />
        <Pressable onPress={load} style={styles.btn}>
          <Text style={styles.btnText}>range</Text>
        </Pressable>
      </View>
      {error ? <Text style={styles.error}>{error}</Text> : null}
      {range ? (
        <Text style={styles.summary}>
          {range.total_likes} likes between {range.from} and {range.to} (
          {range.days} days)
        </Text>
      ) : null}
      <ScrollView horizontal>
        <View style={styles.chart}>
          {visibleBuckets.map((b, idx) => (
            <View key={idx} style={styles.bar}>
              <View
                style={[
                  styles.barFill,
                  { height: 4 + (b.value / peak) * 100 },
                ]}
              />
              {idx % 7 === 0 ? (
                <Text style={styles.barLabel} numberOfLines={1}>
                  {formatDate(series?.origin, b.offset).slice(5)}
                </Text>
              ) : (
                <Text style={styles.barLabel}> </Text>
              )}
            </View>
          ))}
        </View>
      </ScrollView>
      {!loading && !visibleBuckets.length ? (
        <Text style={styles.empty}>no engagement yet</Text>
      ) : null}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background },
  topBar: {
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderBottomColor: colors.border,
    borderBottomWidth: 1,
    flexDirection: 'row',
    alignItems: 'center',
  },
  title: { color: colors.text, fontSize: 18, fontWeight: '600', marginRight: 12 },
  input: {
    color: colors.text,
    borderColor: colors.border,
    borderWidth: 1,
    paddingHorizontal: 8,
    paddingVertical: 6,
    minWidth: 120,
    marginRight: 6,
  },
  btn: {
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderColor: colors.border,
    borderWidth: 1,
  },
  btnPrimary: { borderColor: colors.primary },
  btnText: { color: colors.text, fontSize: 12 },
  btnTextPrimary: { color: colors.primary },
  rangeRow: {
    flexDirection: 'row',
    paddingHorizontal: 16,
    paddingVertical: 8,
    alignItems: 'center',
  },
  summary: {
    color: colors.text,
    paddingHorizontal: 16,
    paddingVertical: 8,
  },
  chart: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    paddingHorizontal: 16,
    paddingVertical: 12,
    minHeight: 160,
  },
  bar: {
    width: BAR_WIDTH,
    alignItems: 'center',
    marginRight: 2,
  },
  barFill: {
    width: BAR_WIDTH - 8,
    backgroundColor: colors.primary,
  },
  barLabel: { fontSize: 9, color: colors.muted, marginTop: 4 },
  empty: { color: colors.muted, textAlign: 'center', marginTop: 24 },
  error: { color: colors.text, padding: 12 },
});
