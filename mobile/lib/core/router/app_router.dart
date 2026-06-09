import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../features/auth/screens/splash_screen.dart';
import '../../features/auth/screens/login_screen.dart';
import '../../features/auth/screens/register_screen.dart';
import '../../features/auth/screens/profile_screen.dart';
import '../../features/cars/screens/cars_screen.dart';
import '../../features/cars/screens/add_car_screen.dart';
import '../../features/cars/screens/car_detail_screen.dart';
import '../../features/chat/screens/threads_screen.dart';
import '../../features/chat/screens/chat_screen.dart';
import '../../features/scan/screens/scan_screen.dart';
import '../../features/scan/screens/contact_screen.dart';
import '../shell/main_shell.dart';

final routerProvider = Provider<GoRouter>((ref) {
  return GoRouter(
    initialLocation: '/splash',
    routes: [
      GoRoute(path: '/splash', builder: (_, __) => const SplashScreen()),
      GoRoute(path: '/login', builder: (_, __) => const LoginScreen()),
      GoRoute(path: '/register', builder: (_, __) => const RegisterScreen()),
      ShellRoute(
        builder: (context, state, child) => MainShell(child: child),
        routes: [
          GoRoute(path: '/scan', builder: (_, __) => const ScanScreen()),
          GoRoute(path: '/cars', builder: (_, __) => const CarsScreen()),
          GoRoute(path: '/cars/add', builder: (_, __) => const AddCarScreen()),
          GoRoute(path: '/cars/:uuid', builder: (_, s) => CarDetailScreen(uuid: s.pathParameters['uuid']!)),
          GoRoute(path: '/chats', builder: (_, __) => const ThreadsScreen()),
          GoRoute(path: '/chats/:threadId', builder: (_, s) => ChatScreen(threadId: s.pathParameters['threadId']!)),
          GoRoute(path: '/profile', builder: (_, __) => const ProfileScreen()),
        ],
      ),
      // Deep link route for QR scan
      GoRoute(
        path: '/contact/:carUuid',
        builder: (_, s) => ContactScreen(carUuid: s.pathParameters['carUuid']!),
      ),
    ],
  );
});
