import React, { useCallback, useEffect, useState } from 'react';
import { NativeStackScreenProps } from '@react-navigation/native-stack';
import { ScrollView, StyleSheet } from 'react-native';
import ScreenContainer from '../components/ScreenContainer';
import GridTile from '../components/GridTile';
import LoadingView from '../components/LoadingView';
import ErrorView from '../components/ErrorView';
import { theme } from '../theme/theme';
import { RootStackParamList } from '../navigation/types';
import { fetchSubjects } from '../api/subjects';
import { useAppStore } from '../store/useStore';
import { Subject } from '../types';

type Props = NativeStackScreenProps<RootStackParamList, 'Subject'>;

export default function SubjectScreen({ route, navigation }: Props) {
  const { semester } = route.params;
  const branch = useAppStore((s) => s.user?.branch);
  const [subjects, setSubjects] = useState<Subject[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    if (!branch) return;
    setLoading(true);
    setError(null);
    try {
      const data = await fetchSubjects(branch, semester);
      setSubjects(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Could not load subjects.');
    } finally {
      setLoading(false);
    }
  }, [branch, semester]);

  useEffect(() => {
    load();
  }, [load]);

  if (loading) {
    return (
      <ScreenContainer>
        <LoadingView label="Loading subjects…" />
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
      <ScrollView contentContainerStyle={styles.grid}>
        {(subjects ?? []).map((subject) => (
          <GridTile
            key={subject.id}
            label={subject.name}
            enabled={subject.enabled}
            onPress={() =>
              navigation.navigate('TopicList', { subjectId: subject.id, subjectName: subject.name })
            }
          />
        ))}
      </ScrollView>
    </ScreenContainer>
  );
}

const styles = StyleSheet.create({
  grid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
    padding: theme.spacing(6),
  },
});
