import { apiClient } from './client';
import { Subject, SubjectProgress } from '../types';

export async function fetchSubjects(branch: string, semester: number): Promise<Subject[]> {
  const { data } = await apiClient.get<Subject[]>('/subjects', {
    params: { branch, semester },
  });
  return data;
}

export async function fetchSubjectProgress(subjectId: string): Promise<SubjectProgress> {
  const { data } = await apiClient.get<SubjectProgress>('/progress', {
    params: { subjectId },
  });
  return data;
}
