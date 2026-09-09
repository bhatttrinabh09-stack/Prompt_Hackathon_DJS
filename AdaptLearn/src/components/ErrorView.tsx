import React from 'react';
import { Pressable, StyleSheet, Text, View } from 'react-native';
import { theme } from '../theme/theme';

interface Props {
  message: string;
  onRetry?: () => void;
}

export default function ErrorView({ message, onRetry }: Props) {
  return (
    <View style={styles.wrapper}>
      <Text style={styles.title}>Something didn't load</Text>
      <Text style={styles.message}>{message}</Text>
      {onRetry && (
        <Pressable onPress={onRetry} style={styles.button}>
          <Text style={styles.buttonLabel}>Try again</Text>
        </Pressable>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  wrapper: { flex: 1, justifyContent: 'center', alignItems: 'center', padding: theme.spacing(6) },
  title: { ...theme.font.subheading, color: theme.color.textPrimary, marginBottom: theme.spacing(2) },
  message: {
    ...theme.font.body,
    color: theme.color.textMuted,
    textAlign: 'center',
    marginBottom: theme.spacing(4),
  },
  button: {
    backgroundColor: theme.color.accent,
    paddingVertical: theme.spacing(3),
    paddingHorizontal: theme.spacing(5),
    borderRadius: theme.radius.md,
  },
  buttonLabel: { color: theme.color.background, fontWeight: '700' },
});
