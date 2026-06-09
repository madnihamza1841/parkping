import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../providers/auth_provider.dart';

class RegisterScreen extends ConsumerStatefulWidget {
  const RegisterScreen({super.key});

  @override
  ConsumerState<RegisterScreen> createState() => _RegisterScreenState();
}

class _RegisterScreenState extends ConsumerState<RegisterScreen> {
  final _form = GlobalKey<FormState>();
  final _name = TextEditingController();
  final _email = TextEditingController();
  final _password = TextEditingController();
  final _dob = TextEditingController();
  final _phone = TextEditingController();

  @override
  void dispose() {
    for (final c in [_name, _email, _password, _dob, _phone]) { c.dispose(); }
    super.dispose();
  }

  Future<void> _submit() async {
    if (!_form.currentState!.validate()) return;
    final ok = await ref.read(authProvider.notifier).register(
      _email.text.trim(), _password.text, _name.text.trim(),
      _dob.text.isEmpty ? null : _dob.text,
      _phone.text.isEmpty ? null : _phone.text,
    );
    if (ok && mounted) context.go('/scan');
  }

  @override
  Widget build(BuildContext context) {
    final auth = ref.watch(authProvider);
    return Scaffold(
      appBar: AppBar(title: const Text('Create account')),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: Form(
            key: _form,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                TextFormField(controller: _name, decoration: const InputDecoration(labelText: 'Full name'),
                    validator: (v) => v!.isNotEmpty ? null : 'Required'),
                const SizedBox(height: 16),
                TextFormField(controller: _email, keyboardType: TextInputType.emailAddress,
                    decoration: const InputDecoration(labelText: 'Email'),
                    validator: (v) => v!.contains('@') ? null : 'Enter a valid email'),
                const SizedBox(height: 16),
                TextFormField(controller: _password, obscureText: true,
                    decoration: const InputDecoration(labelText: 'Password'),
                    validator: (v) => v!.length >= 8 ? null : 'Minimum 8 characters'),
                const SizedBox(height: 16),
                TextFormField(controller: _dob, decoration: const InputDecoration(labelText: 'Date of birth (optional, YYYY-MM-DD)')),
                const SizedBox(height: 16),
                TextFormField(controller: _phone, keyboardType: TextInputType.phone,
                    decoration: const InputDecoration(labelText: 'Phone (optional)')),
                if (auth.error != null) ...[
                  const SizedBox(height: 8),
                  Text(auth.error!, style: const TextStyle(color: Colors.red)),
                ],
                const SizedBox(height: 24),
                ElevatedButton(
                  onPressed: auth.isLoading ? null : _submit,
                  child: auth.isLoading ? const CircularProgressIndicator(color: Colors.white) : const Text('Register'),
                ),
                TextButton(onPressed: () => context.go('/login'), child: const Text('Already have an account? Login')),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
