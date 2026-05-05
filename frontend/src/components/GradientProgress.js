// thin gradient bar used as a top of screen loading indicator.
// when active, fades in. when idle, takes no visual space.
import React, { useEffect, useRef } from 'react';
import { Animated, StyleSheet, View } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';

import { gradientDir, gradientStops } from '../theme';

export default function GradientProgress({ active = false, height = 2 }) {
  const opacity = useRef(new Animated.Value(0)).current;
  useEffect(() => {
    Animated.timing(opacity, {
      toValue: active ? 1 : 0,
      duration: 200,
      useNativeDriver: true,
    }).start();
  }, [active, opacity]);
  return (
    <View style={[styles.track, { height }]} pointerEvents="none">
      <Animated.View style={[styles.fill, { opacity }]}>
        <LinearGradient
          colors={gradientStops}
          start={gradientDir.horizontal.start}
          end={gradientDir.horizontal.end}
          style={[styles.gradient, { height }]}
        />
      </Animated.View>
    </View>
  );
}

const styles = StyleSheet.create({
  track: { width: '100%', overflow: 'hidden' },
  fill: { width: '100%' },
  gradient: { width: '100%' },
});
