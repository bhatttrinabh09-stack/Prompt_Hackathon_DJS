import React, { useState } from 'react';
import { Modal, Pressable, StyleSheet, Text, TextInput, View } from 'react-native';
import { theme } from '../theme/theme';
import { useAppStore } from '../store/useStore';
import { startPanicSession } from '../api/panic';

interface Props {
  visible: boolean;
  onClose: () => void;
}

type Unit = 'days' | 'hours';

export default function PanicModal({ visible, onClose }: Props) {
  const setPanicSession = useAppStore((s) => s.setPanicSession);
  const [value, setValue] = useState('');
  const [unit, setUnit] = useState<Unit>('days');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit() {
    const numeric = Number(value);
    if (!value || Number.isNaN(numeric) || numeric <= 0) {
      setError('Enter a valid number.');
      return;
    }
    setSubmitting(true);
    setError(null);
    try {
      const session = await startPanicSession(numeric, unit);
      setPanicSession(session);
      setValue('');
      onClose();
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Could not start Panic Mode.');
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <Modal visible={visible} transparent animationType="fade" onRequestClose={onClose}>
      <View style={styles.backdrop}>
        <View style={styles.card}>
          <Text style={styles.title}>Exam in how many days/hours?</Text>
          <Text style={styles.subtitle}>
            We'll trim your content down to what matters most for the time you have left.
          </Text>

          <TextInput
            value={value}
            onChangeText={setValue}
            keyboardType="number-pad"
            placeholder="e.g. 3"
            placeholderTextColor={theme.color.textMuted}
            style={styles.input}
          />

          <View style={styles.unitRow}>
            {(['days', 'hours'] as Unit[]).map((u) => (
              <Pressable
                key={u}
                onPress={() => setUnit(u)}
                style={[styles.unitButton, unit === u && styles.unitButtonActive]}
              >
                <Text style={[styles.unitLabel, unit === u && styles.unitLabelActive]}>
                  {u === 'days' ? 'Days' : 'Hours'}
                </Text>
              </Pressable>
            ))}
          </View>

          {error && <Text style={styles.error}>{error}</Text>}

          <View style={styles.actions}>
            <Pressable onPress={onClose} style={styles.secondaryButton} disabled={submitting}>
              <Text style={styles.secondaryLabel}>Cancel</Text>
            </Pressable>
            <Pressable onPress={handleSubmit} style={styles.primaryButton} disabled={submitting}>
              <Text style={styles.primaryLabel}>{submitting ? 'Starting…' : 'Start Panic Mode'}</Text>
            </Pressable>
          </View>
        </View>
      </View>
    </Modal>
  );
}

const styles = StyleSheet.create({
  backdrop: {
    flex: 1,
    backgroundColor: 'rgba(6, 8, 16, 0.72)',
    justifyContent: 'center',
    padding: theme.spacing(6),
  },
  card: {
    backgroundColor: theme.color.surface,
    borderRadius: theme.radius.lg,
    padding: theme.spacing(6),
    borderWidth: 1,
    borderColor: theme.color.border,
  },
  title: { ...theme.font.heading, color: theme.color.textPrimary, marginBottom: theme.spacing(1) },
  subtitle: { ...theme.font.body, color: theme.color.textMuted, marginBottom: theme.spacing(4) },
  input: {
    borderWidth: 1,
    borderColor: theme.color.border,
    borderRadius: theme.radius.md,
    paddingHorizontal: theme.spacing(3),
    paddingVertical: theme.spacing(3),
    color: theme.color.textPrimary,
    fontSize: 18,
    marginBottom: theme.spacing(3),
  },
  unitRow: { flexDirection: 'row', marginBottom: theme.spacing(3) },
  unitButton: {
    flex: 1,
    paddingVertical: theme.spacing(2),
    borderRadius: theme.radius.md,
    borderWidth: 1,
    borderColor: theme.color.border,
    alignItems: 'center',
    marginRight: theme.spacing(2),
  },
  unitButtonActive: {
    backgroundColor: theme.color.accentMuted,
    borderColor: theme.color.accent,
  },
  unitLabel: { color: theme.color.textMuted, fontWeight: '600' },
  unitLabelActive: { color: theme.color.accent },
  error: { color: theme.color.panic, marginBottom: theme.spacing(2) },
  actions: { flexDirection: 'row', justifyContent: 'flex-end', marginTop: theme.spacing(2) },
  secondaryButton: { paddingVertical: theme.spacing(3), paddingHorizontal: theme.spacing(4) },
  secondaryLabel: { color: theme.color.textMuted, fontWeight: '600' },
  primaryButton: {
    backgroundColor: theme.color.accent,
    paddingVertical: theme.spacing(3),
    paddingHorizontal: theme.spacing(5),
    borderRadius: theme.radius.md,
  },
  primaryLabel: { color: theme.color.background, fontWeight: '700' },
});
