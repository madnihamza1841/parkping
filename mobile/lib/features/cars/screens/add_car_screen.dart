import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../core/api/api_client.dart';
import '../providers/cars_provider.dart';

class AddCarScreen extends ConsumerStatefulWidget {
  const AddCarScreen({super.key});

  @override
  ConsumerState<AddCarScreen> createState() => _AddCarScreenState();
}

class _AddCarScreenState extends ConsumerState<AddCarScreen> {
  final _form = GlobalKey<FormState>();
  final _plate = TextEditingController();
  final _make = TextEditingController();
  final _model = TextEditingController();
  final _variant = TextEditingController();
  final _colour = TextEditingController();
  final _nickname = TextEditingController();
  bool _saving = false;

  @override
  void dispose() {
    for (final c in [_plate, _make, _model, _variant, _colour, _nickname]) c.dispose();
    super.dispose();
  }

  Future<void> _save() async {
    if (!_form.currentState!.validate()) return;
    setState(() => _saving = true);
    try {
      await ApiClient().dio.post('/api/cars/', data: {
        'plate_number': _plate.text.trim(),
        'make': _make.text.trim(),
        'model': _model.text.trim(),
        'variant': _variant.text.trim(),
        'colour': _colour.text.trim(),
        'nickname': _nickname.text.trim(),
      });
      ref.invalidate(carsProvider);
      if (mounted) context.pop();
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Error: $e')));
      }
    } finally {
      if (mounted) setState(() => _saving = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Add Car')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Form(
          key: _form,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              for (final (ctrl, label, required) in [
                (_plate, 'Plate number', true),
                (_make, 'Make', true),
                (_model, 'Model', true),
                (_variant, 'Variant', false),
                (_colour, 'Colour', true),
                (_nickname, 'Nickname', true),
              ]) ...[
                TextFormField(
                  controller: ctrl,
                  decoration: InputDecoration(labelText: label),
                  validator: required ? (v) => v!.isNotEmpty ? null : 'Required' : null,
                ),
                const SizedBox(height: 16),
              ],
              ElevatedButton(
                onPressed: _saving ? null : _save,
                child: _saving ? const CircularProgressIndicator(color: Colors.white) : const Text('Save'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
