// rounded chip. variant=solid renders a gradient background with white text;
// variant=outline renders a soft surface chip with gradient text. used by
// category strips, city presets, chain hops, etc.
import React from 'react';
import { Pressable, StyleSheet, Text, View } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';

import {
  colors,
  gradientDir,
  gradientStops,
  radii,
  spacing,
  typography,
} from '../theme';
import GradientText from './GradientText';

export default function GradientPill({
  label,
  onPress,
  variant = 'outline',
  size = 'md',
  selected = false,
  style,
}) {
  const padding =
    size === 'sm'
      ? { paddingVertical: spacing.xs, paddingHorizontal: spacing.md }
      : { paddingVertical: spacing.sm, paddingHorizontal: spacing.lg };

  const Wrapper = onPress ? Pressable : View;
  const wrapperProps = onPress ? { onPress } : {};

  const isSolid = variant === 'solid' || selected;

  if (isSolid) {
    return (
      <Wrapper {...wrapperProps} style={[styles.outer, style]}>
        <LinearGradient
          colors={gradientStops}
          start={gradientDir.diagonal.start}
          end={gradientDir.diagonal.end}
          style={[styles.solid, padding]}
        >
          <Text style={[typography.label, styles.solidLabel]}>{label}</Text>
        </LinearGradient>
      </Wrapper>
    );
  }
  return (
    <Wrapper {...wrapperProps} style={[styles.outer, styles.outline, padding, style]}>
      <GradientText style={typography.label}>{label}</GradientText>
    </Wrapper>
  );
}

const styles = StyleSheet.create({
  outer: { borderRadius: radii.pill, overflow: 'hidden', alignSelf: 'flex-start' },
  outline: {
    backgroundColor: colors.surfaceMuted,
    borderWidth: 0,
  },
  solid: { alignItems: 'center', justifyContent: 'center' },
  solidLabel: { color: '#ffffff', letterSpacing: 0.4 },
});
