export type Branch = 'AIML';

export interface User {
  id: string;
  name: string;
  email: string;
  branch?: Branch;
}

export interface AuthResponse {
  token: string;
  user: User;
}

export type UrgencyLevel = 'low' | 'medium' | 'high';

export interface PanicSession {
  id: string;
  examInValue: number;
  examInUnit: 'days' | 'hours';
  urgencyLevel: UrgencyLevel;
  deadline: string; // ISO timestamp — used to drive the countdown display
}

export interface Subject {
  id: string;
  name: string;
  branch: Branch;
  semester: number;
  enabled: boolean;
}

export interface TopicProgress {
  topicId: string;
  percentComplete: number;
}

export interface SubjectProgress {
  subjectId: string;
  overallPercentComplete: number;
  topics: TopicProgress[];
}

export interface Topic {
  id: string;
  subjectId: string;
  title: string;
  order: number;
}

export type CardType = 'dense' | 'fast' | 'short_video';

export interface SwipeCard {
  id: string;
  type: CardType;
  title: string;
  preview: string; // dense/fast: text preview. short_video: short caption
  thumbnailUrl?: string; // short_video: muted looping preview clip
}

export interface DenseContent {
  mode: 'dense';
  prerequisites: string[];
  textbooks: { title: string; author: string }[];
  notes: string;
  videoUrl: string; // long-form YouTube URL or video id
}

export interface FastContent {
  mode: 'fast';
  bullets: string[];
  videoUrl: string; // shorter YouTube URL or video id
  mustAskTopics: string[];
}

export interface ShortVideoContent {
  mode: 'short_video';
  videos: { id: string; url: string; caption: string }[];
}

export type TopicContent = DenseContent | FastContent | ShortVideoContent;
