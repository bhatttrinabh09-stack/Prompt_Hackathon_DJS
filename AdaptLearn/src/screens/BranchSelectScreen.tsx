import React, { useState } from 'react';
import { Pressable, StyleSheet, Text, View } from 'react-native';
import { theme } from '../theme/theme';
import { useAppStore } from '../store/useStore';
import { setBranch } from '../api/auth';
import type { Branch } from '../types';

// Prototype scope: only AIML is selectable. Add more branches here as the
// backend/content library grows — the UI already renders a list.
const BRANCHES: { code: Branch; label: string; enabled: boolean }[] = [
  { code: 'AIML', label: 'AI & ML', enabled: true },
];

export default function BranchSelectScreen() {
  const user = useAppStore((s) => s.user);
  const setUser = useAppStore((s) => s.setUser);
  const [submitting, setSubmitting] = useState<Branch | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleSelect(branch: Branch) {
    if (!user) return;
    setSubmitting(branch);
    setError(null);
    try {
      const updated = await setBranch(branch);
      setUser(updated);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Could not save your branch.');
    } finally {
      setSubmitting(null);
    }
  }

  return (
    <View style={styles.wrapper}>
      <Text style={styles.title}>Which branch are you in?</Text>
      <Text style={styles.subtitle}>Your subjects and content are matched to your branch.</Text>

      {BRANCHES.map((b) => (
        <Pressable
          key={b.code}
          onPress={() => b.enabled && handleSelect(b.code)}
          style={[styles.option, !b.enabled && styles.optionDisabled]}
        >
          <Text style={styles.optionLabel}>{b.label}</Text>
          <Text style={styles.optionMeta}>
            {submitting === b.code ? 'Saving…' : b.enabled ? '' : 'Coming soon'}
          </Text>
        </Pressable>
      ))}

      {error && <Text style={styles.error}>{error}</Text>}
    </View>
  );
}

const styles = StyleSheet.create({
  wrapper: { flex: 1, backgroundColor: theme.color.background, padding: theme.spacing(6) },
  title: { ...theme.font.heading, color: theme.color.textPrimary, marginBottom: theme.spacing(1) },
  subtitle: { ...theme.font.body, color: theme.color.textMuted, marginBottom: theme.spacing(6) },
  option: {
    borderWidth: 1,
    borderColor: theme.color.border,
    borderRadius: theme.radius.md,
    padding: theme.spacing(4),
    marginBottom: theme.spacing(3),
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: theme.color.surface,
  },
  optionDisabled: { opacity: 0.4 },
  optionLabel: { ...theme.font.subheading, color: theme.color.textPrimary },
  optionMeta: { ...theme.font.caption, color: theme.color.textMuted },
  error: { color: theme.color.panic, marginTop: theme.spacing(2) },
});
