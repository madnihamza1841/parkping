import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/api/api_client.dart';

class CarDetailScreen extends ConsumerStatefulWidget {
  final String uuid;
  const CarDetailScreen({required this.uuid, super.key});

  @override
  ConsumerState<CarDetailScreen> createState() => _CarDetailScreenState();
}

class _CarDetailScreenState extends ConsumerState<CarDetailScreen> {
  Map<String, dynamic>? _car;
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    try {
      final resp = await ApiClient().dio.get('/api/cars/${widget.uuid}/');
      setState(() { _car = resp.data as Map<String, dynamic>; _loading = false; });
    } catch (_) {
      setState(() => _loading = false);
    }
  }

  Future<void> _downloadPdf() async {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('PDF download triggered — open /api/cars/<uuid>/qr/pdf/ in browser')));
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) return const Scaffold(body: Center(child: CircularProgressIndicator()));
    if (_car == null) return const Scaffold(body: Center(child: Text('Car not found')));
    final car = _car!;
    return Scaffold(
      appBar: AppBar(title: Text(car['nickname'] ?? '')),
      body: ListView(
        padding: const EdgeInsets.all(24),
        children: [
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  _row('Plate', car['plate_number']),
                  _row('Make', car['make']),
                  _row('Model', car['model']),
                  if ((car['variant'] ?? '').isNotEmpty) _row('Variant', car['variant']),
                  _row('Colour', car['colour']),
                ],
              ),
            ),
          ),
          const SizedBox(height: 24),
          const Text('QR Code', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
          const SizedBox(height: 8),
          // QR displayed via network image from the backend
          Image.network(
            '${ApiClient().dio.options.baseUrl}/api/cars/${widget.uuid}/qr/',
            headers: {
              'Authorization': 'Bearer ${ApiClient().dio.options.headers['Authorization'] ?? ''}',
            },
            errorBuilder: (_, __, ___) => const Icon(Icons.qr_code, size: 120),
          ),
          const SizedBox(height: 16),
          ElevatedButton.icon(
            onPressed: _downloadPdf,
            icon: const Icon(Icons.download),
            label: const Text('Download PDF'),
          ),
        ],
      ),
    );
  }

  Widget _row(String label, String? value) => Padding(
    padding: const EdgeInsets.symmetric(vertical: 4),
    child: Row(children: [
      Text('$label: ', style: const TextStyle(fontWeight: FontWeight.bold)),
      Text(value ?? ''),
    ]),
  );
}
