// near-invisible 1px rule used between cards and sections.
import React from 'react';
import { StyleSheet, View } from 'react-native';

import { colors, spacing } from '../theme';

export default function SectionDivider({ inset = 0, vertical = false }) {
  if (vertical) {
    return <View style={[styles.vertical, { marginHorizontal: spacing.sm }]} />;
  }
  return <View style={[styles.line, { marginHorizontal: inset }]} />;
}

const styles = StyleSheet.create({
  line: {
    height: 1,
    backgroundColor: colors.border,
  },
  vertical: {
    width: 1,
    alignSelf: 'stretch',
    backgroundColor: colors.border,
  },
});
