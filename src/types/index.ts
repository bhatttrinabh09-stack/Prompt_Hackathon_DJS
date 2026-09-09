export type UrgencyTier = 'high' | 'medium' | 'low';

export interface User {
  id: number;
  email: string;
  name?: string;
}

export interface PanicSession {
  id: number;
  exam_date: string;
  target_hours: number;
  urgency_tier: UrgencyTier;
  is_active: boolean;
}

export interface Topic {
  id: number;
  subject_id: number;
  title: string;
  description: string;
  importance_score: number;
  is_must_ask: boolean;
}

export interface ContentAsset {
  id: number;
  topic_id: number;
  asset_type: 'video' | 'dense_text' | 'fast_paced_text';
  content_url?: string;
  content_body?: string;
  duration_seconds?: number;
}

export interface SwipeEvent {
  id: number;
  topic_id: number;
  direction: 'right' | 'left';
  time_spent: number;
}
