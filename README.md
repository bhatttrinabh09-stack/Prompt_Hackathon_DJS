[Uploading AdaptLearn-frontend.md…]()
# AdaptLearn — React Native (Expo) + TypeScript Frontend

Consolidated file listing for the AdaptLearn prototype (Branch: AIML,
Semester: 3, Subject: Operating Systems). Create a new Expo project with
`npx create-expo-app AdaptLearn -t expo-template-blank-typescript`, then
recreate each file below at the path shown in its heading. A ready-to-copy
`.zip` of this same project is also provided alongside this file.

---

## `package.json`

```json
{
  "name": "adaptlearn",
  "version": "1.0.0",
  "main": "node_modules/expo/AppEntry.js",
  "private": true,
  "scripts": {
    "start": "expo start",
    "android": "expo start --android",
    "ios": "expo start --ios",
    "web": "expo start --web"
  },
  "dependencies": {
    "expo": "~51.0.0",
    "expo-av": "~14.0.0",
    "expo-secure-store": "~13.0.0",
    "expo-status-bar": "~1.12.0",
    "react": "18.2.0",
    "react-native": "0.74.0",
    "react-native-gesture-handler": "~2.16.0",
    "react-native-reanimated": "~3.10.0",
    "react-native-safe-area-context": "4.10.0",
    "react-native-screens": "3.31.0",
    "react-native-svg": "15.2.0",
    "react-native-youtube-iframe": "^2.3.0",
    "react-native-deck-swiper": "^2.0.14",
    "@react-navigation/native": "^6.1.0",
    "@react-navigation/native-stack": "^6.9.0",
    "axios": "^1.7.0",
    "zustand": "^4.5.0"
  },
  "devDependencies": {
    "@babel/core": "^7.24.0",
    "@types/react": "~18.2.0",
    "typescript": "^5.3.0"
  }
}
```

---

## `app.json`

```json
{
  "expo": {
    "name": "AdaptLearn",
    "slug": "adaptlearn",
    "version": "1.0.0",
    "orientation": "portrait",
    "userInterfaceStyle": "dark",
    "scheme": "adaptlearn",
    "assetBundlePatterns": ["**/*"],
    "ios": {
      "supportsTablet": false
    },
    "android": {
      "package": "com.adaptlearn.app"
    }
  }
}
```

---

## `tsconfig.json`

```json
{
  "extends": "expo/tsconfig.base",
  "compilerOptions": {
    "strict": true
  },
  "include": ["**/*.ts", "**/*.tsx"]
}
```

---

## `README.md`

```md
# AdaptLearn — Mobile Frontend (Prototype)

React Native (Expo) + TypeScript frontend for the AdaptLearn prototype.
Scope: **Branch = AIML, Semester = 3, Subject = Operating Systems.**

## Setup

```bash
npx create-expo-app AdaptLearn -t expo-template-blank-typescript
cd AdaptLearn
```

Copy `App.tsx`, `app.json`, `tsconfig.json`, and the entire `src/` folder
from this deliverable into the newly created project, overwriting the
generated placeholders. Then merge the `dependencies` from the provided
`package.json` into your generated one (or replace it outright) and install:

```bash
npm install
npx expo start
```

Set the real backend URL in `src/api/client.ts` (`BASE_URL`) before running
against a live API.

## Project structure

```
App.tsx
src/
  api/          Typed REST client + per-resource API calls
  components/   Shared UI (Panic Toggle, progress bar, cards, states)
  navigation/   React Navigation stack + param types
  screens/      One file per screen in the spec
  store/        Zustand global store
  theme/        Central design tokens
  types/        Shared TypeScript types + ambient module declaration
```

## Known prototype simplifications

- **`react-native-deck-swiper` has no official TypeScript types** — an
  ambient `declare module` stub is included so the project compiles; the
  swiper ref is typed `any` as a result.
- **Swipe deck index sync**: the deck's own internal card index and the
  screen's `cardIndex` state (used to key the countdown ring) are kept in
  sync via the swiper's callbacks, but this is an approximation — worth
  hardening with `react-native-reanimated` + `react-native-gesture-handler`
  directly if you need pixel-perfect gesture control later.
- **Short-form video slide height** is a fixed constant
  (`ContentScreen.tsx`); swap for `Dimensions.get('window').height` for a
  device-accurate full-bleed Reels-style feed.
- **No offline/error-retry queueing** for `POST /swipe-event` — it's
  fire-and-forget so a failed analytics call never blocks navigation.
- **Session restore** assumes a `GET /user/me` endpoint to re-fetch the
  user profile (including `branch`) after a persisted JWT is found on
  cold start — add this endpoint on the backend if it doesn't exist yet.

## Design direction

Dark "study terminal" theme (`src/theme/theme.ts`): deep navy surfaces for
low-glare long study sessions, a mint accent for normal/positive state, and
a coral-red reserved **only** for Panic Mode so urgency is unambiguous at a
glance.
```

---

## `src/types/index.ts`

```ts
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
```

---

## `src/types/react-native-deck-swiper.d.ts`

```ts
// react-native-deck-swiper ships no official type definitions.
// This ambient declaration keeps TypeScript happy; swap in
// @types/react-native-deck-swiper if/when one becomes available.
declare module 'react-native-deck-swiper';
```

---

## `src/theme/theme.ts`

```ts
// Design direction: a focused "study terminal" feel rather than a generic
// SaaS look — deep navy surfaces (calm, low-glare for long study sessions),
// a mint accent for normal/positive state, and a distinct coral-red reserved
// ONLY for Panic Mode so urgency is instantly, unambiguously legible.

export const theme = {
  color: {
    background: '#10152A',
    surface: '#1A2140',
    surfaceRaised: '#232B4D',
    border: '#2E3760',

    textPrimary: '#F5F7FA',
    textMuted: '#9AA3B8',

    accent: '#5EEAD4', // mint — primary actions, progress, calm state
    accentMuted: '#22403D',
    violet: '#8B7CF6', // secondary highlight — Fast Track tag, must-ask chips

    panic: '#FF5D3A', // reserved exclusively for Panic Mode
    panicMuted: '#472A22',

    success: '#4ADE80',
  },
  spacing: (n: number) => n * 4,
  radius: {
    sm: 6,
    md: 12,
    lg: 20,
    pill: 999,
  },
  font: {
    heading: { fontSize: 22, fontWeight: '700' as const },
    subheading: { fontSize: 17, fontWeight: '600' as const },
    body: { fontSize: 15, fontWeight: '400' as const },
    caption: { fontSize: 12, fontWeight: '500' as const },
  },
};

export type Theme = typeof theme;
```

---

## `src/store/useStore.ts`

```ts
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
```

---

## `src/api/client.ts`

```ts
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
```

---

## `src/api/auth.ts`

```ts
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
```

---

## `src/api/panic.ts`

```ts
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
```

---

## `src/api/subjects.ts`

```ts
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
```

---

## `src/api/topics.ts`

```ts
import { apiClient } from './client';
import { CardType, SwipeCard, Topic, TopicContent } from '../types';

export async function fetchTopics(subjectId: string): Promise<Topic[]> {
  const { data } = await apiClient.get<Topic[]>(`/subjects/${subjectId}/topics`);
  return data;
}

export async function fetchSwipeCards(topicId: string): Promise<SwipeCard[]> {
  const { data } = await apiClient.get<SwipeCard[]>(`/topics/${topicId}/cards`);
  return data;
}

export async function postSwipeEvent(
  topicId: string,
  cardId: string,
  cardType: CardType,
  direction: 'left' | 'right'
): Promise<void> {
  await apiClient.post('/swipe-event', { topicId, cardId, cardType, direction });
}

export async function fetchTopicContent(topicId: string, mode: CardType): Promise<TopicContent> {
  const { data } = await apiClient.get<TopicContent>(`/topics/${topicId}/content`, {
    params: { mode },
  });
  return data;
}
```

