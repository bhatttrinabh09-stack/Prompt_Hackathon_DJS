import axios from 'axios';
import { useStore } from '../store/useStore';
import { Platform } from 'react-native';

// For Android emulator, localhost is 10.0.2.2. For iOS/Web, it's localhost or 127.0.0.1.
const getBaseUrl = () => {
  if (Platform.OS === 'android') {
    return 'http://10.0.2.2:8000';
  }
  return 'http://127.0.0.1:8000';
};

export const apiClient = axios.create({
  baseURL: getBaseUrl(),
});

apiClient.interceptors.request.use((config) => {
  const token = useStore.getState().token;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const authApi = {
  login: async (email: string) => {
    const formData = new FormData();
    formData.append('username', email); // OAuth2 expects username
    formData.append('password', 'password');
    const response = await apiClient.post('/auth/token', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },
  signup: async (email: string) => {
    const response = await apiClient.post('/auth/signup', { email, password: 'password' });
    return response.data;
  },
};

export const catalogApi = {
  getSubjects: async () => {
    const response = await apiClient.get('/catalog/subjects');
    return response.data;
  },
  getTopics: async (subjectId: number) => {
    const response = await apiClient.get(`/catalog/subjects/${subjectId}/topics`);
    return response.data;
  },
};

export const contentApi = {
  getTopicContent: async (topicId: number) => {
    const response = await apiClient.get(`/content/topic/${topicId}`);
    return response.data;
  },
};

export const panicApi = {
  setPanicSession: async (targetHours: number) => {
    const response = await apiClient.post('/panic/session', { target_hours: targetHours });
    return response.data;
  },
  getPanicSession: async () => {
    const response = await apiClient.get('/panic/session');
    return response.data;
  },
};

export const swipeApi = {
  recordSwipe: async (topicId: number, direction: 'right' | 'left', timeSpent: number) => {
    const response = await apiClient.post('/swipe/record', {
      topic_id: topicId,
      direction,
      time_spent: timeSpent,
    });
    return response.data;
  },
};

export const progressApi = {
  getProgress: async () => {
    const response = await apiClient.get('/progress/summary');
    return response.data;
  },
};
