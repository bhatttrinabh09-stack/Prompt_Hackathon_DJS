import React from 'react';
import { FlatList, StyleSheet } from 'react-native';
import { NativeStackScreenProps } from '@react-navigation/native-stack';
import { RootStackParamList } from '../navigation/types';
import { ScreenContainer } from '../components/ScreenContainer';
import { GridTile } from '../components/GridTile';
import { theme } from '../theme/theme';

type Props = NativeStackScreenProps<RootStackParamList, 'Home'>;

export const HomeScreen: React.FC<Props> = ({ navigation }) => {
  const semesters = [
    { id: 1, title: 'Semester 1', isLocked: true },
    { id: 2, title: 'Semester 2', isLocked: true },
    { id: 3, title: 'Semester 3', isLocked: false },
    { id: 4, title: 'Semester 4', isLocked: true },
    { id: 5, title: 'Semester 5', isLocked: true },
    { id: 6, title: 'Semester 6', isLocked: true },
    { id: 7, title: 'Semester 7', isLocked: true },
    { id: 8, title: 'Semester 8', isLocked: true },
  ];

  return (
    <ScreenContainer>
      <FlatList
        data={semesters}
        numColumns={2}
        contentContainerStyle={styles.list}
        keyExtractor={(item) => item.id.toString()}
        renderItem={({ item }) => (
          <GridTile
            title={item.title}
            isLocked={item.isLocked}
            onPress={() => navigation.navigate('Subject', { semesterId: item.id })}
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