---

## `src/api/progress.ts`

```ts
import { apiClient } from './client';

export async function markTopicComplete(topicId: string, mode: string): Promise<void> {
  await apiClient.post('/progress/complete', { topicId, mode });
}
```

---

## `src/navigation/types.ts`

```ts
import { CardType } from '../types';

export type RootStackParamList = {
  Auth: undefined;
  BranchSelect: undefined;
  Home: undefined;
  Semester: undefined;
  Subject: { semester: number };
  TopicList: { subjectId: string; subjectName: string };
  Swipe: { topicId: string; topicTitle: string };
  Content: { topicId: string; topicTitle: string; mode: CardType };
};
```

---

## `src/navigation/RootNavigator.tsx`

```tsx
import React from 'react';
import { NavigationContainer, DefaultTheme } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { useAppStore } from '../store/useStore';
import { theme } from '../theme/theme';
import { RootStackParamList } from './types';

import AuthScreen from '../screens/AuthScreen';
import BranchSelectScreen from '../screens/BranchSelectScreen';
import HomeScreen from '../screens/HomeScreen';
import SemesterScreen from '../screens/SemesterScreen';
import SubjectScreen from '../screens/SubjectScreen';
import TopicListScreen from '../screens/TopicListScreen';
import SwipeScreen from '../screens/SwipeScreen';
import ContentScreen from '../screens/ContentScreen';

const Stack = createNativeStackNavigator<RootStackParamList>();

const navTheme = {
  ...DefaultTheme,
  colors: {
    ...DefaultTheme.colors,
    background: theme.color.background,
    card: theme.color.surface,
    text: theme.color.textPrimary,
    border: theme.color.border,
    primary: theme.color.accent,
  },
};

// Three-tier gating: no token -> Auth, token but no branch -> BranchSelect,
// otherwise the full app. This keeps onboarding order enforced (login,
// then branch) without extra guard logic scattered across screens.
export default function RootNavigator() {
  const authToken = useAppStore((s) => s.authToken);
  const user = useAppStore((s) => s.user);

  return (
    <NavigationContainer theme={navTheme}>
      <Stack.Navigator
        screenOptions={{
          headerStyle: { backgroundColor: theme.color.surface },
          headerTintColor: theme.color.textPrimary,
          headerShadowVisible: false,
        }}
      >
        {!authToken ? (
          <Stack.Screen name="Auth" component={AuthScreen} options={{ headerShown: false }} />
        ) : !user?.branch ? (
          <Stack.Screen
            name="BranchSelect"
            component={BranchSelectScreen}
            options={{ title: 'Choose Branch' }}
          />
        ) : (
          <>
            <Stack.Screen name="Home" component={HomeScreen} options={{ headerShown: false }} />
            <Stack.Screen name="Semester" component={SemesterScreen} options={{ title: 'Choose Semester' }} />
            <Stack.Screen name="Subject" component={SubjectScreen} options={{ title: 'Choose Subject' }} />
            <Stack.Screen
              name="TopicList"
              component={TopicListScreen}
              options={({ route }) => ({ title: route.params.subjectName })}
            />
            <Stack.Screen
              name="Swipe"
              component={SwipeScreen}
              options={({ route }) => ({ title: route.params.topicTitle })}
            />
            <Stack.Screen name="Content" component={ContentScreen} options={{ headerShown: false }} />
          </>
        )}
      </Stack.Navigator>
    </NavigationContainer>
  );
}
```

---

## `src/components/ScreenContainer.tsx`

```tsx
import React from 'react';
import { SafeAreaView, StyleSheet, View } from 'react-native';
import { theme } from '../theme/theme';
import PanicToggle from './PanicToggle';

interface Props {
  children: React.ReactNode;
  // Every screen shows the Panic Toggle by default. Only the content
  // player (ContentScreen) opts out, per spec: visible up until — not
  // during — the actual learning/content-consumption flow.
  showPanicToggle?: boolean;
}

export default function ScreenContainer({ children, showPanicToggle = true }: Props) {
  return (
    <SafeAreaView style={styles.safe}>
      {showPanicToggle && <PanicToggle />}
      <View style={styles.content}>{children}</View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: theme.color.background },
  content: { flex: 1 },
});
```

---

## `src/components/PanicToggle.tsx`

```tsx
import React, { useEffect, useState } from 'react';
import { Animated, Pressable, StyleSheet, Text, View } from 'react-native';
import { useAppStore } from '../store/useStore';
import { theme } from '../theme/theme';
import PanicModal from './PanicModal';
import { endPanicSession } from '../api/panic';

function useCountdownLabel(deadline?: string) {
  const [label, setLabel] = useState('--');

  useEffect(() => {
    if (!deadline) {
      setLabel('--');
      return;
    }
    const update = () => {
      const diffMs = new Date(deadline).getTime() - Date.now();
      if (diffMs <= 0) {
        setLabel('Time up');
        return;
      }
      const totalHours = Math.floor(diffMs / (1000 * 60 * 60));
      const minutes = Math.floor((diffMs / (1000 * 60)) % 60);
      if (totalHours >= 24) {
        setLabel(`${Math.floor(totalHours / 24)}d ${totalHours % 24}h left`);
      } else {
        setLabel(`${totalHours}h ${minutes}m left`);
      }
    };
    update();
    const interval = setInterval(update, 60 * 1000);
    return () => clearInterval(interval);
  }, [deadline]);

  return label;
}

export default function PanicToggle() {
  const panicSession = useAppStore((s) => s.panicSession);
  const setPanicSession = useAppStore((s) => s.setPanicSession);
  const [modalVisible, setModalVisible] = useState(false);
  const pulse = React.useRef(new Animated.Value(1)).current;
  const countdownLabel = useCountdownLabel(panicSession?.deadline);

  useEffect(() => {
    if (!panicSession) return;
    const loop = Animated.loop(
      Animated.sequence([
        Animated.timing(pulse, { toValue: 1.15, duration: 700, useNativeDriver: true }),
        Animated.timing(pulse, { toValue: 1, duration: 700, useNativeDriver: true }),
      ])
    );
    loop.start();
    return () => loop.stop();
  }, [panicSession, pulse]);

  async function handlePress() {
    if (panicSession) {
      // Tapping an active toggle ends Panic Mode. Best-effort on the
      // network call — a failed DELETE shouldn't trap the student in a
      // stale urgency state, so we clear local state regardless.
      endPanicSession(panicSession.id).catch(() => {});
      setPanicSession(null);
      return;
    }
    setModalVisible(true);
  }

  return (
    <View style={styles.wrapper}>
      <Pressable
        onPress={handlePress}
        style={[styles.pill, panicSession ? styles.pillActive : styles.pillIdle]}
        accessibilityRole="switch"
        accessibilityState={{ checked: !!panicSession }}
        accessibilityLabel="Panic toggle — set exam countdown"
      >
        <Animated.View
          style={[
            styles.dot,
            { backgroundColor: panicSession ? theme.color.panic : theme.color.textMuted },
            panicSession ? { transform: [{ scale: pulse }] } : null,
          ]}
        />
        <Text style={styles.label}>
          {panicSession ? `Panic Mode · ${countdownLabel}` : 'Panic Toggle'}
        </Text>
      </Pressable>

      <PanicModal visible={modalVisible} onClose={() => setModalVisible(false)} />
    </View>
  );
}

const styles = StyleSheet.create({
  wrapper: {
    paddingHorizontal: theme.spacing(4),
    paddingTop: theme.spacing(2),
    paddingBottom: theme.spacing(1),
    backgroundColor: theme.color.background,
  },
  pill: {
    flexDirection: 'row',
    alignItems: 'center',
    alignSelf: 'flex-start',
    paddingVertical: theme.spacing(2),
    paddingHorizontal: theme.spacing(3),
    borderRadius: theme.radius.pill,
    borderWidth: 1,
  },
  pillIdle: {
    backgroundColor: theme.color.surface,
    borderColor: theme.color.border,
  },
  pillActive: {
    backgroundColor: theme.color.panicMuted,
    borderColor: theme.color.panic,
  },
  dot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    marginRight: theme.spacing(2),
  },
  label: {
    color: theme.color.textPrimary,
    fontWeight: '600',
    fontSize: 13,
  },
});
```

