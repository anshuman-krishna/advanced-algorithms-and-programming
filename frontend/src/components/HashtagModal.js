// posts under a single hashtag. opened by tapping any #tag in search or a
// caption. backed by the lab 1 inverted index drill down endpoint. each tile
// opens the full post.
import React, { useCallback, useEffect, useState } from 'react';
import { Image, Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';

import { api } from '../api/client';
import { useApp } from '../context/AppContext';
import EmptyState from './EmptyState';
import GradientProgress from './GradientProgress';
import OverlayFrame from './OverlayFrame';
import StatRow from './StatRow';
import { colors, gradientDir, gradientStops, radii, spacing, typography } from '../theme';

export default function HashtagModal({ tag }) {
  const { openPost, openProfile, closeTop } = useApp();
  const clean = String(tag || '').replace(/^#/, '');
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const res = await api.hashtagPosts(clean);
      setPosts(res.results || res || []);
    } catch (e) {
      setPosts([]);
    } finally {
      setLoading(false);
    }
  }, [clean]);

  useEffect(() => {
    load();
  }, [load]);

  return (
    <OverlayFrame title={`#${clean}`} onBack={closeTop}>
      <GradientProgress active={loading} />
      <ScrollView contentContainerStyle={styles.scroll}>
        <Text style={[typography.caption, styles.count]}>{posts.length} posts</Text>
        {posts.length === 0 && !loading ? (
          <EmptyState glyph="!" title="nothing here yet" body={`no posts tagged #${clean}.`} />
        ) : (
          posts.map((p) => (
            <View key={p.id} style={styles.row}>
              <Pressable style={styles.thumbWrap} onPress={() => openPost(p.id, p)}>
                {p.image ? (
                  <Image source={{ uri: p.image }} style={styles.thumb} resizeMode="cover" />
                ) : (
                  <LinearGradient
                    colors={gradientStops}
                    start={gradientDir.diagonal.start}
                    end={gradientDir.diagonal.end}
                    style={styles.thumb}
                  />
                )}
              </Pressable>
              <View style={styles.meta}>
                <Text
                  style={[typography.bodyStrong, { color: colors.text }]}
                  onPress={() => openProfile(p.author?.username)}
                >
                  @{p.author?.username || 'unknown'}
                </Text>
                <Text style={[typography.body, { color: colors.text }]} numberOfLines={2}>
                  {p.caption || 'no caption'}
                </Text>
                <View style={{ marginTop: spacing.xs }}>
                  <StatRow
                    size="sm"
                    items={[
                      { value: p.like_count || 0, label: 'likes' },
                      { value: p.comment_count || 0, label: 'comments' },
                    ]}
                  />
                </View>
              </View>
            </View>
          ))
        )}
      </ScrollView>
    </OverlayFrame>
  );
}

const styles = StyleSheet.create({
  scroll: { paddingBottom: spacing.xxl },
  count: { color: colors.muted, padding: spacing.lg },
  row: {
    flexDirection: 'row',
    paddingHorizontal: spacing.lg,
    paddingBottom: spacing.lg,
  },
  thumbWrap: { borderRadius: radii.md, overflow: 'hidden' },
  thumb: { width: 84, height: 84, backgroundColor: colors.surfaceMuted },
  meta: { flex: 1, marginLeft: spacing.md, justifyContent: 'center' },
});
