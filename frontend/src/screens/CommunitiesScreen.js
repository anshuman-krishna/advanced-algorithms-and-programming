// ref: claude.md phase 6. lab 6 ex 2 dfs (communities) and lab 6 ex 3 bfs
// (shortest chain), exposed via /api/social. the screen lists every connected
// component sorted by size and lets you ask for the chain between any two
// usernames.

import React, { useCallback, useEffect, useState } from 'react';
import {
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View,
} from 'react-native';

import { api } from '../api/client';
import { colors } from '../theme/colors';

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
    <View style={styles.container}>
      <View style={styles.topBar}>
        <Text style={styles.title}>communities</Text>
        <Pressable onPress={load} style={styles.btn}>
          <Text style={styles.btnText}>refresh</Text>
        </Pressable>
      </View>
      <View style={styles.row}>
        <TextInput
          value={src}
          onChangeText={setSrc}
          placeholder="from"
          placeholderTextColor={colors.muted}
          style={[styles.input, { flex: 1 }]}
        />
        <TextInput
          value={dst}
          onChangeText={setDst}
          placeholder="to"
          placeholderTextColor={colors.muted}
          style={[styles.input, { flex: 1 }]}
        />
        <Pressable onPress={findChain} style={[styles.btn, styles.btnPrimary]}>
          <Text style={[styles.btnText, styles.btnTextPrimary]}>chain</Text>
        </Pressable>
      </View>
      {chain ? (
        <View style={styles.chainBox}>
          {chain.chain.length === 0 ? (
            <Text style={styles.meta}>no path between {src} and {dst}</Text>
          ) : (
            <Text style={styles.body}>
              {chain.chain.map((u) => '@' + (u.username || u.id)).join(' -> ')}{' '}
              <Text style={styles.meta}>(length {chain.length})</Text>
            </Text>
          )}
        </View>
      ) : null}
      {error ? <Text style={styles.error}>{error}</Text> : null}
      <ScrollView>
        {communities.map((c, idx) => (
          <View key={idx} style={styles.card}>
            <Text style={styles.cardHead}>
              cluster #{idx + 1} ({c.size} members)
            </Text>
            <Text style={styles.body}>
              {c.members.map((m) => `#${m}`).join(', ')}
            </Text>
          </View>
        ))}
        {!loading && communities.length === 0 ? (
          <Text style={styles.empty}>no communities yet</Text>
        ) : null}
      </ScrollView>
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
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  title: { color: colors.text, fontSize: 18, fontWeight: '600' },
  meta: { color: colors.muted, fontSize: 12 },
  row: {
    flexDirection: 'row',
    paddingHorizontal: 16,
    paddingVertical: 8,
    alignItems: 'center',
  },
  input: {
    color: colors.text,
    borderColor: colors.border,
    borderWidth: 1,
    paddingHorizontal: 8,
    paddingVertical: 6,
    marginRight: 6,
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
  chainBox: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderBottomColor: colors.border,
    borderBottomWidth: 1,
  },
  card: {
    padding: 12,
    borderBottomColor: colors.border,
    borderBottomWidth: 1,
  },
  cardHead: { color: colors.text, fontWeight: '600' },
  body: { color: colors.text, marginTop: 4 },
  empty: { color: colors.muted, textAlign: 'center', marginTop: 24 },
  error: { color: colors.text, padding: 12 },
});
