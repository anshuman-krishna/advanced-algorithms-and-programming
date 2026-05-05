// home feed. story strip on top, gradient empty state, faint section dividers.
// the top bar carries the wordmark in the brand gradient and a thin animated
// progress bar for refresh activity.
import React, { useCallback, useEffect, useMemo, useState } from 'react';
import {
  FlatList,
  Pressable,
  RefreshControl,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from 'react-native';

import { api } from '../api/client';
import AvatarRing from '../components/AvatarRing';
import EmptyState from '../components/EmptyState';
import GradientProgress from '../components/GradientProgress';
import GradientText from '../components/GradientText';
import PostCard from '../components/PostCard';
import ScreenContainer from '../components/ScreenContainer';
import SectionDivider from '../components/SectionDivider';
import { colors, spacing, typography } from '../theme';

export default function HomeScreen() {
  const [posts, setPosts] = useState([]);
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.listPosts();
      setPosts(data.results ?? data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  const loadStories = useCallback(async () => {
    try {
      const u = await api.listUsers();
      setUsers((u.results ?? u).slice(0, 12));
    } catch {
      // story rail is decorative; failing here should not break the feed
    }
  }, []);

  useEffect(() => {
    load();
    loadStories();
  }, [load, loadStories]);

  const stories = useMemo(() => users, [users]);

  return (
    <ScreenContainer padded={false}>
      <View style={styles.topBar}>
        <GradientText style={[typography.display, styles.wordmark]}>
          instagram
        </GradientText>
      </View>
      <GradientProgress active={loading} />
      <FlatList
        data={posts}
        keyExtractor={(item) => String(item.id)}
        renderItem={({ item }) => <PostCard post={item} />}
        ItemSeparatorComponent={() => <SectionDivider inset={spacing.lg} />}
        ListHeaderComponent={
          stories.length ? (
            <View style={styles.storyRail}>
              <ScrollView
                horizontal
                showsHorizontalScrollIndicator={false}
                contentContainerStyle={styles.storyContent}
              >
                {stories.map((u) => (
                  <View key={u.id} style={styles.story}>
                    <AvatarRing
                      username={u.username}
                      imageUrl={u.avatar}
                      size={62}
                      ringWidth={2}
                    />
                    <Text
                      style={[typography.caption, styles.storyLabel]}
                      numberOfLines={1}
                    >
                      {u.username}
                    </Text>
                  </View>
                ))}
              </ScrollView>
              <SectionDivider />
            </View>
          ) : null
        }
        contentContainerStyle={styles.list}
        refreshControl={
          <RefreshControl
            refreshing={loading}
            onRefresh={load}
            tintColor={colors.primary}
            colors={[colors.primary]}
          />
        }
        ListEmptyComponent={
          !loading ? (
            <EmptyState
              glyph="o"
              title="your feed is empty"
              body="follow some people from the search tab and their posts will land here."
            />
          ) : null
        }
      />
      {error ? (
        <View style={styles.errorBar}>
          <Text style={[typography.caption, styles.errorText]}>{error}</Text>
          <Pressable onPress={load}>
            <Text style={[typography.label, styles.errorRetry]}>retry</Text>
          </Pressable>
        </View>
      ) : null}
    </ScreenContainer>
  );
}

const styles = StyleSheet.create({
  topBar: {
    paddingHorizontal: spacing.lg,
    paddingTop: spacing.sm,
    paddingBottom: spacing.sm,
    backgroundColor: colors.background,
    borderBottomColor: colors.border,
    borderBottomWidth: 1,
  },
  wordmark: { letterSpacing: -0.6 },
  storyRail: {
    backgroundColor: colors.background,
  },
  storyContent: {
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
  },
  story: {
    alignItems: 'center',
    width: 72,
    marginRight: spacing.sm,
  },
  storyLabel: {
    color: colors.text,
    marginTop: spacing.xs,
    maxWidth: 64,
  },
  list: { paddingBottom: spacing.xxl, flexGrow: 1 },
  errorBar: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: colors.surfaceMuted,
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.sm,
  },
  errorText: { color: colors.text, flex: 1 },
  errorRetry: { color: colors.primary },
});
