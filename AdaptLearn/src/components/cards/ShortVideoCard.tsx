import React from 'react';
import { StyleSheet, Text, View } from 'react-native';
import { ResizeMode, Video } from 'expo-av';
import { theme } from '../../theme/theme';
import { SwipeCard } from '../../types';

export default function ShortVideoCard({ card }: { card: SwipeCard }) {
  return (
    <View style={styles.card}>
      <Text style={styles.tag}>Micro-Learn</Text>
      {card.thumbnailUrl ? (
        <Video
          source={{ uri: card.thumbnailUrl }}
          style={styles.player}
          resizeMode={ResizeMode.COVER}
          isMuted
          isLooping
          shouldPlay
        />
      ) : (
        <View style={styles.placeholder} />
      )}
      <Text style={styles.title}>{card.title}</Text>
      <Text style={styles.hint}>AI-generated short-form video</Text>
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
    justifyContent: 'flex-end',
    overflow: 'hidden',
  },
  player: { ...StyleSheet.absoluteFillObject, borderRadius: theme.radius.lg },
  placeholder: { ...StyleSheet.absoluteFillObject, backgroundColor: theme.color.surfaceRaised },
  tag: { ...theme.font.caption, color: theme.color.panic, marginBottom: theme.spacing(2) },
  title: { ...theme.font.heading, color: '#FFFFFF', marginBottom: theme.spacing(1) },
  hint: { ...theme.font.caption, color: 'rgba(255,255,255,0.8)' },
});
