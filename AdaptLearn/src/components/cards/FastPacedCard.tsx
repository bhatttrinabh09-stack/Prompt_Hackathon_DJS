import React from 'react';
import { StyleSheet, Text, View } from 'react-native';
import { theme } from '../../theme/theme';
import { SwipeCard } from '../../types';

export default function FastPacedCard({ card }: { card: SwipeCard }) {
  const bullets = card.preview.split('\n').filter(Boolean).slice(0, 5);
  return (
    <View style={styles.card}>
      <Text style={styles.tag}>Fast Track</Text>
      <Text style={styles.title}>{card.title}</Text>
      <View>
        {bullets.map((b, i) => (
          <Text key={i} style={styles.bullet}>
            {'\u2022'} {b}
          </Text>
        ))}
      </View>
      <Text style={styles.hint}>Condensed notes · Short videos · Must-ask topics</Text>
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
  tag: { ...theme.font.caption, color: theme.color.violet, marginBottom: theme.spacing(2) },
  title: { ...theme.font.heading, color: theme.color.textPrimary, marginBottom: theme.spacing(3) },
  bullet: { ...theme.font.body, color: theme.color.textPrimary, marginBottom: theme.spacing(2) },
  hint: { ...theme.font.caption, color: theme.color.textMuted, marginTop: theme.spacing(4) },
});
