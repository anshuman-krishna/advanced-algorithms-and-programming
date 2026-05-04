import React, { useCallback, useEffect, useState } from 'react';
import { FlatList, RefreshControl, StyleSheet, Text, View } from 'react-native';

import { colors } from '../theme/colors';

const TRENDING_PATH = '/api/feed/trending/?k=20';

export default function TrendingScreen() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const base = process.env.EXPO_PUBLIC_API_BASE || 'http://127.0.0.1:8000';
      const res = await fetch(`${base}${TRENDING_PATH}`);
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

  return (
    <View style={styles.container}>
      <View style={styles.topBar}>
        <Text style={styles.title}>trending</Text>
      </View>
      {error ? <Text style={styles.error}>{error}</Text> : null}
      <FlatList
        data={items}
        keyExtractor={(item) => String(item.post_id)}
        renderItem={({ item, index }) => (
          <View style={styles.row}>
            <Text style={styles.rank}>#{index + 1}</Text>
            <View style={styles.body}>
              <Text style={styles.author}>@{item.author_username}</Text>
              <Text style={styles.caption} numberOfLines={2}>
                {item.caption || '(no caption)'}
              </Text>
              <Text style={styles.meta}>
                {item.likes} likes · score {item.score?.toFixed(3)}
              </Text>
            </View>
          </View>
        )}
        refreshControl={<RefreshControl refreshing={loading} onRefresh={load} />}
        ListEmptyComponent={
          !loading ? <Text style={styles.empty}>nothing trending yet</Text> : null
        }
      />
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
  },
  title: { color: colors.text, fontSize: 18, fontWeight: '600' },
  row: {
    flexDirection: 'row',
    padding: 12,
    borderBottomColor: colors.border,
    borderBottomWidth: 1,
  },
  rank: { color: colors.text, fontWeight: '600', width: 36 },
  body: { flex: 1 },
  author: { color: colors.text, fontWeight: '600' },
  caption: { color: colors.text, marginTop: 2 },
  meta: { color: colors.muted, fontSize: 12, marginTop: 4 },
  empty: { color: colors.muted, textAlign: 'center', marginTop: 24 },
  error: { color: colors.text, padding: 12 },
});
