import api from './axios'

// Auth
export const register = (data: object) => api.post('/api/auth/register/', data)
export const login = (email: string, password: string) =>
  api.post('/api/auth/token/', { email, password })
export const refreshToken = (refresh: string) =>
  api.post('/api/auth/token/refresh/', { refresh })
export const getProfile = () => api.get('/api/auth/profile/')
export const updateProfile = (data: object) => api.patch('/api/auth/profile/', data)
export const uploadAvatar = (file: File) => {
  const form = new FormData()
  form.append('avatar', file)
  return api.post('/api/auth/profile/avatar/', form)
}

// Cars
export const getCars = () => api.get('/api/cars/')
export const createCar = (data: object) => api.post('/api/cars/', data)
export const getCar = (uuid: string) => api.get(`/api/cars/${uuid}/`)
export const updateCar = (uuid: string, data: object) => api.patch(`/api/cars/${uuid}/`, data)
export const deleteCar = (uuid: string) => api.delete(`/api/cars/${uuid}/`)
export const getCarQrUrl = (uuid: string) =>
  `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/api/cars/${uuid}/qr/`
export const getCarPdfUrl = (uuid: string) =>
  `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/api/cars/${uuid}/qr/pdf/`

// Scan (public)
export const scanCar = (carUuid: string) => api.get(`/api/scan/${carUuid}/`)

// Chat
export const startChat = (carUuid: string) => api.post(`/api/chat/start/${carUuid}/`)
export const getThreads = () => api.get('/api/chat/threads/')
export const getMessages = (threadId: string) =>
  api.get(`/api/chat/${threadId}/messages/`)
export const sendMessage = (threadId: string, content: string) =>
  api.post(`/api/chat/${threadId}/messages/`, { content })
export const blockUser = (threadId: string) => api.post(`/api/chat/${threadId}/block/`)
export const unblockUser = (threadId: string) => api.post(`/api/chat/${threadId}/unblock/`)

// Calls
export const requestCallToken = (carUuid: string) =>
  api.post(`/api/call/token/${carUuid}/`)
export const updateCallStatus = (channelId: string, status: string, durationSeconds?: number) =>
  api.post(`/api/call/status/${channelId}/`, { status, duration_seconds: durationSeconds })

// Notifications
export const registerDevice = (token: string, platform: string) =>
  api.post('/api/notifications/register-device/', { token, platform })
