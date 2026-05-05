// type scale. weights stay in the system stack so we never ship a font file.
import { Platform } from 'react-native';

const fontFamily = Platform.select({
  ios: undefined,
  android: 'sans-serif',
  default: undefined,
});

export const typography = {
  display: {
    fontSize: 22,
    fontWeight: '700',
    letterSpacing: -0.4,
    fontFamily,
  },
  title: {
    fontSize: 18,
    fontWeight: '700',
    letterSpacing: -0.2,
    fontFamily,
  },
  subtitle: {
    fontSize: 15,
    fontWeight: '600',
    letterSpacing: -0.1,
    fontFamily,
  },
  body: {
    fontSize: 14,
    fontWeight: '400',
    fontFamily,
  },
  bodyStrong: {
    fontSize: 14,
    fontWeight: '600',
    fontFamily,
  },
  label: {
    fontSize: 12,
    fontWeight: '600',
    letterSpacing: 0.2,
    fontFamily,
  },
  caption: {
    fontSize: 12,
    fontWeight: '400',
    fontFamily,
  },
};
