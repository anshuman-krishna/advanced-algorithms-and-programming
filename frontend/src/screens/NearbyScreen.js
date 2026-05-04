// ref: claude.md phase 6. lab 7 ex 1 quadtree behind /api/geo/nearby and
// /api/geo/nearest. the screen lets you type a lat / lng and a radius; we keep
// it text only on purpose so we don't pull in a map library that fights the
// minimal styling rule.

import React, { useCallback, useEffect, useState } from 'react';
import {
  FlatList,
  Pressable,
  StyleSheet,
  Text,
  TextInput,
  View,
} from 'react-native';

import { api } from '../api/client';
import { colors } from '../theme/colors';

const PRESETS = [
  { label: 'Lisbon', lat: 38.72, lng: -9.14 },
  { label: 'New York', lat: 40.71, lng: -74.0 },
  { label: 'Tokyo', lat: 35.68, lng: 139.65 },
  { label: 'Mumbai', lat: 19.08, lng: 72.88 },
];

export default function NearbyScreen() {
  const [lat, setLat] = useState('38.72');
  const [lng, setLng] = useState('-9.14');
  const [radius, setRadius] = useState('20');
  const [items, setItems] = useState([]);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState(null);

  const search = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.geoNearby(
        parseFloat(lat),
        parseFloat(lng),
        parseFloat(radius),
        25,
      );
      setItems(res.results || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [lat, lng, radius]);

  useEffect(() => {
    api
      .geoStats()
      .then(setStats)
      .catch(() => undefined);
    search();
  }, [search]);

  return (
    <View style={styles.container}>
      <View style={styles.topBar}>
        <Text style={styles.title}>nearby</Text>
        {stats ? <Text style={styles.meta}>quadtree size {stats.size}</Text> : null}
      </View>
      <View style={styles.row}>
        <TextInput
          value={lat}
          onChangeText={setLat}
          placeholder="lat"
          placeholderTextColor={colors.muted}
          style={styles.input}
        />
        <TextInput
          value={lng}
          onChangeText={setLng}
          placeholder="lng"
          placeholderTextColor={colors.muted}
          style={styles.input}
        />
        <TextInput
          value={radius}
          onChangeText={setRadius}
          placeholder="radius (deg)"
          placeholderTextColor={colors.muted}
          style={styles.input}
        />
        <Pressable onPress={search} style={[styles.btn, styles.btnPrimary]}>
          <Text style={[styles.btnText, styles.btnTextPrimary]}>search</Text>
        </Pressable>
      </View>
      <View style={styles.presets}>
        {PRESETS.map((p) => (
          <Pressable
            key={p.label}
            onPress={() => {
              setLat(String(p.lat));
              setLng(String(p.lng));
            }}
            style={styles.preset}
          >
            <Text style={styles.presetText}>{p.label}</Text>
          </Pressable>
        ))}
      </View>
      {error ? <Text style={styles.error}>{error}</Text> : null}
      <FlatList
        data={items}
        keyExtractor={(item) => String(item.post_id || item.key)}
        renderItem={({ item }) => (
          <View style={styles.card}>
            <Text style={styles.cardHead}>
              @{item.author_username || 'unknown'}
            </Text>
            <Text style={styles.body}>{item.caption || '(no caption)'}</Text>
            <Text style={styles.meta}>
              {item.location} · ({item.y?.toFixed(2)}, {item.x?.toFixed(2)})
            </Text>
          </View>
        )}
        ListEmptyComponent={
          !loading ? <Text style={styles.empty}>no posts in this radius</Text> : null
        }
      />
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
    flex: 1,
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
  presets: {
    flexDirection: 'row',
    paddingHorizontal: 16,
    paddingBottom: 8,
    flexWrap: 'wrap',
  },
  preset: {
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderColor: colors.border,
    borderWidth: 1,
    marginRight: 6,
    marginTop: 6,
  },
  presetText: { color: colors.text, fontSize: 12 },
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
