import React from 'react';
import { NativeStackScreenProps } from '@react-navigation/native-stack';
import { Pressable, StyleSheet, Text, View } from 'react-native';
import ScreenContainer from '../components/ScreenContainer';
import { theme } from '../theme/theme';
import { useAppStore } from '../store/useStore';
import { RootStackParamList } from '../navigation/types';

type Props = NativeStackScreenProps<RootStackParamList, 'Home'>;

export default function HomeScreen({ navigation }: Props) {
  const user = useAppStore((s) => s.user);

  return (
    <ScreenContainer>
      <View style={styles.body}>
        <Text style={styles.greeting}>Hi{user?.name ? `, ${user.name.split(' ')[0]}` : ''}</Text>
        <Text style={styles.subtitle}>Ready to keep going with {user?.branch ?? 'your branch'}?</Text>

        <Pressable style={styles.ctaCard} onPress={() => navigation.navigate('Semester')}>
          <Text style={styles.ctaTitle}>Continue learning</Text>
          <Text style={styles.ctaMeta}>Pick a semester to jump back in</Text>
        </Pressable>
      </View>
    </ScreenContainer>
  );
}

const styles = StyleSheet.create({
  body: { flex: 1, padding: theme.spacing(6) },
  greeting: { ...theme.font.heading, fontSize: 26, color: theme.color.textPrimary },
  subtitle: {
    ...theme.font.body,
    color: theme.color.textMuted,
    marginTop: theme.spacing(1),
    marginBottom: theme.spacing(8),
  },
  ctaCard: {
    backgroundColor: theme.color.surface,
    borderRadius: theme.radius.lg,
    borderWidth: 1,
    borderColor: theme.color.border,
    padding: theme.spacing(5),
  },
  ctaTitle: { ...theme.font.subheading, color: theme.color.textPrimary, marginBottom: theme.spacing(1) },
  ctaMeta: { ...theme.font.caption, color: theme.color.textMuted },
});
