// shared chrome for every full screen overlay (post detail, profile, hashtag,
// story). a thin top bar with a back chevron and a title, then the body. the
// overlay fills the whole shell and sits above the tab content.
import React from 'react';
import { Pressable, StyleSheet, Text, View } from 'react-native';

import GradientText from './GradientText';
import { colors, spacing, typography } from '../theme';

export default function OverlayFrame({ title, onBack, right = null, children, dark = false }) {
  const bg = dark ? '#000' : colors.background;
  const fg = dark ? '#ffffff' : colors.text;
  return (
    <View style={[styles.wrap, { backgroundColor: bg }]}>
      <View style={[styles.bar, dark ? styles.barDark : null]}>
        <Pressable onPress={onBack} hitSlop={12} style={styles.back}>
          <Text style={[styles.chevron, { color: dark ? '#fff' : colors.primary }]}>‹</Text>
          <Text style={[typography.label, { color: dark ? '#fff' : colors.primary }]}>back</Text>
        </Pressable>
        {title ? (
          dark ? (
            <Text style={[typography.bodyStrong, styles.title, { color: fg }]} numberOfLines={1}>
              {title}
            </Text>
          ) : (
            <GradientText style={[typography.bodyStrong, styles.title]} numberOfLines={1}>
              {title}
            </GradientText>
          )
        ) : (
          <View style={styles.title} />
        )}
        <View style={styles.right}>{right}</View>
      </View>
      <View style={styles.body}>{children}</View>
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: { ...StyleSheet.absoluteFillObject, zIndex: 50 },
  bar: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    borderBottomColor: colors.border,
    borderBottomWidth: 1,
  },
  barDark: { borderBottomColor: 'rgba(255,255,255,0.12)' },
  back: { flexDirection: 'row', alignItems: 'center', width: 80 },
  chevron: { fontSize: 26, marginRight: 2, marginTop: -2 },
  title: { flex: 1, textAlign: 'center' },
  right: { width: 80, alignItems: 'flex-end' },
  body: { flex: 1 },
});
