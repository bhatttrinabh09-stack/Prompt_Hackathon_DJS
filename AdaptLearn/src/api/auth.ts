import { apiClient } from './client';
import { AuthResponse, User } from '../types';

export async function login(email: string, password: string): Promise<AuthResponse> {
  const { data } = await apiClient.post<AuthResponse>('/auth/login', { email, password });
  return data;
}

export async function signup(name: string, email: string, password: string): Promise<AuthResponse> {
  const { data } = await apiClient.post<AuthResponse>('/auth/signup', { name, email, password });
  return data;
}

export async function setBranch(branch: User['branch']): Promise<User> {
  const { data } = await apiClient.post<User>('/user/branch', { branch });
  return data;
}

// Used to restore the user profile on app relaunch, once a persisted JWT
// has been found in secure storage.
export async function getCurrentUser(): Promise<User> {
  const { data } = await apiClient.get<User>('/user/me');
  return data;
}
