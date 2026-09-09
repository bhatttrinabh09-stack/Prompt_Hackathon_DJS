# LearnSwipe — Detailed System Architecture

> **Study the way you think, not the way the syllabus was written.**

LearnSwipe is a context-aware learning platform that adapts educational content using two primary dimensions:

1. **Time available before the examination**
2. **Preferred learning mode for the current study session**

The MVP is scoped to:

```text
Branch    → AI & ML (AIML)
Semester  → 3
Subject   → Operating Systems
```

---

## Table of Contents

- [1. System Overview](#1-system-overview)
- [2. Architecture Principles](#2-architecture-principles)
- [3. High-Level Architecture](#3-high-level-architecture)
- [4. Frontend Architecture](#4-frontend-architecture)
- [5. Backend Architecture](#5-backend-architecture)
- [6. Dual-Axis Personalization](#6-dual-axis-personalization)
- [7. Panic Toggle Pipeline](#7-panic-toggle-pipeline)
- [8. Swipe-to-Learn Pipeline](#8-swipe-to-learn-pipeline)
- [9. Content Delivery Pipeline](#9-content-delivery-pipeline)
- [10. Database Architecture](#10-database-architecture)
- [11. Redis Architecture](#11-redis-architecture)
- [12. ML / AI Architecture](#12-ml--ai-architecture)
- [13. Fast Track Pipeline](#13-fast-track-pipeline)
- [14. Micro-Learn Pipeline](#14-micro-learn-pipeline)
- [15. Background Job Architecture](#15-background-job-architecture)
- [16. API Architecture](#16-api-architecture)
- [17. Authentication Flow](#17-authentication-flow)
- [18. End-to-End User Flow](#18-end-to-end-user-flow)
- [19. Object Storage](#19-object-storage)
- [20. Security](#20-security)
- [21. Deployment Architecture](#21-deployment-architecture)
- [22. Scalability](#22-scalability)
- [23. Observability](#23-observability)
- [24. MVP vs Future Architecture](#24-mvp-vs-future-architecture)
- [25. Recommended Repository Structure](#25-recommended-repository-structure)
- [26. Final Architecture](#26-final-architecture)

---

# 1. System Overview

The defining idea of LearnSwipe is:

```text
Time Available + Learning Preference
                ↓
        Content Selection
                ↓
     Personalized Learning
```

The system consists of five major layers:

```text
┌──────────────────────────────────────────────┐
│              PRESENTATION LAYER              │
│          React Native + Expo + TS            │
└─────────────────────────┬────────────────────┘
                          │
                          ▼
┌──────────────────────────────────────────────┐
│              APPLICATION LAYER               │
│             NestJS / Node.js API             │
└─────────────────────────┬────────────────────┘
                          │
            ┌─────────────┼─────────────┐
            ▼             ▼             ▼
       PostgreSQL       Redis        BullMQ
            │             │             │
            └─────────────┼─────────────┘
                          ▼
┌──────────────────────────────────────────────┐
│                AI / ML LAYER                 │
│              Python + FastAPI                │
└─────────────────────────┬────────────────────┘
                          │
             ┌────────────┼────────────┐
             ▼            ▼            ▼
            LLM          TTS       Video Engine
                          │
                          ▼
                    S3 / R2 Storage
```

---

# 2. Architecture Principles

## 2.1 Separation of Concerns

Each component has a clearly defined responsibility.

| Layer | Responsibility |
|---|---|
| Frontend | UI, navigation, gestures, content presentation |
| Backend | Authentication, business logic, content selection, progress |
| PostgreSQL | Persistent relational data |
| Redis | Content caching and queue infrastructure |
| ML Service | Topic analysis and AI content generation |
| Object Storage | Videos and large media assets |
| BullMQ | Asynchronous background processing |

The frontend should not contain the complete content-curation logic.

The backend remains the primary source of truth for content delivery and application state.

---

# 3. High-Level Architecture

```text
                         ┌───────────────────────┐
                         │     LEARNSWIPE APP    │
                         │                       │
                         │ React Native + Expo   │
                         │ TypeScript            │
                         └───────────┬───────────┘
                                     │
                              HTTPS / REST
                                     │
                                     ▼
                         ┌───────────────────────┐
                         │      NESTJS API       │
                         │                       │
                         │ Auth                  │
                         │ Users                 │
                         │ Catalog               │
                         │ Content               │
                         │ Sessions              │
                         │ Progress              │
                         │ Config                │
                         └───────────┬───────────┘
                                     │
              ┌──────────────────────┼──────────────────────┐
              │                      │                      │
              ▼                      ▼                      ▼
       ┌─────────────┐        ┌─────────────┐       ┌─────────────┐
       │ PostgreSQL  │        │    Redis    │       │   BullMQ    │
       │             │        │    Cache    │       │    Queue    │
       └─────────────┘        └─────────────┘       └──────┬──────┘
                                                           │
                                                           ▼
                                                ┌────────────────────┐
                                                │    ML SERVICE      │
                                                │   Python/FastAPI   │
                                                └─────────┬──────────┘
                                                          │
                                      ┌───────────────────┼──────────────────┐
                                      ▼                   ▼                  ▼
                                    LLM                  TTS             Remotion
                                      │                   │                  │
                                      └───────────────────┼──────────────────┘
                                                          ▼
                                                   ┌─────────────┐
                                                   │   S3 / R2   │
                                                   │   Storage   │
                                                   └─────────────┘
```

---

# 4. Frontend Architecture

## Technology Stack

```text
React Native
Expo
TypeScript
React Navigation
Zustand
TanStack React Query
Axios
React Native Reanimated
Expo Secure Store
AsyncStorage
```

## Responsibilities

The frontend handles:

- Branch selection
- Authentication
- Semester selection
- Subject selection
- Panic Toggle
- Swipe-to-Learn
- Content presentation
- Video playback
- Progress display
- Loading states
- Error states
- Empty states
- Locked content states

## Frontend Structure

```text
frontend/
├── App.tsx
└── src/
    ├── navigation/
    ├── screens/
    │   ├── Onboarding/
    │   ├── Home/
    │   ├── SwipeToLearn/
    │   └── ContentDelivery/
    ├── components/
    │   ├── PanicToggle/
    │   ├── ProgressBar.tsx
    │   └── common/
    ├── store/
    │   ├── useUserStore.ts
    │   ├── usePanicStore.ts
    │   └── useProgressStore.ts
    ├── api/
    │   ├── client.ts
    │   ├── auth.ts
    │   ├── content.ts
    │   └── progress.ts
    ├── hooks/
    ├── types/
    └── theme/
```

---

# 5. Backend Architecture

The backend is implemented as a modular NestJS application.

```text
backend/
└── src/
    ├── main.ts
    ├── app.module.ts
    │
    ├── auth/
    │   ├── auth.module.ts
    │   ├── auth.controller.ts
    │   ├── auth.service.ts
    │   └── strategies/
    │
    ├── users/
    │
    ├── catalog/
    │
    ├── content/
    │   ├── content.module.ts
    │   ├── content.controller.ts
    │   ├── content.service.ts
    │   └── content-filter.util.ts
    │
    ├── sessions/
    │
    ├── progress/
    │
    ├── config/
    │
    └── common/
```

## Backend Responsibilities

### Auth

- Signup
- Login
- JWT access tokens
- Refresh tokens
- Authentication guards

### Catalog

- Branches
- Semesters
- Subjects
- Active / locked states

### Content

- Content retrieval
- Mode filtering
- Urgency filtering
- Redis caching

### Progress

- Progress retrieval
- Progress updates
- Per-mode progress persistence

### Sessions

- Study-mode selection
- Urgency-tier recording
- Session tracking

### Config

- Server-driven urgency thresholds

---

# 6. Dual-Axis Personalization

LearnSwipe uses two independent inputs.

```text
                         USER
                          │
             ┌────────────┴────────────┐
             │                         │
             ▼                         ▼
       PANIC TOGGLE              SWIPE-TO-LEARN
             │                         │
             ▼                         ▼
       Time Remaining              Study Mode
             │                         │
             ▼                         ▼
       Urgency Tier              DEEP_FOCUS
             │                   FAST_TRACK
             │                   MICRO_LEARN
             │                         │
             └────────────┬────────────┘
                          ▼
                 CONTENT FILTER
                          │
                          ▼
                PERSONALIZED CONTENT
```

The final content selection can be represented as:

```text
User
+
Subject
+
Mode
+
Urgency Tier
```

Example:

```text
User:          Student A
Subject:       Operating Systems
Mode:          MICRO_LEARN
Urgency Tier:  SHORT

→ Short-form, high-density OS content
```

---

# 7. Panic Toggle Pipeline

The Panic Toggle is a global urgency filter.

```text
User enters time remaining
             │
             ▼
       Time in hours
             │
             ▼
       Tier Classifier
             │
       ┌─────┼─────┐
       ▼     ▼     ▼
      LONG MEDIUM SHORT
       │     │     │
       └─────┼─────┘
             ▼
      Global Content Filter
```

Current MVP rule:

```text
> 72 hours   → LONG
8–72 hours   → MEDIUM
< 8 hours    → SHORT
```

The thresholds should be served by:

```http
GET /config/urgency-tiers
```

rather than permanently hardcoded into the UI.

---

# 8. Swipe-to-Learn Pipeline

On entering a subject, the user sees three preview cards.

```text
                   SUBJECT
                      │
                      ▼
               SWIPE-TO-LEARN
                      │
        ┌─────────────┼─────────────┐
        ▼             ▼             ▼
    DEEP FOCUS     FAST TRACK    MICRO-LEARN
        │             │             │
     Preview        Preview       Preview
        │             │             │
        └─────────────┼─────────────┘
                      │
                 User Swipe
                      │
                ┌─────┴─────┐
                │           │
          Right Swipe    Left Swipe
                │           │
                ▼           ▼
          Select Mode      Skip
                │
                ▼
          POST /sessions
                │
                ▼
        Content Delivery
```

Each card has an approximately five-second preview.

---

# 9. Content Delivery Pipeline

The main content request is:

```http
GET /content?subjectId=&mode=&urgencyTier=
```

Flow:

```text
                         Client
                           │
                           ▼
                    Content Controller
                           │
                           ▼
                     Content Service
                           │
                           ▼
                      Redis Cache
                           │
                    ┌──────┴──────┐
                    │             │
                   HIT           MISS
                    │             │
                    ▼             ▼
                 Return      PostgreSQL
                                  │
                                  ▼
                             Cache Result
                                  │
                                  ▼
                                Return
```

The backend combines:

```text
Subject
+
Mode
+
Urgency Tier
```

Content tagged as `ANY` can be returned regardless of urgency.

---

# 10. Database Architecture

PostgreSQL is the primary application database.

## Entity Relationship

```text
                       ┌──────────────┐
                       │     User     │
                       └──────┬───────┘
                              │
                 ┌────────────┼────────────┐
                 │            │            │
                 ▼            ▼            ▼
          ┌────────────┐ ┌──────────────┐
          │  Progress  │ │ StudySession │
          └─────┬──────┘ └──────┬───────┘
                │               │
                └───────┬───────┘
                        ▼
                  ┌───────────┐
                  │  Subject  │
                  └─────┬─────┘
                        │
                        ▼
                 ┌──────────────┐
                 │ ContentItem  │
                 └──────────────┘
                        ▲
                        │
                  ┌─────┴─────┐
                  │ Semester  │
                  └───────────┘
```

---

## 10.1 Users

```text
users
────────────────────────
id
email
password_hash
branch
created_at
```

---

## 10.2 Semesters

```text
semesters
────────────────────────
id
number
is_active
```

MVP state:

```text
Semester 1  → LOCKED
Semester 2  → LOCKED
Semester 3  → ACTIVE
Semester 4  → LOCKED
Semester 5  → LOCKED
Semester 6  → LOCKED
Semester 7  → LOCKED
Semester 8  → LOCKED
```

---

## 10.3 Subjects

```text
subjects
────────────────────────
id
name
semester_id
is_active
```

MVP:

```text
Operating Systems → ACTIVE
```

---

## 10.4 Content Items

This is the central content table.

```text
content_items
────────────────────────────
id
subject_id
mode
urgency_tier
type
title
url
body_text
order_index
is_ai_generated
created_at
```

### Modes

```text
DEEP_FOCUS
FAST_TRACK
MICRO_LEARN
```

### Urgency Tiers

```text
LONG
MEDIUM
SHORT
ANY
```

### Content Types

```text
VIDEO
NOTES
FLASHCARD
TEXT
```

Example:

```text
┌─────────────────────────────┐
│ Paging in 60 Seconds        │
│                             │
│ Subject: Operating Systems  │
│ Mode: MICRO_LEARN           │
│ Urgency: SHORT              │
│ Type: VIDEO                 │
│ AI Generated: TRUE          │
└─────────────────────────────┘
```

---

# 11. Redis Architecture

Redis has two primary roles.

## 11.1 Content Cache

Cache key:

```text
content:{subjectId}:{mode}:{urgencyTier}
```

Example:

```text
content:os:MICRO_LEARN:SHORT
```

Flow:

```text
GET /content
      │
      ▼
    Redis
      │
 ┌────┴────┐
 │         │
HIT       MISS
 │         │
 ▼         ▼
Return   PostgreSQL
           │
           ▼
         Redis
           │
           ▼
         Return
```

---

## 11.2 Queue Infrastructure

Redis is also used by BullMQ:

```text
Backend
   │
   ▼
BullMQ
   │
   ▼
Redis
   │
   ▼
Worker
```

This allows long-running operations to happen asynchronously.

---

# 12. ML / AI Architecture

The ML service is a separate internal service.

```text
                  NestJS Backend
                        │
                        │ Internal API
                        ▼
               ┌──────────────────┐
               │   ML Service     │
               │ Python/FastAPI   │
               └────────┬─────────┘
                        │
          ┌─────────────┼─────────────┐
          ▼             ▼             ▼
         LLM            TTS       Video Engine
          │             │             │
          └─────────────┼─────────────┘
                        ▼
                    S3 / R2
```

The ML service should not be directly accessible by the mobile application.

---

# 13. Fast Track Pipeline

Fast Track can use a hybrid approach based on past-paper frequency analysis and LLM-assisted topic processing.

```text
Past Question Papers
          │
          ▼
OCR / Text Extraction
          │
          ▼
Question Segmentation
          │
          ▼
Topic Tagging
          │
          ▼
Frequency Aggregation
          │
          ▼
Raw Importance Score
          │
          ▼
LLM Re-ranking
          │
          ▼
Must-Ask Topics
          │
          ▼
Backend ContentItem
          │
          ▼
FAST_TRACK
```

For the MVP, manually curated topics can be used if past papers are not digitized in time.

---

# 14. Micro-Learn Pipeline

For the MVP, Micro-Learn videos should preferably be generated ahead of time.

```text
                 Syllabus Topic
                       │
                       ▼
                 LLM Script
                 Generation
                       │
                       ▼
                  45–60 sec
                    Script
                       │
                       ▼
                      TTS
                       │
                       ▼
                    Audio
                       │
                       ▼
                Video Assembly
                   Remotion
                       │
                       ▼
                  Captions
                   Whisper
                       │
                       ▼
                   Final MP4
                       │
                       ▼
                    S3 / R2
                       │
                       ▼
                 ContentItem
                       │
                       ▼
                 MICRO_LEARN
```

Pre-generation means the user does not have to wait for an entire AI video-generation pipeline during a study session.

---

# 15. Background Job Architecture

Long-running ML operations should be asynchronous.

```text
User / Admin
     │
     ▼
NestJS Backend
     │
     ▼
Create Job
     │
     ▼
BullMQ
     │
     ▼
Redis
     │
     ▼
ML Worker
     │
     ├── LLM
     ├── TTS
     ├── Video Rendering
     ├── Caption Generation
     └── Storage Upload
             │
             ▼
          S3 / R2
             │
             ▼
       Backend Ingestion
             │
             ▼
        ContentItem
```

Possible status endpoint:

```http
GET /content-items/:id/status
```

A future implementation can also use WebSockets for completion notifications.

---

# 16. API Architecture

## Authentication

```http
POST /auth/signup
POST /auth/login
POST /auth/refresh
```

## Catalog

```http
GET /catalog/branches
GET /catalog/semesters?branch=AIML
GET /catalog/subjects?semesterId=
```

## Content

```http
GET /content?subjectId=&mode=&urgencyTier=
```

## Sessions

```http
POST /sessions
```

Example:

```json
{
  "subjectId": "os",
  "mode": "FAST_TRACK",
  "urgencyTier": "SHORT"
}
```

## Progress

```http
GET /progress?subjectId=&mode=
PATCH /progress
```

## Configuration

```http
GET /config/urgency-tiers
```

---

# 17. Authentication Flow

```text
User
 │
 ▼
Signup / Login
 │
 ▼
NestJS Auth Controller
 │
 ▼
Auth Service
 │
 ▼
Credential Validation
 │
 ▼
JWT Generation
 │
 ├───────────────┐
 ▼               ▼
Access Token   Refresh Token
 │               │
 └───────┬───────┘
         ▼
   React Native
         │
         ▼
 Expo Secure Store
```

For authenticated requests:

```text
App
 │
 ▼
Access Token
 │
 ▼
NestJS
 │
 ▼
JWT Guard
 │
 ▼
Authenticated Request
```

---

# 18. End-to-End User Flow

Example:

> A student has 5 hours remaining and chooses Fast Track.

## Step 1 — Time Input

```text
Student enters:

5 hours
```

## Step 2 — Urgency Classification

```text
5 hours
   ↓
SHORT
```

## Step 3 — Mode Selection

The student right-swipes:

```text
FAST_TRACK
```

## Step 4 — Session Creation

```http
POST /sessions
```

```json
{
  "subjectId": "os",
  "mode": "FAST_TRACK",
  "urgencyTier": "SHORT"
}
```

## Step 5 — Content Request

```http
GET /content?subjectId=os&mode=FAST_TRACK&urgencyTier=SHORT
```

## Step 6 — Backend Processing

```text
NestJS
  ↓
Redis
  ↓
PostgreSQL if cache miss
  ↓
Return filtered content
```

## Step 7 — Content Display

```text
High-yield OS topics
Short revision material
Important topics
```

## Step 8 — Progress

```text
Content consumed
      ↓
Local progress update
      ↓
PATCH /progress
      ↓
PostgreSQL
```

---

# 19. Object Storage

Videos and large media assets should not be stored directly in PostgreSQL.

Use:

```text
AWS S3
or
Cloudflare R2
```

PostgreSQL stores metadata:

```text
ContentItem
    │
    └── url
```

The actual file lives in object storage:

```text
S3 / R2
│
├── micro-learn/
│   ├── paging.mp4
│   ├── deadlocks.mp4
│   └── scheduling.mp4
│
└── notes/
```

---

# 20. Security

## Authentication

Use:

```text
JWT Access Token
+
Refresh Token
```

## Password Security

Passwords must be stored as secure hashes.

Never store plaintext passwords.

## Rate Limiting

Authentication endpoints should be rate-limited to reduce brute-force attempts.

## Secrets

Store infrastructure credentials in environment variables:

```text
DATABASE_URL
REDIS_URL
JWT_SECRET
JWT_REFRESH_SECRET
S3_ACCESS_KEY
S3_SECRET_KEY
ML_SERVICE_URL
```

Never commit secrets to GitHub.

## ML Isolation

The ML service should be internal-only.

```text
Internet
   │
   X
   │
ML Service
   ▲
   │
Backend
```

The frontend should never communicate directly with the ML service.

---

# 21. Deployment Architecture

```text
                         INTERNET
                            │
                            ▼
                     ┌─────────────┐
                     │ Mobile App  │
                     └──────┬──────┘
                            │
                          HTTPS
                            │
                            ▼
                     ┌─────────────┐
                     │ API Layer   │
                     └──────┬──────┘
                            │
                            ▼
                     ┌─────────────┐
                     │ NestJS API  │
                     └──────┬──────┘
                            │
             ┌──────────────┼──────────────┐
             ▼              ▼              ▼
        PostgreSQL        Redis          BullMQ
                                           │
                                           ▼
                                     ML Worker
                                           │
                                           ▼
                                      FastAPI ML
                                           │
                            ┌──────────────┼──────────────┐
                            ▼              ▼              ▼
                           LLM            TTS          Remotion
                                                          │
                                                          ▼
                                                       S3 / R2
```

---

# 22. Scalability

## Backend

Multiple NestJS instances can run behind a load balancer.

```text
                  Load Balancer
                       │
             ┌─────────┼─────────┐
             ▼         ▼         ▼
          API #1    API #2    API #3
             │         │         │
             └─────────┼─────────┘
                       ▼
                  PostgreSQL
```

Redis provides shared cache state.

## ML

ML workers can scale independently:

```text
                  BullMQ
                    │
          ┌─────────┼─────────┐
          ▼         ▼         ▼
       Worker 1  Worker 2  Worker 3
          │         │         │
          └─────────┼─────────┘
                    ▼
                ML Service
```

This becomes important when generating content for multiple subjects.

---

# 23. Observability

The production system should eventually monitor:

```text
Application Logs
API Metrics
Database Metrics
Redis Metrics
Queue Metrics
ML Processing Metrics
Error Tracking
```

Important metrics include:

```text
API latency
Content-query latency
Redis cache hit rate
ML generation time
Queue wait time
Video generation failures
Authentication failures
```

---

# 24. MVP vs Future Architecture

## MVP

```text
React Native
      │
      ▼
NestJS
      │
      ├── PostgreSQL
      ├── Redis
      └── BullMQ
             │
             ▼
        Pre-generated
        ML Content
             │
             ▼
           S3 / R2
```

MVP should use:

- Rule-based urgency tiers
- Curated Operating Systems content
- Pre-generated Micro-Learn videos
- Manual Fast Track topic curation if required

---

## Future

```text
React Native
      │
      ▼
API Gateway
      │
      ▼
Backend Services
      │
      ▼
Personalization Engine
      │
      ▼
Recommendation System
      │
      ▼
ML Infrastructure
      │
      ▼
Real-time / On-demand Generation
```

Future personalization can incorporate:

```text
User history
Study speed
Completion rate
Topic difficulty
Past-paper frequency
Preferred content format
Time remaining
Performance
```

---

# 25. Recommended Repository Structure

A monorepo can eventually use:

```text
learnswipe/
│
├── frontend/
│   ├── src/
│   ├── App.tsx
│   └── package.json
│
├── backend/
│   ├── src/
│   ├── prisma/
│   └── package.json
│
├── ml-service/
│   ├── app/
│   ├── requirements.txt
│   └── Dockerfile
│
├── infrastructure/
│   ├── docker/
│   ├── deployment/
│   └── configs/
│
├── docs/
│   ├── architecture/
│   ├── api/
│   └── database/
│
└── README.md
```

Alternatively, frontend, backend, and ML can remain separate repositories.

---

# 26. Final Architecture

```text
                              USER
                               │
                               ▼
                    ┌─────────────────────┐
                    │   React Native App  │
                    └──────────┬──────────┘
                               │
             ┌─────────────────┴─────────────────┐
             │                                   │
             ▼                                   ▼
       PANIC TOGGLE                         SWIPE-TO-LEARN
             │                                   │
             ▼                                   ▼
       Time Remaining                         Study Mode
             │                                   │
             ▼                                   │
       Urgency Tier                              │
             │                                   │
             └─────────────────┬─────────────────┘
                               ▼
                       CONTENT REQUEST
                               │
                               ▼
                     ┌──────────────────┐
                     │   NestJS Backend │
                     └────────┬─────────┘
                              │
                   ┌──────────┼──────────┐
                   ▼          ▼          ▼
                Auth       Content    Progress
                              │
                              ▼
                     ┌────────────────┐
                     │ Content Filter │
                     └───────┬────────┘
                             │
                     ┌───────┴───────┐
                     ▼               ▼
                  Redis          PostgreSQL
                     │               │
                     └───────┬───────┘
                             ▼
                         CONTENT
                             │
                             ▼
                       React Native
                             │
                             ▼
                      Progress Update
                             │
                             ▼
                         PostgreSQL


        ───────────────── AI CONTENT PIPELINE ─────────────────

                   Past Papers / Syllabus
                            │
                ┌───────────┴───────────┐
                ▼                       ▼
          Fast Track                Micro-Learn
                │                       │
                ▼                       ▼
          Topic Analysis             LLM Script
                │                       │
                ▼                       ▼
          Topic Ranking                  TTS
                │                       │
                ▼                       ▼
        Important Topics             Video Render
                │                       │
                └──────────┬────────────┘
                           ▼
                     Python / FastAPI
                           │
                           ▼
                    Backend Ingestion
                           │
                           ▼
                       PostgreSQL
                           │
                           ▼
                         Redis
                           │
                           ▼
                      Mobile App
```

---

## Architecture Summary

The complete LearnSwipe system can be reduced to four core flows:

### Personalization

```text
Time Remaining
      +
Learning Mode
      ↓
Content Selection
```

### Content Delivery

```text
Frontend
   ↓
NestJS
   ↓
Redis / PostgreSQL
   ↓
Personalized Content
```

### AI Content Creation

```text
Syllabus / Past Papers
   ↓
Python ML Service
   ↓
LLM / TTS / Video Processing
   ↓
S3 / R2
   ↓
Backend
```

### Learning Persistence

```text
User
 ↓
Subject
 ↓
Mode
 ↓
Progress
```

The architecture keeps the **student-facing request path fast and predictable**, while computationally expensive AI operations are handled asynchronously or ahead of time.

---

## Related Documentation

- `FRONTEND_README.md` — Frontend implementation
- `BACKEND_README.md` — Backend implementation
- `ML_README.md` — ML / AI implementation
