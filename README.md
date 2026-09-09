# LearnSwipe — Frontend Implementation Guide

## 1. Tech Stack Recommendation

| Layer | Choice | Why |
|---|---|---|
| Framework | **React Native (Expo)** | Single codebase for iOS/Android; fast prototyping; Expo handles native build complexity |
| Navigation | `@react-navigation/native` + `native-stack` | Standard, well-documented, supports nested stacks for Onboarding → Home → Subject → Session flows |
| State management | **Zustand** (or Redux Toolkit if team already knows Redux) | Lightweight global state for: panic-toggle status, selected mode, user session, progress cache |
| Swipe gestures | `react-native-deck-swiper` or `react-native-gesture-handler` + `react-native-reanimated` | Deck-swiper gives Tinder-style cards out of the box; gesture-handler+reanimated if you want custom physics |
| Video playback | `expo-av` (or `react-native-video`) | Needed for long-form lecture videos and Shorts-style micro-clips |
| Networking | `axios` + `@tanstack/react-query` | React Query gives you caching, retries, and background refetch for content pipelines — important since content lists change per mode/urgency |
| Auth | `expo-secure-store` for token storage + backend JWT | Keeps refresh/access tokens off plain AsyncStorage |
| Styling | `NativeWind` (Tailwind for RN) or `styled-components` | Fast iteration on card/toggle UI |
| Local persistence | `AsyncStorage` (for non-sensitive cache like last-selected subject) | Reduces network round-trips on app relaunch |

If you'd rather ship a **web-first prototype** instead of a mobile app, swap React Native for **React + Vite**, use `framer-motion` for swipe/drag gestures instead of deck-swiper, and use `react-router-dom` for navigation. Everything else below still applies conceptually.

---

## 2. Project Structure

```
learnswipe-app/
├── App.tsx
├── src/
│   ├── navigation/
│   │   ├── RootNavigator.tsx
│   │   └── types.ts
│   ├── screens/
│   │   ├── Onboarding/
│   │   │   ├── BranchSelectScreen.tsx
│   │   │   └── AuthScreen.tsx
│   │   ├── Home/
│   │   │   ├── SemesterSelectScreen.tsx
│   │   │   └── SubjectSelectScreen.tsx
│   │   ├── SwipeToLearn/
│   │   │   ├── SwipeDeckScreen.tsx
│   │   │   └── components/PreviewCard.tsx
│   │   └── ContentDelivery/
│   │       ├── DeepFocusScreen.tsx
│   │       ├── FastTrackScreen.tsx
│   │       └── MicroLearnScreen.tsx
│   ├── components/
│   │   ├── PanicToggle/
│   │   │   ├── PanicToggleBar.tsx
│   │   │   ├── PanicToggleModal.tsx
│   │   │   └── PanicToggleBadge.tsx  (collapsed state)
│   │   ├── ProgressBar.tsx
│   │   └── common/ (Button, Card, LoadingSpinner, etc.)
│   ├── store/
│   │   ├── useUserStore.ts
│   │   ├── usePanicStore.ts
│   │   └── useProgressStore.ts
│   ├── api/
│   │   ├── client.ts          (axios instance + interceptors)
│   │   ├── auth.ts
│   │   ├── content.ts
│   │   └── progress.ts
│   ├── hooks/
│   │   ├── useContentQuery.ts
│   │   └── usePanicFilter.ts
│   ├── types/
│   │   └── index.ts           (Card, Subject, Content, UrgencyTier, etc.)
│   └── theme/
│       └── tokens.ts
├── app.json
└── package.json
```

---

## 3. Core Feature Implementation

### 3.1 Panic Toggle (Global Urgency Filter)

**State shape (Zustand store):**
```ts
// store/usePanicStore.ts
import { create } from 'zustand';

type UrgencyTier = 'long' | 'medium' | 'short' | null;

interface PanicState {
  isActive: boolean;
  hoursRemaining: number | null;
  tier: UrgencyTier;
  setTimeRemaining: (hours: number) => void;
  reset: () => void;
}

const computeTier = (hours: number): UrgencyTier => {
  if (hours > 72) return 'long';      // > 3 days
  if (hours > 8) return 'medium';     // 8h–3d
  return 'short';                     // < 8h
};

export const usePanicStore = create<PanicState>((set) => ({
  isActive: false,
  hoursRemaining: null,
  tier: null,
  setTimeRemaining: (hours) =>
    set({ isActive: true, hoursRemaining: hours, tier: computeTier(hours) }),
  reset: () => set({ isActive: false, hoursRemaining: null, tier: null }),
}));
```

