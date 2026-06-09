import { Routes, Route } from 'react-router-dom'
import ProtectedRoute from './components/ProtectedRoute'
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

export default function App() {
  return (
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
  )
}
