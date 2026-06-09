// nearby screen powered by the lab 7 quadtree. lat/lng/radius inputs sit in
// soft rounded fields, city presets are gradient pills, every result row
// surfaces a gradient distance badge and like count.
import React, { useCallback, useEffect, useState } from 'react';
import {
  FlatList,
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
import DistanceBadge from '../components/DistanceBadge';
import EmptyState from '../components/EmptyState';
import GradientButton from '../components/GradientButton';
import GradientPill from '../components/GradientPill';
import GradientProgress from '../components/GradientProgress';
import ScreenContainer from '../components/ScreenContainer';
import StatRow from '../components/StatRow';
import {
  colors,
  radii,
  spacing,
  typography,
} from '../theme';

const PRESETS = [
  { label: 'Lisbon', lat: 38.72, lng: -9.14 },
  { label: 'New York', lat: 40.71, lng: -74.0 },
  { label: 'Tokyo', lat: 35.68, lng: 139.65 },
  { label: 'Mumbai', lat: 19.08, lng: 72.88 },
];

export default function NearbyScreen() {
  const { openPost, openProfile } = useApp();
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
    api.geoStats().then(setStats).catch(() => undefined);
    search();
  }, [search]);

  const distanceFor = useCallback(
    (item) => {
      if (item.distance != null) return item.distance;
      const queryLat = parseFloat(lat);
      const queryLng = parseFloat(lng);
      const dx = (item.x ?? 0) - queryLng;
      const dy = (item.y ?? 0) - queryLat;
      return Math.sqrt(dx * dx + dy * dy);
    },
    [lat, lng],
  );

  return (
    <ScreenContainer>
      <View style={styles.header}>
        <View style={{ flex: 1 }}>
          <Text style={[typography.display, { color: colors.text }]}>nearby</Text>
          {/* internal: posts located by the lab 7 quadtree */}
          <Text style={[typography.caption, { color: colors.muted }]}>
            posts shared around you
          </Text>
        </View>
        {stats ? <StatRow size="sm" items={[{ value: stats.size, label: 'in tree' }]} /> : null}
      </View>
      <View style={styles.inputRow}>
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
          placeholder="radius"
          placeholderTextColor={colors.muted}
          style={styles.input}
        />
        <GradientButton label="search" onPress={search} size="sm" />
      </View>
      <ScrollView
        horizontal
        showsHorizontalScrollIndicator={false}
        contentContainerStyle={styles.presetBar}
      >
        {PRESETS.map((p) => (
          <View key={p.label} style={styles.presetChip}>
            <GradientPill
              label={p.label}
              onPress={() => {
                setLat(String(p.lat));
                setLng(String(p.lng));
              }}
              variant="outline"
              size="sm"
            />
          </View>
        ))}
      </ScrollView>
      <GradientProgress active={loading} />
      <FlatList
        data={items}
        keyExtractor={(item) => String(item.post_id || item.key)}
        contentContainerStyle={styles.list}
        renderItem={({ item }) => (
          <Pressable style={styles.row} onPress={() => openPost(item.post_id)}>
            <Pressable onPress={() => openProfile(item.author_username)} hitSlop={4}>
              <AvatarRing username={item.author_username || ''} size={42} />
            </Pressable>
            <View style={styles.body}>
              <View style={styles.bodyHead}>
                <Text
                  style={[typography.bodyStrong, { color: colors.text }]}
                  onPress={() => openProfile(item.author_username)}
                >
                  @{item.author_username || 'unknown'}
                </Text>
                <DistanceBadge distance={distanceFor(item)} />
              </View>
              <Text style={[typography.body, { color: colors.text }]} numberOfLines={2}>
                {item.caption || 'no caption'}
              </Text>
              <Text style={[typography.caption, { color: colors.muted, marginTop: 2 }]}>
                {item.location || ''} . ({item.y?.toFixed(2)}, {item.x?.toFixed(2)})
              </Text>
            </View>
          </Pressable>
        )}
        ListEmptyComponent={
          !loading ? (
            <EmptyState
              glyph="g"
              title="no posts in this radius"
              body="try a wider radius or pick a city to see posts nearby."
            />
          ) : null
        }
      />
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
  inputRow: {
    flexDirection: 'row',
    paddingHorizontal: spacing.lg,
    paddingBottom: spacing.sm,
    alignItems: 'center',
  },
  input: {
    color: colors.text,
    backgroundColor: colors.inputBackground,
    borderRadius: radii.md,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    flex: 1,
    marginRight: spacing.sm,
  },
  presetBar: {
    paddingHorizontal: spacing.lg,
    paddingBottom: spacing.sm,
  },
  presetChip: { marginRight: spacing.sm },
  list: { paddingTop: spacing.sm, paddingBottom: spacing.xxl, flexGrow: 1 },
  row: {
    flexDirection: 'row',
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
    borderBottomColor: colors.border,
    borderBottomWidth: 1,
  },
  body: { flex: 1, marginLeft: spacing.md },
  bodyHead: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 2,
  },
  error: { color: colors.text, padding: spacing.md },
});
