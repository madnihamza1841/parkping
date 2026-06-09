import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../providers/cars_provider.dart';

class CarsScreen extends ConsumerWidget {
  const CarsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final cars = ref.watch(carsProvider);
    return Scaffold(
      appBar: AppBar(title: const Text('My Cars')),
      floatingActionButton: FloatingActionButton(
        onPressed: () => context.push('/cars/add'),
        child: const Icon(Icons.add),
      ),
      body: cars.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => Center(child: Text('Error: $e')),
        data: (list) => list.isEmpty
            ? const Center(child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(Icons.directions_car, size: 64, color: Colors.grey),
                  SizedBox(height: 12),
                  Text('No cars yet — tap + to add your first', style: TextStyle(color: Colors.grey)),
                ],
              ))
            : ListView.builder(
                padding: const EdgeInsets.all(16),
                itemCount: list.length,
                itemBuilder: (context, i) {
                  final car = list[i];
                  return Card(
                    margin: const EdgeInsets.only(bottom: 12),
                    child: ListTile(
                      leading: const Icon(Icons.directions_car, color: Color(0xFF1A73E8)),
                      title: Text(car['nickname'] ?? ''),
                      subtitle: Text('${car['make']} ${car['model']} · ${car['plate_number']}'),
                      trailing: const Icon(Icons.chevron_right),
                      onTap: () => context.push('/cars/${car['uuid']}'),
                    ),
                  );
                },
              ),
      ),
    );
  }
}
