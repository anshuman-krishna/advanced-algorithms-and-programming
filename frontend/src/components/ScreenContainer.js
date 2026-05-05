// thin screen-level wrapper. App.js already owns the safe area, the web
// shell, and the tabbar; this component just provides a consistent body
// background and optional horizontal padding.
import React from 'react';
import { StyleSheet, View } from 'react-native';

import { colors, spacing } from '../theme';

export default function ScreenContainer({ children, padded = false, style }) {
  return (
    <View style={[styles.body, padded && styles.padded, style]}>{children}</View>
  );
}

const styles = StyleSheet.create({
  body: { flex: 1, backgroundColor: colors.background },
  padded: { paddingHorizontal: spacing.screen },
});
