import React from 'react';
import { View, FlatList, StyleSheet } from 'react-native';
import { NativeStackScreenProps } from '@react-navigation/native-stack';
import { RootStackParamList } from '../navigation/types';
import { ScreenContainer } from '../components/ScreenContainer';
import { GridTile } from '../components/GridTile';
import { theme } from '../theme/theme';

type Props = NativeStackScreenProps<RootStackParamList, 'BranchSelect'>;

export const BranchSelectScreen: React.FC<Props> = ({ navigation }) => {
  const branches = [
    { id: '1', title: 'AIML', isLocked: false },
    { id: '2', title: 'Computer Science', isLocked: true },
    { id: '3', title: 'Information Tech', isLocked: true },
    { id: '4', title: 'Data Science', isLocked: true },
  ];

  return (
    <ScreenContainer>
      <FlatList
        data={branches}
        numColumns={2}
        contentContainerStyle={styles.list}
        keyExtractor={(item) => item.id}
        renderItem={({ item }) => (
          <GridTile
            title={item.title}
            isLocked={item.isLocked}
            onPress={() => navigation.navigate('Home')}
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
