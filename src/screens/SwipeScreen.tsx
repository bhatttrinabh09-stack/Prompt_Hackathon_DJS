import React, { useEffect, useState, useRef } from 'react';
import { View, Text, StyleSheet, Dimensions, Animated } from 'react-native';
import { NativeStackScreenProps } from '@react-navigation/native-stack';
import { RootStackParamList } from '../navigation/types';
import Swiper from 'react-native-deck-swiper';
import { catalogApi, swipeApi } from '../api/client';
import { theme } from '../theme/theme';
import { Topic } from '../types';

type Props = NativeStackScreenProps<RootStackParamList, 'Swipe'>;
const { width, height } = Dimensions.get('window');

export const SwipeScreen: React.FC<Props> = ({ navigation, route }) => {
  const { subjectId } = route.params;
  const [topics, setTopics] = useState<Topic[]>([]);
  const [loading, setLoading] = useState(true);
  const swiperRef = useRef<Swiper<Topic>>(null);
  
  // Timer for auto-advance (e.g., 5 seconds)
  const [progress, setProgress] = useState(new Animated.Value(0));
  const swipeStartTime = useRef(Date.now());

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

  useEffect(() => {
    if (!loading && topics.length > 0) {
      startTimer();
    }
  }, [loading, topics]);

  const startTimer = () => {
    progress.setValue(0);
    swipeStartTime.current = Date.now();
    Animated.timing(progress, {
      toValue: 1,
      duration: 5000,
      useNativeDriver: false,
    }).start(({ finished }) => {
      if (finished) {
        // Auto-swipe right (or next) on timeout
        swiperRef.current?.swipeLeft();
      }
    });
  };

  const handleSwipe = async (cardIndex: number, direction: 'right' | 'left') => {
    progress.stopAnimation();
    const topic = topics[cardIndex];
    if (!topic) return;

    const timeSpent = (Date.now() - swipeStartTime.current) / 1000;
    try {
      await swipeApi.recordSwipe(topic.id, direction, timeSpent);
    } catch (e) {
      console.error(e);
    }

    if (direction === 'right') {
      // User matched/liked -> Go deeper
      navigation.navigate('Content', { topicId: topic.id });
    } else {
      // User swiped left -> Next card
      startTimer();
    }
  };

  const renderCard = (card: Topic) => {
    return (
      <View style={styles.card}>
        <Text style={styles.cardTitle}>{card.title}</Text>
        <Text style={styles.cardDesc}>{card.description}</Text>
        {card.is_must_ask && (
          <View style={styles.badge}>
            <Text style={styles.badgeText}>Must Ask</Text>
          </View>
        )}
      </View>
    );
  };

  if (loading) return null; // In real app, show spinner

  return (
    <View style={styles.container}>
      {/* Progress Bar */}
      <View style={styles.progressBarContainer}>
        <Animated.View 
          style={[
            styles.progressBar, 
            { 
              width: progress.interpolate({
                inputRange: [0, 1],
                outputRange: ['0%', '100%'],
              }) 
            }
          ]} 
        />
      </View>

      <Swiper
        ref={swiperRef}
        cards={topics}
        renderCard={renderCard}
        onSwipedLeft={(index) => handleSwipe(index, 'left')}
        onSwipedRight={(index) => handleSwipe(index, 'right')}
        backgroundColor={theme.colors.background}
        stackSize={3}
        cardIndex={0}
        disableTopSwipe
        disableBottomSwipe
        overlayLabels={{
          left: { title: 'SKIP', style: { label: { color: theme.colors.error, borderColor: theme.colors.error } } },
          right: { title: 'LEARN', style: { label: { color: theme.colors.success, borderColor: theme.colors.success } } },
        }}
        onSwipedAll={() => navigation.goBack()}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  progressBarContainer: {
    height: 4,
    backgroundColor: theme.colors.surface,
    width: '100%',
  },
  progressBar: {
    height: '100%',
    backgroundColor: theme.colors.primary,
  },
  card: {
    flex: 0.7,
    borderRadius: theme.borderRadius.lg,
    borderWidth: 2,
    borderColor: theme.colors.primary,
    justifyContent: 'center',
    backgroundColor: theme.colors.surface,
    padding: theme.spacing.xl,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.2,
    shadowRadius: 4,
    elevation: 5,
  },
  cardTitle: {
    fontSize: theme.typography.h1.fontSize,
    fontWeight: 'bold',
    color: theme.colors.text,
    marginBottom: theme.spacing.lg,
    textAlign: 'center',
  },
  cardDesc: {
    fontSize: theme.typography.h3.fontSize,
    color: theme.colors.textSecondary,
    textAlign: 'center',
    marginBottom: theme.spacing.xl,
  },
  badge: {
    backgroundColor: theme.colors.urgency.high,
    padding: theme.spacing.sm,
    borderRadius: theme.borderRadius.sm,
    alignSelf: 'center',
    marginTop: theme.spacing.lg,
  },
  badgeText: {
    color: theme.colors.text,
    fontWeight: 'bold',
  },
});
