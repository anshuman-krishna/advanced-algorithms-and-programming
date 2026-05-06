// drawn magnifier icon. circle (border-only View) plus a rotated handle
// (a thin View with a border-radius cap). zero deps and stays crisp at any
// size since it is rendered by react native, not a font glyph.
import React from 'react';
import { StyleSheet, View } from 'react-native';

import { colors } from '../theme';

export default function MagnifierGlyph({ size = 14, color = colors.muted }) {
  const ringSize = Math.round(size * 0.7);
  const handleLength = Math.round(size * 0.4);
  return (
    <View style={[styles.wrap, { width: size, height: size }]}>
      <View
        style={[
          styles.ring,
          {
            width: ringSize,
            height: ringSize,
            borderRadius: ringSize / 2,
            borderColor: color,
          },
        ]}
      />
      <View
        style={[
          styles.handle,
          {
            width: handleLength,
            backgroundColor: color,
            top: ringSize - 2,
            left: ringSize - 2,
          },
        ]}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: {
    alignItems: 'flex-start',
    justifyContent: 'flex-start',
    position: 'relative',
  },
  ring: {
    borderWidth: 1.5,
    backgroundColor: 'transparent',
  },
  handle: {
    position: 'absolute',
    height: 1.5,
    borderRadius: 1,
    transform: [{ rotate: '45deg' }],
  },
});
