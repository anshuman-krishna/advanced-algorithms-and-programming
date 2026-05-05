// post card with story-ring avatar, soft hierarchy, and a tinted like button.
// the placeholder block uses a soft gradient so a missing image still feels
// alive rather than a blank square.
import React, { useCallback, useState } from 'react';
import { Image, Pressable, StyleSheet, Text, View } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';

import { api } from '../api/client';
import {
  colors,
  gradientDir,
  gradientStops,
  radii,
  spacing,
  typography,
} from '../theme';
import AvatarRing from './AvatarRing';
import GradientText from './GradientText';

function relative(ts) {
  if (!ts) return '';
  const then = new Date(ts).getTime();
  const diff = Math.max(0, Date.now() - then) / 1000;
  if (diff < 60) return `${Math.floor(diff)}s`;
  if (diff < 3600) return `${Math.floor(diff / 60)}m`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}h`;
  return `${Math.floor(diff / 86400)}d`;
}

export default function PostCard({ post, onComment }) {
  const [liked, setLiked] = useState(Boolean(post.is_liked));
  const [count, setCount] = useState(post.like_count || 0);
  const [busy, setBusy] = useState(false);

  const toggleLike = useCallback(async () => {
    if (busy) return;
    const next = !liked;
    setLiked(next);
    setCount((c) => c + (next ? 1 : -1));
    setBusy(true);
    try {
      if (next) {
        await api.likePost(post.id);
      } else {
        await api.unlikePost(post.id);
      }
    } catch (e) {
      // revert on error so the ui never lies about server state
      setLiked(!next);
      setCount((c) => c + (next ? -1 : 1));
    } finally {
      setBusy(false);
    }
  }, [busy, liked, post.id]);

  const username = post.author?.username || 'unknown';
  return (
    <View style={styles.card}>
      <View style={styles.header}>
        <AvatarRing username={username} size={38} ringWidth={2} />
        <View style={styles.headerText}>
          <Text style={[typography.bodyStrong, styles.username]}>{username}</Text>
          {post.location ? (
            <Text style={[typography.caption, styles.location]}>{post.location}</Text>
          ) : null}
        </View>
        <Text style={[typography.caption, styles.timestamp]}>
          {relative(post.created_at)}
        </Text>
      </View>
      {post.image ? (
        <Image
          source={{ uri: post.image }}
          style={styles.image}
          resizeMode="cover"
        />
      ) : (
        <LinearGradient
          colors={[colors.surfaceMuted, '#eaeaef']}
          start={gradientDir.diagonal.start}
          end={gradientDir.diagonal.end}
          style={styles.imagePlaceholder}
        >
          <Text style={[typography.title, styles.placeholderText]}>
            {(post.caption || username).slice(0, 1).toUpperCase()}
          </Text>
        </LinearGradient>
      )}
      <View style={styles.actions}>
        <Pressable onPress={toggleLike} hitSlop={8} style={styles.actionBtn}>
          {liked ? (
            <GradientText style={[typography.bodyStrong, styles.actionLabel]}>
              liked
            </GradientText>
          ) : (
            <Text style={[typography.bodyStrong, styles.actionLabel, { color: colors.text }]}>
              like
            </Text>
          )}
        </Pressable>
        <Pressable onPress={onComment} hitSlop={8} style={styles.actionBtn}>
          <Text style={[typography.bodyStrong, styles.actionLabel, { color: colors.text }]}>
            comment
          </Text>
        </Pressable>
      </View>
      <View style={styles.body}>
        <Text style={[typography.bodyStrong, styles.likeCount]}>
          {count} likes
        </Text>
        {post.caption ? (
          <Text style={[typography.body, styles.caption]} numberOfLines={3}>
            <Text style={typography.bodyStrong}>{username} </Text>
            {post.caption}
          </Text>
        ) : null}
        {post.comment_count ? (
          <Pressable onPress={onComment}>
            <Text style={[typography.caption, styles.commentLink]}>
              view all {post.comment_count} comments
            </Text>
          </Pressable>
        ) : null}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: colors.background,
    marginBottom: spacing.lg,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.sm,
  },
  headerText: { flex: 1, marginLeft: spacing.md },
  username: { color: colors.text },
  location: { color: colors.muted, marginTop: 1 },
  timestamp: { color: colors.muted },
  image: {
    width: '100%',
    aspectRatio: 1,
    borderRadius: radii.md,
    backgroundColor: colors.surfaceMuted,
  },
  imagePlaceholder: {
    width: '100%',
    aspectRatio: 1,
    borderRadius: radii.md,
    alignItems: 'center',
    justifyContent: 'center',
  },
  placeholderText: {
    color: colors.muted,
    fontSize: 56,
  },
  actions: {
    flexDirection: 'row',
    paddingHorizontal: spacing.sm,
    paddingTop: spacing.sm,
  },
  actionBtn: { marginRight: spacing.lg },
  actionLabel: { fontSize: 13 },
  body: {
    paddingHorizontal: spacing.sm,
    paddingTop: spacing.xs,
    paddingBottom: spacing.sm,
  },
  likeCount: { color: colors.text, marginBottom: spacing.xs },
  caption: { color: colors.text },
  commentLink: { color: colors.muted, marginTop: spacing.xs },
});
