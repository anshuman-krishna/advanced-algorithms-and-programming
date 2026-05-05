// gradient distance label used by the nearby screen results. converts the
// raw planar distance returned by the lab 7 quadtree into a human compact form.
import React from 'react';
import { StyleSheet } from 'react-native';

import { spacing } from '../theme';
import GradientPill from './GradientPill';

function formatDistance(d) {
  if (d == null) return '';
  if (d < 0.01) return '<0.01';
  if (d < 1) return `${d.toFixed(2)}`;
  return `${d.toFixed(1)}`;
}

export default function DistanceBadge({ distance, unit = 'deg' }) {
  return (
    <GradientPill
      label={`${formatDistance(distance)} ${unit}`}
      variant="outline"
      size="sm"
      style={styles.badge}
    />
  );
}

const styles = StyleSheet.create({
  badge: { marginLeft: spacing.sm },
});
