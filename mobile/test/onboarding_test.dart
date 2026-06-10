import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:parkping/features/auth/screens/onboarding_screen.dart';

void main() {
  setUp(() {
    SharedPreferences.setMockInitialValues({});
  });

  group('OnboardingScreen', () {
    testWidgets('shows first page with Scan a QR', (tester) async {
      await tester.pumpWidget(const MaterialApp(home: OnboardingScreen()));
      expect(find.text('Scan a QR'), findsOneWidget);
      expect(find.text('Next'), findsOneWidget);
    });

    testWidgets('swiping through pages reaches Get started', (tester) async {
      await tester.pumpWidget(const MaterialApp(home: OnboardingScreen()));

      await tester.tap(find.text('Next'));
      await tester.pumpAndSettle();
      expect(find.text('Chat Anonymously'), findsOneWidget);

      await tester.tap(find.text('Next'));
      await tester.pumpAndSettle();
      expect(find.text('Call Instantly'), findsOneWidget);
      expect(find.text('Get started'), findsOneWidget);
    });
  });
}
