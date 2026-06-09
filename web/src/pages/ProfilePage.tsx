import { useState, useEffect, FormEvent } from 'react'
import { getProfile, updateProfile } from '../api'
import { useAuthStore } from '../store/authStore'
import Spinner from '../components/Spinner'
import toast from 'react-hot-toast'

export default function ProfilePage() {
  const { user, setUser } = useAuthStore()
  const [fullName, setFullName] = useState(user?.full_name || '')
  const [saving, setSaving] = useState(false)
  const [loading, setLoading] = useState(!user)

  useEffect(() => {
    if (!user) {
      getProfile().then((r) => { setUser(r.data); setFullName(r.data.full_name) }).finally(() => setLoading(false))
    }
  }, [user, setUser])

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setSaving(true)
    try {
      const { data } = await updateProfile({ full_name: fullName })
      setUser(data)
      toast.success('Profile updated')
    } catch {
      toast.error('Failed to update profile')
    } finally {
      setSaving(false)
    }
  }

  if (loading) return <div className="flex justify-center py-20"><Spinner size="lg" /></div>

  return (
    <div className="max-w-md mx-auto">
      <h1 className="text-2xl font-bold mb-6">Profile</h1>
      <div className="bg-surface rounded-2xl shadow-sm p-6 flex flex-col gap-4">
        <div className="flex items-center gap-4">
          <div className="w-16 h-16 bg-blue-50 rounded-full flex items-center justify-center text-2xl">👤</div>
          <div>
            <p className="font-semibold">{user?.full_name}</p>
            <p className="text-text-secondary text-sm">{user?.email}</p>
          </div>
        </div>
        <form onSubmit={handleSubmit} className="flex flex-col gap-3">
          <div>
            <label className="block text-sm font-medium text-text-secondary mb-1">Full name</label>
            <input
              value={fullName} onChange={(e) => setFullName(e.target.value)} required
              className="w-full border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-primary"
            />
          </div>
          <button
            type="submit" disabled={saving}
            className="bg-primary text-white rounded-xl py-3 font-semibold flex items-center justify-center gap-2 disabled:opacity-60"
          >
            {saving && <Spinner size="sm" />} Save changes
          </button>
        </form>
      </div>
    </div>
  )
}
