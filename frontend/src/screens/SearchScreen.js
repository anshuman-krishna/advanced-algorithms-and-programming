// search screen. soft rounded SearchInput on top, gradient pill chips for the
// lab 5 generalized tree categories, and a two column masonry of results.
// users + hashtags surface above the post grid as compact gradient cards.
import React, { useEffect, useMemo, useState } from 'react';
import {
  FlatList,
  Image,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';

import { api } from '../api/client';
import { useApp } from '../context/AppContext';
import AvatarRing from '../components/AvatarRing';
import EmptyState from '../components/EmptyState';
import GradientPill from '../components/GradientPill';
import GradientProgress from '../components/GradientProgress';
import GradientText from '../components/GradientText';
import HoverPreview from '../components/HoverPreview';
import ScreenContainer from '../components/ScreenContainer';
import SearchInput from '../components/SearchInput';
import StatPill from '../components/StatPill';
import {
  colors,
  gradientDir,
  gradientStops,
  radii,
  spacing,
  typography,
} from '../theme';

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
  const { openProfile, openHashtag, requireAuth } = useApp();
  const [query, setQuery] = useState('');
  const [followed, setFollowed] = useState({});

  const follow = async (username) => {
    if (!requireAuth()) return;
    setFollowed((m) => ({ ...m, [username]: true }));
    try {
      await api.toggleFollow(username);
    } catch (e) {
      setFollowed((m) => ({ ...m, [username]: false }));
    }
  };

  const [users, setUsers] = useState([]);
  const [tags, setTags] = useState([]);
  const [posts, setPosts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [trendingTags, setTrendingTags] = useState([]);
  const [activeCategory, setActiveCategory] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const trimmed = useMemo(() => query.trim(), [query]);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const [tree, trendingResp] = await Promise.all([
          fetchJson('/api/search/explore/'),
          api.trendingHashtags(10).catch(() => ({ results: [] })),
        ]);
        if (cancelled) return;
        const flat = flattenCategories(tree).filter((c) => c.id && c.id > 0);
        setCategories(flat);
        setTrendingTags(trendingResp.results || []);
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
    setLoading(true);
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
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [trimmed]);

  // split posts into two columns for a masonry feel
  const grid = useMemo(() => {
    const left = [];
    const right = [];
    posts.forEach((p, i) => (i % 2 === 0 ? left : right).push(p));
    return { left, right };
  }, [posts]);

  return (
    <ScreenContainer>
      <View style={styles.searchWrap}>
        <SearchInput
          value={query}
          onChangeText={setQuery}
          placeholder="search posts, users, or hashtags"
          onClear={() => setQuery('')}
        />
      </View>
      <GradientProgress active={loading} />
      {trendingTags.length > 0 && !trimmed ? (
        <View style={styles.trendingWrap}>
          <Text style={[typography.label, styles.sectionTitle]}>
            trending tags
          </Text>
          <ScrollView
            horizontal
            showsHorizontalScrollIndicator={false}
            contentContainerStyle={styles.chipBar}
          >
            {trendingTags.map((tag) => (
              <Pressable
                key={tag.hashtag_id}
                style={styles.trendingChip}
                onPress={() => openHashtag(tag.hashtag)}
              >
                <GradientText
                  style={[typography.bodyStrong, { fontSize: 13 }]}
                >
                  #{tag.hashtag}
                </GradientText>
                <Text
                  style={[typography.caption, { color: colors.muted, marginLeft: 6 }]}
                >
                  {tag.post_count}
                </Text>
              </Pressable>
            ))}
          </ScrollView>
        </View>
      ) : null}
      {categories.length > 0 ? (
        <ScrollView
          horizontal
          showsHorizontalScrollIndicator={false}
          contentContainerStyle={styles.chipBar}
        >
          {categories.map((cat) => (
            <View key={cat.id} style={styles.chipWrap}>
              <GradientPill
                label={`${cat.depth > 0 ? '· ' : ''}${cat.name} ${cat.total_posts}`}
                onPress={() =>
                  setActiveCategory(activeCategory === cat.id ? null : cat.id)
                }
                selected={activeCategory === cat.id}
                size="sm"
              />
            </View>
          ))}
        </ScrollView>
      ) : null}
      {error ? <Text style={styles.error}>{error}</Text> : null}
      <ScrollView contentContainerStyle={styles.body}>
        {/* internal: hits the lab 1 inverted index, the lab 8 user trie, and the hashtag trie at once */}
        {!trimmed ? (
          <EmptyState
            glyph="s"
            title="search the network"
            body="find people, posts, and hashtags as you type."
          />
        ) : null}
        {users.length > 0 ? (
          <View style={styles.section}>
            <Text style={[typography.label, styles.sectionTitle]}>
              users  {users.length}
            </Text>
            {users.map((u) => (
              <View key={u.user_id || u.id} style={styles.userRow}>
                <Pressable
                  style={styles.userTap}
                  onPress={() => openProfile(u.username)}
                  hitSlop={4}
                >
                  <AvatarRing username={u.username} size={36} />
                  <View style={{ flex: 1, marginLeft: spacing.md }}>
                    <Text style={[typography.bodyStrong, { color: colors.text }]}>
                      @{u.username}
                    </Text>
                    <Text style={[typography.caption, { color: colors.muted }]}>
                      tap to view profile
                    </Text>
                  </View>
                </Pressable>
                <Pressable hitSlop={8} style={styles.followBtn} onPress={() => follow(u.username)}>
                  <GradientText style={typography.label}>
                    {followed[u.username] ? 'following' : 'follow'}
                  </GradientText>
                </Pressable>
              </View>
            ))}
          </View>
        ) : null}
        {tags.length > 0 ? (
          <View style={styles.section}>
            <Text style={[typography.label, styles.sectionTitle]}>
              hashtags  {tags.length}
            </Text>
            <View style={styles.tagWrap}>
              {tags.map((t) => (
                <Pressable
                  key={t.hashtag}
                  style={styles.tagPill}
                  onPress={() => openHashtag(t.hashtag)}
                >
                  <GradientText style={[typography.bodyStrong, { fontSize: 13 }]}>
                    #{t.hashtag}
                  </GradientText>
                  <Text style={[typography.caption, { color: colors.muted, marginLeft: 6 }]}>
                    {t.post_count}
                  </Text>
                </Pressable>
              ))}
            </View>
          </View>
        ) : null}
        {posts.length > 0 ? (
          <View style={styles.section}>
            <Text style={[typography.label, styles.sectionTitle]}>
              posts  {posts.length}
            </Text>
            <View style={styles.grid}>
              <View style={styles.col}>
                {grid.left.map((p) => (
                  <PostTile key={p.id} post={p} />
                ))}
              </View>
              <View style={styles.col}>
                {grid.right.map((p) => (
                  <PostTile key={p.id} post={p} />
                ))}
              </View>
            </View>
          </View>
        ) : null}
        {trimmed && !loading && users.length === 0 && tags.length === 0 && posts.length === 0 ? (
          <EmptyState
            glyph="!"
            title="no results"
            body="nothing matches that search yet."
          />
        ) : null}
      </ScrollView>
    </ScreenContainer>
  );
}

