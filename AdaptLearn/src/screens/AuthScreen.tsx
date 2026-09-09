import React, { useState } from 'react';
import { KeyboardAvoidingView, Platform, Pressable, StyleSheet, Text, TextInput, View } from 'react-native';
import { theme } from '../theme/theme';
import { useAppStore } from '../store/useStore';
import { login, signup } from '../api/auth';

type Mode = 'login' | 'signup';

export default function AuthScreen() {
  const setSession = useAppStore((s) => s.setSession);
  const [mode, setMode] = useState<Mode>('login');
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit() {
    if (!email || !password || (mode === 'signup' && !name)) {
      setError('Please fill in all fields.');
      return;
    }
    setSubmitting(true);
    setError(null);
    try {
      const result =
        mode === 'login' ? await login(email, password) : await signup(name, email, password);
      await setSession(result.token, result.user);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Authentication failed.');
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <KeyboardAvoidingView style={styles.wrapper} behavior={Platform.OS === 'ios' ? 'padding' : undefined}>
      <Text style={styles.brand}>AdaptLearn</Text>
      <Text style={styles.tagline}>Study at the pace your exam actually gives you.</Text>

      <View>
        {mode === 'signup' && (
          <TextInput
            value={name}
            onChangeText={setName}
            placeholder="Full name"
            placeholderTextColor={theme.color.textMuted}
            style={styles.input}
          />
        )}
        <TextInput
          value={email}
          onChangeText={setEmail}
          placeholder="Email"
          placeholderTextColor={theme.color.textMuted}
          autoCapitalize="none"
          keyboardType="email-address"
          style={styles.input}
        />
        <TextInput
          value={password}
          onChangeText={setPassword}
          placeholder="Password"
          placeholderTextColor={theme.color.textMuted}
          secureTextEntry
          style={styles.input}
        />

        {error && <Text style={styles.error}>{error}</Text>}

        <Pressable style={styles.primaryButton} onPress={handleSubmit} disabled={submitting}>
          <Text style={styles.primaryLabel}>
            {submitting ? 'Please wait…' : mode === 'login' ? 'Log In' : 'Sign Up'}
          </Text>
        </Pressable>

        <Pressable onPress={() => setMode(mode === 'login' ? 'signup' : 'login')}>
          <Text style={styles.switchMode}>
            {mode === 'login' ? 'New here? Create an account' : 'Already have an account? Log in'}
          </Text>
        </Pressable>
      </View>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  wrapper: { flex: 1, backgroundColor: theme.color.background, justifyContent: 'center', padding: theme.spacing(6) },
  brand: { ...theme.font.heading, fontSize: 30, color: theme.color.accent, marginBottom: theme.spacing(1) },
  tagline: { ...theme.font.body, color: theme.color.textMuted, marginBottom: theme.spacing(8) },
  input: {
    borderWidth: 1,
    borderColor: theme.color.border,
    borderRadius: theme.radius.md,
    paddingHorizontal: theme.spacing(3),
    paddingVertical: theme.spacing(3),
    color: theme.color.textPrimary,
    marginBottom: theme.spacing(3),
  },
  error: { color: theme.color.panic, marginBottom: theme.spacing(2) },
  primaryButton: {
    backgroundColor: theme.color.accent,
    borderRadius: theme.radius.md,
    paddingVertical: theme.spacing(3),
    alignItems: 'center',
    marginBottom: theme.spacing(3),
  },
  primaryLabel: { color: theme.color.background, fontWeight: '700', fontSize: 16 },
  switchMode: { color: theme.color.textMuted, textAlign: 'center' },
});