---

## `src/components/PanicModal.tsx`

```tsx
import React, { useState } from 'react';
import { Modal, Pressable, StyleSheet, Text, TextInput, View } from 'react-native';
import { theme } from '../theme/theme';
import { useAppStore } from '../store/useStore';
import { startPanicSession } from '../api/panic';

interface Props {
  visible: boolean;
  onClose: () => void;
}

type Unit = 'days' | 'hours';

export default function PanicModal({ visible, onClose }: Props) {
  const setPanicSession = useAppStore((s) => s.setPanicSession);
  const [value, setValue] = useState('');
  const [unit, setUnit] = useState<Unit>('days');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit() {
    const numeric = Number(value);
    if (!value || Number.isNaN(numeric) || numeric <= 0) {
      setError('Enter a valid number.');
      return;
    }
    setSubmitting(true);
    setError(null);
    try {
      const session = await startPanicSession(numeric, unit);
      setPanicSession(session);
      setValue('');
      onClose();
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Could not start Panic Mode.');
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <Modal visible={visible} transparent animationType="fade" onRequestClose={onClose}>
      <View style={styles.backdrop}>
        <View style={styles.card}>
          <Text style={styles.title}>Exam in how many days/hours?</Text>
          <Text style={styles.subtitle}>
            We'll trim your content down to what matters most for the time you have left.
          </Text>

          <TextInput
            value={value}
            onChangeText={setValue}
            keyboardType="number-pad"
            placeholder="e.g. 3"
            placeholderTextColor={theme.color.textMuted}
            style={styles.input}
          />

          <View style={styles.unitRow}>
            {(['days', 'hours'] as Unit[]).map((u) => (
              <Pressable
                key={u}
                onPress={() => setUnit(u)}
                style={[styles.unitButton, unit === u && styles.unitButtonActive]}
              >
                <Text style={[styles.unitLabel, unit === u && styles.unitLabelActive]}>
                  {u === 'days' ? 'Days' : 'Hours'}
                </Text>
              </Pressable>
            ))}
          </View>

          {error && <Text style={styles.error}>{error}</Text>}

          <View style={styles.actions}>
            <Pressable onPress={onClose} style={styles.secondaryButton} disabled={submitting}>
              <Text style={styles.secondaryLabel}>Cancel</Text>
            </Pressable>
            <Pressable onPress={handleSubmit} style={styles.primaryButton} disabled={submitting}>
              <Text style={styles.primaryLabel}>{submitting ? 'Starting…' : 'Start Panic Mode'}</Text>
            </Pressable>
          </View>
        </View>
      </View>
    </Modal>
  );
}

const styles = StyleSheet.create({
  backdrop: {
    flex: 1,
    backgroundColor: 'rgba(6, 8, 16, 0.72)',
    justifyContent: 'center',
    padding: theme.spacing(6),
  },
  card: {
    backgroundColor: theme.color.surface,
    borderRadius: theme.radius.lg,
    padding: theme.spacing(6),
    borderWidth: 1,
    borderColor: theme.color.border,
  },
  title: { ...theme.font.heading, color: theme.color.textPrimary, marginBottom: theme.spacing(1) },
  subtitle: { ...theme.font.body, color: theme.color.textMuted, marginBottom: theme.spacing(4) },
  input: {
    borderWidth: 1,
    borderColor: theme.color.border,
    borderRadius: theme.radius.md,
    paddingHorizontal: theme.spacing(3),
    paddingVertical: theme.spacing(3),
    color: theme.color.textPrimary,
    fontSize: 18,
    marginBottom: theme.spacing(3),
  },
  unitRow: { flexDirection: 'row', marginBottom: theme.spacing(3) },
  unitButton: {
    flex: 1,
    paddingVertical: theme.spacing(2),
    borderRadius: theme.radius.md,
    borderWidth: 1,
    borderColor: theme.color.border,
    alignItems: 'center',
    marginRight: theme.spacing(2),
  },
  unitButtonActive: {
    backgroundColor: theme.color.accentMuted,
    borderColor: theme.color.accent,
  },
  unitLabel: { color: theme.color.textMuted, fontWeight: '600' },
  unitLabelActive: { color: theme.color.accent },
  error: { color: theme.color.panic, marginBottom: theme.spacing(2) },
  actions: { flexDirection: 'row', justifyContent: 'flex-end', marginTop: theme.spacing(2) },
  secondaryButton: { paddingVertical: theme.spacing(3), paddingHorizontal: theme.spacing(4) },
  secondaryLabel: { color: theme.color.textMuted, fontWeight: '600' },
  primaryButton: {
    backgroundColor: theme.color.accent,
    paddingVertical: theme.spacing(3),
    paddingHorizontal: theme.spacing(5),
    borderRadius: theme.radius.md,
  },
  primaryLabel: { color: theme.color.background, fontWeight: '700' },
});
```

---

## `src/components/ProgressBar.tsx`

```tsx
import React from 'react';
import { StyleSheet, Text, View } from 'react-native';
import { theme } from '../theme/theme';

interface Props {
  percent: number; // 0-100
  label?: string;
  compact?: boolean;
}

export default function ProgressBar({ percent, label, compact }: Props) {
  const clamped = Math.max(0, Math.min(100, percent));
  return (
    <View style={compact ? styles.compactWrapper : styles.wrapper}>
      {label && <Text style={styles.label}>{label}</Text>}
      <View style={styles.track}>
        <View style={[styles.fill, { width: `${clamped}%` }]} />
      </View>
      <Text style={styles.percent}>{Math.round(clamped)}%</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  wrapper: { marginBottom: theme.spacing(4) },
  compactWrapper: { marginBottom: theme.spacing(2) },
  label: { ...theme.font.caption, color: theme.color.textMuted, marginBottom: theme.spacing(1) },
  track: {
    height: 8,
    borderRadius: theme.radius.pill,
    backgroundColor: theme.color.surfaceRaised,
    overflow: 'hidden',
  },
  fill: {
    height: '100%',
    backgroundColor: theme.color.accent,
    borderRadius: theme.radius.pill,
  },
  percent: {
    ...theme.font.caption,
    color: theme.color.textMuted,
    marginTop: theme.spacing(1),
    alignSelf: 'flex-end',
  },
});
```

---

## `src/components/CountdownRing.tsx`

