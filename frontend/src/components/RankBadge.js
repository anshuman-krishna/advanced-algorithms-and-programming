// gradient pill used to label trending positions on items the lab 8 max heap
// surfaces as #1 / #2 / #3.
import React from 'react';
import { StyleSheet, Text } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';

import { gradientDir, gradientStops, radii, spacing, typography } from '../theme';

export default function RankBadge({ rank }) {
  return (
    <LinearGradient
      colors={gradientStops}
      start={gradientDir.diagonal.start}
      end={gradientDir.diagonal.end}
      style={styles.pill}
    >
      <Text style={[typography.label, styles.label]}>#{rank}</Text>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  pill: {
    paddingHorizontal: spacing.sm,
    paddingVertical: 2,
    borderRadius: radii.pill,
    alignSelf: 'flex-start',
  },
  label: { color: '#ffffff', letterSpacing: 0.4 },
});
