// soft gray rounded search field with a leading magnifier glyph and an
// optional clear button. matches the modern instagram search look.
import React from 'react';
import { Pressable, StyleSheet, Text, TextInput, View } from 'react-native';

import { colors, radii, spacing, typography } from '../theme';

export default function SearchInput({
  value,
  onChangeText,
  placeholder = 'search',
  onClear,
  autoFocus = false,
  onSubmitEditing,
}) {
  return (
    <View style={styles.wrap}>
      <Text style={styles.glyph}>q</Text>
      <TextInput
        value={value}
        onChangeText={onChangeText}
        placeholder={placeholder}
        placeholderTextColor={colors.muted}
        autoFocus={autoFocus}
        onSubmitEditing={onSubmitEditing}
        style={[typography.body, styles.input]}
        autoCorrect={false}
        autoCapitalize="none"
      />
      {value ? (
        <Pressable onPress={onClear} hitSlop={8} style={styles.clear}>
          <Text style={styles.clearText}>x</Text>
        </Pressable>
      ) : null}
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.inputBackground,
    borderRadius: radii.lg,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
  },
  glyph: {
    color: colors.muted,
    fontSize: 14,
    fontWeight: '700',
    marginRight: spacing.sm,
    transform: [{ rotate: '45deg' }],
  },
  input: {
    flex: 1,
    color: colors.text,
    paddingVertical: 0,
  },
  clear: {
    width: 18,
    height: 18,
    borderRadius: 9,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: colors.borderStrong,
  },
  clearText: { color: colors.background, fontSize: 11, fontWeight: '700' },
});
