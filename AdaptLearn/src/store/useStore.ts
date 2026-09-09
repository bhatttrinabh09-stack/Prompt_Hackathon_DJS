import { create } from 'zustand';
import * as SecureStore from 'expo-secure-store';
import { PanicSession, SubjectProgress, User } from '../types';

interface AppState {
  authToken: string | null;
  user: User | null;
  panicSession: PanicSession | null;
  currentSubjectProgress: SubjectProgress | null;

  setSession: (token: string, user: User) => Promise<void>;
  clearSession: () => Promise<void>;
  setUser: (user: User) => void;
  setPanicSession: (session: PanicSession | null) => void;
  setSubjectProgress: (progress: SubjectProgress | null) => void;
}

export const useAppStore = create<AppState>((set) => ({
  authToken: null,
  user: null,
  panicSession: null,
  currentSubjectProgress: null,

  setSession: async (token, user) => {
    await SecureStore.setItemAsync('authToken', token);
    set({ authToken: token, user });
  },

  clearSession: async () => {
    await SecureStore.deleteItemAsync('authToken');
    set({ authToken: null, user: null, panicSession: null, currentSubjectProgress: null });
  },

  setUser: (user) => set({ user }),
  setPanicSession: (session) => set({ panicSession: session }),
  setSubjectProgress: (progress) => set({ currentSubjectProgress: progress }),
}));

// On cold start, restore a persisted token so the user isn't logged out
// every time the app is reopened. The user profile itself (including
// `branch`) should be re-fetched by the caller once authToken is set,
// since we only persist the token, not the profile.
export async function hydrateSessionFromSecureStore(): Promise<string | null> {
  const token = await SecureStore.getItemAsync('authToken');
  if (token) {
    useAppStore.setState({ authToken: token });
  }
  return token;
}
