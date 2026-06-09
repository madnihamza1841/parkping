import { useEffect, useState } from 'react'
import { Routes, Route } from 'react-router-dom'
import ProtectedRoute from './components/ProtectedRoute'
import OfflineBanner from './components/OfflineBanner'
import CallOverlay from './components/CallOverlay'
import HomePage from './pages/HomePage'
import ScanPage from './pages/ScanPage'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import CarsPage from './pages/CarsPage'
import CarDetailPage from './pages/CarDetailPage'
import ChatListPage from './pages/ChatListPage'
import ChatThreadPage from './pages/ChatThreadPage'
import ProfilePage from './pages/ProfilePage'
import NotFoundPage from './pages/NotFoundPage'
import NavLayout from './components/NavLayout'
import { useAuthStore } from './store/authStore'
import { requestNotificationPermission, onForegroundMessage } from './api/firebase'
import { registerDevice } from './api'
import toast from 'react-hot-toast'

interface IncomingCall {
  channelId: string
  token: string
  carNickname: string
}

export default function App() {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated)
  const [incomingCall, setIncomingCall] = useState<IncomingCall | null>(null)

  // Register FCM device token once authenticated
  useEffect(() => {
    if (!isAuthenticated) return
    requestNotificationPermission().then((token) => {
      if (token) registerDevice(token, 'web').catch(() => {})
    })
  }, [isAuthenticated])

  // Handle foreground FCM messages
  useEffect(() => {
    const unsub = onForegroundMessage((payload) => {
      const data = payload.data ?? {}

      // Incoming call → show CallOverlay instead of a toast
      if (data.type === 'incoming_call' && data.channel_id && data.token) {
        setIncomingCall({
          channelId: data.channel_id,
          token: data.token,
          carNickname: data.car_nickname ?? 'your car',
        })
        return
      }

      // All other pushes (new message, scan notification) → toast
      const title = payload.notification?.title ?? 'ParkPing'
      const body = payload.notification?.body ?? ''
      toast(body ? `${title}: ${body}` : title, { icon: '🔔' })
    })
    return unsub
  }, [])

  const appId = import.meta.env.VITE_AGORA_APP_ID ?? ''

  return (
    <>
      <OfflineBanner />

      {/* Incoming call overlay — rendered on top of any route */}
      {incomingCall && (
        <CallOverlay
          mode="incoming"
          channelId={incomingCall.channelId}
          token={incomingCall.token}
          appId={appId}
          carNickname={incomingCall.carNickname}
          onClose={() => setIncomingCall(null)}
        />
      )}

      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/scan/:uuid" element={<ScanPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route element={<NavLayout />}>
          <Route path="/cars" element={<ProtectedRoute><CarsPage /></ProtectedRoute>} />
          <Route path="/cars/:uuid" element={<ProtectedRoute><CarDetailPage /></ProtectedRoute>} />
          <Route path="/chat" element={<ProtectedRoute><ChatListPage /></ProtectedRoute>} />
          <Route path="/chat/:threadId" element={<ProtectedRoute><ChatThreadPage /></ProtectedRoute>} />
          <Route path="/profile" element={<ProtectedRoute><ProfilePage /></ProtectedRoute>} />
        </Route>
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </>
  )
}
