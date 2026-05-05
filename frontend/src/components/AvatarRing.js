// gradient story ring around an avatar. the ring is a gradient circle with a
// white inner spacer and a colored disc that holds the user initial.
import React from 'react';
import { Image, StyleSheet, Text, View } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';

import { colors, gradientDir, gradientStops, typography } from '../theme';

const SOLID_COLORS = ['#fa7e1e', '#d62976', '#962fbf', '#4f5bd5', '#feda75'];

function colorFor(seed = '') {
  if (!seed) return SOLID_COLORS[0];
  let hash = 0;
  for (let i = 0; i < seed.length; i += 1) {
    hash = (hash * 31 + seed.charCodeAt(i)) >>> 0;
  }
  return SOLID_COLORS[hash % SOLID_COLORS.length];
}

export default function AvatarRing({
  username = '',
  imageUrl,
  size = 44,
  ringWidth = 2,
  showRing = true,
}) {
  const innerSize = size - ringWidth * 2;
  const discSize = innerSize - 2;
  const initial = (username || '?').slice(0, 1).toUpperCase();
  const fallbackColor = colorFor(username);
  const inner = (
    <View
      style={[
        styles.innerWrap,
        { width: innerSize, height: innerSize, borderRadius: innerSize / 2 },
      ]}
    >
      {imageUrl ? (
        <Image
          source={{ uri: imageUrl }}
          style={{ width: discSize, height: discSize, borderRadius: discSize / 2 }}
        />
      ) : (
        <View
          style={[
            styles.disc,
            {
              width: discSize,
              height: discSize,
              borderRadius: discSize / 2,
              backgroundColor: fallbackColor,
            },
          ]}
        >
          <Text style={[typography.bodyStrong, styles.initial]}>{initial}</Text>
        </View>
      )}
    </View>
  );
  if (!showRing) {
    return (
      <View style={{ width: size, height: size, borderRadius: size / 2, alignItems: 'center', justifyContent: 'center' }}>
        {inner}
      </View>
    );
  }
  return (
    <LinearGradient
      colors={gradientStops}
      start={gradientDir.diagonal.start}
      end={gradientDir.diagonal.end}
      style={[styles.ring, { width: size, height: size, borderRadius: size / 2 }]}
    >
      {inner}
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  ring: { alignItems: 'center', justifyContent: 'center' },
  innerWrap: {
    backgroundColor: colors.background,
    alignItems: 'center',
    justifyContent: 'center',
  },
  disc: { alignItems: 'center', justifyContent: 'center' },
  initial: { color: '#ffffff' },
});
