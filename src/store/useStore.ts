import { create } from 'zustand';
import { User, PanicSession, UrgencyTier } from '../types';

interface AppState {
  token: string | null;
  user: User | null;
  activeSession: PanicSession | null;
  urgency: UrgencyTier;
  setAuth: (token: string, user: User) => void;
  logout: () => void;
  setPanicSession: (session: PanicSession | null) => void;
  setUrgency: (urgency: UrgencyTier) => void;
}

export const useStore = create<AppState>((set) => ({
  token: null,
  user: null,
  activeSession: null,
  urgency: 'low',
  setAuth: (token, user) => set({ token, user }),
  logout: () => set({ token: null, user: null, activeSession: null, urgency: 'low' }),
  setPanicSession: (session) => set({ activeSession: session }),
  setUrgency: (urgency) => set({ urgency }),
}));
