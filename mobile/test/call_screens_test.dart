import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:parkping/core/api/api_client.dart';
import 'package:parkping/features/call/screens/active_call_screen.dart';
import 'package:parkping/features/call/screens/incoming_call_screen.dart';

void main() {
  setUpAll(() {
    dotenv.testLoad(fileInput: 'API_BASE_URL=http://localhost:9\nAGORA_APP_ID=test');
    ApiClient().init();
  });

  group('ActiveCallScreen', () {
    Widget build() => const MaterialApp(
          home: ActiveCallScreen(
            channelId: 'chan123',
            token: 'tok123',
            appId: 'app123',
            carNickname: 'Test Car',
          ),
        );

    testWidgets('shows nickname, timer and call controls', (tester) async {
      await tester.pumpWidget(build());
      expect(find.text('Test Car'), findsOneWidget);
      expect(find.text('00:00'), findsOneWidget);
      expect(find.text('Mute'), findsOneWidget);
      expect(find.text('Speaker'), findsOneWidget);
      expect(find.byIcon(Icons.call_end), findsOneWidget);
      // Let the 1s periodic timer be disposed cleanly
      await tester.pumpWidget(const SizedBox());
    });

    testWidgets('timer ticks up', (tester) async {
      await tester.pumpWidget(build());
      await tester.pump(const Duration(seconds: 2));
      expect(find.text('00:02'), findsOneWidget);
      await tester.pumpWidget(const SizedBox());
    });

    testWidgets('mute toggles label', (tester) async {
      await tester.pumpWidget(build());
      await tester.tap(find.byIcon(Icons.mic));
      await tester.pump();
      expect(find.text('Unmute'), findsOneWidget);
      expect(find.byIcon(Icons.mic_off), findsOneWidget);
      await tester.pumpWidget(const SizedBox());
    });
  });

  group('IncomingCallScreen', () {
    testWidgets('shows caller context and accept/decline', (tester) async {
      await tester.pumpWidget(const MaterialApp(
        home: IncomingCallScreen(
          channelId: 'chan456',
          token: 'tok456',
          appId: 'app123',
          carNickname: 'My Audi',
        ),
      ));
      expect(find.text('Visitor is calling about'), findsOneWidget);
      expect(find.text('My Audi'), findsOneWidget);
      expect(find.text('Accept'), findsOneWidget);
      expect(find.text('Decline'), findsOneWidget);
      expect(find.byIcon(Icons.call), findsOneWidget);
      expect(find.byIcon(Icons.call_end), findsOneWidget);
    });

    testWidgets('accept navigates to active call', (tester) async {
      await tester.pumpWidget(const MaterialApp(
        home: IncomingCallScreen(
          channelId: 'chan456',
          token: 'tok456',
          appId: 'app123',
          carNickname: 'My Audi',
        ),
      ));
      await tester.tap(find.byIcon(Icons.call));
      await tester.pumpAndSettle();
      expect(find.byType(ActiveCallScreen), findsOneWidget);
      await tester.pumpWidget(const SizedBox());
    });
  });
}
