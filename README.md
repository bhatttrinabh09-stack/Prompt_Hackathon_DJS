# LearnSwipe — Backend Implementation Guide

## 1. Tech Stack Recommendation

| Layer | Choice | Why |
|---|---|---|
| Runtime/Framework | **Node.js + NestJS** (or FastAPI/Python if the ML service and backend should share a language) | NestJS gives you structured modules/controllers/services out of the box — good fit for a multi-domain app (auth, content, progress, config) |
| Database | **PostgreSQL** | Relational data (users, subjects, progress) with clear foreign keys; good fit for the per-(user, subject, mode) progress model |
| ORM | **Prisma** | Type-safe queries, easy migrations, pairs well with TypeScript on frontend too |
| Caching | **Redis** | Cache curated content lists per (subject, mode, urgencyTier) since these change infrequently but are read often |
| Auth | **JWT (access + refresh tokens)** via `@nestjs/jwt` + `passport-jwt` | Standard, stateless, works well with mobile clients |
| File/video storage | **S3-compatible bucket** (AWS S3 / Cloudflare R2) for any hosted video/notes assets | Cheap, scalable, CDN-friendly |
| Background jobs | **BullMQ (Redis-backed queue)** | For anything async — e.g., triggering the ML service to generate a Micro-Learn short-form video on demand |
| API style | **REST** (GraphQL is overkill for this MVP's query patterns) | The content-fetch pattern is simple filter-and-return; REST + query params is sufficient |

---

## 2. Project Structure

```
learnswipe-api/
├── src/
│   ├── main.ts
│   ├── app.module.ts
│   ├── auth/
│   │   ├── auth.module.ts
│   │   ├── auth.controller.ts
│   │   ├── auth.service.ts
│   │   └── strategies/jwt.strategy.ts
│   ├── users/
│   │   ├── users.module.ts
│   │   ├── users.controller.ts
│   │   └── users.service.ts
│   ├── catalog/                  (branches, semesters, subjects)
│   │   ├── catalog.module.ts
│   │   ├── catalog.controller.ts
│   │   └── catalog.service.ts
│   ├── content/
│   │   ├── content.module.ts
│   │   ├── content.controller.ts
│   │   ├── content.service.ts     ← core filtering logic lives here
│   │   └── content-filter.util.ts
│   ├── sessions/                 (records a user's swipe-mode choice)
│   │   ├── sessions.module.ts
│   │   ├── sessions.controller.ts
│   │   └── sessions.service.ts
│   ├── progress/
│   │   ├── progress.module.ts
│   │   ├── progress.controller.ts
│   │   └── progress.service.ts
│   ├── config/                   (serves tunable urgency-tier thresholds)
│   │   └── config.controller.ts
│   └── common/
│       ├── guards/jwt-auth.guard.ts
│       └── interceptors/
├── prisma/
│   ├── schema.prisma
│   └── migrations/
├── .env
└── package.json
```

---

## 3. Database Schema (Prisma)

```prisma
model User {
  id            String    @id @default(uuid())
  email         String    @unique
  passwordHash  String
  branch        String    // "AIML" for MVP
  createdAt     DateTime  @default(now())
  progress      Progress[]
  sessions      StudySession[]
}

model Semester {
  id        String    @id @default(uuid())
  number    Int       // 1–8
  isActive  Boolean   @default(false) // only Semester 3 = true in MVP
  subjects  Subject[]
}

model Subject {
  id          String    @id @default(uuid())
  name        String    // "Operating Systems"
  semesterId  String
  semester    Semester  @relation(fields: [semesterId], references: [id])
  isActive    Boolean   @default(false)
  contentItems ContentItem[]
}

model ContentItem {
  id          String   @id @default(uuid())
  subjectId   String
  subject     Subject  @relation(fields: [subjectId], references: [id])
  mode        Mode     // DEEP_FOCUS | FAST_TRACK | MICRO_LEARN
  urgencyTier UrgencyTier // LONG | MEDIUM | SHORT | ANY
  type        ContentType // VIDEO | NOTES | FLASHCARD | TEXT
  title       String
  url         String?     // S3 or YouTube link
  bodyText    String?     // for notes/flashcards
  orderIndex  Int         // sequencing within a mode/tier
  isAiGenerated Boolean   @default(false)
  createdAt   DateTime  @default(now())
}

model StudySession {
  id          String   @id @default(uuid())
  userId      String
  user        User     @relation(fields: [userId], references: [id])
  subjectId   String
  mode        Mode
  urgencyTier UrgencyTier?
  startedAt   DateTime @default(now())
}

model Progress {
  id          String   @id @default(uuid())
  userId      String
  user        User     @relation(fields: [userId], references: [id])
  subjectId   String
  mode        Mode
  completedItemIds String[]  // ContentItem ids consumed
  percentComplete  Float    @default(0)
  updatedAt   DateTime @updatedAt

  @@unique([userId, subjectId, mode])  // one progress row per (user, subject, mode)
}

enum Mode {
  DEEP_FOCUS
  FAST_TRACK
  MICRO_LEARN
}

enum UrgencyTier {
  LONG
  MEDIUM
  SHORT
  ANY
}

enum ContentType {
  VIDEO
  NOTES
  FLASHCARD
  TEXT
}
```

**Why `@@unique([userId, subjectId, mode])` on Progress:** this directly implements the PRD requirement that "switching modes doesn't erase prior progress" — each mode gets its own row, keyed per user+subject.

---

## 4. Core API Endpoints

### 4.1 Auth
```
POST /auth/signup       { email, password, branch }
POST /auth/login        { email, password } → { accessToken, refreshToken }
POST /auth/refresh      { refreshToken }
```

### 4.2 Content Delivery (the core differentiator lives here)
```
GET /content?subjectId=&mode=&urgencyTier=
```
**Service logic (`content.service.ts`):**
```ts
async getContent(subjectId: string, mode: Mode, urgencyTier?: UrgencyTier) {
  const cacheKey = `content:${subjectId}:${mode}:${urgencyTier ?? 'ANY'}`;
  const cached = await this.redis.get(cacheKey);
  if (cached) return JSON.parse(cached);

  const items = await this.prisma.contentItem.findMany({
    where: {
      subjectId,
      mode,
      OR: [
        { urgencyTier: urgencyTier ?? 'ANY' },
        { urgencyTier: 'ANY' }, // items valid regardless of urgency
      ],
    },
    orderBy: { orderIndex: 'asc' },
  });

  await this.redis.set(cacheKey, JSON.stringify(items), 'EX', 3600);
  return items;
}
```
This single function is where the PRD's "two features compose together" requirement is implemented: **mode** picks the content family, **urgencyTier** narrows it further. No branching logic needed on the frontend at all.

### 4.3 Catalog
```
GET /catalog/branches
GET /catalog/semesters?branch=AIML
GET /catalog/subjects?semesterId=
```
Return `isActive` flags so the frontend can render locked/unlocked states without separate endpoints.

### 4.4 Sessions
```
POST /sessions   { subjectId, mode, urgencyTier }
```
Fire-and-forget analytics + used to know "which mode is this user currently in" if they background/foreground the app.

### 4.5 Progress
```
GET   /progress?subjectId=&mode=
PATCH /progress   { subjectId, mode, completedItemId }
```
`PATCH` should be idempotent (adding an already-completed item id is a no-op) and recompute `percentComplete` server-side as `completedItemIds.length / totalItemsForModeAndTier`.

### 4.6 Config (for tunable urgency thresholds)
```
GET /config/urgency-tiers → { longMinHours: 72, mediumMinHours: 8 }
```
Lets you answer the PRD's open question ("should thresholds be configurable?") by making them server-driven from day one — change a DB row instead of shipping an app update.

---

## 5. Where the ML Service Plugs In

- **Fast Track "important/must-ask" topics:** exposed by ML as `GET /ml/important-topics?subjectId=` — backend calls this once and caches the result in `ContentItem` rows (batch job), rather than calling ML on every request.
- **Micro-Learn short-form video generation:** if generated on-demand (per the PRD's open question), the backend enqueues a BullMQ job (`generate-short-video`) that calls the ML service asynchronously, then notifies the client via polling (`GET /content-items/:id/status`) or a websocket event once the asset lands in S3.
- Keep the **ML service behind an internal-only API** (not exposed to the frontend directly) so you can swap models/providers without touching client code. See ML README §5 for the contract.

---

## 6. Non-Functional Notes

- **Rate limiting** on `/auth/*` (e.g., `@nestjs/throttler`) to prevent brute force.
- **Seed script** (`prisma/seed.ts`) should populate: 1 branch (AIML), 8 semesters (only #3 active), a handful of subjects (only OS active), and a realistic set of `ContentItem` rows across all 3 modes × 3 urgency tiers for OS — this is what makes the MVP demo believable.
- **Environment config**: keep DB URL, Redis URL, JWT secrets, S3 credentials in `.env`, never committed.
- **Testing**: prioritize integration tests on `content.service.ts`'s filter logic — it's the crux of the whole product.
