// 8px gradient dot. used to flag unread or priority items.
import React from 'react';
import { StyleSheet } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';

import { gradientDir, gradientStops } from '../theme';

export default function GradientDot({ size = 8 }) {
  return (
    <LinearGradient
      colors={gradientStops}
      start={gradientDir.diagonal.start}
      end={gradientDir.diagonal.end}
      style={[styles.dot, { width: size, height: size, borderRadius: size / 2 }]}
    />
  );
}

const styles = StyleSheet.create({
  dot: { alignSelf: 'center' },
});
