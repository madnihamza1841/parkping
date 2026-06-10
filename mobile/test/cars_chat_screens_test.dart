import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:parkping/features/cars/providers/cars_provider.dart';
import 'package:parkping/features/cars/screens/cars_screen.dart';
import 'package:parkping/features/chat/screens/threads_screen.dart';

Widget wrapWithRouter(Widget child, {List<Override> overrides = const []}) {
  final router = GoRouter(routes: [
    GoRoute(path: '/', builder: (_, __) => child),
    GoRoute(path: '/cars/add', builder: (_, __) => const Scaffold(body: Text('add-car-route'))),
    GoRoute(path: '/cars/:uuid', builder: (_, __) => const Scaffold(body: Text('car-detail-route'))),
    GoRoute(path: '/chats/:id', builder: (_, __) => const Scaffold(body: Text('chat-route'))),
  ]);
  return ProviderScope(
    overrides: overrides,
    child: MaterialApp.router(routerConfig: router),
  );
}

void main() {
  group('CarsScreen', () {
    testWidgets('shows empty state when user has no cars', (tester) async {
      await tester.pumpWidget(wrapWithRouter(
        const CarsScreen(),
        overrides: [carsProvider.overrideWith((ref) async => [])],
      ));
      await tester.pumpAndSettle();
      expect(find.text('No cars yet — tap + to add your first'), findsOneWidget);
      expect(find.byType(FloatingActionButton), findsOneWidget);
    });

    testWidgets('renders car cards with nickname, make/model and plate', (tester) async {
      await tester.pumpWidget(wrapWithRouter(
        const CarsScreen(),
        overrides: [
          carsProvider.overrideWith((ref) async => [
                {
                  'uuid': 'abc-123',
                  'nickname': 'Blue Beast',
                  'make': 'BMW',
                  'model': 'M3',
                  'plate_number': 'TEST123',
                },
              ]),
        ],
      ));
      await tester.pumpAndSettle();
      expect(find.text('Blue Beast'), findsOneWidget);
      expect(find.text('BMW M3 · TEST123'), findsOneWidget);
    });

    testWidgets('shows error state when load fails', (tester) async {
      await tester.pumpWidget(wrapWithRouter(
        const CarsScreen(),
        overrides: [
          carsProvider.overrideWith((ref) async => throw Exception('network down')),
        ],
      ));
      await tester.pumpAndSettle();
      expect(find.textContaining('Error'), findsOneWidget);
    });

    testWidgets('FAB navigates to add car', (tester) async {
      await tester.pumpWidget(wrapWithRouter(
        const CarsScreen(),
        overrides: [carsProvider.overrideWith((ref) async => [])],
      ));
      await tester.pumpAndSettle();
      await tester.tap(find.byType(FloatingActionButton));
      await tester.pumpAndSettle();
      expect(find.text('add-car-route'), findsOneWidget);
    });
  });

  group('ThreadsScreen', () {
    testWidgets('shows empty state with no conversations', (tester) async {
      await tester.pumpWidget(wrapWithRouter(
        const ThreadsScreen(),
        overrides: [threadsProvider.overrideWith((ref) async => [])],
      ));
      await tester.pumpAndSettle();
      expect(find.text('No conversations yet'), findsOneWidget);
    });

    testWidgets('renders thread with car nickname and last message', (tester) async {
      await tester.pumpWidget(wrapWithRouter(
        const ThreadsScreen(),
        overrides: [
          threadsProvider.overrideWith((ref) async => [
                {
                  'uuid': 'thread-1',
                  'car_nickname': 'Red Rocket',
                  'last_message': {'content': 'Please move it', 'timestamp': '2026-06-10T10:00:00Z'},
                },
              ]),
        ],
      ));
      await tester.pumpAndSettle();
      expect(find.text('Red Rocket'), findsOneWidget);
      expect(find.text('Please move it'), findsOneWidget);
    });

    testWidgets('thread with no messages shows placeholder', (tester) async {
      await tester.pumpWidget(wrapWithRouter(
        const ThreadsScreen(),
        overrides: [
          threadsProvider.overrideWith((ref) async => [
                {'uuid': 'thread-2', 'car_nickname': 'Quiet Car', 'last_message': null},
              ]),
        ],
      ));
      await tester.pumpAndSettle();
      expect(find.text('No messages yet'), findsOneWidget);
    });
  });
}
