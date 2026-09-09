import { apiClient } from './client';

export async function markTopicComplete(topicId: string, mode: string): Promise<void> {
  await apiClient.post('/progress/complete', { topicId, mode });
}
