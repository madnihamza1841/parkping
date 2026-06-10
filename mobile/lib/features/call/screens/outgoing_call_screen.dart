import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import '../../../core/api/api_client.dart';
import 'active_call_screen.dart';

class OutgoingCallScreen extends StatefulWidget {
  final String carUuid;
  final String carNickname;
  const OutgoingCallScreen({required this.carUuid, required this.carNickname, super.key});

  @override
  State<OutgoingCallScreen> createState() => _OutgoingCallScreenState();
}

class _OutgoingCallScreenState extends State<OutgoingCallScreen> {
  bool _loading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _startCall();
  }

  Future<void> _startCall() async {
    try {
      final resp = await ApiClient().dio.post('/api/call/token/${widget.carUuid}/');
      final channelId = resp.data['channel_id'] as String;
      final token = resp.data['token'] as String;
      final appId = resp.data['app_id'] as String? ?? dotenv.env['AGORA_APP_ID'] ?? '';
      if (mounted) {
        Navigator.pushReplacement(context, MaterialPageRoute(
          builder: (_) => ActiveCallScreen(channelId: channelId, token: token, appId: appId, carNickname: widget.carNickname),
        ));
      }
    } catch (e) {
      setState(() { _loading = false; _error = e.toString(); });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black,
      body: SafeArea(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.directions_car, size: 80, color: Colors.white),
            const SizedBox(height: 16),
            Text(widget.carNickname, style: const TextStyle(color: Colors.white, fontSize: 24, fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            if (_loading) ...[
              const Text('Calling car owner...', style: TextStyle(color: Colors.white70)),
              const SizedBox(height: 24),
              const CircularProgressIndicator(color: Colors.white),
            ],
            if (_error != null) Text(_error!, style: const TextStyle(color: Colors.red)),
            const Spacer(),
            FloatingActionButton(
              heroTag: 'cancel_outgoing_call',
              backgroundColor: Colors.red,
              onPressed: () => Navigator.pop(context),
              child: const Icon(Icons.call_end),
            ),
            const SizedBox(height: 40),
          ],
        ),
      ),
    );
  }
}
