// outer chrome of the app: phone shaped 450px max width on web with a soft
// drop shadow, full bleed on native, safe area inset at the top, and an
// optional tabbar slot. extracted from App.js so adding a real bottom
// navigator later is a localized change.
import React from 'react';
import { Platform, StyleSheet, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { colors, layout } from '../theme';

const isWeb = Platform.OS === 'web';

export default function RootShell({ topBar, children, bottomBar = null, overlay = null }) {
  return (
    <View style={styles.outer}>
      <View style={styles.shell}>
        <SafeAreaView style={styles.safe} edges={['top']}>
          {topBar}
          <View style={styles.body}>{children}</View>
          {bottomBar}
        </SafeAreaView>
        {overlay ? (
          <SafeAreaView style={styles.overlay} edges={['top']}>
            {overlay}
          </SafeAreaView>
        ) : null}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  outer: {
    flex: 1,
    backgroundColor: isWeb ? '#ececef' : colors.background,
    alignItems: 'center',
    justifyContent: 'center',
  },
  shell: {
    flex: 1,
    width: '100%',
    maxWidth: layout.maxAppWidth,
    backgroundColor: colors.background,
    ...(isWeb && {
      shadowColor: '#000',
      shadowOpacity: 0.12,
      shadowRadius: 28,
      shadowOffset: { width: 0, height: 6 },
    }),
  },
  safe: { flex: 1, backgroundColor: colors.background },
  body: { flex: 1, backgroundColor: colors.background },
  overlay: { ...StyleSheet.absoluteFillObject, backgroundColor: 'transparent', zIndex: 40 },
});
