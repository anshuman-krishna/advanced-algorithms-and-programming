// full post view. opened by tapping a post anywhere (feed, search, trending,
// nearby, notifications, a profile grid). shows the image, the author (tap to
// open their profile), like / comment / share stats, the caption, and the
// comment list. comments are readable while logged out; liking a post, liking a
// comment, and posting a comment all open the login prompt first.
import React, { useCallback, useEffect, useState } from 'react';
import {
  Image,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';

import { api } from '../api/client';
import { useApp } from '../context/AppContext';
import AvatarRing from './AvatarRing';
import GradientButton from './GradientButton';
import GradientProgress from './GradientProgress';
import GradientText from './GradientText';
import OverlayFrame from './OverlayFrame';
import StatRow from './StatRow';
import {
  colors,
  gradientDir,
  gradientStops,
  radii,
  spacing,
  typography,
} from '../theme';

function relative(ts) {
  if (!ts) return '';
  const diff = Math.max(0, Date.now() - new Date(ts).getTime()) / 1000;
  if (diff < 60) return `${Math.floor(diff)}s`;
  if (diff < 3600) return `${Math.floor(diff / 60)}m`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}h`;
  return `${Math.floor(diff / 86400)}d`;
}

export default function PostDetailModal({ postId, post: seed }) {
  const { user, requireAuth, openProfile, closeTop } = useApp();
  const [post, setPost] = useState(seed || null);
  const [comments, setComments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [liked, setLiked] = useState(Boolean(seed?.is_liked));
  const [likeCount, setLikeCount] = useState(seed?.like_count || 0);
  const [replyTo, setReplyTo] = useState(null);
  const [text, setText] = useState('');
  const [busy, setBusy] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const [p, c] = await Promise.all([
        api.getPost(postId),
        api.listComments(postId).catch(() => []),
      ]);
      setPost(p);
      setLiked(Boolean(p.is_liked));
      setLikeCount(p.like_count || 0);
      setComments(c.results || c || []);
    } catch (e) {
      // leave whatever seed we had
    } finally {
      setLoading(false);
    }
  }, [postId]);

  useEffect(() => {
    load();
  }, [load, user]);

  const toggleLike = useCallback(async () => {
    if (!requireAuth()) return;
    const next = !liked;
    setLiked(next);
    setLikeCount((n) => n + (next ? 1 : -1));
    try {
      if (next) await api.likePost(postId);
      else await api.unlikePost(postId);
    } catch (e) {
      setLiked(!next);
      setLikeCount((n) => n + (next ? -1 : 1));
    }
  }, [liked, postId, requireAuth]);

  const submit = useCallback(async () => {
    if (!requireAuth()) return;
    if (!text.trim() || busy) return;
    setBusy(true);
    try {
      await api.createComment(postId, text.trim(), replyTo?.id || null);
      setText('');
      setReplyTo(null);
      await load();
    } catch (e) {
      // ignore, the box keeps the text so the user can retry
    } finally {
      setBusy(false);
    }
  }, [text, busy, postId, replyTo, requireAuth, load]);

  const username = post?.author?.username || seed?.author?.username || 'unknown';
  const image = post?.image || seed?.image;

  return (
    <OverlayFrame title="post" onBack={closeTop}>
      <GradientProgress active={loading} />
      <ScrollView contentContainerStyle={styles.scroll} keyboardShouldPersistTaps="handled">
        <View style={styles.header}>
          <Pressable
            style={styles.authorTap}
            onPress={() => openProfile(username)}
            hitSlop={6}
          >
            <AvatarRing username={username} imageUrl={post?.author?.avatar} size={40} ringWidth={2} />
            <View style={styles.headerText}>
              <Text style={[typography.bodyStrong, { color: colors.text }]}>{username}</Text>
              {post?.location ? (
                <Text style={[typography.caption, { color: colors.muted }]}>{post.location}</Text>
              ) : null}
            </View>
          </Pressable>
          <Text style={[typography.caption, { color: colors.muted }]}>
            {relative(post?.created_at)}
          </Text>
        </View>

        {image ? (
          <Image source={{ uri: image }} style={styles.image} resizeMode="cover" />
        ) : (
          <LinearGradient
            colors={gradientStops}
            start={gradientDir.diagonal.start}
            end={gradientDir.diagonal.end}
            style={styles.image}
          />
        )}

        <View style={styles.actions}>
          <Pressable onPress={toggleLike} hitSlop={8} style={styles.actionBtn}>
            {liked ? (
              <GradientText style={[typography.bodyStrong, styles.actionLabel]}>liked</GradientText>
            ) : (
              <Text style={[typography.bodyStrong, styles.actionLabel, { color: colors.text }]}>
                like
              </Text>
            )}
          </Pressable>
          <Pressable
            onPress={() => {
              if (!requireAuth()) return;
              setReplyTo(null);
            }}
            hitSlop={8}
            style={styles.actionBtn}
          >
            <Text style={[typography.bodyStrong, styles.actionLabel, { color: colors.text }]}>
              comment
            </Text>
          </Pressable>
        </View>

        <View style={styles.statWrap}>
          <StatRow
            items={[
              { value: likeCount, label: likeCount === 1 ? 'like' : 'likes' },
              { value: post?.comment_count ?? comments.length, label: 'comments' },
              { value: post?.share_count || 0, label: 'shares' },
            ]}
            size="md"
          />
        </View>

        {post?.caption ? (
          <Text style={[typography.body, styles.caption]}>
            <Text style={typography.bodyStrong}>{username} </Text>
            {post.caption}
          </Text>
        ) : null}

        <Text style={[typography.label, styles.commentsTitle]}>
          comments  {comments.length}
        </Text>
        {comments.length === 0 && !loading ? (
          <Text style={[typography.body, { color: colors.muted, paddingHorizontal: spacing.lg }]}>
            no comments yet. be the first.
          </Text>
        ) : null}
        {comments.map((c) => (
          <CommentRow
            key={c.id}
            comment={c}
            onProfile={openProfile}
            requireAuth={requireAuth}
            onReply={(cm) => {
              if (!requireAuth()) return;
              setReplyTo({ id: cm.id, username: cm.author?.username });
            }}
          />
        ))}
      </ScrollView>

      <View style={styles.composer}>
        {replyTo ? (
          <View style={styles.replyBanner}>
            <Text style={[typography.caption, { color: colors.muted }]}>
              replying to @{replyTo.username}
            </Text>
            <Pressable onPress={() => setReplyTo(null)} hitSlop={8}>
              <Text style={[typography.caption, { color: colors.primary }]}>cancel</Text>
            </Pressable>
          </View>
        ) : null}
        <View style={styles.composerRow}>
          <TextInput
            value={text}
            onChangeText={setText}
            placeholder={replyTo ? 'write a reply' : 'add a comment'}
            placeholderTextColor={colors.muted}
            style={styles.input}
            onFocus={() => requireAuth()}
          />
          <GradientButton label="post" onPress={submit} size="sm" disabled={busy} />
        </View>
      </View>
    </OverlayFrame>
  );
}

function CommentRow({ comment, onProfile, onReply, requireAuth }) {
  const [liked, setLiked] = useState(Boolean(comment.is_liked));
  const [count, setCount] = useState(comment.like_count || 0);
  const cu = comment.author?.username || 'unknown';

  const toggle = useCallback(async () => {
    if (!requireAuth()) return;
    const next = !liked;
    setLiked(next);
    setCount((n) => n + (next ? 1 : -1));
    try {
      if (next) await api.likeComment(comment.id);
      else await api.unlikeComment(comment.id);
    } catch (e) {
      setLiked(!next);
      setCount((n) => n + (next ? -1 : 1));
    }
  }, [liked, comment.id, requireAuth]);

  return (
    <View style={styles.commentRow}>
      <Pressable onPress={() => onProfile(cu)} hitSlop={4}>
        <AvatarRing username={cu} size={32} ringWidth={1.5} />
      </Pressable>
      <View style={styles.commentBody}>
        <Text style={[typography.body, { color: colors.text }]}>
          <Text style={typography.bodyStrong} onPress={() => onProfile(cu)}>
            {cu}{' '}
          </Text>
          {comment.is_deleted ? '(removed)' : comment.content}
        </Text>
        <View style={styles.commentMeta}>
          <Pressable onPress={toggle} hitSlop={6}>
            {liked ? (
              <GradientText style={[typography.label, { fontSize: 11 }]}>liked</GradientText>
            ) : (
              <Text style={[typography.label, { color: colors.muted, fontSize: 11 }]}>like</Text>
            )}
          </Pressable>
          <Pressable onPress={() => onReply(comment)} hitSlop={6}>
            <Text style={[typography.label, { color: colors.muted, fontSize: 11 }]}>reply</Text>
          </Pressable>
          {count ? (
            <GradientText style={[typography.label, { fontSize: 11 }]}>
              {count} {count === 1 ? 'like' : 'likes'}
            </GradientText>
          ) : null}
          {comment.reply_count ? (
            <Text style={[typography.label, { color: colors.muted, fontSize: 11 }]}>
              {comment.reply_count} {comment.reply_count === 1 ? 'reply' : 'replies'}
            </Text>
          ) : null}
        </View>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  scroll: { paddingBottom: spacing.xl },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.sm,
  },
  authorTap: { flexDirection: 'row', alignItems: 'center', flex: 1 },
  headerText: { marginLeft: spacing.md },
  image: { width: '100%', aspectRatio: 1, backgroundColor: colors.surfaceMuted },
  actions: {
    flexDirection: 'row',
    paddingHorizontal: spacing.lg,
    paddingTop: spacing.md,
  },
  actionBtn: { marginRight: spacing.xl },
  actionLabel: { fontSize: 14 },
  statWrap: { paddingHorizontal: spacing.lg, paddingTop: spacing.sm },
  caption: { color: colors.text, paddingHorizontal: spacing.lg, paddingTop: spacing.sm },
  commentsTitle: {
    color: colors.muted,
    paddingHorizontal: spacing.lg,
    paddingTop: spacing.lg,
    paddingBottom: spacing.sm,
    textTransform: 'uppercase',
  },
  commentRow: {
    flexDirection: 'row',
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.sm,
  },
  commentBody: { flex: 1, marginLeft: spacing.sm },
  commentMeta: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 4,
    columnGap: spacing.lg,
  },
  composer: {
    borderTopColor: colors.border,
    borderTopWidth: 1,
    padding: spacing.md,
    backgroundColor: colors.background,
  },
  replyBanner: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: spacing.xs,
  },
  composerRow: { flexDirection: 'row', alignItems: 'center' },
  input: {
    flex: 1,
    color: colors.text,
    backgroundColor: colors.inputBackground,
    borderRadius: radii.md,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    marginRight: spacing.sm,
  },
});
