import 'package:flutter/material.dart';

class CarDetailScreen extends StatelessWidget {
  final String uuid;
  const CarDetailScreen({required this.uuid, super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('CarDetailScreen')),
      body: const Center(child: Text('CarDetailScreen')),
    );
  }
}