```tsx
import React, { useEffect, useRef } from 'react';
import { Animated, Easing, StyleSheet, View } from 'react-native';
import Svg, { Circle } from 'react-native-svg';
import { theme } from '../theme/theme';

const AnimatedCircle = Animated.createAnimatedComponent(Circle);
const SIZE = 40;
const STROKE = 4;
const RADIUS = (SIZE - STROKE) / 2;
const CIRCUMFERENCE = 2 * Math.PI * RADIUS;

interface Props {
  durationMs: number;
  onComplete: () => void;
  active: boolean;
}

export default function CountdownRing({ durationMs, onComplete, active }: Props) {
  const progress = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    if (!active) return;
    progress.setValue(0);
    // strokeDashoffset is not an animatable native-driver property, so
    // this animation must run on the JS thread (useNativeDriver: false).
    const animation = Animated.timing(progress, {
      toValue: 1,
      duration: durationMs,
      easing: Easing.linear,
      useNativeDriver: false,
    });
    animation.start(({ finished }) => {
      if (finished) onComplete();
    });
    return () => animation.stop();
  }, [active, durationMs, onComplete, progress]);

  const strokeDashoffset = progress.interpolate({
    inputRange: [0, 1],
    outputRange: [0, CIRCUMFERENCE],
  });

  return (
    <View style={styles.wrapper} pointerEvents="none">
      <Svg width={SIZE} height={SIZE}>
        <Circle
          cx={SIZE / 2}
          cy={SIZE / 2}
          r={RADIUS}
          stroke={theme.color.surfaceRaised}
          strokeWidth={STROKE}
          fill="none"
        />
        <AnimatedCircle
          cx={SIZE / 2}
          cy={SIZE / 2}
          r={RADIUS}
          stroke={theme.color.accent}
          strokeWidth={STROKE}
          fill="none"
          strokeDasharray={CIRCUMFERENCE}
          strokeDashoffset={strokeDashoffset}
          strokeLinecap="round"
          rotation="-90"
          origin={`${SIZE / 2}, ${SIZE / 2}`}
        />
      </Svg>
    </View>
  );
}

const styles = StyleSheet.create({
  wrapper: {
    position: 'absolute',
    top: theme.spacing(3),
    right: theme.spacing(3),
    zIndex: 10,
  },
});
```

---

## `src/components/GridTile.tsx`

```tsx
import React from 'react';
import { Pressable, StyleSheet, Text } from 'react-native';
import { theme } from '../theme/theme';

interface Props {
  label: string;
  sublabel?: string;
  enabled: boolean;
  onPress: () => void;
}

export default function GridTile({ label, sublabel, enabled, onPress }: Props) {
  return (
    <Pressable
      onPress={enabled ? onPress : undefined}
      style={[styles.tile, !enabled && styles.tileDisabled]}
      accessibilityState={{ disabled: !enabled }}
    >
      <Text style={[styles.label, !enabled && styles.labelDisabled]}>{label}</Text>
      {sublabel ? <Text style={styles.sublabel}>{sublabel}</Text> : null}
      {!enabled && <Text style={styles.lockedTag}>Coming soon</Text>}
    </Pressable>
  );
}

const styles = StyleSheet.create({
  tile: {
    width: '47%',
    aspectRatio: 1.1,
    backgroundColor: theme.color.surface,
    borderRadius: theme.radius.lg,
    borderWidth: 1,
    borderColor: theme.color.border,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: theme.spacing(4),
  },
  tileDisabled: { opacity: 0.4 },
  label: { ...theme.font.subheading, color: theme.color.textPrimary },
  labelDisabled: { color: theme.color.textMuted },
  sublabel: { ...theme.font.caption, color: theme.color.textMuted, marginTop: theme.spacing(1) },
  lockedTag: {
    ...theme.font.caption,
    color: theme.color.textMuted,
    marginTop: theme.spacing(2),
  },
});
```

---

## `src/components/LoadingView.tsx`

```tsx
import React from 'react';
import { ActivityIndicator, StyleSheet, Text, View } from 'react-native';
import { theme } from '../theme/theme';

export default function LoadingView({ label = 'Loading…' }: { label?: string }) {
  return (
    <View style={styles.wrapper}>
      <ActivityIndicator color={theme.color.accent} size="large" />
      <Text style={styles.label}>{label}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  wrapper: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  label: { ...theme.font.body, color: theme.color.textMuted, marginTop: theme.spacing(3) },
});
```

---

## `src/components/ErrorView.tsx`

```tsx
import React from 'react';
import { Pressable, StyleSheet, Text, View } from 'react-native';
import { theme } from '../theme/theme';

interface Props {
  message: string;
  onRetry?: () => void;
}

export default function ErrorView({ message, onRetry }: Props) {
  return (
    <View style={styles.wrapper}>
      <Text style={styles.title}>Something didn't load</Text>
      <Text style={styles.message}>{message}</Text>
      {onRetry && (
        <Pressable onPress={onRetry} style={styles.button}>
          <Text style={styles.buttonLabel}>Try again</Text>
        </Pressable>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  wrapper: { flex: 1, justifyContent: 'center', alignItems: 'center', padding: theme.spacing(6) },
  title: { ...theme.font.subheading, color: theme.color.textPrimary, marginBottom: theme.spacing(2) },
  message: {
    ...theme.font.body,
    color: theme.color.textMuted,
    textAlign: 'center',
    marginBottom: theme.spacing(4),
  },
  button: {
    backgroundColor: theme.color.accent,
    paddingVertical: theme.spacing(3),
    paddingHorizontal: theme.spacing(5),
    borderRadius: theme.radius.md,
  },
  buttonLabel: { color: theme.color.background, fontWeight: '700' },
});
```

---

## `src/components/cards/DenseTextCard.tsx`

```tsx
import React from 'react';
import { StyleSheet, Text, View } from 'react-native';
import { theme } from '../../theme/theme';
import { SwipeCard } from '../../types';

export default function DenseTextCard({ card }: { card: SwipeCard }) {
  return (
    <View style={styles.card}>
      <Text style={styles.tag}>Deep Focus</Text>
      <Text style={styles.title}>{card.title}</Text>
      <Text style={styles.preview} numberOfLines={8}>
        {card.preview}
      </Text>
      <Text style={styles.hint}>Prerequisites · Textbooks · Full notes · Long lecture</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    flex: 1,
    borderRadius: theme.radius.lg,
    padding: theme.spacing(6),
    borderWidth: 1,
    borderColor: theme.color.border,
    backgroundColor: theme.color.surface,
    justifyContent: 'space-between',
  },
  tag: { ...theme.font.caption, color: theme.color.accent, marginBottom: theme.spacing(2) },
  title: { ...theme.font.heading, color: theme.color.textPrimary, marginBottom: theme.spacing(3) },
  preview: { ...theme.font.body, color: theme.color.textMuted, lineHeight: 22 },
  hint: { ...theme.font.caption, color: theme.color.textMuted, marginTop: theme.spacing(4) },
});
```

---

## `src/components/cards/FastPacedCard.tsx`

```tsx
import React from 'react';
import { StyleSheet, Text, View } from 'react-native';
import { theme } from '../../theme/theme';
import { SwipeCard } from '../../types';

export default function FastPacedCard({ card }: { card: SwipeCard }) {
  const bullets = card.preview.split('\n').filter(Boolean).slice(0, 5);
  return (
    <View style={styles.card}>
      <Text style={styles.tag}>Fast Track</Text>
      <Text style={styles.title}>{card.title}</Text>
      <View>
        {bullets.map((b, i) => (
          <Text key={i} style={styles.bullet}>
            {'\u2022'} {b}
          </Text>
        ))}
      </View>
      <Text style={styles.hint}>Condensed notes · Short videos · Must-ask topics</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    flex: 1,
    borderRadius: theme.radius.lg,
    padding: theme.spacing(6),
    borderWidth: 1,
    borderColor: theme.color.border,
    backgroundColor: theme.color.surface,
    justifyContent: 'space-between',
  },
  tag: { ...theme.font.caption, color: theme.color.violet, marginBottom: theme.spacing(2) },
  title: { ...theme.font.heading, color: theme.color.textPrimary, marginBottom: theme.spacing(3) },
  bullet: { ...theme.font.body, color: theme.color.textPrimary, marginBottom: theme.spacing(2) },
  hint: { ...theme.font.caption, color: theme.color.textMuted, marginTop: theme.spacing(4) },
});
```

