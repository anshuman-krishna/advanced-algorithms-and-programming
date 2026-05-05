// gradient aware tabbar. lives at the top of the app shell. active tab gets
// a gradient text label and a 2px gradient underline; inactive tabs stay
// in muted gray for a calm rest state.
import React from 'react';
import { Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';

import {
  colors,
  gradientDir,
  gradientStops,
  spacing,
  typography,
} from '../theme';
import GradientText from './GradientText';

export default function TabBar({ tabs, active, onChange }) {
  return (
    <View style={styles.bar}>
      <ScrollView
        horizontal
        showsHorizontalScrollIndicator={false}
        contentContainerStyle={styles.content}
      >
        {tabs.map((tab) => {
          const isActive = tab === active;
          return (
            <Pressable
              key={tab}
              onPress={() => onChange(tab)}
              style={styles.tab}
              hitSlop={6}
            >
              {isActive ? (
                <GradientText style={[typography.label, styles.label, styles.labelActive]}>
                  {tab}
                </GradientText>
              ) : (
                <Text style={[typography.label, styles.label]}>{tab}</Text>
              )}
              {isActive ? (
                <LinearGradient
                  colors={gradientStops}
                  start={gradientDir.horizontal.start}
                  end={gradientDir.horizontal.end}
                  style={styles.underline}
                />
              ) : (
                <View style={styles.underlineRest} />
              )}
            </Pressable>
          );
        })}
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  bar: {
    backgroundColor: colors.background,
    borderBottomColor: colors.border,
    borderBottomWidth: 1,
  },
  content: { paddingHorizontal: spacing.sm },
  tab: {
    paddingHorizontal: spacing.lg,
    paddingTop: spacing.md,
    alignItems: 'center',
  },
  label: { color: colors.muted, letterSpacing: 0.5, textTransform: 'uppercase' },
  labelActive: { color: colors.text },
  underline: {
    marginTop: spacing.sm,
    height: 2,
    width: '100%',
    borderRadius: 2,
    alignSelf: 'stretch',
  },
  underlineRest: {
    marginTop: spacing.sm,
    height: 2,
  },
});
