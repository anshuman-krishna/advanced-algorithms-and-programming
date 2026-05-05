// instagram inspired palette. backgrounds stay neutral; gradients are reserved
// for active states, primary ctas, story rings, and engagement accents.

export const colors = {
  background: '#ffffff',
  surface: '#fbfbfd',
  surfaceMuted: '#f4f4f6',
  text: '#0a0a0c',
  textSubtle: '#3a3a3f',
  muted: '#8e8e93',
  border: '#ececef',
  borderStrong: '#d9d9de',
  primary: '#d6249f',
  scrim: 'rgba(0, 0, 0, 0.55)',
  inputBackground: '#f1f1f4',
};

// the gradient stops, in order. yellow into orange into pink into purple,
// matched to the classic instagram logo wash.
export const gradientStops = ['#feda75', '#fa7e1e', '#d62976', '#962fbf', '#4f5bd5'];

// short two-stop variants for compact surfaces (small dots, pill chips).
export const gradientStopsShort = ['#fa7e1e', '#962fbf'];

// directions kept here so every gradient renders identically.
export const gradientDir = {
  diagonal: { start: { x: 0, y: 0 }, end: { x: 1, y: 1 } },
  horizontal: { start: { x: 0, y: 0.5 }, end: { x: 1, y: 0.5 } },
  vertical: { start: { x: 0.5, y: 0 }, end: { x: 0.5, y: 1 } },
  bottomScrim: { start: { x: 0.5, y: 0 }, end: { x: 0.5, y: 1 } },
};
