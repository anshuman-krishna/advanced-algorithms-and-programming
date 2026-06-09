// communities + chain finder. lab 6 ex 2 dfs surfaces clusters as cards
// with a gradient size badge; lab 6 ex 3 bfs renders the chain as a row of
// gradient pills with subtle arrow separators.
import React, { useCallback, useEffect, useState } from 'react';
import {
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View,
} from 'react-native';

import { api } from '../api/client';
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
  const [communities, setCommunities] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const [src, setSrc] = useState('alice');
  const [dst, setDst] = useState('eve');
  const [chain, setChain] = useState(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.communities();
      setCommunities(res.components || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

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
  }, [load]);

  return (
    <ScreenContainer>
      <View style={styles.header}>
        <View style={{ flex: 1 }}>
          <Text style={[typography.display, { color: colors.text }]}>
            communities
          </Text>
          {/* internal: dfs clusters from lab 6 ex 2, bfs chains from lab 6 ex 3 */}
          <Text style={[typography.caption, { color: colors.muted }]}>
            circles in your network and how people connect
          </Text>
        </View>
        <OutlineButton label="refresh" onPress={load} size="sm" />
      </View>
      <View style={styles.chainCard}>
        <Text style={[typography.label, styles.sectionTitle]}>
          shortest chain
        </Text>
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
                  <View key={u.id} style={styles.hopRow}>
                    <GradientPill
                      label={`@${u.username || u.id}`}
                      variant={i === 0 || i === chain.chain.length - 1 ? 'solid' : 'outline'}
                      size="sm"
                    />
                    {i < chain.chain.length - 1 ? (
                      <GradientText style={styles.arrow}>{'>'}</GradientText>
                    ) : null}
                  </View>
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
      <GradientProgress active={loading} />
      <ScrollView contentContainerStyle={styles.scroll}>
        {communities.map((c, idx) => (
          <View key={idx} style={styles.clusterWrap}>
            <GradientCardBorder>
              <View style={styles.cluster}>
                <View style={styles.clusterHead}>
                  <RankBadge rank={idx + 1} />
                  <View style={{ flex: 1 }} />
                  <StatRow size="sm" items={[{ value: c.size, label: 'members' }]} />
                </View>
                <View style={styles.memberWrap}>
                  {c.members.map((m) => (
                    <View key={m} style={styles.memberPill}>
                      <Text style={[typography.caption, { color: colors.text }]}>
                        #{m}
                      </Text>
                    </View>
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
      </ScrollView>
      {error ? <Text style={styles.error}>{error}</Text> : null}
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
  chainCard: {
    paddingHorizontal: spacing.lg,
    paddingBottom: spacing.md,
  },
  sectionTitle: {
    color: colors.muted,
    marginBottom: spacing.xs,
    textTransform: 'uppercase',
  },
  chainRow: { flexDirection: 'row', alignItems: 'center' },
  chainResult: { marginTop: spacing.sm },
  hopRow: { flexDirection: 'row', alignItems: 'center' },
  arrow: {
    fontSize: 14,
    fontWeight: '700',
    marginHorizontal: spacing.xs,
  },
  scroll: { paddingHorizontal: spacing.lg, paddingBottom: spacing.xxl, flexGrow: 1 },
  clusterWrap: { marginBottom: spacing.md },
  cluster: { padding: spacing.lg, backgroundColor: colors.background },
  clusterHead: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: spacing.sm,
  },
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
