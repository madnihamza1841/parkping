import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../../core/api/api_client.dart';

class ContactScreen extends StatefulWidget {
  final String carUuid;
  const ContactScreen({required this.carUuid, super.key});

  @override
  State<ContactScreen> createState() => _ContactScreenState();
}

class _ContactScreenState extends State<ContactScreen> {
  Map<String, dynamic>? _car;
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    try {
      final resp = await ApiClient().dio.get('/api/scan/${widget.carUuid}/');
      setState(() { _car = resp.data as Map<String, dynamic>; _loading = false; });
    } catch (_) {
      setState(() => _loading = false);
    }
  }

  Future<void> _startChat() async {
    try {
      final resp = await ApiClient().dio.post('/api/chat/start/${widget.carUuid}/');
      final threadId = resp.data['uuid'];
      if (mounted) context.push('/chats/$threadId');
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Error: $e')));
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) return const Scaffold(body: Center(child: CircularProgressIndicator()));

    if (_car == null) {
      return Scaffold(
        appBar: AppBar(title: const Text('Car not found')),
        body: const Center(child: Text('This QR code is not recognised.')),
      );
    }

    final car = _car!;
    return Scaffold(
      appBar: AppBar(title: Text(car['nickname'] ?? 'Contact Owner')),
      body: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const Icon(Icons.directions_car, size: 72, color: Color(0xFF1A73E8)),
            const SizedBox(height: 16),
            Text(car['nickname'] ?? '', textAlign: TextAlign.center,
                style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold)),
            Text('${car['make']} ${car['model']}', textAlign: TextAlign.center,
                style: const TextStyle(color: Colors.grey)),
            const Spacer(),
            ElevatedButton.icon(
              onPressed: _startChat,
              icon: const Icon(Icons.message),
              label: const Text('Send Message'),
            ),
            const SizedBox(height: 12),
            OutlinedButton.icon(
              onPressed: () {
                // Call flow handled in PR 12
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('Calling — coming in PR 12')));
              },
              icon: const Icon(Icons.call),
              label: const Text('Call Owner'),
            ),
          ],
        ),
      ),
    );
  }
}
