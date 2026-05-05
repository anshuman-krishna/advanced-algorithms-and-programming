// thread viewer. each reply level draws a thin gray vertical connector so the
// lab 4 recursive structure reads visually. like buttons go gradient when
// active, comment counts surface as gradient stats.
import React, { useCallback, useEffect, useMemo, useState } from 'react';
import {
  Pressable,
  RefreshControl,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View,
} from 'react-native';

import { api } from '../api/client';
import AvatarRing from '../components/AvatarRing';
import EmptyState from '../components/EmptyState';
import GradientButton from '../components/GradientButton';
import GradientProgress from '../components/GradientProgress';
import GradientText from '../components/GradientText';
import OutlineButton from '../components/OutlineButton';
import ScreenContainer from '../components/ScreenContainer';
import StatRow from '../components/StatRow';
import {
  colors,
  radii,
  spacing,
  typography,
} from '../theme';

function CommentNode({ node, depth, onReply, onDelete, onLike, likedSet }) {
  const liked = likedSet.has(node.comment_id);
  const username = `user ${node.user_id}`;
  return (
    <View style={[styles.node, { paddingLeft: depth === 0 ? 0 : spacing.md }]}>
      {depth > 0 ? <View style={styles.connector} /> : null}
      <View style={styles.nodeRow}>
        <AvatarRing username={username} size={32} ringWidth={1.5} />
        <View style={styles.nodeBody}>
          <View style={styles.nodeHead}>
            <Text style={[typography.bodyStrong, { color: colors.text, fontSize: 13 }]}>
              {node.is_deleted ? '[deleted]' : `@${username}`}
            </Text>
            {node.likes ? (
              <GradientText style={[typography.label, { fontSize: 11 }]}>
                {node.likes} likes
              </GradientText>
            ) : null}
          </View>
          <Text style={[typography.body, { color: colors.text }]}>
            {node.is_deleted ? '(removed)' : node.content}
          </Text>
          <View style={styles.actions}>
            <Pressable onPress={() => onLike(node.comment_id)} hitSlop={6}>
              {liked ? (
                <GradientText style={[typography.label, { fontSize: 11 }]}>
                  liked
                </GradientText>
              ) : (
                <Text style={[typography.label, { color: colors.muted, fontSize: 11 }]}>
                  like
                </Text>
              )}
            </Pressable>
            <Pressable onPress={() => onReply(node.comment_id)} hitSlop={6}>
              <Text style={[typography.label, { color: colors.muted, fontSize: 11 }]}>
                reply
              </Text>
            </Pressable>
            {!node.is_deleted ? (
              <Pressable onPress={() => onDelete(node.comment_id)} hitSlop={6}>
                <Text style={[typography.label, { color: colors.muted, fontSize: 11 }]}>
                  delete
                </Text>
              </Pressable>
            ) : null}
          </View>
        </View>
      </View>
      {node.replies?.map((c) => (
        <CommentNode
          key={c.comment_id}
          node={c}
          depth={depth + 1}
          onReply={onReply}
          onDelete={onDelete}
          onLike={onLike}
          likedSet={likedSet}
        />
      ))}
    </View>
  );
}

