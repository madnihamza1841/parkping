# ParkPing Mobile (Flutter)

Anonymous parking QR contact app — Flutter front-end.

## Setup

### Prerequisites
- Flutter 3.44+
- Dart 3.6+
- Android SDK 34+ with JDK 17 (or Xcode for iOS)

### Steps

```bash
cd mobile
cp .env.example .env
# Edit .env: set API_BASE_URL to your local backend (Android emulator: http://10.0.2.2:8000)

flutter pub get
flutter run
```

### Testing

```bash
flutter analyze         # static analysis — must report 0 issues
flutter test            # 26 widget tests: auth validation, cars/threads
                        # states, call screen controls, onboarding flow
flutter build apk --debug   # full Android build check
```

### Environment Variables

| Variable | Description |
|----------|-------------|
| `API_BASE_URL` | Django backend URL |
| `AGORA_APP_ID` | Agora App ID for VoIP calls |

### Firebase Setup

1. Add `google-services.json` (Android) to `android/app/`
2. Add `GoogleService-Info.plist` (iOS) to `ios/Runner/`
3. These files are in `.gitignore` — never commit them.

### Folder Structure

```
lib/
  core/
    api/         — Dio client with JWT auto-attach + auto-refresh on 401
    router/      — go_router with deep link handler (parkping://scan/<uuid>)
    theme/       — AppTheme (primary #1A73E8, Inter font, 12px radius)
    constants/   — AppConstants (app scheme, web base URL)
    shell/       — Bottom nav shell
  features/
    auth/        — Splash, Login, Register, Profile screens + Riverpod providers
    cars/        — My Cars, Add/Edit Car, Car Detail + QR screens
    chat/        — Thread list, Chat screen (WebSocket real-time)
    call/        — Outgoing, Active, Incoming call screens (Agora RTC)
    scan/        — QR Scanner screen, Contact screen
  shared/
    widgets/     — Reusable UI components
```

### Deep Links

The app handles `parkping://scan/<uuid>` deep links via the go_router.
On Android configure intent filters in `AndroidManifest.xml`; on iOS configure
URL types in `Info.plist`.
