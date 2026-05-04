// ref: claude.md phase 5. lab 3 ex 2 NotificationQueue exposed over rest.
// pulling the list endpoint also drains the in memory queue, so this screen
// effectively acts as the consumer process when the user opens it.

import React, { useCallback, useEffect, useState } from 'react';
import {
  FlatList,
  Pressable,
  RefreshControl,
  StyleSheet,
  Text,
  View,
} from 'react-native';

import { api } from '../api/client';
import { colors } from '../theme/colors';

const KIND_LABEL = {
  like: 'liked your post',
  comment: 'commented on your post',
  reply: 'replied to your comment',
  follow: 'started following you',
};

export default function NotificationsScreen() {
  const [items, setItems] = useState([]);
  const [stats, setStats] = useState({ pending: 0, processed: 0 });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [list, queue] = await Promise.all([
        api.listNotifications(),
        api.notificationsQueueStats(),
      ]);
      setItems(list.results || list || []);
      setStats(queue || { pending: 0, processed: 0 });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  const drain = useCallback(async () => {
    try {
      await api.drainNotifications();
      await load();
    } catch (err) {
      setError(err.message);
    }
  }, [load]);

  const markRead = useCallback(async () => {
    try {
      await api.markNotificationsRead();
      await load();
    } catch (err) {
      setError(err.message);
    }
  }, [load]);

  useEffect(() => {
    load();
  }, [load]);

  return (
    <View style={styles.container}>
      <View style={styles.topBar}>
        <Text style={styles.title}>notifications</Text>
        <View style={styles.actions}>
          <Pressable onPress={drain} style={styles.btn}>
            <Text style={styles.btnText}>drain ({stats.pending})</Text>
          </Pressable>
          <Pressable onPress={markRead} style={[styles.btn, styles.btnPrimary]}>
            <Text style={[styles.btnText, styles.btnTextPrimary]}>mark read</Text>
          </Pressable>
        </View>
      </View>
      {error ? <Text style={styles.error}>{error}</Text> : null}
      <FlatList
        data={items}
        keyExtractor={(n) => String(n.id)}
        refreshControl={<RefreshControl refreshing={loading} onRefresh={load} />}
        renderItem={({ item }) => (
          <View
            style={[
              styles.row,
              !item.is_read && styles.rowUnread,
              item.is_priority && styles.rowPriority,
            ]}
          >
            <Text style={styles.rowText}>
              <Text style={styles.bold}>@{item.actor_username}</Text>{' '}
              {KIND_LABEL[item.kind] || item.kind}
            </Text>
            <Text style={styles.meta}>
              {new Date(item.created_at).toLocaleString()}
              {item.is_priority ? ' · priority' : ''}
            </Text>
          </View>
        )}
        ListEmptyComponent={
          !loading ? <Text style={styles.empty}>no notifications</Text> : null
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
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  title: { color: colors.text, fontSize: 18, fontWeight: '600' },
  actions: { flexDirection: 'row' },
  btn: {
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderColor: colors.border,
    borderWidth: 1,
    marginLeft: 6,
  },
  btnPrimary: { borderColor: colors.primary },
  btnText: { color: colors.text, fontSize: 12 },
  btnTextPrimary: { color: colors.primary },
  row: {
    padding: 12,
    borderBottomColor: colors.border,
    borderBottomWidth: 1,
  },
  rowUnread: { backgroundColor: '#f7f7f7' },
  rowPriority: { borderLeftColor: colors.primary, borderLeftWidth: 3 },
  rowText: { color: colors.text },
  bold: { fontWeight: '600' },
  meta: { color: colors.muted, fontSize: 12, marginTop: 4 },
  empty: { color: colors.muted, textAlign: 'center', marginTop: 24 },
  error: { color: colors.text, padding: 12 },
});
