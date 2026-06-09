import { Outlet, NavLink, useNavigate } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'

export default function NavLayout() {
  const logout = useAuthStore((s) => s.logout)
  const navigate = useNavigate()

  const link = ({ isActive }: { isActive: boolean }) =>
    `px-3 py-2 rounded text-sm font-medium transition-colors ${isActive ? 'text-primary' : 'text-text-secondary hover:text-text-primary'}`

  return (
    <div className="min-h-screen flex flex-col">
      <nav className="bg-surface border-b border-gray-100 px-4 py-3 flex items-center justify-between sticky top-0 z-10">
        <NavLink to="/" className="font-bold text-primary text-lg">ParkPing</NavLink>
        <div className="flex gap-1">
          <NavLink to="/cars" className={link}>My Cars</NavLink>
          <NavLink to="/chat" className={link}>Chats</NavLink>
          <NavLink to="/profile" className={link}>Profile</NavLink>
          <button
            onClick={() => { logout(); navigate('/login') }}
            className="px-3 py-2 text-sm text-red-500 hover:text-red-700"
          >
            Logout
          </button>
        </div>
      </nav>
      <main className="flex-1 max-w-4xl mx-auto w-full px-4 py-6">
        <Outlet />
      </main>
    </div>
  )
}