---

## `src/components/cards/ShortVideoCard.tsx`

```tsx
import React from 'react';
import { StyleSheet, Text, View } from 'react-native';
import { ResizeMode, Video } from 'expo-av';
import { theme } from '../../theme/theme';
import { SwipeCard } from '../../types';

export default function ShortVideoCard({ card }: { card: SwipeCard }) {
  return (
    <View style={styles.card}>
      <Text style={styles.tag}>Micro-Learn</Text>
      {card.thumbnailUrl ? (
        <Video
          source={{ uri: card.thumbnailUrl }}
          style={styles.player}
          resizeMode={ResizeMode.COVER}
          isMuted
          isLooping
          shouldPlay
        />
      ) : (
        <View style={styles.placeholder} />
      )}
      <Text style={styles.title}>{card.title}</Text>
      <Text style={styles.hint}>AI-generated short-form video</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    flex: 1,
    borderRadius: theme.radius.lg,
    padding: theme.spacing(6),
    borderWidth: 1,
    borderColor: theme.color.border,
    backgroundColor: theme.color.surface,
    justifyContent: 'flex-end',
    overflow: 'hidden',
  },
  player: { ...StyleSheet.absoluteFillObject, borderRadius: theme.radius.lg },
  placeholder: { ...StyleSheet.absoluteFillObject, backgroundColor: theme.color.surfaceRaised },
  tag: { ...theme.font.caption, color: theme.color.panic, marginBottom: theme.spacing(2) },
  title: { ...theme.font.heading, color: '#FFFFFF', marginBottom: theme.spacing(1) },
  hint: { ...theme.font.caption, color: 'rgba(255,255,255,0.8)' },
});
```

---

## `src/screens/AuthScreen.tsx`

```tsx
import React, { useState } from 'react';
import { KeyboardAvoidingView, Platform, Pressable, StyleSheet, Text, TextInput, View } from 'react-native';
import { theme } from '../theme/theme';
import { useAppStore } from '../store/useStore';
import { login, signup } from '../api/auth';

type Mode = 'login' | 'signup';

export default function AuthScreen() {
  const setSession = useAppStore((s) => s.setSession);
  const [mode, setMode] = useState<Mode>('login');
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit() {
    if (!email || !password || (mode === 'signup' && !name)) {
      setError('Please fill in all fields.');
      return;
    }
    setSubmitting(true);
    setError(null);
    try {
      const result =
        mode === 'login' ? await login(email, password) : await signup(name, email, password);
      await setSession(result.token, result.user);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Authentication failed.');
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <KeyboardAvoidingView style={styles.wrapper} behavior={Platform.OS === 'ios' ? 'padding' : undefined}>
      <Text style={styles.brand}>AdaptLearn</Text>
      <Text style={styles.tagline}>Study at the pace your exam actually gives you.</Text>

      <View>
        {mode === 'signup' && (
          <TextInput
            value={name}
            onChangeText={setName}
            placeholder="Full name"
            placeholderTextColor={theme.color.textMuted}
            style={styles.input}
          />
        )}
        <TextInput
          value={email}
          onChangeText={setEmail}
          placeholder="Email"
          placeholderTextColor={theme.color.textMuted}
          autoCapitalize="none"
          keyboardType="email-address"
          style={styles.input}
        />
        <TextInput
          value={password}
          onChangeText={setPassword}
          placeholder="Password"
          placeholderTextColor={theme.color.textMuted}
          secureTextEntry
          style={styles.input}
        />

        {error && <Text style={styles.error}>{error}</Text>}

        <Pressable style={styles.primaryButton} onPress={handleSubmit} disabled={submitting}>
          <Text style={styles.primaryLabel}>
            {submitting ? 'Please wait…' : mode === 'login' ? 'Log In' : 'Sign Up'}
          </Text>
        </Pressable>

        <Pressable onPress={() => setMode(mode === 'login' ? 'signup' : 'login')}>
          <Text style={styles.switchMode}>
            {mode === 'login' ? 'New here? Create an account' : 'Already have an account? Log in'}
          </Text>
        </Pressable>
      </View>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  wrapper: { flex: 1, backgroundColor: theme.color.background, justifyContent: 'center', padding: theme.spacing(6) },
  brand: { ...theme.font.heading, fontSize: 30, color: theme.color.accent, marginBottom: theme.spacing(1) },
  tagline: { ...theme.font.body, color: theme.color.textMuted, marginBottom: theme.spacing(8) },
  input: {
    borderWidth: 1,
    borderColor: theme.color.border,
    borderRadius: theme.radius.md,
    paddingHorizontal: theme.spacing(3),
    paddingVertical: theme.spacing(3),
    color: theme.color.textPrimary,
    marginBottom: theme.spacing(3),
  },
  error: { color: theme.color.panic, marginBottom: theme.spacing(2) },
  primaryButton: {
    backgroundColor: theme.color.accent,
    borderRadius: theme.radius.md,
    paddingVertical: theme.spacing(3),
    alignItems: 'center',
    marginBottom: theme.spacing(3),
  },
  primaryLabel: { color: theme.color.background, fontWeight: '700', fontSize: 16 },
  switchMode: { color: theme.color.textMuted, textAlign: 'center' },
});
```

---

## `src/screens/BranchSelectScreen.tsx`

```tsx
import React, { useState } from 'react';
import { Pressable, StyleSheet, Text, View } from 'react-native';
import { theme } from '../theme/theme';
import { useAppStore } from '../store/useStore';
import { setBranch } from '../api/auth';
import type { Branch } from '../types';

// Prototype scope: only AIML is selectable. Add more branches here as the
// backend/content library grows — the UI already renders a list.
const BRANCHES: { code: Branch; label: string; enabled: boolean }[] = [
  { code: 'AIML', label: 'AI & ML', enabled: true },
];

export default function BranchSelectScreen() {
  const user = useAppStore((s) => s.user);
  const setUser = useAppStore((s) => s.setUser);
  const [submitting, setSubmitting] = useState<Branch | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleSelect(branch: Branch) {
    if (!user) return;
    setSubmitting(branch);
    setError(null);
    try {
      const updated = await setBranch(branch);
      setUser(updated);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Could not save your branch.');
    } finally {
      setSubmitting(null);
    }
  }

  return (
    <View style={styles.wrapper}>
      <Text style={styles.title}>Which branch are you in?</Text>
      <Text style={styles.subtitle}>Your subjects and content are matched to your branch.</Text>

      {BRANCHES.map((b) => (
        <Pressable
          key={b.code}
          onPress={() => b.enabled && handleSelect(b.code)}
          style={[styles.option, !b.enabled && styles.optionDisabled]}
        >
          <Text style={styles.optionLabel}>{b.label}</Text>
          <Text style={styles.optionMeta}>
            {submitting === b.code ? 'Saving…' : b.enabled ? '' : 'Coming soon'}
          </Text>
        </Pressable>
      ))}

      {error && <Text style={styles.error}>{error}</Text>}
    </View>
  );
}

const styles = StyleSheet.create({
  wrapper: { flex: 1, backgroundColor: theme.color.background, padding: theme.spacing(6) },
  title: { ...theme.font.heading, color: theme.color.textPrimary, marginBottom: theme.spacing(1) },
  subtitle: { ...theme.font.body, color: theme.color.textMuted, marginBottom: theme.spacing(6) },
  option: {
    borderWidth: 1,
    borderColor: theme.color.border,
    borderRadius: theme.radius.md,
    padding: theme.spacing(4),
    marginBottom: theme.spacing(3),
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: theme.color.surface,
  },
  optionDisabled: { opacity: 0.4 },
  optionLabel: { ...theme.font.subheading, color: theme.color.textPrimary },
  optionMeta: { ...theme.font.caption, color: theme.color.textMuted },
  error: { color: theme.color.panic, marginTop: theme.spacing(2) },
});
```

