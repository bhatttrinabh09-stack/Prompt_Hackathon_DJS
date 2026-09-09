import React from 'react';
import { NativeStackScreenProps } from '@react-navigation/native-stack';
import { ScrollView, StyleSheet } from 'react-native';
import ScreenContainer from '../components/ScreenContainer';
import GridTile from '../components/GridTile';
import { theme } from '../theme/theme';
import { RootStackParamList } from '../navigation/types';

type Props = NativeStackScreenProps<RootStackParamList, 'Semester'>;

const PROTOTYPE_ENABLED_SEMESTER = 3;

export default function SemesterScreen({ navigation }: Props) {
  return (
    <ScreenContainer>
      <ScrollView contentContainerStyle={styles.grid}>
        {Array.from({ length: 8 }, (_, i) => i + 1).map((sem) => (
          <GridTile
            key={sem}
            label={`Semester ${sem}`}
            enabled={sem === PROTOTYPE_ENABLED_SEMESTER}
            onPress={() => navigation.navigate('Subject', { semester: sem })}
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
