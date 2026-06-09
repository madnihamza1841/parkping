import 'package:flutter/material.dart';
import 'package:shimmer/shimmer.dart';

class LoadingSkeleton extends StatelessWidget {
  final double height;
  final double? width;
  final double radius;

  const LoadingSkeleton({this.height = 16, this.width, this.radius = 8, super.key});

  @override
  Widget build(BuildContext context) {
    return Shimmer.fromColors(
      baseColor: Colors.grey[300]!,
      highlightColor: Colors.grey[100]!,
      child: Container(
        height: height,
        width: width ?? double.infinity,
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(radius),
        ),
      ),
    );
  }
}

class CardSkeleton extends StatelessWidget {
  const CardSkeleton({super.key});

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const LoadingSkeleton(height: 20, width: 200),
            const SizedBox(height: 8),
            const LoadingSkeleton(height: 14),
            const SizedBox(height: 4),
            const LoadingSkeleton(height: 14, width: 150),
          ],
        ),
      ),
    );
  }
}