---

## `src/screens/HomeScreen.tsx`

```tsx
import React from 'react';
import { NativeStackScreenProps } from '@react-navigation/native-stack';
import { Pressable, StyleSheet, Text, View } from 'react-native';
import ScreenContainer from '../components/ScreenContainer';
import { theme } from '../theme/theme';
import { useAppStore } from '../store/useStore';
import { RootStackParamList } from '../navigation/types';

type Props = NativeStackScreenProps<RootStackParamList, 'Home'>;

export default function HomeScreen({ navigation }: Props) {
  const user = useAppStore((s) => s.user);

  return (
    <ScreenContainer>
      <View style={styles.body}>
        <Text style={styles.greeting}>Hi{user?.name ? `, ${user.name.split(' ')[0]}` : ''}</Text>
        <Text style={styles.subtitle}>Ready to keep going with {user?.branch ?? 'your branch'}?</Text>

        <Pressable style={styles.ctaCard} onPress={() => navigation.navigate('Semester')}>
          <Text style={styles.ctaTitle}>Continue learning</Text>
          <Text style={styles.ctaMeta}>Pick a semester to jump back in</Text>
        </Pressable>
      </View>
    </ScreenContainer>
  );
}

const styles = StyleSheet.create({
  body: { flex: 1, padding: theme.spacing(6) },
  greeting: { ...theme.font.heading, fontSize: 26, color: theme.color.textPrimary },
  subtitle: {
    ...theme.font.body,
    color: theme.color.textMuted,
    marginTop: theme.spacing(1),
    marginBottom: theme.spacing(8),
  },
  ctaCard: {
    backgroundColor: theme.color.surface,
    borderRadius: theme.radius.lg,
    borderWidth: 1,
    borderColor: theme.color.border,
    padding: theme.spacing(5),
  },
  ctaTitle: { ...theme.font.subheading, color: theme.color.textPrimary, marginBottom: theme.spacing(1) },
  ctaMeta: { ...theme.font.caption, color: theme.color.textMuted },
});
```

---

## `src/screens/SemesterScreen.tsx`

```tsx
import React from 'react';
import { NativeStackScreenProps } from '@react-navigation/native-stack';
import { ScrollView, StyleSheet } from 'react-native';
import ScreenContainer from '../components/ScreenContainer';
import GridTile from '../components/GridTile';
import { theme } from '../theme/theme';
import { RootStackParamList } from '../navigation/types';

type Props = NativeStackScreenProps<RootStackParamList, 'Semester'>;

const PROTOTYPE_ENABLED_SEMESTER = 3;

export default function SemesterScreen({ navigation }: Props) {
  return (
    <ScreenContainer>
      <ScrollView contentContainerStyle={styles.grid}>
        {Array.from({ length: 8 }, (_, i) => i + 1).map((sem) => (
          <GridTile
            key={sem}
            label={`Semester ${sem}`}
            enabled={sem === PROTOTYPE_ENABLED_SEMESTER}
            onPress={() => navigation.navigate('Subject', { semester: sem })}
          />
        ))}
      </ScrollView>
    </ScreenContainer>
  );
}

const styles = StyleSheet.create({
  grid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
    padding: theme.spacing(6),
  },
});
```

---

## `src/screens/SubjectScreen.tsx`

```tsx
import React, { useCallback, useEffect, useState } from 'react';
import { NativeStackScreenProps } from '@react-navigation/native-stack';
import { ScrollView, StyleSheet } from 'react-native';
import ScreenContainer from '../components/ScreenContainer';
import GridTile from '../components/GridTile';
import LoadingView from '../components/LoadingView';
import ErrorView from '../components/ErrorView';
import { theme } from '../theme/theme';
import { RootStackParamList } from '../navigation/types';
import { fetchSubjects } from '../api/subjects';
import { useAppStore } from '../store/useStore';
import { Subject } from '../types';

type Props = NativeStackScreenProps<RootStackParamList, 'Subject'>;

export default function SubjectScreen({ route, navigation }: Props) {
  const { semester } = route.params;
  const branch = useAppStore((s) => s.user?.branch);
  const [subjects, setSubjects] = useState<Subject[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    if (!branch) return;
    setLoading(true);
    setError(null);
    try {
      const data = await fetchSubjects(branch, semester);
      setSubjects(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Could not load subjects.');
    } finally {
      setLoading(false);
    }
  }, [branch, semester]);

  useEffect(() => {
    load();
  }, [load]);

  if (loading) {
    return (
      <ScreenContainer>
        <LoadingView label="Loading subjects…" />
      </ScreenContainer>
    );
  }
  if (error) {
    return (
      <ScreenContainer>
        <ErrorView message={error} onRetry={load} />
      </ScreenContainer>
    );
  }

  return (
    <ScreenContainer>
      <ScrollView contentContainerStyle={styles.grid}>
        {(subjects ?? []).map((subject) => (
          <GridTile
            key={subject.id}
            label={subject.name}
            enabled={subject.enabled}
            onPress={() =>
              navigation.navigate('TopicList', { subjectId: subject.id, subjectName: subject.name })
            }
          />
        ))}
      </ScrollView>
    </ScreenContainer>
  );
}

const styles = StyleSheet.create({
  grid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
    padding: theme.spacing(6),
  },
});
```

---

## `src/screens/TopicListScreen.tsx`

```tsx
import React, { useCallback, useEffect, useState } from 'react';
import { NativeStackScreenProps } from '@react-navigation/native-stack';
import { FlatList, Pressable, StyleSheet, Text, View } from 'react-native';
import ScreenContainer from '../components/ScreenContainer';
import ProgressBar from '../components/ProgressBar';
import LoadingView from '../components/LoadingView';
import ErrorView from '../components/ErrorView';
import { theme } from '../theme/theme';
import { RootStackParamList } from '../navigation/types';
import { fetchTopics } from '../api/topics';
import { fetchSubjectProgress } from '../api/subjects';
import { useAppStore } from '../store/useStore';
import { Topic } from '../types';

type Props = NativeStackScreenProps<RootStackParamList, 'TopicList'>;

export default function TopicListScreen({ route, navigation }: Props) {
  const { subjectId, subjectName } = route.params;
  const setSubjectProgress = useAppStore((s) => s.setSubjectProgress);
  const progress = useAppStore((s) => s.currentSubjectProgress);
  const [topics, setTopics] = useState<Topic[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [topicData, progressData] = await Promise.all([
        fetchTopics(subjectId),
        fetchSubjectProgress(subjectId),
      ]);
      setTopics(topicData);
      setSubjectProgress(progressData);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Could not load topics.');
    } finally {
      setLoading(false);
    }
  }, [subjectId, setSubjectProgress]);

  useEffect(() => {
    load();
  }, [load]);

  if (loading) {
    return (
      <ScreenContainer>
        <LoadingView label="Loading topics…" />
      </ScreenContainer>
    );
  }
  if (error) {
    return (
      <ScreenContainer>
        <ErrorView message={error} onRetry={load} />
      </ScreenContainer>
    );
  }

  return (
    <ScreenContainer>
      <View style={styles.header}>
        <Text style={styles.subjectName}>{subjectName}</Text>
        <ProgressBar percent={progress?.overallPercentComplete ?? 0} label="Overall progress" />
      </View>

      <FlatList
        data={topics ?? []}
        keyExtractor={(item) => item.id}
        contentContainerStyle={styles.list}
        renderItem={({ item }) => {
          const topicPercent =
            progress?.topics.find((t) => t.topicId === item.id)?.percentComplete ?? 0;
          return (
            <Pressable
              style={styles.topicRow}
              onPress={() => navigation.navigate('Swipe', { topicId: item.id, topicTitle: item.title })}
            >
              <Text style={styles.topicTitle}>{item.title}</Text>
              <ProgressBar percent={topicPercent} compact />
            </Pressable>
          );
        }}
      />
    </ScreenContainer>
  );
}

const styles = StyleSheet.create({
  header: { padding: theme.spacing(6), paddingBottom: theme.spacing(2) },
  subjectName: { ...theme.font.heading, color: theme.color.textPrimary, marginBottom: theme.spacing(3) },
  list: { paddingHorizontal: theme.spacing(6), paddingBottom: theme.spacing(6) },
  topicRow: {
    backgroundColor: theme.color.surface,
    borderRadius: theme.radius.md,
    borderWidth: 1,
    borderColor: theme.color.border,
    padding: theme.spacing(4),
    marginBottom: theme.spacing(3),
  },
  topicTitle: { ...theme.font.subheading, color: theme.color.textPrimary, marginBottom: theme.spacing(2) },
});
```

