// wraps the active screen in safe area + a 450px web shell so the app reads
// as a phone interface inside a browser tab.
import React from 'react';
import { Platform, StyleSheet, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { colors, layout, spacing } from '../theme';

export default function ScreenContainer({
  children,
  padded = true,
  edges = ['top'],
  scrollable = false,
}) {
  const inner = (
    <View style={[styles.inner, padded && styles.padded]}>{children}</View>
  );

  return (
    <View style={styles.outer}>
      <SafeAreaView edges={edges} style={styles.shell}>
        {inner}
      </SafeAreaView>
    </View>
  );
}

const isWeb = Platform.OS === 'web';

const styles = StyleSheet.create({
  outer: {
    flex: 1,
    backgroundColor: isWeb ? '#ececef' : colors.background,
    alignItems: 'center',
  },
  shell: {
    flex: 1,
    width: '100%',
    maxWidth: layout.maxAppWidth,
    backgroundColor: colors.background,
    ...(isWeb && {
      shadowColor: '#000',
      shadowOpacity: 0.08,
      shadowRadius: 24,
      shadowOffset: { width: 0, height: 4 },
    }),
  },
  inner: {
    flex: 1,
    backgroundColor: colors.background,
  },
  padded: {
    paddingHorizontal: spacing.screen,
  },
});
