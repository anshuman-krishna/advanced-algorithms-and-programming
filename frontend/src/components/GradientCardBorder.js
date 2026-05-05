// thin gradient border via a 1px gradient frame around a white inner card.
// used for highlight cards (analytics summary, niche post groups) so they
// stand out without filling the whole surface with color.
import React from 'react';
import { StyleSheet, View } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';

import { colors, gradientDir, gradientStops, radii } from '../theme';

export default function GradientCardBorder({ children, radius = radii.lg, style }) {
  return (
    <LinearGradient
      colors={gradientStops}
      start={gradientDir.diagonal.start}
      end={gradientDir.diagonal.end}
      style={[styles.frame, { borderRadius: radius }, style]}
    >
      <View style={[styles.inner, { borderRadius: radius - 1 }]}>{children}</View>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  frame: { padding: 1 },
  inner: { backgroundColor: colors.background, overflow: 'hidden' },
});
