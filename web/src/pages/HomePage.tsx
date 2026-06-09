import { Link } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'

export default function HomePage() {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated)
  return (
    <div className="min-h-screen bg-background flex flex-col items-center justify-center p-8 text-center">
      <div className="text-6xl mb-4">🅿️</div>
      <h1 className="text-4xl font-bold text-primary mb-2">ParkPing</h1>
      <p className="text-text-secondary text-lg mb-8 max-w-md">
        Scan the QR code on a windshield to contact the car owner anonymously — no phone numbers, ever.
      </p>
      <div className="flex flex-col sm:flex-row gap-3">
        {isAuthenticated ? (
          <Link to="/cars" className="bg-primary text-white rounded-xl px-8 py-3 font-semibold">
            My Cars
          </Link>
        ) : (
          <>
            <Link to="/register" className="bg-primary text-white rounded-xl px-8 py-3 font-semibold">
              Get started free
            </Link>
            <Link to="/login" className="border border-gray-200 text-text-secondary rounded-xl px-8 py-3 text-sm">
              Login
            </Link>
          </>
        )}
      </div>
    </div>
  )
}
