// a person's profile. opened by tapping any username or avatar. shows the bio,
// follower / following / post counts, a follow / following toggle (gated behind
// login), and a grid of their posts that each open the post detail view.
import React, { useCallback, useEffect, useState } from 'react';
import {
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
import AvatarRing from './AvatarRing';
import EmptyState from './EmptyState';
import GradientButton from './GradientButton';
import GradientProgress from './GradientProgress';
import OutlineButton from './OutlineButton';
import OverlayFrame from './OverlayFrame';
import StatRow from './StatRow';
import { colors, radii, spacing, typography } from '../theme';

export default function ProfileModal({ identifier }) {
  const { user, requireAuth, openPost, closeTop, refresh } = useApp();
  const [profile, setProfile] = useState(null);
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [following, setFollowing] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);

  const isSelf = user && profile && user.id === profile.id;

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const p = await api.getUser(identifier);
      setProfile(p);
      const mine = await api.userPosts(p.id).catch(() => ({ results: [] }));
      setPosts(mine.results || mine || []);
      if (user && user.id !== p.id) {
        try {
          const rel = await api.relationship(user.username, p.username);
          setFollowing(Boolean(rel.a_follows_b));
        } catch (e) {
          setFollowing(false);
        }
      }
    } catch (e) {
      setError('could not load this profile.');
    } finally {
      setLoading(false);
    }
  }, [identifier, user]);

  useEffect(() => {
    load();
  }, [load]);

  const toggleFollow = useCallback(async () => {
    if (!requireAuth()) return;
    if (!profile || busy) return;
    const next = !following;
    setFollowing(next);
    setBusy(true);
    // reflect the count optimistically
    setProfile((p) => ({
      ...p,
      follower_count: (p.follower_count || 0) + (next ? 1 : -1),
    }));
    try {
      await api.toggleFollow(profile.username);
      refresh();
    } catch (e) {
      setFollowing(!next);
      setProfile((p) => ({
        ...p,
        follower_count: (p.follower_count || 0) + (next ? -1 : 1),
      }));
    } finally {
      setBusy(false);
    }
  }, [following, profile, busy, requireAuth, refresh]);

  const username = profile?.username || identifier;

  return (
    <OverlayFrame title={`@${username}`} onBack={closeTop}>
      <GradientProgress active={loading} />
      <ScrollView contentContainerStyle={styles.scroll}>
        <View style={styles.head}>
          <AvatarRing username={username} imageUrl={profile?.avatar} size={84} ringWidth={3} />
          <View style={styles.headStats}>
            <StatRow
              items={[
                { value: profile?.post_count || 0, label: 'posts' },
                { value: profile?.follower_count || 0, label: 'followers' },
                { value: profile?.following_count || 0, label: 'following' },
              ]}
              size="md"
            />
          </View>
        </View>
        <Text style={[typography.bodyStrong, styles.name]}>@{username}</Text>
        {profile?.bio ? (
          <Text style={[typography.body, styles.bio]}>{profile.bio}</Text>
        ) : null}
        {profile?.website ? (
          <Text style={[typography.caption, { color: colors.primary, paddingHorizontal: spacing.lg }]}>
            {profile.website}
          </Text>
        ) : null}

        <View style={styles.cta}>
          {isSelf ? (
            <OutlineButton label="this is you" onPress={() => {}} fullWidth />
          ) : following ? (
            <OutlineButton label="following" onPress={toggleFollow} fullWidth />
          ) : (
            <GradientButton label="follow" onPress={toggleFollow} fullWidth />
          )}
        </View>

        <Text style={[typography.label, styles.gridTitle]}>posts  {posts.length}</Text>
        {posts.length === 0 && !loading ? (
          <EmptyState glyph="o" title="no posts yet" body="this account has not posted anything." />
        ) : (
          <View style={styles.grid}>
            {posts.map((p) => (
              <Pressable key={p.id} style={styles.tile} onPress={() => openPost(p.id, p)}>
                {p.image ? (
                  <Image source={{ uri: p.image }} style={styles.tileImg} resizeMode="cover" />
                ) : (
                  <LinearGradient
                    colors={[colors.surfaceMuted, '#eaeaef']}
                    style={styles.tileImg}
                  />
                )}
              </Pressable>
            ))}
          </View>
        )}
        {error ? <Text style={styles.error}>{error}</Text> : null}
      </ScrollView>
    </OverlayFrame>
  );
}

const TILE = '32.5%';

const styles = StyleSheet.create({
  scroll: { paddingBottom: spacing.xxl },
  head: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: spacing.lg,
    paddingTop: spacing.lg,
  },
  headStats: { flex: 1, marginLeft: spacing.lg },
  name: { color: colors.text, paddingHorizontal: spacing.lg, paddingTop: spacing.md },
  bio: { color: colors.text, paddingHorizontal: spacing.lg, paddingTop: spacing.xs },
  cta: { paddingHorizontal: spacing.lg, paddingTop: spacing.md },
  gridTitle: {
    color: colors.muted,
    paddingHorizontal: spacing.lg,
    paddingTop: spacing.lg,
    paddingBottom: spacing.sm,
    textTransform: 'uppercase',
  },
  grid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    paddingHorizontal: spacing.sm,
    justifyContent: 'flex-start',
  },
  tile: {
    width: TILE,
    aspectRatio: 1,
    margin: '0.4%',
    borderRadius: radii.sm,
    overflow: 'hidden',
    backgroundColor: colors.surfaceMuted,
  },
  tileImg: { width: '100%', height: '100%' },
  error: { color: colors.text, padding: spacing.md },
});
