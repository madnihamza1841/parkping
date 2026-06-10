import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:parkping/shared/widgets/loading_skeleton.dart';

void main() {
  group('LoadingSkeleton', () {
    testWidgets('renders shimmer placeholder', (tester) async {
      await tester.pumpWidget(const MaterialApp(
        home: Scaffold(body: LoadingSkeleton(height: 20, width: 100)),
      ));
      expect(find.byType(LoadingSkeleton), findsOneWidget);
    });

    testWidgets('CardSkeleton shows three placeholder bars', (tester) async {
      await tester.pumpWidget(const MaterialApp(
        home: Scaffold(body: CardSkeleton()),
      ));
      expect(find.byType(LoadingSkeleton), findsNWidgets(3));
    });
  });
}
