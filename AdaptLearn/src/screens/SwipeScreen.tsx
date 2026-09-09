import React, { useCallback, useEffect, useRef, useState } from 'react';
import { NativeStackScreenProps } from '@react-navigation/native-stack';
import { StyleSheet, Text, View } from 'react-native';
import Swiper from 'react-native-deck-swiper';
import ScreenContainer from '../components/ScreenContainer';
import LoadingView from '../components/LoadingView';
import ErrorView from '../components/ErrorView';
import CountdownRing from '../components/CountdownRing';
import DenseTextCard from '../components/cards/DenseTextCard';
import FastPacedCard from '../components/cards/FastPacedCard';
import ShortVideoCard from '../components/cards/ShortVideoCard';
import { theme } from '../theme/theme';
import { RootStackParamList } from '../navigation/types';
import { fetchSwipeCards, postSwipeEvent } from '../api/topics';
import { SwipeCard } from '../types';

type Props = NativeStackScreenProps<RootStackParamList, 'Swipe'>;

const AUTO_ADVANCE_MS = 5000;

export default function SwipeScreen({ route, navigation }: Props) {
  const { topicId, topicTitle } = route.params;
  const [cards, setCards] = useState<SwipeCard[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [cardIndex, setCardIndex] = useState(0);
  // Bumping deckKey remounts <Swiper>, which is how we "restart the deck"
  // after all three cards have been rejected.
  const [deckKey, setDeckKey] = useState(0);
  // react-native-deck-swiper ships no official TS types (see the ambient
  // declaration in src/types), so the ref is intentionally untyped here.
  const swiperRef = useRef<any>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchSwipeCards(topicId);
      setCards(data);
      setCardIndex(0);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Could not load study previews.');
    } finally {
      setLoading(false);
    }
  }, [topicId]);

  useEffect(() => {
    load();
  }, [load]);

  async function handleSwipeRight(card: SwipeCard) {
    postSwipeEvent(topicId, card.id, card.type, 'right').catch(() => {
      // Non-fatal for the prototype — don't block navigation on telemetry.
    });
    navigation.navigate('Content', { topicId, topicTitle, mode: card.type });
  }

  function handleAllSwipedLeft() {
    // Every mode was rejected — restart the deck instead of dead-ending
    // the flow, so the student can reconsider.
    setDeckKey((k) => k + 1);
    setCardIndex(0);
  }

  function renderCard(card: SwipeCard) {
    if (!card) return null;
    switch (card.type) {
      case 'dense':
        return <DenseTextCard card={card} />;
      case 'fast':
        return <FastPacedCard card={card} />;
      case 'short_video':
        return <ShortVideoCard card={card} />;
      default:
        return null;
    }
  }

  if (loading) {
    return (
      <ScreenContainer>
        <LoadingView label="Preparing your study modes…" />
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
  if (!cards || cards.length === 0) {
    return (
      <ScreenContainer>
        <ErrorView message="No study previews available for this topic yet." onRetry={load} />
      </ScreenContainer>
    );
  }

  const activeCard = cards[cardIndex];

  return (
    <ScreenContainer>
      <View style={styles.header}>
        <Text style={styles.title}>{topicTitle}</Text>
        <Text style={styles.subtitle}>Swipe right on how you want to study this topic</Text>
      </View>

      <View style={styles.deckArea}>
        {activeCard && (
          <CountdownRing
            key={`${deckKey}-${activeCard.id}`}
            durationMs={AUTO_ADVANCE_MS}
            active
            onComplete={() => swiperRef.current?.swipeLeft()}
          />
        )}

        <Swiper
          key={deckKey}
          ref={swiperRef}
          cards={cards}
          renderCard={renderCard}
          cardIndex={cardIndex}
          onSwipedLeft={(i: number) => setCardIndex((prev) => Math.min(prev + 1, cards.length - 1))}
          onSwipedRight={(i: number) => handleSwipeRight(cards[i])}
          onSwipedAll={handleAllSwipedLeft}
          backgroundColor="transparent"
          stackSize={3}
          verticalSwipe={false}
          disableBottomSwipe
          disableTopSwipe
        />
      </View>
    </ScreenContainer>
  );
}

const styles = StyleSheet.create({
  header: { paddingHorizontal: theme.spacing(6), paddingTop: theme.spacing(2) },
  title: { ...theme.font.heading, color: theme.color.textPrimary },
  subtitle: {
    ...theme.font.body,
    color: theme.color.textMuted,
    marginTop: theme.spacing(1),
    marginBottom: theme.spacing(4),
  },
  deckArea: { flex: 1, paddingBottom: theme.spacing(8) },
});
