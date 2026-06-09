import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { getCar, deleteCar, getCarQrUrl, getCarPdfUrl } from '../api'
import Spinner from '../components/Spinner'
import toast from 'react-hot-toast'
import type { Car } from '../types'

export default function CarDetailPage() {
  const { uuid } = useParams<{ uuid: string }>()
  const navigate = useNavigate()
  const qc = useQueryClient()
  const { data: car, isLoading } = useQuery<Car>({
    queryKey: ['car', uuid],
    queryFn: () => getCar(uuid!).then((r) => r.data),
    enabled: !!uuid,
  })

  async function handleDelete() {
    if (!uuid || !confirm('Delete this car? This cannot be undone.')) return
    try {
      await deleteCar(uuid)
      await qc.invalidateQueries({ queryKey: ['cars'] })
      toast.success('Car deleted')
      navigate('/cars')
    } catch {
      toast.error('Failed to delete car')
    }
  }

  if (isLoading) return <div className="flex justify-center py-20"><Spinner size="lg" /></div>
  if (!car) return <p className="text-center py-20 text-text-secondary">Car not found.</p>

  const token = localStorage.getItem('access_token')
  const qrUrl = getCarQrUrl(uuid!)
  const pdfUrl = getCarPdfUrl(uuid!)

  return (
    <div className="max-w-md mx-auto">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">{car.nickname}</h1>
        <button onClick={handleDelete} className="text-red-500 text-sm hover:underline">Delete</button>
      </div>

      <div className="bg-surface rounded-2xl shadow-sm p-6 mb-4">
        {[['Plate', car.plate_number], ['Make', car.make], ['Model', car.model],
          ...(car.variant ? [['Variant', car.variant]] : []),
          ['Colour', car.colour]].map(([label, value]) => (
          <div key={label} className="flex justify-between py-2 border-b border-gray-50 last:border-0">
            <span className="text-text-secondary text-sm">{label}</span>
            <span className="text-sm font-medium">{value}</span>
          </div>
        ))}
      </div>

      <div className="bg-surface rounded-2xl shadow-sm p-6 mb-4 flex flex-col items-center gap-4">
        <p className="font-semibold">QR Code</p>
        <img
          src={qrUrl}
          alt="QR code"
          className="w-48 h-48 rounded-xl"
          onError={(e) => { (e.target as HTMLImageElement).style.display = 'none' }}
        />
        <a
          href={pdfUrl}
          download
          className="w-full text-center bg-primary text-white rounded-xl py-3 font-semibold text-sm"
        >
          ⬇ Download PDF
        </a>
      </div>
    </div>
  )
}