**UI behavior:**
- `PanicToggleBar` renders full-width at the top of every screen in the `Home` and `SwipeToLearn` stacks.
- On tap → opens `PanicToggleModal` with a segmented input (Days / Hours) and a numeric stepper.
- Once a session/content screen (`ContentDelivery/*`) mounts, swap `PanicToggleBar` for `PanicToggleBadge` (a small pill in the header) — use `navigation.setOptions({ headerRight: ... })` per screen, or a shared layout wrapper that reads current route name.
- Thresholds should NOT be hardcoded in the component — pull them from a config file or a backend-served config endpoint (`GET /config/urgency-tiers`) so product can tune them without an app release (see Open Question in the PRD about configurable tiers).

### 3.2 Swipe-to-Learn Deck

Use `react-native-deck-swiper`:
```tsx
// screens/SwipeToLearn/SwipeDeckScreen.tsx
import Swiper from 'react-native-deck-swiper';

const cards = [
  { id: 'deep_focus', title: 'Deep Focus', preview: <DenseTextPreview /> },
  { id: 'fast_track', title: 'Fast Track', preview: <FastPacedPreview /> },
  { id: 'micro_learn', title: 'Micro-Learn', preview: <ShortsPreview /> },
];

<Swiper
  cards={cards}
  renderCard={(card) => <PreviewCard card={card} autoAdvanceMs={5000} />}
  onSwipedRight={(index) => handleModeSelect(cards[index].id)}
  onSwipedLeft={(index) => advanceToNextCard()} // skip
  stackSize={3}
  backgroundColor="transparent"
/>
```
- `PreviewCard` should internally run a 5-second `setTimeout`/progress-ring animation (via `reanimated`) that auto-advances to the next card if the user takes no action — matches the PRD's "5-second preview" spec.
- On right-swipe, call `handleModeSelect(modeId)` which:
  1. Persists the choice via `POST /sessions` `{ subjectId, mode, urgencyTier }`.
  2. Navigates to the matching `ContentDelivery` screen.

### 3.3 Content Delivery Screens

Each of the three screens (`DeepFocusScreen`, `FastTrackScreen`, `MicroLearnScreen`) should be a **thin wrapper** around a shared `ContentList` or `ContentPlayer` component, differentiated only by the query params sent to the backend:

```ts
// hooks/useContentQuery.ts
export function useContent(subjectId: string, mode: Mode) {
  const { tier } = usePanicStore();
  return useQuery({
    queryKey: ['content', subjectId, mode, tier],
    queryFn: () => api.content.getContent({ subjectId, mode, urgencyTier: tier }),
  });
}
```
This is the key composition point where **Panic Toggle × Swipe Mode** intersect — both are just query params sent to one backend endpoint, keeping frontend logic dumb and backend logic smart (see Backend README §4.2).

### 3.4 Progress Bar & Persistence

- `ProgressBar` reads from `useProgressStore`, which is hydrated on screen mount via `GET /progress?subjectId=&mode=` and updated optimistically as the user scrolls/completes content items, then synced with `PATCH /progress` (debounced, e.g. every 5s or on screen blur) so you're not spamming the API on every scroll pixel.
- Keep progress **per (userId, subjectId, mode)** tuple client-side so switching modes doesn't clobber another mode's progress — mirrors the backend schema in the Backend README.

---

## 4. Screen-by-Screen Build Order (Suggested Sprint Plan)

1. Navigation shell + placeholder screens (get routing working end-to-end first)
2. Auth screen + branch selector (static AIML only)
3. Semester/Subject selectors (static, Sem 3 / OS only, others visually locked)
4. Panic Toggle bar + modal (local state only, no backend yet)
5. Swipe deck UI with the 3 static preview cards
6. Content delivery screens wired to **mocked/static JSON** content
7. Wire real backend endpoints in place of mocks
8. Progress bar + persistence
9. Polish: animations, locked-semester grayscale treatment, loading/error states

---

## 5. Key UX Details Not to Skip

- **Locked semesters/branches** (Sem 1–2, 4–8; non-AIML branches) should be visibly present but tapping them shows a "Coming soon" toast — this is explicitly called out in the PRD as "demo polish."
- **Panic Toggle reset** must be one tap and should immediately re-trigger the content query with `tier: null` (i.e., unfiltered).
- Handle the **empty state** where a mode + urgency combination has too little curated content (e.g., "Micro-Learn + Long runway" might have thin coverage in MVP) — show a friendly fallback rather than a blank screen.
