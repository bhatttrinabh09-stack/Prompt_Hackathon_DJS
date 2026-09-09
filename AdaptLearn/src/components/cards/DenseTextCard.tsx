import React from 'react';
import { StyleSheet, Text, View } from 'react-native';
import { theme } from '../../theme/theme';
import { SwipeCard } from '../../types';

export default function DenseTextCard({ card }: { card: SwipeCard }) {
  return (
    <View style={styles.card}>
      <Text style={styles.tag}>Deep Focus</Text>
      <Text style={styles.title}>{card.title}</Text>
      <Text style={styles.preview} numberOfLines={8}>
        {card.preview}
      </Text>
      <Text style={styles.hint}>Prerequisites · Textbooks · Full notes · Long lecture</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    flex: 1,
    borderRadius: theme.radius.lg,
    padding: theme.spacing(6),
    borderWidth: 1,
    borderColor: theme.color.border,
    backgroundColor: theme.color.surface,
    justifyContent: 'space-between',
  },
  tag: { ...theme.font.caption, color: theme.color.accent, marginBottom: theme.spacing(2) },
  title: { ...theme.font.heading, color: theme.color.textPrimary, marginBottom: theme.spacing(3) },
  preview: { ...theme.font.body, color: theme.color.textMuted, lineHeight: 22 },
  hint: { ...theme.font.caption, color: theme.color.textMuted, marginTop: theme.spacing(4) },
});
