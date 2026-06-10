import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:parkping/core/theme/app_theme.dart';

void main() {
  group('AppTheme', () {
    test('brand colours match spec', () {
      expect(AppTheme.primary, const Color(0xFF1A73E8));
      expect(AppTheme.background, const Color(0xFFF8F9FA));
      expect(AppTheme.surface, Colors.white);
      expect(AppTheme.textPrimary, const Color(0xFF1C1C1E));
      expect(AppTheme.radius, 12.0);
    });

    test('light theme uses Inter and material 3', () {
      final theme = AppTheme.light;
      expect(theme.useMaterial3, isTrue);
      expect(theme.scaffoldBackgroundColor, AppTheme.background);
    });

    test('elevated buttons are full-width with 12px radius', () {
      final style = AppTheme.light.elevatedButtonTheme.style!;
      final shape = style.shape!.resolve({}) as RoundedRectangleBorder;
      expect(shape.borderRadius, BorderRadius.circular(12));
      final size = style.minimumSize!.resolve({});
      expect(size!.height, 52);
    });
  });
}
