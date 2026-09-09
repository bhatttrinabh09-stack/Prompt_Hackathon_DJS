import React from 'react';
import { SafeAreaView, StyleSheet, View } from 'react-native';
import { theme } from '../theme/theme';
import PanicToggle from './PanicToggle';

interface Props {
  children: React.ReactNode;
  // Every screen shows the Panic Toggle by default. Only the content
  // player (ContentScreen) opts out, per spec: visible up until — not
  // during — the actual learning/content-consumption flow.
  showPanicToggle?: boolean;
}

export default function ScreenContainer({ children, showPanicToggle = true }: Props) {
  return (
    <SafeAreaView style={styles.safe}>
      {showPanicToggle && <PanicToggle />}
      <View style={styles.content}>{children}</View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: theme.color.background },
  content: { flex: 1 },
});
