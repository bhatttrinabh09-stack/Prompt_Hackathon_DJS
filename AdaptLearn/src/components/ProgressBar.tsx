import React from 'react';
import { StyleSheet, Text, View } from 'react-native';
import { theme } from '../theme/theme';

interface Props {
  percent: number; // 0-100
  label?: string;
  compact?: boolean;
}

export default function ProgressBar({ percent, label, compact }: Props) {
  const clamped = Math.max(0, Math.min(100, percent));
  return (
    <View style={compact ? styles.compactWrapper : styles.wrapper}>
      {label && <Text style={styles.label}>{label}</Text>}
      <View style={styles.track}>
        <View style={[styles.fill, { width: `${clamped}%` }]} />
      </View>
      <Text style={styles.percent}>{Math.round(clamped)}%</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  wrapper: { marginBottom: theme.spacing(4) },
  compactWrapper: { marginBottom: theme.spacing(2) },
  label: { ...theme.font.caption, color: theme.color.textMuted, marginBottom: theme.spacing(1) },
  track: {
    height: 8,
    borderRadius: theme.radius.pill,
    backgroundColor: theme.color.surfaceRaised,
    overflow: 'hidden',
  },
  fill: {
    height: '100%',
    backgroundColor: theme.color.accent,
    borderRadius: theme.radius.pill,
  },
  percent: {
    ...theme.font.caption,
    color: theme.color.textMuted,
    marginTop: theme.spacing(1),
    alignSelf: 'flex-end',
  },
});
