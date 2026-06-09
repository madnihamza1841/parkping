import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:qr_code_scanner/qr_code_scanner.dart';

class ScanScreen extends StatefulWidget {
  const ScanScreen({super.key});

  @override
  State<ScanScreen> createState() => _ScanScreenState();
}

class _ScanScreenState extends State<ScanScreen> {
  final GlobalKey _qrKey = GlobalKey(debugLabel: 'QR');
  QRViewController? _controller;
  bool _scanned = false;

  @override
  void dispose() {
    _controller?.dispose();
    super.dispose();
  }

  void _onQrViewCreated(QRViewController controller) {
    _controller = controller;
    controller.scannedDataStream.listen((scan) {
      if (_scanned || scan.code == null) return;
      final code = scan.code!;
      // Extract car UUID from parkping://scan/<uuid> or https://parkping.app/scan/<uuid>
      final match = RegExp(r'/scan/([0-9a-f-]{36})').firstMatch(code);
      if (match != null) {
        _scanned = true;
        _controller?.pauseCamera();
        context.push('/contact/${match.group(1)}');
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Scan QR')),
      body: Stack(
        children: [
          QRView(key: _qrKey, onQRViewCreated: _onQrViewCreated,
              overlay: QrScannerOverlayShape(
                borderColor: const Color(0xFF1A73E8),
                borderRadius: 12,
                borderLength: 40,
                borderWidth: 6,
                cutOutSize: 260,
              )),
          Positioned(bottom: 40, left: 0, right: 0,
            child: const Text('Point camera at a ParkPing QR code',
              textAlign: TextAlign.center,
              style: TextStyle(color: Colors.white, fontSize: 15))),
        ],
      ),
    );
  }
}
