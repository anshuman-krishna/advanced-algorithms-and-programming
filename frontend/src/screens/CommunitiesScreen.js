// communities + chain finder + people to follow. lab 6 ex 2 dfs surfaces
// clusters as cards labelled by their most followed member; member pills and
// chain hops are tappable and open that person's profile. lab 6 ex 3 bfs renders
// the shortest chain as a row of gradient pills. a suggestions strip on top uses
// the lab 8 friend of friend bst when signed in, or a discover list otherwise.
import React, { useCallback, useEffect, useMemo, useState } from 'react';
import {
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View,
} from 'react-native';

import { api } from '../api/client';
import { useApp } from '../context/AppContext';
import AvatarRing from '../components/AvatarRing';
import EmptyState from '../components/EmptyState';
import GradientButton from '../components/GradientButton';
import GradientCardBorder from '../components/GradientCardBorder';
import GradientPill from '../components/GradientPill';
import GradientProgress from '../components/GradientProgress';
import GradientText from '../components/GradientText';
import OutlineButton from '../components/OutlineButton';
import RankBadge from '../components/RankBadge';
import ScreenContainer from '../components/ScreenContainer';
import StatRow from '../components/StatRow';
import {
  colors,
  radii,
  spacing,
  typography,
} from '../theme';

export default function CommunitiesScreen() {
  const { user, requireAuth, openProfile } = useApp();
  const [communities, setCommunities] = useState([]);
  const [usersById, setUsersById] = useState({});
  const [suggestions, setSuggestions] = useState([]);
  const [followed, setFollowed] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const [src, setSrc] = useState('alice');
  const [dst, setDst] = useState('eve');
  const [chain, setChain] = useState(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [res, users] = await Promise.all([
        api.communities(),
        api.listUsers().catch(() => ({ results: [] })),
      ]);
      setCommunities(res.components || []);
      const map = {};
      (users.results || users || []).forEach((u) => {
        map[u.id] = u;
      });
      setUsersById(map);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  const loadSuggestions = useCallback(async () => {
    try {
      if (user) {
        const res = await api.suggestions(8);
        setSuggestions(res.results || []);
      } else {
        const users = await api.listUsers();
        setSuggestions((users.results || users || []).slice(0, 8));
      }
    } catch (e) {
      setSuggestions([]);
    }
  }, [user]);

  const findChain = useCallback(async () => {
    if (!src || !dst) return;
    setError(null);
    try {
      const res = await api.shortestChain(src, dst);
      setChain(res);
    } catch (err) {
      setError(err.message);
    }
  }, [src, dst]);

  useEffect(() => {
    load();
    loadSuggestions();
  }, [load, loadSuggestions]);

  const follow = useCallback(
    async (username) => {
      if (!requireAuth()) return;
      setFollowed((m) => ({ ...m, [username]: true }));
      try {
        await api.toggleFollow(username);
      } catch (e) {
        setFollowed((m) => ({ ...m, [username]: false }));
      }
    },
    [requireAuth],
  );

  const nameFor = useCallback((id) => usersById[id]?.username || `user ${id}`, [usersById]);

  return (
    <ScreenContainer>
      <View style={styles.header}>
        <View style={{ flex: 1 }}>
          <Text style={[typography.display, { color: colors.text }]}>communities</Text>
          {/* internal: dfs clusters from lab 6 ex 2, bfs chains from lab 6 ex 3 */}
          <Text style={[typography.caption, { color: colors.muted }]}>
            circles in your network and how people connect
          </Text>
        </View>
        <OutlineButton label="refresh" onPress={load} size="sm" />
      </View>

      <GradientProgress active={loading} />
      <ScrollView contentContainerStyle={styles.scroll}>
        {/* people to follow */}
        {suggestions.length > 0 ? (
          <View style={styles.suggestWrap}>
            <Text style={[typography.label, styles.sectionTitle]}>
              {user ? 'suggested for you' : 'people to discover'}
            </Text>
            <ScrollView horizontal showsHorizontalScrollIndicator={false}>
              {suggestions.map((s) => {
                const uname = s.username;
                return (
                  <View key={s.id || uname} style={styles.suggestCard}>
                    <Pressable onPress={() => openProfile(uname)} style={{ alignItems: 'center' }}>
                      <AvatarRing username={uname} imageUrl={s.avatar} size={56} />
                      <Text style={[typography.bodyStrong, styles.suggestName]} numberOfLines={1}>
                        @{uname}
                      </Text>
                      {s.mutual_count ? (
                        <Text style={[typography.caption, { color: colors.muted }]}>
                          {s.mutual_count} mutual
                        </Text>
                      ) : (
                        <Text style={[typography.caption, { color: colors.muted }]} numberOfLines={1}>
                          {s.bio ? s.bio.split('·')[0].trim() : 'on petgram'}
                        </Text>
                      )}
                    </Pressable>
                    <Pressable
                      style={styles.suggestFollow}
                      onPress={() => follow(uname)}
                      hitSlop={6}
                    >
                      <GradientText style={typography.label}>
                        {followed[uname] ? 'following' : 'follow'}
                      </GradientText>
                    </Pressable>
                  </View>
                );
              })}
            </ScrollView>
          </View>
        ) : null}

        {/* shortest chain finder */}
        <View style={styles.chainCard}>
          <Text style={[typography.label, styles.sectionTitle]}>shortest chain</Text>
          <View style={styles.chainRow}>
            <TextInput
              value={src}
              onChangeText={setSrc}
              placeholder="from"
              placeholderTextColor={colors.muted}
              style={[styles.input, { flex: 1 }]}
              autoCapitalize="none"
            />
            <TextInput
              value={dst}
              onChangeText={setDst}
              placeholder="to"
              placeholderTextColor={colors.muted}
              style={[styles.input, { flex: 1 }]}
              autoCapitalize="none"
            />
            <GradientButton label="find" onPress={findChain} size="sm" />
          </View>
          {chain ? (
            <View style={styles.chainResult}>
              {chain.chain.length === 0 ? (
                <Text style={[typography.body, { color: colors.muted }]}>
                  no path between @{src} and @{dst}
                </Text>
              ) : (
                <ScrollView horizontal showsHorizontalScrollIndicator={false}>
                  {chain.chain.map((u, i) => (
                    <Pressable
                      key={u.id}
                      style={styles.hopRow}
                      onPress={() => openProfile(u.username || u.id)}
                    >
                      <GradientPill
                        label={`@${u.username || u.id}`}
                        variant={i === 0 || i === chain.chain.length - 1 ? 'solid' : 'outline'}
                        size="sm"
                      />
                      {i < chain.chain.length - 1 ? (
                        <GradientText style={styles.arrow}>{'>'}</GradientText>
                      ) : null}
                    </Pressable>
                  ))}
                </ScrollView>
              )}
              {chain.chain.length > 0 ? (
                <Text style={[typography.caption, { color: colors.muted, marginTop: spacing.xs }]}>
                  hops {chain.length}
                </Text>
              ) : null}
            </View>
          ) : null}
        </View>

        {/* community clusters */}
        {communities.map((c, idx) => (
          <View key={idx} style={styles.clusterWrap}>
            <GradientCardBorder>
              <View style={styles.cluster}>
                <View style={styles.clusterHead}>
                  <RankBadge rank={idx + 1} />
                  <Text style={[typography.bodyStrong, styles.clusterLabel]} numberOfLines={1}>
                    {c.label ? `@${c.label}'s circle` : `circle ${idx + 1}`}
                  </Text>
                  <StatRow size="sm" items={[{ value: c.size, label: 'members' }]} />
                </View>
                <View style={styles.memberWrap}>
                  {c.members.map((m) => (
                    <Pressable
                      key={m}
                      style={styles.memberPill}
                      onPress={() => openProfile(nameFor(m))}
                    >
                      <Text style={[typography.caption, { color: colors.text }]}>
                        @{nameFor(m)}
                      </Text>
                    </Pressable>
                  ))}
                </View>
              </View>
            </GradientCardBorder>
          </View>
        ))}
        {!loading && communities.length === 0 ? (
          <EmptyState
            glyph="d"
            title="no communities yet"
            body="follow a few people and refresh to see circles form."
          />
        ) : null}
        {error ? <Text style={styles.error}>{error}</Text> : null}
      </ScrollView>
    </ScreenContainer>
  );
}

const styles = StyleSheet.create({
  header: {
    paddingHorizontal: spacing.lg,
    paddingTop: spacing.md,
    paddingBottom: spacing.sm,
    flexDirection: 'row',
    alignItems: 'flex-end',
  },
  sectionTitle: {
    color: colors.muted,
    marginBottom: spacing.sm,
    textTransform: 'uppercase',
  },
  suggestWrap: { marginBottom: spacing.lg },
  suggestCard: {
    width: 110,
    alignItems: 'center',
    padding: spacing.sm,
    marginRight: spacing.sm,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: radii.md,
  },
  suggestName: { color: colors.text, marginTop: spacing.xs, maxWidth: 96 },
  suggestFollow: {
    marginTop: spacing.sm,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.xs,
    backgroundColor: colors.surfaceMuted,
    borderRadius: radii.pill,
  },
  chainCard: { paddingBottom: spacing.md },
  chainRow: { flexDirection: 'row', alignItems: 'center' },
  chainResult: { marginTop: spacing.sm },
  hopRow: { flexDirection: 'row', alignItems: 'center' },
  arrow: { fontSize: 14, fontWeight: '700', marginHorizontal: spacing.xs },
  scroll: { paddingHorizontal: spacing.lg, paddingTop: spacing.md, paddingBottom: spacing.xxl, flexGrow: 1 },
  clusterWrap: { marginBottom: spacing.md },
  cluster: { padding: spacing.lg, backgroundColor: colors.background },
  clusterHead: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: spacing.sm,
  },
  clusterLabel: { flex: 1, color: colors.text, marginLeft: spacing.sm },
  memberWrap: { flexDirection: 'row', flexWrap: 'wrap' },
  memberPill: {
    paddingHorizontal: spacing.sm,
    paddingVertical: 4,
    backgroundColor: colors.surfaceMuted,
    borderRadius: radii.pill,
    marginRight: spacing.xs,
    marginBottom: spacing.xs,
  },
  input: {
    color: colors.text,
    backgroundColor: colors.inputBackground,
    borderRadius: radii.md,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    marginRight: spacing.sm,
  },
  error: { color: colors.text, padding: spacing.md },
});
