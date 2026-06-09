import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../core/api/api_client.dart';

final threadsProvider = FutureProvider<List<Map<String, dynamic>>>((ref) async {
  final resp = await ApiClient().dio.get('/api/chat/threads/');
  return List<Map<String, dynamic>>.from(resp.data as List);
});

class ThreadsScreen extends ConsumerWidget {
  const ThreadsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final threads = ref.watch(threadsProvider);
    return Scaffold(
      appBar: AppBar(title: const Text('Chats')),
      body: threads.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => Center(child: Text('Error: $e')),
        data: (list) => list.isEmpty
            ? const Center(child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(Icons.chat_bubble_outline, size: 64, color: Colors.grey),
                  SizedBox(height: 12),
                  Text('No conversations yet', style: TextStyle(color: Colors.grey)),
                ],
              ))
            : ListView.builder(
                itemCount: list.length,
                itemBuilder: (context, i) {
                  final t = list[i];
                  final last = t['last_message'] as Map<String, dynamic>?;
                  return ListTile(
                    leading: const Icon(Icons.directions_car),
                    title: Text(t['car_nickname'] ?? ''),
                    subtitle: Text(last?['content'] ?? 'No messages yet'),
                    trailing: const Icon(Icons.chevron_right),
                    onTap: () => context.push('/chats/${t['uuid']}'),
                  );
                },
              ),
      ),
    );
  }
}
