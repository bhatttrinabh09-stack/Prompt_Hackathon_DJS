import React, { useEffect, useState } from 'react';
import { View, Text, FlatList, StyleSheet, TouchableOpacity } from 'react-native';
import { NativeStackScreenProps } from '@react-navigation/native-stack';
import { RootStackParamList } from '../navigation/types';
import { ScreenContainer } from '../components/ScreenContainer';
import { catalogApi } from '../api/client';
import { theme } from '../theme/theme';
import { Topic } from '../types';

type Props = NativeStackScreenProps<RootStackParamList, 'TopicList'>;

export const TopicListScreen: React.FC<Props> = ({ navigation, route }) => {
  const { subjectId } = route.params;
  const [topics, setTopics] = useState<Topic[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchTopics = async () => {
      try {
        const data = await catalogApi.getTopics(subjectId);
        setTopics(data);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    };
    fetchTopics();
  }, [subjectId]);

  return (
    <ScreenContainer loading={loading}>
      <View style={styles.header}>
        <TouchableOpacity
          style={styles.swipeButton}
          onPress={() => navigation.navigate('Swipe', { subjectId })}
        >
          <Text style={styles.swipeButtonText}>Start Swiping (Learn Mode)</Text>
        </TouchableOpacity>
      </View>
      <FlatList
        data={topics}
        contentContainerStyle={styles.list}
        keyExtractor={(item) => item.id.toString()}
        renderItem={({ item }) => (
          <TouchableOpacity 
            style={styles.topicCard}
            onPress={() => navigation.navigate('Content', { topicId: item.id })}
          >
            <View style={styles.topicHeader}>
              <Text style={styles.topicTitle}>{item.title}</Text>
              {item.is_must_ask && (
                <View style={styles.badge}>
                  <Text style={styles.badgeText}>Must Ask</Text>
                </View>
              )}
            </View>
            <Text style={styles.topicDesc} numberOfLines={2}>{item.description}</Text>
          </TouchableOpacity>
        )}
      />
    </ScreenContainer>
  );
};

const styles = StyleSheet.create({
  header: {
    padding: theme.spacing.md,
  },
  swipeButton: {
    backgroundColor: theme.colors.primary,
    padding: theme.spacing.lg,
    borderRadius: theme.borderRadius.full,
    alignItems: 'center',
  },
  swipeButtonText: {
    color: theme.colors.text,
    fontSize: theme.typography.h3.fontSize,
    fontWeight: 'bold',
  },
  list: {
    padding: theme.spacing.md,
  },
  topicCard: {
    backgroundColor: theme.colors.surface,
    padding: theme.spacing.lg,
    borderRadius: theme.borderRadius.md,
    marginBottom: theme.spacing.md,
  },
  topicHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: theme.spacing.sm,
  },
  topicTitle: {
    color: theme.colors.text,
    fontSize: theme.typography.body1.fontSize,
    fontWeight: 'bold',
    flex: 1,
  },
  badge: {
    backgroundColor: theme.colors.urgency.high,
    paddingHorizontal: theme.spacing.sm,
    paddingVertical: 2,
    borderRadius: theme.borderRadius.sm,
    marginLeft: theme.spacing.sm,
  },
  badgeText: {
    color: theme.colors.text,
    fontSize: theme.typography.caption.fontSize,
    fontWeight: 'bold',
  },
  topicDesc: {
    color: theme.colors.textSecondary,
    fontSize: theme.typography.body2.fontSize,
  },
});
