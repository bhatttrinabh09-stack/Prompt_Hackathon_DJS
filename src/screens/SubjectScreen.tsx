import React, { useEffect, useState } from 'react';
import { FlatList, StyleSheet } from 'react-native';
import { NativeStackScreenProps } from '@react-navigation/native-stack';
import { RootStackParamList } from '../navigation/types';
import { ScreenContainer } from '../components/ScreenContainer';
import { GridTile } from '../components/GridTile';
import { catalogApi } from '../api/client';
import { theme } from '../theme/theme';

type Props = NativeStackScreenProps<RootStackParamList, 'Subject'>;

export const SubjectScreen: React.FC<Props> = ({ navigation, route }) => {
  const [subjects, setSubjects] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchSubjects = async () => {
      try {
        const data = await catalogApi.getSubjects();
        setSubjects(data);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    };
    fetchSubjects();
  }, []);

  return (
    <ScreenContainer loading={loading}>
      <FlatList
        data={subjects}
        numColumns={1}
        contentContainerStyle={styles.list}
        keyExtractor={(item) => item.id.toString()}
        renderItem={({ item }) => (
          <GridTile
            title={item.name}
            onPress={() => navigation.navigate('TopicList', { subjectId: item.id })}
          />
        )}
      />
    </ScreenContainer>
  );
};

const styles = StyleSheet.create({
  list: {
    padding: theme.spacing.sm,
  },
});
