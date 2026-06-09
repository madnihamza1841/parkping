import 'package:flutter/material.dart';
import 'package:connectivity_plus/connectivity_plus.dart';

class OfflineBanner extends StatelessWidget {
  final Widget child;
  const OfflineBanner({required this.child, super.key});

  @override
  Widget build(BuildContext context) {
    return StreamBuilder<List<ConnectivityResult>>(
      stream: Connectivity().onConnectivityChanged,
      builder: (context, snapshot) {
        final results = snapshot.data ?? [];
        final offline = results.isNotEmpty && results.every((r) => r == ConnectivityResult.none);
        return Column(
          children: [
            if (offline)
              Container(
                width: double.infinity,
                color: Colors.red,
                padding: const EdgeInsets.symmetric(vertical: 6),
                child: const Text(
                  'You\'re offline — messages will send when reconnected',
                  textAlign: TextAlign.center,
                  style: TextStyle(color: Colors.white, fontSize: 12),
                ),
              ),
            Expanded(child: child),
          ],
        );
      },
    );
  }
}
