// notifications inbox. listing the endpoint also drains the lab 3 ex 2
// queue, so this screen acts as the consumer when opened. unread rows get
// a soft tinted background and a gradient dot; priority rows surface a
// gradient left border to call out the lab 3 priority lane.
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
import AvatarRing from '../components/AvatarRing';
import EmptyState from '../components/EmptyState';
import GradientButton from '../components/GradientButton';
import GradientDot from '../components/GradientDot';
import GradientProgress from '../components/GradientProgress';
import GradientText from '../components/GradientText';
import OutlineButton from '../components/OutlineButton';
import ScreenContainer from '../components/ScreenContainer';
import StatPill from '../components/StatPill';
import { colors, radii, spacing, typography } from '../theme';

const KIND_LABEL = {
  like: 'liked your post',
  comment: 'commented on your post',
  reply: 'replied to your comment',
  follow: 'started following you',
};

function formatRel(ts) {
  if (!ts) return '';
  const diff = Math.max(0, Date.now() - new Date(ts).getTime()) / 1000;
  if (diff < 60) return `${Math.floor(diff)}s`;
  if (diff < 3600) return `${Math.floor(diff / 60)}m`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}h`;
  return `${Math.floor(diff / 86400)}d`;
}

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

  const unread = items.filter((n) => !n.is_read).length;

  return (
    <ScreenContainer>
      <View style={styles.header}>
        <View style={{ flex: 1 }}>
          <Text style={[typography.display, styles.title]}>activity</Text>
          {/* internal: backed by the lab 3 fifo + priority queue */}
          <Text style={[typography.caption, styles.subtitle]}>
            likes, comments, and new followers as they happen
          </Text>
        </View>
        <View style={styles.statBlock}>
          <StatPill value={unread} label="unread" />
          <StatPill value={stats.pending} label="pending" />
        </View>
      </View>
      <View style={styles.actions}>
        <OutlineButton label={`drain ${stats.pending}`} onPress={drain} size="sm" />
        <View style={{ width: spacing.sm }} />
        <GradientButton label="mark all read" onPress={markRead} size="sm" />
      </View>
      <GradientProgress active={loading} />
      <FlatList
        data={items}
        keyExtractor={(n) => String(n.id)}
        refreshControl={
          <RefreshControl
            refreshing={loading}
            onRefresh={load}
            tintColor={colors.primary}
            colors={[colors.primary]}
          />
        }
        contentContainerStyle={styles.list}
        renderItem={({ item }) => (
          <View
            style={[
              styles.row,
              !item.is_read && styles.rowUnread,
              item.is_priority && styles.rowPriority,
            ]}
          >
            <AvatarRing username={item.actor_username || ''} size={40} />
            <View style={styles.body}>
              <Text style={[typography.body, { color: colors.text }]} numberOfLines={2}>
                <Text style={typography.bodyStrong}>@{item.actor_username} </Text>
                {KIND_LABEL[item.kind] || item.kind}
              </Text>
              <View style={styles.metaLine}>
                <Text style={[typography.caption, { color: colors.muted }]}>
                  {formatRel(item.created_at)}
                </Text>
                {item.is_priority ? (
                  <>
                    <Text style={[typography.caption, { color: colors.muted, marginHorizontal: spacing.xs }]}>
                      .
                    </Text>
                    <GradientText style={[typography.caption, { fontWeight: '700' }]}>
                      priority
                    </GradientText>
                  </>
                ) : null}
              </View>
            </View>
            {!item.is_read ? <GradientDot size={10} /> : null}
          </View>
        )}
        ListEmptyComponent={
          !loading ? (
            <EmptyState
              glyph="n"
              title="no activity yet"
              body="likes, comments, replies, and follows will land here as the queue drains."
            />
          ) : null
        }
      />
      {error ? <Text style={styles.error}>{error}</Text> : null}
    </ScreenContainer>
  );
}

const styles = StyleSheet.create({
  header: {
    paddingHorizontal: spacing.lg,
    paddingTop: spacing.md,
    paddingBottom: spacing.sm,
    flexDirection: 'row',
    alignItems: 'flex-end',
  },
  title: { color: colors.text },
  subtitle: { color: colors.muted, marginTop: 2 },
  statBlock: { flexDirection: 'row', alignItems: 'baseline' },
  actions: {
    flexDirection: 'row',
    paddingHorizontal: spacing.lg,
    paddingBottom: spacing.sm,
  },
  list: { paddingTop: spacing.sm, paddingBottom: spacing.xxl, flexGrow: 1 },
  row: {
    flexDirection: 'row',
    alignItems: 'center',
    marginHorizontal: spacing.lg,
    marginBottom: spacing.sm,
    padding: spacing.md,
    borderRadius: radii.md,
    backgroundColor: colors.background,
    borderWidth: 1,
    borderColor: colors.border,
  },
  rowUnread: { backgroundColor: '#fff8fb' },
  rowPriority: { borderLeftColor: '#d62976', borderLeftWidth: 3 },
  body: { flex: 1, marginLeft: spacing.md, marginRight: spacing.sm },
  metaLine: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 2,
  },
  error: { color: colors.text, padding: spacing.md },
});
