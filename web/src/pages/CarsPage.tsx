import { useState } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { getCars, createCar } from '../api'
import Spinner from '../components/Spinner'
import toast from 'react-hot-toast'
import type { Car } from '../types'

function AddCarModal({ onClose }: { onClose: () => void }) {
  const qc = useQueryClient()
  const [form, setForm] = useState({ plate_number: '', make: '', model: '', variant: '', colour: '', nickname: '' })
  const [saving, setSaving] = useState(false)

  function set(f: string) {
    return (e: React.ChangeEvent<HTMLInputElement>) => setForm((p) => ({ ...p, [f]: e.target.value }))
  }

  async function handleSave(e: React.FormEvent) {
    e.preventDefault()
    setSaving(true)
    try {
      await createCar(form)
      await qc.invalidateQueries({ queryKey: ['cars'] })
      toast.success('Car added!')
      onClose()
    } catch {
      toast.error('Failed to add car')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4">
      <div className="bg-surface rounded-2xl p-6 w-full max-w-sm">
        <h2 className="text-lg font-bold mb-4">Add car</h2>
        <form onSubmit={handleSave} className="flex flex-col gap-3">
          {(['plate_number', 'make', 'model', 'variant', 'colour', 'nickname'] as const).map((field) => (
            <input key={field} value={form[field]} onChange={set(field)} placeholder={field.replace('_', ' ')}
              required={field !== 'variant'}
              className="border border-gray-200 rounded-xl px-4 py-2 text-sm focus:outline-none focus:border-primary" />
          ))}
          <div className="flex gap-2 mt-2">
            <button type="button" onClick={onClose} className="flex-1 border border-gray-200 rounded-xl py-2 text-sm">Cancel</button>
            <button type="submit" disabled={saving}
              className="flex-1 bg-primary text-white rounded-xl py-2 text-sm flex items-center justify-center gap-1 disabled:opacity-60">
              {saving && <Spinner size="sm" />} Save
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default function CarsPage() {
  const { data: cars, isLoading } = useQuery<Car[]>({ queryKey: ['cars'], queryFn: () => getCars().then((r) => r.data) })
  const [showAdd, setShowAdd] = useState(false)

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">My Cars</h1>
        <button onClick={() => setShowAdd(true)} className="bg-primary text-white rounded-xl px-4 py-2 text-sm font-medium">+ Add car</button>
      </div>

      {isLoading ? (
        <div className="flex justify-center py-20"><Spinner size="lg" /></div>
      ) : !cars?.length ? (
        <div className="text-center py-20 text-text-secondary">
          <div className="text-5xl mb-4">🚗</div>
          <p>No cars yet — add your first one to get your QR code</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {cars.map((car) => (
            <Link key={car.uuid} to={`/cars/${car.uuid}`}
              className="bg-surface rounded-2xl shadow-sm p-5 flex gap-4 hover:shadow-md transition-shadow">
              <div className="w-4 h-4 rounded-full mt-1 flex-shrink-0" style={{ backgroundColor: car.colour.toLowerCase() }} />
              <div>
                <p className="font-semibold">{car.nickname}</p>
                <p className="text-text-secondary text-sm">{car.make} {car.model}</p>
                <p className="text-xs text-gray-400 mt-1">{car.plate_number}</p>
              </div>
            </Link>
          ))}
        </div>
      )}

      {showAdd && <AddCarModal onClose={() => setShowAdd(false)} />}
    </div>
  )
}
