import React from 'react';
import { Pressable, StyleSheet, Text } from 'react-native';
import { theme } from '../theme/theme';

interface Props {
  label: string;
  sublabel?: string;
  enabled: boolean;
  onPress: () => void;
}

export default function GridTile({ label, sublabel, enabled, onPress }: Props) {
  return (
    <Pressable
      onPress={enabled ? onPress : undefined}
      style={[styles.tile, !enabled && styles.tileDisabled]}
      accessibilityState={{ disabled: !enabled }}
    >
      <Text style={[styles.label, !enabled && styles.labelDisabled]}>{label}</Text>
      {sublabel ? <Text style={styles.sublabel}>{sublabel}</Text> : null}
      {!enabled && <Text style={styles.lockedTag}>Coming soon</Text>}
    </Pressable>
  );
}

const styles = StyleSheet.create({
  tile: {
    width: '47%',
    aspectRatio: 1.1,
    backgroundColor: theme.color.surface,
    borderRadius: theme.radius.lg,
    borderWidth: 1,
    borderColor: theme.color.border,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: theme.spacing(4),
  },
  tileDisabled: { opacity: 0.4 },
  label: { ...theme.font.subheading, color: theme.color.textPrimary },
  labelDisabled: { color: theme.color.textMuted },
  sublabel: { ...theme.font.caption, color: theme.color.textMuted, marginTop: theme.spacing(1) },
  lockedTag: {
    ...theme.font.caption,
    color: theme.color.textMuted,
    marginTop: theme.spacing(2),
  },
});
