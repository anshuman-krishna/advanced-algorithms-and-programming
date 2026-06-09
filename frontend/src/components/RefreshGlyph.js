// drawn refresh icon. an open ring (a circle View with one transparent border
// edge to leave a gap) plus a small triangle arrowhead at the gap. zero deps and
// stays crisp at any size since react native draws it, not a font glyph.
import React from 'react';
import { StyleSheet, View } from 'react-native';

import { colors } from '../theme';

export default function RefreshGlyph({ size = 18, color = colors.primary }) {
  const ring = Math.round(size);
  const head = Math.round(size * 0.32);
  return (
    <View style={[styles.wrap, { width: ring, height: ring }]}>
      <View
        style={{
          width: ring,
          height: ring,
          borderRadius: ring / 2,
          borderWidth: 2,
          borderColor: color,
          borderTopColor: 'transparent',
          transform: [{ rotate: '40deg' }],
        }}
      />
      <View
        style={{
          position: 'absolute',
          top: -1,
          right: 0,
          width: 0,
          height: 0,
          borderLeftWidth: head,
          borderRightWidth: head,
          borderBottomWidth: head * 1.4,
          borderLeftColor: 'transparent',
          borderRightColor: 'transparent',
          borderBottomColor: color,
          transform: [{ rotate: '110deg' }],
        }}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: { alignItems: 'center', justifyContent: 'center', position: 'relative' },
});
