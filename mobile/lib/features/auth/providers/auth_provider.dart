import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import '../../../core/api/api_client.dart';

class AuthState {
  final bool isAuthenticated;
  final bool isLoading;
  final String? error;
  final Map<String, dynamic>? user;

  const AuthState({
    this.isAuthenticated = false,
    this.isLoading = false,
    this.error,
    this.user,
  });

  AuthState copyWith({bool? isAuthenticated, bool? isLoading, String? error, Map<String, dynamic>? user}) =>
      AuthState(
        isAuthenticated: isAuthenticated ?? this.isAuthenticated,
        isLoading: isLoading ?? this.isLoading,
        error: error,
        user: user ?? this.user,
      );
}

class AuthNotifier extends StateNotifier<AuthState> {
  AuthNotifier() : super(const AuthState());

  final _storage = const FlutterSecureStorage();
  final _api = ApiClient().dio;

  Future<void> checkAuth() async {
    final token = await _storage.read(key: 'access_token');
    if (token == null) { state = const AuthState(isAuthenticated: false); return; }
    try {
      final resp = await _api.get('/api/auth/profile/');
      state = AuthState(isAuthenticated: true, user: resp.data as Map<String, dynamic>);
    } catch (_) {
      state = const AuthState(isAuthenticated: false);
    }
  }

  Future<bool> login(String email, String password) async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      final resp = await _api.post('/api/auth/token/', data: {'email': email, 'password': password});
      await _storage.write(key: 'access_token', value: resp.data['access']);
      await _storage.write(key: 'refresh_token', value: resp.data['refresh']);
      await checkAuth();
      return true;
    } catch (e) {
      state = state.copyWith(isLoading: false, error: 'Invalid credentials');
      return false;
    }
  }

  Future<bool> register(String email, String password, String fullName, String? dob, String? phone) async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      await _api.post('/api/auth/register/', data: {
        'email': email, 'password': password, 'full_name': fullName,
        if (dob != null) 'date_of_birth': dob,
        if (phone != null) 'phone_number': phone,
      });
      return await login(email, password);
    } catch (e) {
      state = state.copyWith(isLoading: false, error: 'Registration failed');
      return false;
    }
  }

  Future<void> logout() async {
    await _storage.deleteAll();
    state = const AuthState(isAuthenticated: false);
  }
}

final authProvider = StateNotifierProvider<AuthNotifier, AuthState>((ref) => AuthNotifier());
