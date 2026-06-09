import 'package:flutter/material.dart';

class ContactScreen extends StatelessWidget {
  final String carUuid;
  const ContactScreen({{required this.carUuid, super.key}});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('ContactScreen')),
      body: const Center(child: Text('ContactScreen')),
    );
  }
}
