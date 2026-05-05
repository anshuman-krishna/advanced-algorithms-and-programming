// gradient icon block plus a friendly title + body. used everywhere a list
// could be empty so screens never look broken.
import React from 'react';
import { StyleSheet, Text, View } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';

import {
  colors,
  gradientDir,
  gradientStops,
  radii,
  spacing,
  typography,
} from '../theme';

export default function EmptyState({
  glyph = '',
  title = 'nothing here yet',
  body = 'come back after some action happens.',
  action = null,
}) {
  return (
    <View style={styles.wrap}>
      <LinearGradient
        colors={gradientStops}
        start={gradientDir.diagonal.start}
        end={gradientDir.diagonal.end}
        style={styles.icon}
      >
        <Text style={styles.glyph}>{glyph || ' '}</Text>
      </LinearGradient>
      <Text style={[typography.title, styles.title]}>{title}</Text>
      <Text style={[typography.body, styles.body]}>{body}</Text>
      {action ? <View style={styles.action}>{action}</View> : null}
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: spacing.xl,
    paddingVertical: spacing.xxxl,
  },
  icon: {
    width: 72,
    height: 72,
    borderRadius: radii.lg,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: spacing.lg,
  },
  glyph: {
    color: '#ffffff',
    fontSize: 30,
    fontWeight: '700',
  },
  title: {
    color: colors.text,
    textAlign: 'center',
    marginBottom: spacing.xs,
  },
  body: {
    color: colors.muted,
    textAlign: 'center',
    maxWidth: 280,
  },
  action: { marginTop: spacing.lg },
});
