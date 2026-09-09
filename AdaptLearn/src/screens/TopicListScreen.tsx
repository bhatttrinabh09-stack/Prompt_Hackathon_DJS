import React, { useCallback, useEffect, useState } from 'react';
import { NativeStackScreenProps } from '@react-navigation/native-stack';
import { FlatList, Pressable, StyleSheet, Text, View } from 'react-native';
import ScreenContainer from '../components/ScreenContainer';
import ProgressBar from '../components/ProgressBar';
import LoadingView from '../components/LoadingView';
import ErrorView from '../components/ErrorView';
import { theme } from '../theme/theme';
import { RootStackParamList } from '../navigation/types';
import { fetchTopics } from '../api/topics';
import { fetchSubjectProgress } from '../api/subjects';
import { useAppStore } from '../store/useStore';
import { Topic } from '../types';

type Props = NativeStackScreenProps<RootStackParamList, 'TopicList'>;

export default function TopicListScreen({ route, navigation }: Props) {
  const { subjectId, subjectName } = route.params;
  const setSubjectProgress = useAppStore((s) => s.setSubjectProgress);
  const progress = useAppStore((s) => s.currentSubjectProgress);
  const [topics, setTopics] = useState<Topic[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [topicData, progressData] = await Promise.all([
        fetchTopics(subjectId),
        fetchSubjectProgress(subjectId),
      ]);
      setTopics(topicData);
      setSubjectProgress(progressData);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Could not load topics.');
    } finally {
      setLoading(false);
    }
  }, [subjectId, setSubjectProgress]);

  useEffect(() => {
    load();
  }, [load]);

  if (loading) {
    return (
      <ScreenContainer>
        <LoadingView label="Loading topics…" />
      </ScreenContainer>
    );
  }
  if (error) {
    return (
      <ScreenContainer>
        <ErrorView message={error} onRetry={load} />
      </ScreenContainer>
    );
  }

  return (
    <ScreenContainer>
      <View style={styles.header}>
        <Text style={styles.subjectName}>{subjectName}</Text>
        <ProgressBar percent={progress?.overallPercentComplete ?? 0} label="Overall progress" />
      </View>

      <FlatList
        data={topics ?? []}
        keyExtractor={(item) => item.id}
        contentContainerStyle={styles.list}
        renderItem={({ item }) => {
          const topicPercent =
            progress?.topics.find((t) => t.topicId === item.id)?.percentComplete ?? 0;
          return (
            <Pressable
              style={styles.topicRow}
              onPress={() => navigation.navigate('Swipe', { topicId: item.id, topicTitle: item.title })}
            >
              <Text style={styles.topicTitle}>{item.title}</Text>
              <ProgressBar percent={topicPercent} compact />
            </Pressable>
          );
        }}
      />
    </ScreenContainer>
  );
}

const styles = StyleSheet.create({
  header: { padding: theme.spacing(6), paddingBottom: theme.spacing(2) },
  subjectName: { ...theme.font.heading, color: theme.color.textPrimary, marginBottom: theme.spacing(3) },
  list: { paddingHorizontal: theme.spacing(6), paddingBottom: theme.spacing(6) },
  topicRow: {
    backgroundColor: theme.color.surface,
    borderRadius: theme.radius.md,
    borderWidth: 1,
    borderColor: theme.color.border,
    padding: theme.spacing(4),
    marginBottom: theme.spacing(3),
  },
  topicTitle: { ...theme.font.subheading, color: theme.color.textPrimary, marginBottom: theme.spacing(2) },
});
