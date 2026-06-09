import 'package:flutter/material.dart';

class ChatScreen extends StatelessWidget {
  final String threadId;
  const ChatScreen({{required this.threadId, super.key}});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('ChatScreen')),
      body: const Center(child: Text('ChatScreen')),
    );
  }
}
