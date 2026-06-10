import 'package:flutter/material.dart';
import '../../../core/api/api_client.dart';
import 'active_call_screen.dart';

class IncomingCallScreen extends StatelessWidget {
  final String channelId;
  final String token;
  final String appId;
  final String carNickname;

  const IncomingCallScreen({
    required this.channelId,
    required this.token,
    required this.appId,
    required this.carNickname,
    super.key,
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black,
      body: SafeArea(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.call_received, size: 72, color: Colors.white),
            const SizedBox(height: 16),
            const Text('Visitor is calling about', style: TextStyle(color: Colors.white70, fontSize: 16)),
            const SizedBox(height: 4),
            Text(carNickname, style: const TextStyle(color: Colors.white, fontSize: 24, fontWeight: FontWeight.bold)),
            const Spacer(),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                Column(children: [
                  FloatingActionButton(
                    heroTag: 'decline_call',
                    backgroundColor: Colors.red,
                    onPressed: () async {
                      await ApiClient().dio.post('/api/call/status/$channelId/', data: {'status': 'declined'});
                      if (context.mounted) Navigator.pop(context);
                    },
                    child: const Icon(Icons.call_end),
                  ),
                  const SizedBox(height: 8),
                  const Text('Decline', style: TextStyle(color: Colors.white70)),
                ]),
                Column(children: [
                  FloatingActionButton(
                    heroTag: 'accept_call',
                    backgroundColor: Colors.green,
                    onPressed: () => Navigator.pushReplacement(context, MaterialPageRoute(
                      builder: (_) => ActiveCallScreen(channelId: channelId, token: token, appId: appId, carNickname: carNickname),
                    )),
                    child: const Icon(Icons.call),
                  ),
                  const SizedBox(height: 8),
                  const Text('Accept', style: TextStyle(color: Colors.white70)),
                ]),
              ],
            ),
            const SizedBox(height: 60),
          ],
        ),
      ),
    );
  }
}
