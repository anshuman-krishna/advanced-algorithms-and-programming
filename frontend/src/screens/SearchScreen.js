import React, { useEffect, useMemo, useState } from 'react';
import { FlatList, Pressable, ScrollView, StyleSheet, Text, TextInput, View } from 'react-native';

import { colors } from '../theme/colors';

const BASE = process.env.EXPO_PUBLIC_API_BASE || 'http://127.0.0.1:8000';

async function fetchJson(path) {
  const res = await fetch(`${BASE}${path}`);
  if (!res.ok) throw new Error(`api ${res.status}`);
  return res.json();
}

function flattenCategories(node, depth = 0, acc = []) {
  if (!node || !node.name) return acc;
  acc.push({ id: node.category_id, name: node.name, depth, total_posts: node.total_posts });
  (node.children || []).forEach((child) => flattenCategories(child, depth + 1, acc));
  return acc;
}

export default function SearchScreen() {
  const [query, setQuery] = useState('');
  const [users, setUsers] = useState([]);
  const [tags, setTags] = useState([]);
  const [posts, setPosts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [activeCategory, setActiveCategory] = useState(null);
  const [error, setError] = useState(null);

  const trimmed = useMemo(() => query.trim(), [query]);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const tree = await fetchJson('/api/search/explore/');
        if (cancelled) return;
        const flat = flattenCategories(tree).filter((c) => c.id && c.id > 0);
        setCategories(flat);
      } catch (err) {
        if (!cancelled) setError(err.message);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    let cancelled = false;
    if (!trimmed) {
      setUsers([]);
      setTags([]);
      setPosts([]);
      return () => {};
    }
    setError(null);
    (async () => {
      try {
        const [u, h, p] = await Promise.all([
          fetchJson(`/api/search/autocomplete/users/?q=${encodeURIComponent(trimmed)}&limit=5`),
          fetchJson(`/api/search/autocomplete/hashtags/?q=${encodeURIComponent(trimmed)}&limit=5`),
          fetchJson(`/api/search/posts/?q=${encodeURIComponent(trimmed)}`),
        ]);
        if (cancelled) return;
        setUsers(u.results || []);
        setTags(h.results || []);
        setPosts(p.results || []);
      } catch (err) {
        if (!cancelled) setError(err.message);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [trimmed]);

  return (
    <View style={styles.container}>
      <View style={styles.topBar}>
        <TextInput
          value={query}
          onChangeText={setQuery}
          placeholder="search posts, @users, #tags"
          placeholderTextColor={colors.muted}
          style={styles.input}
          autoCapitalize="none"
          autoCorrect={false}
        />
      </View>
      {categories.length > 0 ? (
        <ScrollView
          horizontal
          showsHorizontalScrollIndicator={false}
          style={styles.categoryBar}
          contentContainerStyle={styles.categoryBarContent}
        >
          {categories.map((cat) => (
            <Pressable
              key={cat.id}
              onPress={() => setActiveCategory(activeCategory === cat.id ? null : cat.id)}
              style={[
                styles.categoryChip,
                activeCategory === cat.id && styles.categoryChipActive,
              ]}
            >
              <Text
                style={[
                  styles.categoryChipText,
                  activeCategory === cat.id && styles.categoryChipTextActive,
                ]}
              >
                {cat.depth > 0 ? '· ' : ''}
                {cat.name} ({cat.total_posts})
              </Text>
            </Pressable>
          ))}
        </ScrollView>
      ) : null}
      {error ? <Text style={styles.error}>{error}</Text> : null}
      <FlatList
        data={[
          { type: 'header', label: 'users', count: users.length },
          ...users.map((u) => ({ type: 'user', ...u })),
          { type: 'header', label: 'hashtags', count: tags.length },
          ...tags.map((t) => ({ type: 'tag', ...t })),
          { type: 'header', label: 'posts', count: posts.length },
          ...posts.map((p) => ({ type: 'post', ...p })),
        ]}
        keyExtractor={(item, idx) =>
          item.type === 'header' ? `h-${item.label}` : `${item.type}-${item.id || item.user_id || item.hashtag_id || idx}`
        }
        renderItem={({ item }) => {
          if (item.type === 'header') {
            return (
              <Text style={styles.section}>
                {item.label} ({item.count})
              </Text>
            );
          }
          if (item.type === 'user') {
            return <Text style={styles.row}>@{item.username}</Text>;
          }
          if (item.type === 'tag') {
            return (
              <Text style={styles.row}>
                #{item.hashtag} · {item.post_count} posts
              </Text>
            );
          }
          return (
            <View style={styles.postRow}>
              <Text style={styles.username}>@{item.author?.username}</Text>
              <Text numberOfLines={2} style={styles.caption}>
                {item.caption}
              </Text>
            </View>
          );
        }}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background },
  topBar: {
    paddingVertical: 10,
    paddingHorizontal: 12,
    borderBottomColor: colors.border,
    borderBottomWidth: 1,
  },
  input: {
    borderColor: colors.border,
    borderWidth: 1,
    paddingHorizontal: 10,
    paddingVertical: 8,
    color: colors.text,
  },
  section: {
    paddingTop: 14,
    paddingHorizontal: 12,
    paddingBottom: 6,
    color: colors.muted,
    fontSize: 12,
    textTransform: 'uppercase',
  },
  row: {
    paddingHorizontal: 12,
    paddingVertical: 10,
    borderBottomColor: colors.border,
    borderBottomWidth: 1,
    color: colors.text,
  },
  postRow: {
    paddingHorizontal: 12,
    paddingVertical: 10,
    borderBottomColor: colors.border,
    borderBottomWidth: 1,
  },
  username: { color: colors.text, fontWeight: '600' },
  caption: { color: colors.text, marginTop: 4 },
  error: { color: colors.text, padding: 12 },
  categoryBar: {
    maxHeight: 44,
    borderBottomColor: colors.border,
    borderBottomWidth: 1,
  },
  categoryBarContent: {
    paddingHorizontal: 8,
    alignItems: 'center',
  },
  categoryChip: {
    borderColor: colors.border,
    borderWidth: 1,
    paddingHorizontal: 10,
    paddingVertical: 6,
    marginHorizontal: 4,
  },
  categoryChipActive: {
    borderColor: colors.primary,
  },
  categoryChipText: {
    color: colors.muted,
    fontSize: 12,
  },
  categoryChipTextActive: {
    color: colors.text,
    fontWeight: '600',
  },
});
