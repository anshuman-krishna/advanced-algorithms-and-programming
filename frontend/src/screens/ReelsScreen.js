// reels feed. each card takes the full screen height and snaps. text and
// action buttons sit on a dark gradient scrim so white reads cleanly. the
// dll on the backend (lab 3 ex 1) drives cursor pagination; we mark a card
// viewed when the user pauses on it for a moment.
import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import {
  Dimensions,
  FlatList,
  Image,
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
import GradientButton from '../components/GradientButton';
import GradientProgress from '../components/GradientProgress';
import StatRow from '../components/StatRow';
import { colors, spacing, typography } from '../theme';

function formatRel(ts) {
  if (!ts) return '';
  const diff = Math.max(0, Date.now() - new Date(ts).getTime()) / 1000;
  if (diff < 60) return `${Math.floor(diff)}s ago`;
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
  return `${Math.floor(diff / 86400)}d ago`;
}

export default function ReelsScreen() {
  const [items, setItems] = useState([]);
  const [cursor, setCursor] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [cardHeight, setCardHeight] = useState(
    Dimensions.get('window').height - 120,
  );
  const seen = useRef(new Set());
  const viewedRef = useRef(new Set());

  const load = useCallback(
    async (anchor = cursor) => {
      setLoading(true);
      setError(null);
      try {
        const res = await api.reelsPage(anchor, 'next', 5);
        const fresh = (res.results || []).filter((p) => !seen.current.has(p.id));
        fresh.forEach((p) => seen.current.add(p.id));
        setItems((prev) => [...prev, ...fresh]);
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
    viewedRef.current = new Set();
    setItems([]);
    setCursor(null);
    await load(null);
  }, [load]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const onViewable = useCallback(({ viewableItems }) => {
    viewableItems.forEach((entry) => {
      const id = entry.item?.id;
      if (id == null || viewedRef.current.has(id)) return;
      viewedRef.current.add(id);
      api.reelsMarkViewed(id).catch(() => undefined);
    });
  }, []);

  const viewabilityConfig = useMemo(
    () => ({ itemVisiblePercentThreshold: 70 }),
    [],
  );

  return (
    <View style={styles.container} onLayout={(e) => setCardHeight(e.nativeEvent.layout.height)}>
      <GradientProgress active={loading} />
      <FlatList
        data={items}
        keyExtractor={(item) => String(item.id)}
        snapToInterval={cardHeight}
        decelerationRate="fast"
        snapToAlignment="start"
        showsVerticalScrollIndicator={false}
        onEndReached={() => !loading && load()}
        onEndReachedThreshold={0.6}
        onViewableItemsChanged={onViewable}
        viewabilityConfig={viewabilityConfig}
        renderItem={({ item, index }) => (
          <ReelCard item={item} index={index} height={cardHeight} />
        )}
        ListEmptyComponent={
          !loading ? (
            <View style={{ height: cardHeight }}>
              <EmptyState
                glyph="r"
                title="no reels yet"
                body="pull down to refresh and the latest posts will show up here."
              />
            </View>
          ) : null
        }
      />
      {error ? <Text style={styles.error}>{error}</Text> : null}
    </View>
  );
}

function ReelCard({ item, height }) {
  const { requireAuth, openProfile, openPost } = useApp();
  const [following, setFollowing] = useState(false);
  const [liked, setLiked] = useState(Boolean(item.is_liked));
  const [likes, setLikes] = useState(item.like_count || 0);

  const author = item.author_username || '';

  const follow = useCallback(async () => {
    if (!requireAuth()) return;
    const next = !following;
    setFollowing(next);
    try {
      await api.toggleFollow(author);
    } catch (e) {
      setFollowing(!next);
    }
  }, [following, author, requireAuth]);

  const toggleLike = useCallback(async () => {
    if (!requireAuth()) return;
    const next = !liked;
    setLiked(next);
    setLikes((n) => n + (next ? 1 : -1));
    try {
      if (next) await api.likePost(item.id);
      else await api.unlikePost(item.id);
    } catch (e) {
      setLiked(!next);
      setLikes((n) => n + (next ? -1 : 1));
    }
  }, [liked, item.id, requireAuth]);

  return (
    <View style={[styles.card, { height }]}>
      {item.image_url ? (
        <Image source={{ uri: item.image_url }} style={styles.background} resizeMode="cover" />
      ) : (
        <LinearGradient
          colors={['#feda75', '#fa7e1e', '#d62976', '#962fbf']}
          start={{ x: 0, y: 0 }}
          end={{ x: 1, y: 1 }}
          style={styles.background}
        >
          <Text style={styles.bgGlyph}>
            {(item.caption || author || '?').slice(0, 1).toUpperCase()}
          </Text>
        </LinearGradient>
      )}
      <LinearGradient
        colors={['rgba(0,0,0,0)', 'rgba(0,0,0,0.55)', 'rgba(0,0,0,0.85)']}
        start={{ x: 0.5, y: 0 }}
        end={{ x: 0.5, y: 1 }}
        style={styles.scrim}
        pointerEvents="none"
      />
      <View style={styles.overlay}>
        <View style={styles.author}>
          <Pressable
            style={styles.authorTap}
            onPress={() => openProfile(author)}
            hitSlop={6}
          >
            <AvatarRing username={author} size={42} />
            <View style={styles.authorText}>
              <Text style={[typography.bodyStrong, styles.authorName]}>@{author}</Text>
              <Text style={[typography.caption, styles.timestamp]}>
                {formatRel(item.created_at)}
              </Text>
            </View>
          </Pressable>
          <Pressable hitSlop={8} style={styles.followBtn} onPress={follow}>
            <GradientButton label={following ? 'following' : 'follow'} size="sm" />
          </Pressable>
        </View>
        {item.caption ? (
          <Pressable onPress={() => openPost(item.id, item)}>
            <Text style={[typography.body, styles.caption]} numberOfLines={3}>
              {item.caption}
            </Text>
          </Pressable>
        ) : null}
        <View style={styles.reelActions}>
          <Pressable onPress={toggleLike} hitSlop={8} style={styles.reelAction}>
            <Text style={[typography.bodyStrong, styles.reelActionLabel]}>
              {liked ? 'liked' : 'like'}
            </Text>
          </Pressable>
          <Pressable onPress={() => openPost(item.id, item)} hitSlop={8} style={styles.reelAction}>
            <Text style={[typography.bodyStrong, styles.reelActionLabel]}>comment</Text>
          </Pressable>
        </View>
        <View style={styles.statRow}>
          <StatRow
            inverted
            items={[
              { value: likes, label: 'likes' },
              { value: item.views || 0, label: 'views' },
            ]}
          />
        </View>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#000' },
  card: { width: '100%', position: 'relative', overflow: 'hidden' },
  background: { ...StyleSheet.absoluteFillObject, alignItems: 'center', justifyContent: 'center' },
  bgGlyph: { fontSize: 220, color: 'rgba(255,255,255,0.18)', fontWeight: '700' },
  scrim: { ...StyleSheet.absoluteFillObject },
  overlay: {
    flex: 1,
    justifyContent: 'flex-end',
    padding: spacing.xl,
  },
  author: { flexDirection: 'row', alignItems: 'center' },
  authorTap: { flex: 1, flexDirection: 'row', alignItems: 'center' },
  authorText: { flex: 1, marginLeft: spacing.md },
  authorName: { color: '#ffffff' },
  timestamp: { color: 'rgba(255,255,255,0.75)', marginTop: 2 },
  followBtn: { marginLeft: spacing.md },
  caption: {
    color: '#ffffff',
    marginTop: spacing.md,
  },
  reelActions: { flexDirection: 'row', marginTop: spacing.md },
  reelAction: { marginRight: spacing.xl },
  reelActionLabel: { color: '#ffffff', fontSize: 14 },
  statRow: { marginTop: spacing.lg },
  error: {
    position: 'absolute',
    bottom: spacing.xl,
    left: spacing.xl,
    right: spacing.xl,
    color: '#ffffff',
    backgroundColor: 'rgba(0,0,0,0.6)',
    padding: spacing.sm,
    borderRadius: 8,
  },
});
