// gradient number + muted label, optionally inside a soft surface chip.
// the engagement numbers should always be the brightest element on the card
// since they are what every screen is selling. when `chip` is true we add a
// soft pill background so it can stand alone over an image.
import React from 'react';
import { Platform, StyleSheet, Text, View } from 'react-native';

import { colors, radii, spacing, typography } from '../theme';
import GradientText from './GradientText';

function compactNumber(n) {
  if (n == null) return '0';
  if (typeof n !== 'number') return String(n);
  if (n < 1000) return String(n);
  if (n < 1_000_000) return `${(n / 1000).toFixed(n < 10_000 ? 1 : 0)}k`;
  return `${(n / 1_000_000).toFixed(1)}m`;
}

export default function StatPill({
  value,
  label,
  chip = false,
  size = 'md',
  inverted = false,
}) {
  const numberStyle = size === 'sm' ? styles.numberSm : styles.numberMd;
  const labelStyle = size === 'sm' ? styles.labelSm : styles.labelMd;
  const display = compactNumber(value);
  const Wrapper = chip ? View : React.Fragment;
  const wrapperProps = chip ? { style: styles.chip } : {};
  return (
    <Wrapper {...wrapperProps}>
      <View style={styles.row}>
        {inverted ? (
          <Text style={[numberStyle, styles.numberInverted]}>{display}</Text>
        ) : (
          <GradientText style={numberStyle}>{display}</GradientText>
        )}
        {label ? (
          <Text
            style={[
              labelStyle,
              { color: inverted ? 'rgba(255,255,255,0.85)' : colors.muted },
            ]}
          >
            {label}
          </Text>
        ) : null}
      </View>
    </Wrapper>
  );
}

const baseNumber = {
  ...typography.title,
  letterSpacing: -0.4,
  ...(Platform.OS === 'web' ? { lineHeight: 22 } : {}),
};

const styles = StyleSheet.create({
  chip: {
    backgroundColor: colors.surfaceMuted,
    borderRadius: radii.pill,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.xs,
    alignSelf: 'flex-start',
  },
  row: { flexDirection: 'row', alignItems: 'baseline' },
  numberMd: { ...baseNumber, fontSize: 18 },
  numberSm: { ...baseNumber, fontSize: 14 },
  numberInverted: { ...baseNumber, color: '#ffffff' },
  labelMd: {
    ...typography.caption,
    marginLeft: spacing.xs,
    fontSize: 12,
  },
  labelSm: {
    ...typography.caption,
    marginLeft: spacing.xs,
    fontSize: 11,
  },
});
