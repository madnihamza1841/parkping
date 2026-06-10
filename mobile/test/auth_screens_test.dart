import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:parkping/core/api/api_client.dart';
import 'package:parkping/features/auth/screens/login_screen.dart';
import 'package:parkping/features/auth/screens/register_screen.dart';

Widget wrap(Widget child) =>
    ProviderScope(child: MaterialApp(home: child));

void main() {
  setUpAll(() {
    dotenv.testLoad(fileInput: 'API_BASE_URL=http://localhost:9\nAGORA_APP_ID=test');
    ApiClient().init();
  });

  group('LoginScreen', () {
    testWidgets('renders email, password fields and buttons', (tester) async {
      await tester.pumpWidget(wrap(const LoginScreen()));
      expect(find.text('ParkPing'), findsOneWidget);
      expect(find.byType(TextFormField), findsNWidgets(2));
      expect(find.widgetWithText(ElevatedButton, 'Login'), findsOneWidget);
      expect(find.text('No account? Register'), findsOneWidget);
    });

    testWidgets('rejects invalid email', (tester) async {
      await tester.pumpWidget(wrap(const LoginScreen()));
      await tester.enterText(find.byType(TextFormField).first, 'not-an-email');
      await tester.enterText(find.byType(TextFormField).last, 'password123');
      await tester.tap(find.widgetWithText(ElevatedButton, 'Login'));
      await tester.pump();
      expect(find.text('Enter a valid email'), findsOneWidget);
    });

    testWidgets('rejects short password', (tester) async {
      await tester.pumpWidget(wrap(const LoginScreen()));
      await tester.enterText(find.byType(TextFormField).first, 'a@b.com');
      await tester.enterText(find.byType(TextFormField).last, '123');
      await tester.tap(find.widgetWithText(ElevatedButton, 'Login'));
      await tester.pump();
      expect(find.text('Too short'), findsOneWidget);
    });

    testWidgets('password visibility toggle works', (tester) async {
      await tester.pumpWidget(wrap(const LoginScreen()));
      expect(find.byIcon(Icons.visibility), findsOneWidget);
      await tester.tap(find.byIcon(Icons.visibility));
      await tester.pump();
      expect(find.byIcon(Icons.visibility_off), findsOneWidget);
    });
  });

  group('RegisterScreen', () {
    testWidgets('renders all five fields', (tester) async {
      await tester.pumpWidget(wrap(const RegisterScreen()));
      expect(find.byType(TextFormField), findsNWidgets(5));
      expect(find.widgetWithText(ElevatedButton, 'Register'), findsOneWidget);
    });

    testWidgets('requires name, email and 8+ char password', (tester) async {
      await tester.pumpWidget(wrap(const RegisterScreen()));
      await tester.tap(find.widgetWithText(ElevatedButton, 'Register'));
      await tester.pump();
      expect(find.text('Required'), findsOneWidget);
      expect(find.text('Enter a valid email'), findsOneWidget);
      expect(find.text('Minimum 8 characters'), findsOneWidget);
    });

    testWidgets('keeps text while typing (no focus-loss regression)', (tester) async {
      await tester.pumpWidget(wrap(const RegisterScreen()));
      final nameField = find.byType(TextFormField).first;
      await tester.enterText(nameField, 'John Doe');
      await tester.pump();
      expect(find.text('John Doe'), findsOneWidget);
    });
  });
}
