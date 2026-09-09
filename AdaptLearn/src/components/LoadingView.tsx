import React from 'react';
import { ActivityIndicator, StyleSheet, Text, View } from 'react-native';
import { theme } from '../theme/theme';

export default function LoadingView({ label = 'Loading…' }: { label?: string }) {
  return (
    <View style={styles.wrapper}>
      <ActivityIndicator color={theme.color.accent} size="large" />
      <Text style={styles.label}>{label}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  wrapper: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  label: { ...theme.font.body, color: theme.color.textMuted, marginTop: theme.spacing(3) },
});
