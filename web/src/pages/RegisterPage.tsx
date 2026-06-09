import { useState, FormEvent } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { register, login, getProfile } from '../api'
import { useAuthStore } from '../store/authStore'
import Spinner from '../components/Spinner'

export default function RegisterPage() {
  const navigate = useNavigate()
  const [params] = useSearchParams()
  const next = params.get('next') || '/cars'
  const { login: storeLogin, setUser } = useAuthStore()

  const [fullName, setFullName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [dob, setDob] = useState('')
  const [phone, setPhone] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setError(null)
    setLoading(true)
    try {
      await register({
        full_name: fullName,
        email,
        password,
        ...(dob ? { date_of_birth: dob } : {}),
        ...(phone ? { phone_number: phone } : {}),
      })
      const { data } = await login(email, password)
      storeLogin(data.access, data.refresh)
      const profile = await getProfile()
      setUser(profile.data)
      navigate(next, { replace: true })
    } catch {
      setError('Registration failed. Email may already be in use.')
    } finally {
      setLoading(false)
    }
  }

  const inputCls = 'w-full border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-primary'
  const labelCls = 'block text-sm font-medium text-text-secondary mb-1'

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-6">
      <div className="bg-surface rounded-2xl shadow-md max-w-sm w-full p-8">
        <h1 className="text-2xl font-bold text-text-primary mb-6 text-center">Create account</h1>

        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <div>
            <label className={labelCls}>Full name</label>
            <input
              className={inputCls}
              type="text"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              required
              autoComplete="name"
            />
          </div>

          <div>
            <label className={labelCls}>Email</label>
            <input
              className={inputCls}
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              autoComplete="email"
            />
          </div>

          <div>
            <label className={labelCls}>Password</label>
            <input
              className={inputCls}
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              autoComplete="new-password"
              minLength={8}
            />
          </div>

          <div>
            <label className={labelCls}>Date of birth <span className="text-gray-400 font-normal">(optional)</span></label>
            <input
              className={inputCls}
              type="date"
              value={dob}
              onChange={(e) => setDob(e.target.value)}
            />
          </div>

          <div>
            <label className={labelCls}>Phone number <span className="text-gray-400 font-normal">(optional)</span></label>
            <input
              className={inputCls}
              type="tel"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              autoComplete="tel"
            />
          </div>

          {error && <p className="text-red-500 text-sm">{error}</p>}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-primary text-white rounded-xl py-3 font-semibold flex items-center justify-center gap-2 disabled:opacity-60"
          >
            {loading && <Spinner size="sm" />} Create account
          </button>
        </form>

        <p className="text-center text-sm text-text-secondary mt-4">
          Already have an account?{' '}
          <Link
            to={`/login${params.get('next') ? `?next=${params.get('next')}` : ''}`}
            className="text-primary"
          >
            Login
          </Link>
        </p>
      </div>
    </div>
  )
}
