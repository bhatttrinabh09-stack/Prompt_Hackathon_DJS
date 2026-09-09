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
