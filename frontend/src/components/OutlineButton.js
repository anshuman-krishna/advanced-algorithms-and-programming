// secondary cta. faint border, dark text. complements GradientButton.
import React from 'react';
import { Pressable, StyleSheet, Text } from 'react-native';

import { colors, radii, spacing, typography } from '../theme';

export default function OutlineButton({ label, onPress, size = 'md', style, disabled = false }) {
  const padding =
    size === 'sm'
      ? { paddingVertical: spacing.sm, paddingHorizontal: spacing.lg }
      : { paddingVertical: spacing.md, paddingHorizontal: spacing.xl };
  return (
    <Pressable
      onPress={disabled ? undefined : onPress}
      style={({ pressed }) => [
        styles.btn,
        padding,
        pressed && !disabled && styles.pressed,
        disabled && styles.disabled,
        style,
      ]}
    >
      <Text style={[typography.bodyStrong, styles.label]}>{label}</Text>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  btn: {
    borderRadius: radii.lg,
    borderWidth: 1,
    borderColor: colors.borderStrong,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: colors.background,
  },
  pressed: { backgroundColor: colors.surfaceMuted },
  disabled: { opacity: 0.55 },
  label: { color: colors.text },
});
