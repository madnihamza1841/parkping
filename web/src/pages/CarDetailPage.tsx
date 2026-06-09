import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { getCar, deleteCar } from '../api'
import api from '../api/axios'
import Spinner from '../components/Spinner'
import toast from 'react-hot-toast'
import type { Car } from '../types'

// Fetch a binary resource with the JWT token and return a local blob URL
async function fetchAuthBlob(url: string): Promise<string> {
  const resp = await api.get(url, { responseType: 'blob' })
  return URL.createObjectURL(resp.data)
}

export default function CarDetailPage() {
  const { uuid } = useParams<{ uuid: string }>()
  const navigate = useNavigate()
  const qc = useQueryClient()

  const { data: car, isLoading } = useQuery<Car>({
    queryKey: ['car', uuid],
    queryFn: () => getCar(uuid!).then((r) => r.data),
    enabled: !!uuid,
  })

  // Fetch QR image as an authenticated blob → data URL for <img>
  const { data: qrBlobUrl, isLoading: qrLoading } = useQuery<string>({
    queryKey: ['car-qr', uuid],
    queryFn: () => fetchAuthBlob(`/api/cars/${uuid}/qr/`),
    enabled: !!uuid,
    staleTime: Infinity,   // QR won't change; no need to refetch
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

  async function handleDownloadPdf() {
    try {
      const blobUrl = await fetchAuthBlob(`/api/cars/${uuid}/qr/pdf/`)
      // Trigger browser download
      const a = document.createElement('a')
      a.href = blobUrl
      a.download = `${car?.plate_number ?? uuid}_qr.pdf`
      a.click()
      URL.revokeObjectURL(blobUrl)
    } catch {
      toast.error('Failed to download PDF')
    }
  }

  if (isLoading) return <div className="flex justify-center py-20"><Spinner size="lg" /></div>
  if (!car) return <p className="text-center py-20 text-text-secondary">Car not found.</p>

  return (
    <div className="max-w-md mx-auto">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">{car.nickname}</h1>
        <button onClick={handleDelete} className="text-red-500 text-sm hover:underline">Delete</button>
      </div>

      <div className="bg-surface rounded-2xl shadow-sm p-6 mb-4">
        {[
          ['Plate', car.plate_number],
          ['Make', car.make],
          ['Model', car.model],
          ...(car.variant ? [['Variant', car.variant]] : []),
          ['Colour', car.colour],
        ].map(([label, value]) => (
          <div key={label} className="flex justify-between py-2 border-b border-gray-50 last:border-0">
            <span className="text-text-secondary text-sm">{label}</span>
            <span className="text-sm font-medium">{value}</span>
          </div>
        ))}
      </div>

      <div className="bg-surface rounded-2xl shadow-sm p-6 mb-4 flex flex-col items-center gap-4">
        <p className="font-semibold">QR Code</p>

        {qrLoading ? (
          <div className="w-48 h-48 flex items-center justify-center">
            <Spinner size="md" />
          </div>
        ) : qrBlobUrl ? (
          <img
            src={qrBlobUrl}
            alt="QR code"
            className="w-48 h-48 rounded-xl"
          />
        ) : (
          <div className="w-48 h-48 bg-gray-50 rounded-xl flex items-center justify-center text-gray-400 text-sm">
            QR unavailable
          </div>
        )}

        <button
          onClick={handleDownloadPdf}
          className="w-full text-center bg-primary text-white rounded-xl py-3 font-semibold text-sm"
        >
          ⬇ Download PDF
        </button>
      </div>
    </div>
  )
}
