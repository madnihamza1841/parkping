import { Link } from 'react-router-dom'

export default function NotFoundPage() {
  return (
    <div className="min-h-screen bg-background flex flex-col items-center justify-center p-8 text-center">
      <div className="text-7xl mb-4">🅿️</div>
      <h1 className="text-5xl font-bold text-primary mb-2">404</h1>
      <p className="text-text-secondary text-lg mb-6">This page doesn't exist.</p>
      <Link to="/" className="bg-primary text-white rounded-xl px-8 py-3 font-semibold">Go home</Link>
    </div>
  )
}
