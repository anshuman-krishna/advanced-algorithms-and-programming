// gradient glyphs via the CSS background-clip trick on web. on native we fall
// back to a strong solid tint from the middle of the gradient so we don't
// pull in optional libraries like MaskedView.
import React from 'react';
import { Platform, Text } from 'react-native';

import { gradientStops } from '../theme';

export default function GradientText({ children, style, stops = gradientStops }) {
  if (Platform.OS === 'web') {
    return (
      <Text
        style={[
          style,
          {
            backgroundImage: `linear-gradient(135deg, ${stops.join(', ')})`,
            backgroundClip: 'text',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            color: 'transparent',
          },
        ]}
      >
        {children}
      </Text>
    );
  }
  return <Text style={[style, { color: stops[2] }]}>{children}</Text>;
}
