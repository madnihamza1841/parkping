import { useEffect, useState } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import { startChat, scanCar } from '../api'
import Spinner from '../components/Spinner'
import type { PublicCar } from '../types'

export default function ScanPage() {
  const { uuid } = useParams<{ uuid: string }>()
  const navigate = useNavigate()
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated)
  const [car, setCar] = useState<PublicCar | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [starting, setStarting] = useState(false)

  useEffect(() => {
    if (!uuid) return
    scanCar(uuid)
      .then((r) => setCar(r.data))
      .catch(() => setError('QR code not recognised.'))
      .finally(() => setLoading(false))
  }, [uuid])

  useEffect(() => {
    if (car) document.title = `Contact owner of ${car.nickname} — ParkPing`
  }, [car])

  async function handleMessage() {
    if (!uuid) return
    setStarting(true)
    try {
      const { data } = await startChat(uuid)
      navigate(`/chat/${data.uuid}`)
    } catch {
      setError('Could not start chat. Try again.')
    } finally {
      setStarting(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <Spinner size="lg" />
      </div>
    )
  }

  if (error || !car) {
    return (
      <div className="min-h-screen bg-background flex flex-col items-center justify-center gap-4 p-8">
        <p className="text-text-secondary text-lg">{error || 'Car not found.'}</p>
        <Link to="/" className="text-primary underline">Go home</Link>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background flex flex-col items-center justify-center p-6">
      <div className="bg-surface rounded-2xl shadow-md max-w-sm w-full p-8 flex flex-col items-center gap-4">
        <div className="w-20 h-20 bg-blue-50 rounded-full flex items-center justify-center text-4xl">🚗</div>

        <div className="text-center">
          <h1 className="text-2xl font-bold text-text-primary">{car.nickname}</h1>
          <p className="text-text-secondary">{car.make} {car.model}</p>
        </div>

        {isAuthenticated ? (
          <div className="w-full flex flex-col gap-3 mt-2">
            <button
              onClick={handleMessage}
              disabled={starting}
              className="w-full bg-primary text-white rounded-xl py-3 font-semibold flex items-center justify-center gap-2 disabled:opacity-60"
            >
              {starting ? <Spinner size="sm" /> : '💬'} Send Message
            </button>
            <button
              onClick={() => navigate(`/scan/${uuid}/call`)}
              className="w-full border border-primary text-primary rounded-xl py-3 font-semibold"
            >
              📞 Call Owner
            </button>
          </div>
        ) : (
          <div className="w-full flex flex-col gap-3 mt-2 text-center">
            <p className="text-text-secondary text-sm">
              To contact this car owner, create a free account — it takes 30 seconds.
            </p>
            <Link
              to={`/register?next=/scan/${uuid}`}
              className="w-full bg-primary text-white rounded-xl py-3 font-semibold block text-center"
            >
              Create free account
            </Link>
            <Link
              to={`/login?next=/scan/${uuid}`}
              className="w-full border border-gray-200 text-text-secondary rounded-xl py-3 text-sm block text-center"
            >
              Already have an account? Login
            </Link>
          </div>
        )}

        <p className="text-xs text-gray-400 mt-2 text-center">
          Owner's name, phone, and email are never shown.
        </p>
      </div>

      <footer className="mt-8 text-center text-xs text-gray-400">
        <a href="/" className="text-primary">ParkPing</a> — anonymous car contact
      </footer>
    </div>
  )
}
