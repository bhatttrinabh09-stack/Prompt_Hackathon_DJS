import axios from 'axios';
import * as SecureStore from 'expo-secure-store';
import { useAppStore } from '../store/useStore';

// TODO: point this at the real AdaptLearn backend before shipping.
export const BASE_URL = 'https://api.adaptlearn.dev';

export const apiClient = axios.create({
  baseURL: BASE_URL,
  timeout: 15000,
});

// Every request carries the JWT (if logged in) and the current urgency
// level (if Panic Mode is active), so the backend can apply the same
// dense/fast/short_video filtering logic server-side without every screen
// having to thread the urgency level through manually.
apiClient.interceptors.request.use(async (config) => {
  const token = await SecureStore.getItemAsync('authToken');
  if (token) {
    config.headers = config.headers ?? {};
    config.headers.Authorization = `Bearer ${token}`;
  }

  const urgencyLevel = useAppStore.getState().panicSession?.urgencyLevel;
  if (urgencyLevel) {
    config.headers = config.headers ?? {};
    config.headers['X-Urgency-Level'] = urgencyLevel;
  }

  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const message =
      error?.response?.data?.message ?? error?.message ?? 'Something went wrong. Please try again.';
    return Promise.reject(new Error(message));
  }
);
