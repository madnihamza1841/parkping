import 'dart:async';
import 'package:flutter/material.dart';
import '../../../core/api/api_client.dart';

class ActiveCallScreen extends StatefulWidget {
  final String channelId;
  final String token;
  final String appId;
  final String carNickname;

  const ActiveCallScreen({
    required this.channelId,
    required this.token,
    required this.appId,
    required this.carNickname,
    super.key,
  });

  @override
  State<ActiveCallScreen> createState() => _ActiveCallScreenState();
}

class _ActiveCallScreenState extends State<ActiveCallScreen> {
  bool _muted = false;
  bool _speakerOn = false;
  int _seconds = 0;
  Timer? _timer;

  @override
  void initState() {
    super.initState();
    _timer = Timer.periodic(const Duration(seconds: 1), (_) {
      setState(() => _seconds++);
    });
    // NOTE: Agora join happens here when agora_rtc_engine is initialised.
    // The engine.joinChannel() call uses widget.appId, widget.channelId, widget.token.
  }

  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }

  String get _duration {
    final m = _seconds ~/ 60;
    final s = _seconds % 60;
    return '${m.toString().padLeft(2, '0')}:${s.toString().padLeft(2, '0')}';
  }

  Future<void> _endCall() async {
    _timer?.cancel();
    try {
      await ApiClient().dio.post('/api/call/status/${widget.channelId}/', data: {
        'status': 'ended',
        'duration_seconds': _seconds,
      });
    } catch (_) {}
    if (mounted) Navigator.pop(context);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black,
      body: SafeArea(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.person, size: 80, color: Colors.white),
            const SizedBox(height: 8),
            Text(widget.carNickname, style: const TextStyle(color: Colors.white, fontSize: 22, fontWeight: FontWeight.bold)),
            const SizedBox(height: 4),
            Text(_duration, style: const TextStyle(color: Colors.white70, fontSize: 18)),
            const Spacer(),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                _CallButton(
                  icon: _muted ? Icons.mic_off : Icons.mic,
                  label: _muted ? 'Unmute' : 'Mute',
                  onTap: () => setState(() => _muted = !_muted),
                ),
                FloatingActionButton(
                  backgroundColor: Colors.red,
                  onPressed: _endCall,
                  child: const Icon(Icons.call_end, size: 32),
                ),
                _CallButton(
                  icon: _speakerOn ? Icons.volume_up : Icons.volume_down,
                  label: 'Speaker',
                  onTap: () => setState(() => _speakerOn = !_speakerOn),
                ),
              ],
            ),
            const SizedBox(height: 48),
          ],
        ),
      ),
    );
  }
}

class _CallButton extends StatelessWidget {
  final IconData icon;
  final String label;
  final VoidCallback onTap;
  const _CallButton({required this.icon, required this.label, required this.onTap});

  @override
  Widget build(BuildContext context) => Column(
    children: [
      CircleAvatar(radius: 28, backgroundColor: Colors.white24, child: IconButton(icon: Icon(icon, color: Colors.white), onPressed: onTap)),
      const SizedBox(height: 4),
      Text(label, style: const TextStyle(color: Colors.white70, fontSize: 12)),
    ],
  );
}