---

## `src/screens/SwipeScreen.tsx`

```tsx
import React, { useCallback, useEffect, useRef, useState } from 'react';
import { NativeStackScreenProps } from '@react-navigation/native-stack';
import { StyleSheet, Text, View } from 'react-native';
import Swiper from 'react-native-deck-swiper';
import ScreenContainer from '../components/ScreenContainer';
import LoadingView from '../components/LoadingView';
import ErrorView from '../components/ErrorView';
import CountdownRing from '../components/CountdownRing';
import DenseTextCard from '../components/cards/DenseTextCard';
import FastPacedCard from '../components/cards/FastPacedCard';
import ShortVideoCard from '../components/cards/ShortVideoCard';
import { theme } from '../theme/theme';
import { RootStackParamList } from '../navigation/types';
import { fetchSwipeCards, postSwipeEvent } from '../api/topics';
import { SwipeCard } from '../types';

type Props = NativeStackScreenProps<RootStackParamList, 'Swipe'>;

const AUTO_ADVANCE_MS = 5000;

export default function SwipeScreen({ route, navigation }: Props) {
  const { topicId, topicTitle } = route.params;
  const [cards, setCards] = useState<SwipeCard[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [cardIndex, setCardIndex] = useState(0);
  // Bumping deckKey remounts <Swiper>, which is how we "restart the deck"
  // after all three cards have been rejected.
  const [deckKey, setDeckKey] = useState(0);
  // react-native-deck-swiper ships no official TS types (see the ambient
  // declaration in src/types), so the ref is intentionally untyped here.
  const swiperRef = useRef<any>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchSwipeCards(topicId);
      setCards(data);
      setCardIndex(0);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Could not load study previews.');
    } finally {
      setLoading(false);
    }
  }, [topicId]);

  useEffect(() => {
    load();
  }, [load]);

  async function handleSwipeRight(card: SwipeCard) {
    postSwipeEvent(topicId, card.id, card.type, 'right').catch(() => {
      // Non-fatal for the prototype — don't block navigation on telemetry.
    });
    navigation.navigate('Content', { topicId, topicTitle, mode: card.type });
  }

  function handleAllSwipedLeft() {
    // Every mode was rejected — restart the deck instead of dead-ending
    // the flow, so the student can reconsider.
    setDeckKey((k) => k + 1);
    setCardIndex(0);
  }

  function renderCard(card: SwipeCard) {
    if (!card) return null;
    switch (card.type) {
      case 'dense':
        return <DenseTextCard card={card} />;
      case 'fast':
        return <FastPacedCard card={card} />;
      case 'short_video':
        return <ShortVideoCard card={card} />;
      default:
        return null;
    }
  }

  if (loading) {
    return (
      <ScreenContainer>
        <LoadingView label="Preparing your study modes…" />
      </ScreenContainer>
    );
  }
  if (error) {
    return (
      <ScreenContainer>
        <ErrorView message={error} onRetry={load} />
      </ScreenContainer>
    );
  }
  if (!cards || cards.length === 0) {
    return (
      <ScreenContainer>
        <ErrorView message="No study previews available for this topic yet." onRetry={load} />
      </ScreenContainer>
    );
  }

  const activeCard = cards[cardIndex];

  return (
    <ScreenContainer>
      <View style={styles.header}>
        <Text style={styles.title}>{topicTitle}</Text>
        <Text style={styles.subtitle}>Swipe right on how you want to study this topic</Text>
      </View>

      <View style={styles.deckArea}>
        {activeCard && (
          <CountdownRing
            key={`${deckKey}-${activeCard.id}`}
            durationMs={AUTO_ADVANCE_MS}
            active
            onComplete={() => swiperRef.current?.swipeLeft()}
          />
        )}

        <Swiper
          key={deckKey}
          ref={swiperRef}
          cards={cards}
          renderCard={renderCard}
          cardIndex={cardIndex}
          onSwipedLeft={(i: number) => setCardIndex((prev) => Math.min(prev + 1, cards.length - 1))}
          onSwipedRight={(i: number) => handleSwipeRight(cards[i])}
          onSwipedAll={handleAllSwipedLeft}
          backgroundColor="transparent"
          stackSize={3}
          verticalSwipe={false}
          disableBottomSwipe
          disableTopSwipe
        />
      </View>
    </ScreenContainer>
  );
}

const styles = StyleSheet.create({
  header: { paddingHorizontal: theme.spacing(6), paddingTop: theme.spacing(2) },
  title: { ...theme.font.heading, color: theme.color.textPrimary },
  subtitle: {
    ...theme.font.body,
    color: theme.color.textMuted,
    marginTop: theme.spacing(1),
    marginBottom: theme.spacing(4),
  },
  deckArea: { flex: 1, paddingBottom: theme.spacing(8) },
});
```

---

## `src/screens/ContentScreen.tsx`

