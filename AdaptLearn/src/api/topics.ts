import { apiClient } from './client';
import { CardType, SwipeCard, Topic, TopicContent } from '../types';

export async function fetchTopics(subjectId: string): Promise<Topic[]> {
  const { data } = await apiClient.get<Topic[]>(`/subjects/${subjectId}/topics`);
  return data;
}

export async function fetchSwipeCards(topicId: string): Promise<SwipeCard[]> {
  const { data } = await apiClient.get<SwipeCard[]>(`/topics/${topicId}/cards`);
  return data;
}

export async function postSwipeEvent(
  topicId: string,
  cardId: string,
  cardType: CardType,
  direction: 'left' | 'right'
): Promise<void> {
  await apiClient.post('/swipe-event', { topicId, cardId, cardType, direction });
}

export async function fetchTopicContent(topicId: string, mode: CardType): Promise<TopicContent> {
  const { data } = await apiClient.get<TopicContent>(`/topics/${topicId}/content`, {
    params: { mode },
  });
  return data;
}
