// post card with story-ring avatar, soft hierarchy, and a tinted like button.
// tapping the image, the caption, or "view comments" opens the full post; the
// username and avatar open that person's profile. liking gates behind login.
// the placeholder block uses a soft gradient so a missing image still feels
// alive rather than a blank square.
import React, { useCallback, useState } from 'react';
import { Image, Pressable, StyleSheet, Text, View } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';

import { api } from '../api/client';
import { useApp } from '../context/AppContext';
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
import StatRow from './StatRow';

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
  const { requireAuth, openPost, openProfile } = useApp();
  const [liked, setLiked] = useState(Boolean(post.is_liked));
  const [count, setCount] = useState(post.like_count || 0);
  const [busy, setBusy] = useState(false);

  const username = post.author?.username || 'unknown';
  const openThis = useCallback(() => openPost(post.id, post), [openPost, post]);
  const goProfile = useCallback(() => openProfile(username), [openProfile, username]);
  const handleComment = onComment || openThis;

  const toggleLike = useCallback(async () => {
    if (!requireAuth()) return;
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
  }, [busy, liked, post.id, requireAuth]);

  return (
    <View style={styles.card}>
      <View style={styles.header}>
        <Pressable onPress={goProfile} hitSlop={4} style={styles.headerTap}>
          <AvatarRing username={username} imageUrl={post.author?.avatar} size={38} ringWidth={2} />
          <View style={styles.headerText}>
            <Text style={[typography.bodyStrong, styles.username]}>{username}</Text>
            {post.location ? (
              <Text style={[typography.caption, styles.location]}>{post.location}</Text>
            ) : null}
          </View>
        </Pressable>
        <Text style={[typography.caption, styles.timestamp]}>
          {relative(post.created_at)}
        </Text>
      </View>
      <Pressable onPress={openThis}>
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
      </Pressable>
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
        <Pressable onPress={handleComment} hitSlop={8} style={styles.actionBtn}>
          <Text style={[typography.bodyStrong, styles.actionLabel, { color: colors.text }]}>
            comment
          </Text>
        </Pressable>
      </View>
      <View style={styles.body}>
        <StatRow
          items={[
            { value: count, label: count === 1 ? 'like' : 'likes' },
            { value: post.comment_count || 0, label: 'comments' },
            { value: post.share_count || 0, label: 'shares' },
          ]}
          size="md"
        />
        {post.caption ? (
          <Pressable onPress={openThis}>
            <Text style={[typography.body, styles.caption]} numberOfLines={3}>
              <Text style={typography.bodyStrong}>{username} </Text>
              {post.caption}
            </Text>
          </Pressable>
        ) : null}
        {post.comment_count ? (
          <Pressable onPress={handleComment}>
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
  headerTap: { flex: 1, flexDirection: 'row', alignItems: 'center' },
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
    paddingTop: spacing.sm,
    paddingBottom: spacing.sm,
  },
  caption: { color: colors.text, marginTop: spacing.sm },
  commentLink: { color: colors.muted, marginTop: spacing.xs },
});
