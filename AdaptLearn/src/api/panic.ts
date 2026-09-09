import { apiClient } from './client';
import { PanicSession } from '../types';

export async function startPanicSession(
  value: number,
  unit: 'days' | 'hours'
): Promise<PanicSession> {
  const { data } = await apiClient.post<PanicSession>('/panic-session', {
    examIn: value,
    unit,
  });
  return data;
}

export async function endPanicSession(sessionId: string): Promise<void> {
  await apiClient.delete(`/panic-session/${sessionId}`);
}
