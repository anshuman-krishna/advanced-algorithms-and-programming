// primary cta with the instagram gradient. handles pressed and disabled.
import React from 'react';
import { Pressable, StyleSheet, Text } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';

import { colors, gradientDir, gradientStops, radii, spacing, typography } from '../theme';

export default function GradientButton({
  label,
  onPress,
  disabled = false,
  size = 'md',
  style,
  fullWidth = false,
}) {
  const padding =
    size === 'sm'
      ? { paddingVertical: spacing.sm, paddingHorizontal: spacing.lg }
      : { paddingVertical: spacing.md, paddingHorizontal: spacing.xl };
  return (
    <Pressable
      onPress={disabled ? undefined : onPress}
      style={({ pressed }) => [
        styles.wrap,
        fullWidth && styles.fullWidth,
        pressed && !disabled && styles.pressed,
        disabled && styles.disabled,
        style,
      ]}
    >
      <LinearGradient
        colors={disabled ? [colors.borderStrong, colors.borderStrong] : gradientStops}
        start={gradientDir.diagonal.start}
        end={gradientDir.diagonal.end}
        style={[styles.gradient, padding]}
      >
        <Text style={[typography.bodyStrong, styles.label]}>{label}</Text>
      </LinearGradient>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  wrap: { borderRadius: radii.lg, overflow: 'hidden' },
  fullWidth: { alignSelf: 'stretch' },
  pressed: { opacity: 0.85 },
  disabled: { opacity: 0.6 },
  gradient: { alignItems: 'center', justifyContent: 'center' },
  label: { color: '#ffffff', letterSpacing: 0.2 },
});
