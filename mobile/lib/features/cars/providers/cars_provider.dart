import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/api/api_client.dart';

final carsProvider = FutureProvider<List<Map<String, dynamic>>>((ref) async {
  final resp = await ApiClient().dio.get('/api/cars/');
  return List<Map<String, dynamic>>.from(resp.data as List);
});