function PostTile({ post }) {
  const { openPost, openProfile } = useApp();
  const seed = post.caption || post.author?.username || `${post.id}`;
  const overlay = (
    <View>
      <Text style={tileStyles.overlayAuthor} numberOfLines={1}>
        @{post.author?.username || 'unknown'}
      </Text>
      <Text style={tileStyles.overlayCaption} numberOfLines={6}>
        {post.caption || 'no caption'}
      </Text>
      <View style={{ marginTop: spacing.xs }}>
        <StatPill
          value={post.like_count || 0}
          label="likes"
          size="sm"
          inverted
        />
      </View>
    </View>
  );
  return (
    <View style={tileStyles.tile}>
      <Pressable onPress={() => openPost(post.id, post)}>
        <HoverPreview overlay={overlay} radius={radii.lg}>
          {post.image ? (
            <Image source={{ uri: post.image }} style={tileStyles.cover} resizeMode="cover" />
          ) : (
            <LinearGradient
              colors={gradientStops}
              start={gradientDir.diagonal.start}
              end={gradientDir.diagonal.end}
              style={tileStyles.cover}
            >
              <Text style={tileStyles.coverGlyph}>
                {seed.slice(0, 1).toUpperCase()}
              </Text>
            </LinearGradient>
          )}
        </HoverPreview>
      </Pressable>
      <View style={tileStyles.meta}>
        <Text
          style={[typography.bodyStrong, { color: colors.text, fontSize: 13 }]}
          numberOfLines={1}
          onPress={() => openProfile(post.author?.username)}
        >
          @{post.author?.username || 'unknown'}
        </Text>
        <Text style={[typography.body, { color: colors.text, fontSize: 12 }]}
              numberOfLines={2}>
          {post.caption}
        </Text>
        <View style={tileStyles.statRow}>
          <StatPill value={post.like_count || 0} label="likes" size="sm" />
        </View>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  searchWrap: {
    paddingHorizontal: spacing.lg,
    paddingTop: spacing.md,
    paddingBottom: spacing.sm,
  },
  chipBar: {
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.sm,
  },
  trendingWrap: {
    paddingTop: spacing.sm,
  },
  trendingChip: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.surfaceMuted,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    borderRadius: 999,
    marginRight: spacing.sm,
  },
  chipWrap: { marginRight: spacing.sm },
  body: { padding: spacing.lg, flexGrow: 1 },
  section: { marginBottom: spacing.xl },
  sectionTitle: {
    color: colors.muted,
    marginBottom: spacing.sm,
    textTransform: 'uppercase',
  },
  userRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: spacing.sm,
  },
  userTap: { flex: 1, flexDirection: 'row', alignItems: 'center' },
  followBtn: {
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.xs,
    borderRadius: radii.pill,
    backgroundColor: colors.surfaceMuted,
  },
  tagWrap: { flexDirection: 'row', flexWrap: 'wrap' },
  tagPill: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.surfaceMuted,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    borderRadius: radii.pill,
    marginRight: spacing.sm,
    marginBottom: spacing.sm,
  },
  grid: { flexDirection: 'row' },
  col: { flex: 1, marginHorizontal: spacing.xs },
  error: { color: colors.text, padding: spacing.md },
});

const tileStyles = StyleSheet.create({
  tile: {
    backgroundColor: colors.background,
    borderRadius: radii.lg,
    overflow: 'hidden',
    marginBottom: spacing.md,
    borderWidth: 1,
    borderColor: colors.border,
  },
  cover: {
    width: '100%',
    aspectRatio: 1,
    alignItems: 'center',
    justifyContent: 'center',
  },
  coverGlyph: { fontSize: 48, color: '#ffffff', fontWeight: '700' },
  meta: { padding: spacing.sm },
  statRow: { marginTop: spacing.xs },
  overlayAuthor: { color: '#ffffff', fontWeight: '700', fontSize: 12 },
  overlayCaption: { color: 'rgba(255,255,255,0.95)', fontSize: 12, marginTop: 2 },
});