export default function ThreadScreen({ postId: postIdProp }) {
  const [postId, setPostId] = useState(postIdProp ? String(postIdProp) : '');
  const [tree, setTree] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [reply, setReply] = useState({ parentId: null, text: '' });
  const [search, setSearch] = useState('');
  const [searchResults, setSearchResults] = useState(null);
  const [likedSet, setLikedSet] = useState(new Set());

  const numericId = useMemo(() => {
    const n = parseInt(postId, 10);
    return Number.isNaN(n) ? null : n;
  }, [postId]);

  const load = useCallback(async () => {
    if (numericId == null) return;
    setLoading(true);
    setError(null);
    try {
      const [thread, metrics] = await Promise.all([
        api.thread(numericId, true),
        api.threadStats(numericId),
      ]);
      setTree(thread.results || []);
      setStats(metrics);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [numericId]);

  useEffect(() => {
    load();
  }, [load]);

  const submitReply = useCallback(async () => {
    if (numericId == null || !reply.text.trim()) return;
    try {
      await api.createComment(numericId, reply.text.trim(), reply.parentId);
      setReply({ parentId: null, text: '' });
      await load();
    } catch (err) {
      setError(err.message);
    }
  }, [numericId, reply, load]);

  const onDelete = useCallback(
    async (commentId) => {
      try {
        await api.deleteComment(commentId);
        await load();
      } catch (err) {
        setError(err.message);
      }
    },
    [load],
  );

  const onLike = useCallback(
    async (commentId) => {
      // optimistic toggle of the gradient state; the next refresh resyncs likes
      setLikedSet((prev) => {
        const next = new Set(prev);
        if (next.has(commentId)) {
          next.delete(commentId);
        } else {
          next.add(commentId);
        }
        return next;
      });
      try {
        if (likedSet.has(commentId)) {
          await api.unlikeComment(commentId);
        } else {
          await api.likeComment(commentId);
        }
        await load();
      } catch (err) {
        setError(err.message);
      }
    },
    [likedSet, load],
  );

  const runSearch = useCallback(async () => {
    if (numericId == null || !search.trim()) {
      setSearchResults(null);
      return;
    }
    try {
      const res = await api.threadSearch(numericId, search.trim());
      setSearchResults(res.results || []);
    } catch (err) {
      setError(err.message);
    }
  }, [numericId, search]);

  return (
    <ScreenContainer>
      <View style={styles.header}>
        <Text style={[typography.display, { color: colors.text }]}>thread</Text>
        <Text style={[typography.caption, { color: colors.muted }]}>
          recursive comment tree from lab 4
        </Text>
      </View>
      <View style={styles.idRow}>
        <TextInput
          value={postId}
          onChangeText={setPostId}
          placeholder="post id"
          placeholderTextColor={colors.muted}
          keyboardType="number-pad"
          style={styles.input}
        />
        <GradientButton label="load" onPress={load} size="sm" />
      </View>
      {stats ? (
        <View style={styles.statBar}>
          <StatRow
            items={[
              { value: stats.count || 0, label: 'comments' },
              { value: stats.max_depth || 0, label: 'depth' },
              { value: stats.total_likes || 0, label: 'likes' },
            ]}
            size="sm"
          />
        </View>
      ) : null}
      <View style={styles.searchRow}>
        <TextInput
          value={search}
          onChangeText={setSearch}
          placeholder="keyword search the tree (lab 4 ex 1)"
          placeholderTextColor={colors.muted}
          style={[styles.input, { flex: 1 }]}
        />
        <OutlineButton label="search" onPress={runSearch} size="sm" />
      </View>
      {searchResults ? (
        <View style={styles.searchPanel}>
          <Text style={[typography.caption, { color: colors.muted }]}>
            {searchResults.length} matches
          </Text>
          {searchResults.slice(0, 5).map((m) => (
            <Text
              key={m.id}
              style={[typography.body, { color: colors.text }]}
              numberOfLines={1}
            >
              · {m.content}
            </Text>
          ))}
        </View>
      ) : null}
      <GradientProgress active={loading} />
      <ScrollView
        contentContainerStyle={styles.scroll}
        refreshControl={
          <RefreshControl
            refreshing={loading}
            onRefresh={load}
            tintColor={colors.primary}
            colors={[colors.primary]}
          />
        }
      >
        {tree.map((root) => (
          <CommentNode
            key={root.comment_id}
            node={root}
            depth={0}
            onReply={(id) => setReply({ parentId: id, text: '' })}
            onDelete={onDelete}
            onLike={onLike}
            likedSet={likedSet}
          />
        ))}
        {!loading && tree.length === 0 ? (
          <EmptyState
            glyph="c"
            title={numericId == null ? 'pick a post' : 'no comments yet'}
            body={
              numericId == null
                ? 'enter a post id above to load its recursive thread.'
                : 'be the first to add a comment using the box below.'
            }
          />
        ) : null}
      </ScrollView>
      <View style={styles.composer}>
        {reply.parentId ? (
          <Text style={[typography.caption, { color: colors.muted, marginBottom: spacing.xs }]}>
            replying to comment {reply.parentId}
          </Text>
        ) : null}
        <View style={styles.composerRow}>
          <TextInput
            value={reply.text}
            onChangeText={(text) => setReply((r) => ({ ...r, text }))}
            placeholder={reply.parentId ? 'reply...' : 'add a comment'}
            placeholderTextColor={colors.muted}
            style={[styles.input, { flex: 1 }]}
          />
          <GradientButton label="send" onPress={submitReply} size="sm" />
        </View>
      </View>
      {error ? <Text style={styles.error}>{error}</Text> : null}
    </ScreenContainer>
  );
}

const styles = StyleSheet.create({
  header: {
    paddingHorizontal: spacing.lg,
    paddingTop: spacing.md,
    paddingBottom: spacing.sm,
  },
  idRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: spacing.lg,
    paddingBottom: spacing.sm,
  },
  statBar: {
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.sm,
    backgroundColor: colors.surface,
    borderTopColor: colors.border,
    borderBottomColor: colors.border,
    borderTopWidth: 1,
    borderBottomWidth: 1,
  },
  searchRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: spacing.lg,
    paddingTop: spacing.md,
  },
  searchPanel: {
    paddingHorizontal: spacing.lg,
    paddingBottom: spacing.sm,
  },
  scroll: {
    paddingHorizontal: spacing.lg,
    paddingTop: spacing.md,
    paddingBottom: spacing.lg,
    flexGrow: 1,
  },
  node: { marginBottom: spacing.md, position: 'relative' },
  connector: {
    position: 'absolute',
    left: 0,
    top: 0,
    bottom: 0,
    width: 1,
    backgroundColor: colors.border,
    marginLeft: spacing.xs,
  },
  nodeRow: { flexDirection: 'row', alignItems: 'flex-start' },
  nodeBody: { flex: 1, marginLeft: spacing.sm },
  nodeHead: {
    flexDirection: 'row',
    alignItems: 'baseline',
    justifyContent: 'space-between',
    marginBottom: 2,
  },
  actions: {
    flexDirection: 'row',
    marginTop: spacing.xs,
    columnGap: spacing.lg,
  },
  composer: {
    borderTopColor: colors.border,
    borderTopWidth: 1,
    padding: spacing.md,
  },
  composerRow: { flexDirection: 'row', alignItems: 'center' },
  input: {
    color: colors.text,
    backgroundColor: colors.inputBackground,
    borderRadius: radii.md,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    minWidth: 100,
    marginRight: spacing.sm,
  },
  error: { color: colors.text, padding: spacing.md },
});
