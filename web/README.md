# ParkPing Web (React + Vite + TypeScript)

Anonymous parking QR contact app — web front-end.

## Setup

### Prerequisites
- Node.js 20+
- npm or pnpm

### Steps

```bash
cd web
cp .env.example .env
# Edit .env with your values

npm install
npm run dev
```

Runs on http://localhost:5173 by default.

### Environment Variables

| Variable | Description |
|----------|-------------|
| `VITE_API_BASE_URL` | Django backend URL (e.g. `http://localhost:8000`) |
| `VITE_AGORA_APP_ID` | Agora App ID for VoIP |
| `VITE_FIREBASE_*` | Firebase config for web push notifications |
| `VITE_FIREBASE_VAPID_KEY` | Firebase VAPID key for web push |

### Firebase Web Push

1. Create a Firebase project and enable Cloud Messaging.
2. Copy the web app config values into `.env`.
3. Generate a VAPID key in Project Settings → Cloud Messaging → Web configuration.
4. Place the generated `firebase-messaging-sw.js` in `public/`.

### Agora Web VoIP

Set `VITE_AGORA_APP_ID` in `.env`. Agora RTC is initialised in the call pages
using `agora-rtc-sdk-ng`. Browser microphone permission is requested on call start.

### Folder Structure

```
src/
  api/         — axios instance (JWT auto-attach, 401 refresh) + all API calls
  components/  — ProtectedRoute, NavLayout, Spinner, Skeleton, etc.
  pages/       — one file per route
  store/       — zustand auth store
  types/       — TypeScript interfaces (Car, Message, ChatThread, etc.)
```

### Key Route

`/scan/:uuid` is the most performance-critical route — it must load fast even on
cold mobile connections and works without JavaScript for the basic info display.
