// horizontal row of StatPills with vertical hairline separators between them.
// used at the bottom of cards / under usernames so engagement reads in one
// glance: 240 likes . 18 comments . 4k views.
import React from 'react';
import { StyleSheet, View } from 'react-native';

import { colors, spacing } from '../theme';
import StatPill from './StatPill';

export default function StatRow({ items = [], inverted = false, size = 'md' }) {
  const visible = items.filter(Boolean);
  return (
    <View style={styles.row}>
      {visible.map((item, idx) => (
        <React.Fragment key={`${item.label || ''}-${idx}`}>
          <StatPill
            value={item.value}
            label={item.label}
            inverted={inverted}
            size={size}
          />
          {idx < visible.length - 1 ? (
            <View
              style={[
                styles.divider,
                { backgroundColor: inverted ? 'rgba(255,255,255,0.4)' : colors.border },
              ]}
            />
          ) : null}
        </React.Fragment>
      ))}
    </View>
  );
}

const styles = StyleSheet.create({
  row: {
    flexDirection: 'row',
    alignItems: 'center',
    flexWrap: 'wrap',
  },
  divider: {
    width: 1,
    height: 14,
    marginHorizontal: spacing.md,
  },
});
