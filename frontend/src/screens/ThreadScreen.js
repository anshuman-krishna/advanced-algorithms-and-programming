// ref: claude.md phase 5. lab 4 ex 1 recursive comment thread, ex 2 aggregation,
// ex 3 explicit stack iteration. the screen accepts a postId and renders the
// nested tree returned by the api with indentation per depth.

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
import { colors } from '../theme/colors';

function CommentNode({ node, depth, onReply, onDelete, onLike }) {
  return (
    <View style={[styles.node, { marginLeft: Math.min(depth, 6) * 12 }]}>
      <View style={styles.nodeHead}>
        <Text style={styles.author}>
          {node.is_deleted ? '[deleted]' : `user ${node.user_id}`}
        </Text>
        <Text style={styles.meta}>{node.likes} likes</Text>
      </View>
      <Text style={styles.body}>{node.is_deleted ? '(removed)' : node.content}</Text>
      <View style={styles.actions}>
        <Pressable onPress={() => onLike(node.comment_id)} style={styles.action}>
          <Text style={styles.actionText}>like</Text>
        </Pressable>
        <Pressable onPress={() => onReply(node.comment_id)} style={styles.action}>
          <Text style={styles.actionText}>reply</Text>
        </Pressable>
        {!node.is_deleted ? (
          <Pressable onPress={() => onDelete(node.comment_id)} style={styles.action}>
            <Text style={styles.actionText}>delete</Text>
          </Pressable>
        ) : null}
      </View>
      {node.replies?.map((c) => (
        <CommentNode
          key={c.comment_id}
          node={c}
          depth={depth + 1}
          onReply={onReply}
          onDelete={onDelete}
          onLike={onLike}
        />
      ))}
    </View>
  );
}

export default function ThreadScreen({ postId: postIdProp }) {
  const [postId, setPostId] = useState(postIdProp || '');
  const [tree, setTree] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [reply, setReply] = useState({ parentId: null, text: '' });
  const [search, setSearch] = useState('');
  const [searchResults, setSearchResults] = useState(null);

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
      try {
        await api.likeComment(commentId);
        await load();
      } catch (err) {
        setError(err.message);
      }
    },
    [load],
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
    <View style={styles.container}>
      <View style={styles.topBar}>
        <Text style={styles.title}>thread</Text>
        <TextInput
          value={postId}
          onChangeText={setPostId}
          placeholder="post id"
          placeholderTextColor={colors.muted}
          keyboardType="number-pad"
          style={styles.input}
        />
        <Pressable onPress={load} style={[styles.btn, styles.btnPrimary]}>
          <Text style={[styles.btnText, styles.btnTextPrimary]}>load</Text>
        </Pressable>
      </View>
      {stats ? (
        <Text style={styles.statsLine}>
          {stats.count} comments · depth {stats.max_depth} · {stats.total_likes} likes
          · engagement {stats.engagement?.toFixed?.(1) ?? stats.engagement}
        </Text>
      ) : null}
      <View style={styles.searchRow}>
        <TextInput
          value={search}
          onChangeText={setSearch}
          placeholder="keyword search (lab 4 ex 1)"
          placeholderTextColor={colors.muted}
          style={[styles.input, { flex: 1 }]}
        />
        <Pressable onPress={runSearch} style={styles.btn}>
          <Text style={styles.btnText}>search</Text>
        </Pressable>
      </View>
      {searchResults ? (
        <View style={styles.searchPanel}>
          <Text style={styles.meta}>{searchResults.length} matches</Text>
          {searchResults.slice(0, 5).map((m) => (
            <Text key={m.id} style={styles.searchHit} numberOfLines={1}>
              · {m.content}
            </Text>
          ))}
        </View>
      ) : null}
      {error ? <Text style={styles.error}>{error}</Text> : null}
      <ScrollView
        refreshControl={<RefreshControl refreshing={loading} onRefresh={load} />}
      >
        {tree.map((root) => (
          <CommentNode
            key={root.comment_id}
            node={root}
            depth={0}
            onReply={(id) => setReply({ parentId: id, text: '' })}
            onDelete={onDelete}
            onLike={onLike}
          />
        ))}
        {!loading && tree.length === 0 ? (
          <Text style={styles.empty}>no comments yet</Text>
        ) : null}
      </ScrollView>
      <View style={styles.composer}>
        {reply.parentId ? (
          <Text style={styles.meta}>replying to comment {reply.parentId}</Text>
        ) : null}
        <View style={styles.composerRow}>
          <TextInput
            value={reply.text}
            onChangeText={(text) => setReply((r) => ({ ...r, text }))}
            placeholder={reply.parentId ? 'reply...' : 'add a comment'}
            placeholderTextColor={colors.muted}
            style={[styles.input, { flex: 1 }]}
          />
          <Pressable onPress={submitReply} style={[styles.btn, styles.btnPrimary]}>
            <Text style={[styles.btnText, styles.btnTextPrimary]}>send</Text>
          </Pressable>
        </View>
      </View>
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
    minWidth: 80,
    marginRight: 8,
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
  statsLine: {
    color: colors.muted,
    fontSize: 12,
    paddingHorizontal: 16,
    paddingVertical: 6,
    borderBottomColor: colors.border,
    borderBottomWidth: 1,
  },
  searchRow: {
    flexDirection: 'row',
    paddingHorizontal: 16,
    paddingVertical: 8,
    alignItems: 'center',
  },
  searchPanel: {
    paddingHorizontal: 16,
    paddingBottom: 8,
    borderBottomColor: colors.border,
    borderBottomWidth: 1,
  },
  searchHit: { color: colors.text, fontSize: 13 },
  node: {
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderLeftColor: colors.border,
    borderLeftWidth: 1,
  },
  nodeHead: { flexDirection: 'row', justifyContent: 'space-between' },
  author: { color: colors.text, fontWeight: '600' },
  body: { color: colors.text, marginVertical: 4 },
  meta: { color: colors.muted, fontSize: 12 },
  actions: { flexDirection: 'row', marginTop: 4 },
  action: { marginRight: 12 },
  actionText: { color: colors.primary, fontSize: 12 },
  composer: {
    borderTopColor: colors.border,
    borderTopWidth: 1,
    padding: 8,
  },
  composerRow: { flexDirection: 'row', alignItems: 'center' },
  empty: { color: colors.muted, textAlign: 'center', marginTop: 24 },
  error: { color: colors.text, padding: 12 },
});
