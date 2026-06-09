# ParkPing

Anonymous parking QR contact app — scan a QR on a windshield to chat or call the car owner anonymously.

## Projects

| Directory | Stack | README |
|-----------|-------|--------|
| [`backend/`](backend/README.md) | Django REST Framework + Channels | [Setup](backend/README.md) |
| [`mobile/`](mobile/README.md) | Flutter | [Setup](mobile/README.md) |
| [`web/`](web/README.md) | React + Vite + TypeScript | [Setup](web/README.md) |

## How it works

1. Car owner registers, adds their car, downloads the QR code PDF, and sticks it on their windshield.
2. A passerby scans the QR → lands on the web app or mobile app.
3. The contact screen shows only the car's nickname, make, and model — no owner PII ever.
4. The visitor can send an anonymous text message or start an anonymous VoIP call.
5. Neither party ever sees the other's real name, phone number, or email.

## Architecture

```
Flutter app ──┐
              ├─▶ Django REST API (DRF + JWT)
React web  ──┘         │
                        ├─▶ PostgreSQL
                        ├─▶ Redis / Django Channels (WebSocket chat)
                        ├─▶ Agora RTC (anonymous VoIP)
                        └─▶ Firebase FCM (push notifications)
```
