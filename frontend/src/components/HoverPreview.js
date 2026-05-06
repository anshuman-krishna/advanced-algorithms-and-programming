// child wrapper that reveals an absolutely positioned overlay when the user
// hovers (web) or long presses (native) the underlying tile. designed for
// small tiles where the caption cannot fit; the overlay surfaces the full
// caption + author + stats over a soft scrim.
import React, { useState } from 'react';
import { Pressable, StyleSheet, View } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';

import { radii } from '../theme';

export default function HoverPreview({ children, overlay, radius = radii.lg }) {
  const [active, setActive] = useState(false);
  return (
    <Pressable
      onHoverIn={() => setActive(true)}
      onHoverOut={() => setActive(false)}
      onLongPress={() => setActive(true)}
      onPressOut={() => setActive(false)}
      delayLongPress={250}
      style={[styles.wrap, { borderRadius: radius }]}
    >
      {children}
      {active ? (
        <LinearGradient
          colors={['rgba(0,0,0,0.05)', 'rgba(0,0,0,0.75)']}
          start={{ x: 0.5, y: 0 }}
          end={{ x: 0.5, y: 1 }}
          style={[StyleSheet.absoluteFillObject, { borderRadius: radius, padding: 12 }]}
          pointerEvents="none"
        >
          <View style={styles.overlay} pointerEvents="none">
            {overlay}
          </View>
        </LinearGradient>
      ) : null}
    </Pressable>
  );
}

const styles = StyleSheet.create({
  wrap: { overflow: 'hidden' },
  overlay: { flex: 1, justifyContent: 'flex-end' },
});
