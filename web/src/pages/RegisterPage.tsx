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
  const [form, setForm] = useState({ full_name: '', email: '', password: '', date_of_birth: '', phone_number: '' })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  function set(field: string) {
    return (e: React.ChangeEvent<HTMLInputElement>) => setForm((f) => ({ ...f, [field]: e.target.value }))
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setError(null)
    setLoading(true)
    try {
      await register({
        full_name: form.full_name,
        email: form.email,
        password: form.password,
        ...(form.date_of_birth ? { date_of_birth: form.date_of_birth } : {}),
        ...(form.phone_number ? { phone_number: form.phone_number } : {}),
      })
      const { data } = await login(form.email, form.password)
      storeLogin(data.access, data.refresh)
      const profile = await getProfile()
      setUser(profile.data)
      navigate(next, { replace: true })
    } catch (err: unknown) {
      setError('Registration failed. Email may already be in use.')
    } finally {
      setLoading(false)
    }
  }

  const Field = ({ label, field, type = 'text', required = true }: { label: string; field: string; type?: string; required?: boolean }) => (
    <div>
      <label className="block text-sm font-medium text-text-secondary mb-1">{label}{!required && ' (optional)'}</label>
      <input
        type={type} value={(form as Record<string, string>)[field]}
        onChange={set(field)} required={required}
        className="w-full border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-primary"
      />
    </div>
  )

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-6">
      <div className="bg-surface rounded-2xl shadow-md max-w-sm w-full p-8">
        <h1 className="text-2xl font-bold text-text-primary mb-6 text-center">Create account</h1>
        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <Field label="Full name" field="full_name" />
          <Field label="Email" field="email" type="email" />
          <Field label="Password" field="password" type="password" />
          <Field label="Date of birth" field="date_of_birth" type="date" required={false} />
          <Field label="Phone number" field="phone_number" type="tel" required={false} />
          {error && <p className="text-red-500 text-sm">{error}</p>}
          <button
            type="submit" disabled={loading}
            className="w-full bg-primary text-white rounded-xl py-3 font-semibold flex items-center justify-center gap-2 disabled:opacity-60"
          >
            {loading && <Spinner size="sm" />} Create account
          </button>
        </form>
        <p className="text-center text-sm text-text-secondary mt-4">
          Already have an account?{' '}
          <Link to={`/login${params.get('next') ? `?next=${params.get('next')}` : ''}`} className="text-primary">Login</Link>
        </p>
      </div>
    </div>
  )
}
