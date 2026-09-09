// Design direction: a focused "study terminal" feel rather than a generic
// SaaS look — deep navy surfaces (calm, low-glare for long study sessions),
// a mint accent for normal/positive state, and a distinct coral-red reserved
// ONLY for Panic Mode so urgency is instantly, unambiguously legible.

export const theme = {
  color: {
    background: '#10152A',
    surface: '#1A2140',
    surfaceRaised: '#232B4D',
    border: '#2E3760',

    textPrimary: '#F5F7FA',
    textMuted: '#9AA3B8',

    accent: '#5EEAD4', // mint — primary actions, progress, calm state
    accentMuted: '#22403D',
    violet: '#8B7CF6', // secondary highlight — Fast Track tag, must-ask chips

    panic: '#FF5D3A', // reserved exclusively for Panic Mode
    panicMuted: '#472A22',

    success: '#4ADE80',
  },
  spacing: (n: number) => n * 4,
  radius: {
    sm: 6,
    md: 12,
    lg: 20,
    pill: 999,
  },
  font: {
    heading: { fontSize: 22, fontWeight: '700' as const },
    subheading: { fontSize: 17, fontWeight: '600' as const },
    body: { fontSize: 15, fontWeight: '400' as const },
    caption: { fontSize: 12, fontWeight: '500' as const },
  },
};

export type Theme = typeof theme;
