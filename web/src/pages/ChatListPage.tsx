import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { getThreads } from '../api'
import Spinner from '../components/Spinner'
import type { ChatThread } from '../types'

export default function ChatListPage() {
  const { data: threads, isLoading } = useQuery<ChatThread[]>({
    queryKey: ['threads'],
    queryFn: () => getThreads().then((r) => r.data),
    refetchInterval: 10_000,
  })

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Chats</h1>
      {isLoading ? (
        <div className="flex justify-center py-20"><Spinner size="lg" /></div>
      ) : !threads?.length ? (
        <div className="text-center py-20 text-text-secondary">
          <div className="text-5xl mb-4">💬</div>
          <p>No conversations yet</p>
          <p className="text-sm mt-1">Scan a QR code to start one</p>
        </div>
      ) : (
        <div className="flex flex-col gap-2">
          {threads.map((t) => (
            <Link key={t.uuid} to={`/chat/${t.uuid}`}
              className="bg-surface rounded-2xl shadow-sm p-4 flex gap-3 items-center hover:shadow-md transition-shadow">
              <div className="w-10 h-10 bg-blue-50 rounded-full flex items-center justify-center text-lg">🚗</div>
              <div className="flex-1 min-w-0">
                <p className="font-medium truncate">{t.car_nickname}</p>
                <p className="text-text-secondary text-sm truncate">{t.last_message?.content || 'No messages yet'}</p>
              </div>
              {t.last_message && (
                <p className="text-xs text-gray-400 flex-shrink-0">
                  {new Date(t.last_message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </p>
              )}
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}
