import { useState, FormEvent } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { login, getProfile } from '../api'
import { useAuthStore } from '../store/authStore'
import Spinner from '../components/Spinner'
import toast from 'react-hot-toast'

export default function LoginPage() {
  const navigate = useNavigate()
  const [params] = useSearchParams()
  const next = params.get('next') || '/cars'
  const { login: storeLogin, setUser } = useAuthStore()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setError(null)
    setLoading(true)
    try {
      const { data } = await login(email, password)
      storeLogin(data.access, data.refresh)
      const profile = await getProfile()
      setUser(profile.data)
      navigate(next, { replace: true })
    } catch {
      setError('Invalid email or password.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-6">
      <div className="bg-surface rounded-2xl shadow-md max-w-sm w-full p-8">
        <h1 className="text-2xl font-bold text-text-primary mb-6 text-center">Login</h1>
        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <div>
            <label className="block text-sm font-medium text-text-secondary mb-1">Email</label>
            <input
              type="email" value={email} required
              onChange={(e) => setEmail(e.target.value)}
              className="w-full border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-primary"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-text-secondary mb-1">Password</label>
            <input
              type="password" value={password} required
              onChange={(e) => setPassword(e.target.value)}
              className="w-full border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-primary"
            />
          </div>
          {error && <p className="text-red-500 text-sm">{error}</p>}
          <button
            type="submit" disabled={loading}
            className="w-full bg-primary text-white rounded-xl py-3 font-semibold flex items-center justify-center gap-2 disabled:opacity-60"
          >
            {loading && <Spinner size="sm" />} Login
          </button>
        </form>
        <p className="text-center text-sm text-text-secondary mt-4">
          No account?{' '}
          <Link to={`/register${params.get('next') ? `?next=${params.get('next')}` : ''}`} className="text-primary">
            Register
          </Link>
        </p>
      </div>
    </div>
  )
}
