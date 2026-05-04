// ref: claude.md phase 5. lab 3 ex 1 doubly linked list backed reels feed.
// the dll lives on the backend; the screen just calls reelsPage with a cursor
// and lets the backend walk forward / backward through it.

import React, { useCallback, useEffect, useRef, useState } from 'react';
import {
  Pressable,
  RefreshControl,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from 'react-native';

import { api } from '../api/client';
import { colors } from '../theme/colors';

export default function ReelsScreen() {
  const [items, setItems] = useState([]);
  const [cursor, setCursor] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const seen = useRef(new Set());

  const load = useCallback(
    async (direction = 'next', anchor = cursor) => {
      setLoading(true);
      setError(null);
      try {
        const res = await api.reelsPage(anchor, direction, 5);
        const fresh = (res.results || []).filter((p) => !seen.current.has(p.id));
        fresh.forEach((p) => seen.current.add(p.id));
        if (direction === 'next') {
          setItems((prev) => [...prev, ...fresh]);
        } else {
          setItems((prev) => [...fresh.reverse(), ...prev]);
        }
        if (res.next_cursor != null) setCursor(res.next_cursor);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    },
    [cursor],
  );

  const refresh = useCallback(async () => {
    seen.current = new Set();
    setItems([]);
    setCursor(null);
    await load('next', null);
  }, [load]);

  const markViewed = useCallback(async (postId) => {
    try {
      await api.reelsMarkViewed(postId);
    } catch (err) {
      // viewing is best effort; do not surface as an error
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  return (
    <View style={styles.container}>
      <View style={styles.topBar}>
        <Text style={styles.title}>reels</Text>
        <Text style={styles.meta}>{items.length} loaded</Text>
      </View>
      {error ? <Text style={styles.error}>{error}</Text> : null}
      <ScrollView
        refreshControl={<RefreshControl refreshing={loading} onRefresh={refresh} />}
        onMomentumScrollEnd={({ nativeEvent }) => {
          const { layoutMeasurement, contentOffset, contentSize } = nativeEvent;
          const atBottom =
            layoutMeasurement.height + contentOffset.y >= contentSize.height - 40;
          if (atBottom && !loading) load('next');
        }}
      >
        {items.map((p) => (
          <Pressable key={p.id} onPress={() => markViewed(p.id)} style={styles.card}>
            <View style={styles.cardHead}>
              <Text style={styles.author}>@{p.author_username}</Text>
              <Text style={styles.meta}>views {p.views}</Text>
            </View>
            <Text style={styles.caption} numberOfLines={3}>
              {p.caption || '(no caption)'}
            </Text>
            <Text style={styles.meta}>
              {p.like_count} likes · {new Date(p.created_at).toLocaleString()}
            </Text>
          </Pressable>
        ))}
        {!loading && items.length === 0 ? (
          <Text style={styles.empty}>no reels yet, seed the backend</Text>
        ) : null}
      </ScrollView>
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
    justifyContent: 'space-between',
  },
  title: { color: colors.text, fontSize: 18, fontWeight: '600' },
  meta: { color: colors.muted, fontSize: 12 },
  card: {
    padding: 16,
    borderBottomColor: colors.border,
    borderBottomWidth: 1,
  },
  cardHead: { flexDirection: 'row', justifyContent: 'space-between' },
  author: { color: colors.text, fontWeight: '600' },
  caption: { color: colors.text, marginVertical: 8, fontSize: 16 },
  empty: { color: colors.muted, textAlign: 'center', marginTop: 24 },
  error: { color: colors.text, padding: 12 },
});