```tsx
import React, { useCallback, useEffect, useState } from 'react';
import { NativeStackScreenProps } from '@react-navigation/native-stack';
import { FlatList, Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';
import { ResizeMode, Video } from 'expo-av';
import YoutubePlayer from 'react-native-youtube-iframe';
import ScreenContainer from '../components/ScreenContainer';
import LoadingView from '../components/LoadingView';
import ErrorView from '../components/ErrorView';
import { theme } from '../theme/theme';
import { RootStackParamList } from '../navigation/types';
import { fetchTopicContent } from '../api/topics';
import { markTopicComplete } from '../api/progress';
import { DenseContent, FastContent, ShortVideoContent, TopicContent } from '../types';

type Props = NativeStackScreenProps<RootStackParamList, 'Content'>;

export default function ContentScreen({ route, navigation }: Props) {
  const { topicId, topicTitle, mode } = route.params;
  const [content, setContent] = useState<TopicContent | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [completing, setCompleting] = useState(false);
  const [completed, setCompleted] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchTopicContent(topicId, mode);
      setContent(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Could not load this content.');
    } finally {
      setLoading(false);
    }
  }, [topicId, mode]);

  useEffect(() => {
    load();
  }, [load]);

  async function handleComplete() {
    setCompleting(true);
    try {
      await markTopicComplete(topicId, mode);
      setCompleted(true);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Could not save your progress.');
    } finally {
      setCompleting(false);
    }
  }

  return (
    // Panic Toggle intentionally hidden here: visible up until — not
    // during — the active learning/content-consumption flow.
    <ScreenContainer showPanicToggle={false}>
      <View style={styles.header}>
        <Pressable onPress={() => navigation.goBack()} hitSlop={12}>
          <Text style={styles.back}>{'\u2190'} Back</Text>
        </Pressable>
        <Text style={styles.title} numberOfLines={1}>
          {topicTitle}
        </Text>
      </View>

      {loading && <LoadingView label="Loading content…" />}
      {!loading && error && <ErrorView message={error} onRetry={load} />}

      {!loading && !error && content?.mode === 'dense' && <DenseContentView content={content} />}
      {!loading && !error && content?.mode === 'fast' && <FastContentView content={content} />}
      {!loading && !error && content?.mode === 'short_video' && (
        <ShortVideoContentView content={content} />
      )}

      {!loading && !error && content && (
        <View style={styles.footer}>
          <Pressable
            style={[styles.completeButton, completed && styles.completeButtonDone]}
            onPress={handleComplete}
            disabled={completing || completed}
          >
            <Text style={styles.completeLabel}>
              {completed ? 'Marked complete ✓' : completing ? 'Saving…' : 'Mark Complete'}
            </Text>
          </Pressable>
        </View>
      )}
    </ScreenContainer>
  );
}

function getYoutubeId(url: string): string {
  const match = url.match(/(?:v=|youtu\.be\/|embed\/)([\w-]{11})/);
  return match ? match[1] : url;
}

function DenseContentView({ content }: { content: DenseContent }) {
  return (
    <ScrollView contentContainerStyle={styles.body}>
      <Section title="Prerequisites">
        {content.prerequisites.map((p, i) => (
          <Text key={i} style={styles.listItem}>
            {'\u2022'} {p}
          </Text>
        ))}
      </Section>

      <Section title="Recommended textbooks">
        {content.textbooks.map((t, i) => (
          <Text key={i} style={styles.listItem}>
            {t.title} — {t.author}
          </Text>
        ))}
      </Section>

      <Section title="Notes">
        <Text style={styles.notes}>{content.notes}</Text>
      </Section>

      <Section title="Lecture video">
        <YoutubePlayer height={210} videoId={getYoutubeId(content.videoUrl)} />
      </Section>
    </ScrollView>
  );
}

function FastContentView({ content }: { content: FastContent }) {
  return (
    <ScrollView contentContainerStyle={styles.body}>
      <Section title="Key points">
        {content.bullets.map((b, i) => (
          <Text key={i} style={styles.listItem}>
            {'\u2022'} {b}
          </Text>
        ))}
      </Section>

      <Section title="Must-ask topics">
        <View style={styles.tagRow}>
          {content.mustAskTopics.map((t, i) => (
            <View key={i} style={styles.tag}>
              <Text style={styles.tagLabel}>{t}</Text>
            </View>
          ))}
        </View>
      </Section>

      <Section title="Quick video">
        <YoutubePlayer height={210} videoId={getYoutubeId(content.videoUrl)} />
      </Section>
    </ScrollView>
  );
}

function ShortVideoContentView({ content }: { content: ShortVideoContent }) {
  return (
    <FlatList
      data={content.videos}
      keyExtractor={(item) => item.id}
      pagingEnabled
      showsVerticalScrollIndicator={false}
      renderItem={({ item }) => (
        <View style={styles.shortSlide}>
          <Video
            source={{ uri: item.url }}
            style={StyleSheet.absoluteFillObject}
            resizeMode={ResizeMode.COVER}
            isLooping
            shouldPlay
            useNativeControls={false}
          />
          <View style={styles.shortCaptionWrap}>
            <Text style={styles.shortCaption}>{item.caption}</Text>
          </View>
        </View>
      )}
    />
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <View style={styles.section}>
      <Text style={styles.sectionTitle}>{title}</Text>
      {children}
    </View>
  );
}

const styles = StyleSheet.create({
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: theme.spacing(6),
    paddingBottom: theme.spacing(3),
  },
  back: { color: theme.color.accent, fontWeight: '600', marginRight: theme.spacing(4) },
  title: { ...theme.font.subheading, color: theme.color.textPrimary, flexShrink: 1 },
  body: { padding: theme.spacing(6), paddingBottom: theme.spacing(12) },
  section: { marginBottom: theme.spacing(6) },
  sectionTitle: { ...theme.font.subheading, color: theme.color.textPrimary, marginBottom: theme.spacing(2) },
  listItem: { ...theme.font.body, color: theme.color.textMuted, marginBottom: theme.spacing(1) },
  notes: { ...theme.font.body, color: theme.color.textMuted, lineHeight: 22 },
  tagRow: { flexDirection: 'row', flexWrap: 'wrap' },
  tag: {
    backgroundColor: theme.color.accentMuted,
    borderRadius: theme.radius.pill,
    paddingHorizontal: theme.spacing(3),
    paddingVertical: theme.spacing(1),
    marginRight: theme.spacing(2),
    marginBottom: theme.spacing(2),
  },
  tagLabel: { color: theme.color.accent, fontWeight: '600', fontSize: 12 },
  footer: { padding: theme.spacing(6) },
  completeButton: {
    backgroundColor: theme.color.accent,
    borderRadius: theme.radius.md,
    paddingVertical: theme.spacing(3),
    alignItems: 'center',
  },
  completeButtonDone: { backgroundColor: theme.color.success },
  completeLabel: { color: theme.color.background, fontWeight: '700' },
  shortSlide: {
    // Approximate one-screen height for the prototype. Swap for
    // Dimensions.get('window').height in production so it's exact on
    // every device.
    height: 640,
    justifyContent: 'flex-end',
    backgroundColor: '#000',
  },
  shortCaptionWrap: { padding: theme.spacing(6) },
  shortCaption: { color: '#fff', fontWeight: '600', fontSize: 15 },
});
```

---

## `App.tsx`

```tsx
import 'react-native-gesture-handler';
import React, { useEffect, useState } from 'react';
import { StatusBar } from 'expo-status-bar';
import RootNavigator from './src/navigation/RootNavigator';
import LoadingView from './src/components/LoadingView';
import { theme } from './src/theme/theme';
import { useAppStore, hydrateSessionFromSecureStore } from './src/store/useStore';
import { getCurrentUser } from './src/api/auth';
import { View, StyleSheet } from 'react-native';

export default function App() {
  const [hydrating, setHydrating] = useState(true);
  const setUser = useAppStore((s) => s.setUser);
  const clearSession = useAppStore((s) => s.clearSession);

  useEffect(() => {
    (async () => {
      const token = await hydrateSessionFromSecureStore();
      if (token) {
        try {
          const user = await getCurrentUser();
          setUser(user);
        } catch {
          // Persisted token is no longer valid — fall back to the auth
          // screen rather than getting stuck on a broken session.
          await clearSession();
        }
      }
      setHydrating(false);
    })();
  }, [setUser, clearSession]);

  if (hydrating) {
    return (
      <View style={styles.splash}>
        <LoadingView label="Getting things ready…" />
      </View>
    );
  }

  return (
    <>
      <StatusBar style="light" />
      <RootNavigator />
    </>
  );
}

const styles = StyleSheet.create({
  splash: { flex: 1, backgroundColor: theme.color.background },
});
```

---

