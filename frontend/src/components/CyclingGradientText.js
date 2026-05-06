// gradient text whose stops slowly rotate over time so the wordmark feels
// alive without a heavy animation. on web we re-emit the css gradient with
// a shifted stop list every `interval` ms; on native we fall back to the
// static brand-tinted text since GradientText already does so.
import React, { useEffect, useState } from 'react';
import { Platform, Text } from 'react-native';

import { gradientStops } from '../theme';
import GradientText from './GradientText';

function rotate(arr, n) {
  if (!arr.length) return arr;
  const k = ((n % arr.length) + arr.length) % arr.length;
  return arr.slice(k).concat(arr.slice(0, k));
}

export default function CyclingGradientText({
  children,
  style,
  intervalMs = 2400,
  baseStops = gradientStops,
}) {
  const [tick, setTick] = useState(0);
  useEffect(() => {
    const id = setInterval(() => setTick((t) => t + 1), intervalMs);
    return () => clearInterval(id);
  }, [intervalMs]);

  if (Platform.OS !== 'web') {
    // GradientText already renders a calm brand tint on native; we keep it
    // static there to honour the "no heavy animations" rule
    return <GradientText style={style}>{children}</GradientText>;
  }
  const rotated = rotate(baseStops, tick);
  return (
    <Text
      style={[
        style,
        {
          backgroundImage: `linear-gradient(135deg, ${rotated.join(', ')})`,
          backgroundClip: 'text',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          color: 'transparent',
          transition: 'background-image 0.6s ease',
        },
      ]}
    >
      {children}
    </Text>
  );
}
