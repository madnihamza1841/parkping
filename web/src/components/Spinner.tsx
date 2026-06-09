export default function Spinner({ size = 'md' }: { size?: 'sm' | 'md' | 'lg' }) {
  const cls = { sm: 'h-4 w-4', md: 'h-8 w-8', lg: 'h-16 w-16' }[size]
  return (
    <div className={`animate-spin rounded-full border-4 border-primary border-t-transparent ${cls}`} />
  )
}
