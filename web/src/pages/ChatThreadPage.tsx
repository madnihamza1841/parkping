import { useEffect, useRef, useState, FormEvent } from 'react'
import { useParams } from 'react-router-dom'
import { getMessages, getThreads, requestCallToken, blockUser, unblockUser } from '../api'
import Spinner from '../components/Spinner'
import CallOverlay from '../components/CallOverlay'
import toast from 'react-hot-toast'
import type { Message, CallToken, ChatThread } from '../types'

export default function ChatThreadPage() {
  const { threadId } = useParams<{ threadId: string }>()
  const [messages, setMessages] = useState<Message[]>([])
  const [loading, setLoading] = useState(true)
  const [input, setInput] = useState('')
  const [thread, setThread] = useState<ChatThread | null>(null)
  const [activeCall, setActiveCall] = useState<CallToken | null>(null)
  const [calling, setCalling] = useState(false)
  const wsRef = useRef<WebSocket | null>(null)
  const bottomRef = useRef<HTMLDivElement>(null)

  async function refreshThread() {
    try {
      const r = await getThreads()
      const t = (r.data as ChatThread[]).find((x) => x.uuid === threadId)
      if (t) setThread(t)
    } catch { /* non-fatal */ }
  }

  useEffect(() => { refreshThread() }, [threadId])

  useEffect(() => {
    if (!threadId) return

    getMessages(threadId)
      .then((r) => setMessages(r.data))
      .finally(() => setLoading(false))

    const base = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000').replace(/^http/, 'ws')
    const token = localStorage.getItem('access_token')
    const ws = new WebSocket(`${base}/ws/chat/${threadId}/?token=${token}`)
    wsRef.current = ws

    ws.onmessage = (e) => {
      const data = JSON.parse(e.data)
      if (data.error === 'blocked') {
        toast.error('You cannot contact this user.')
        refreshThread()
        return
      }
      setMessages((prev) => [...prev, data as Message])
    }

    return () => ws.close()
  }, [threadId])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  function handleSend(e: FormEvent) {
    e.preventDefault()
    if (!input.trim() || !wsRef.current) return
    wsRef.current.send(JSON.stringify({ content: input.trim() }))
    setInput('')
  }

  async function handleCall() {
    if (!thread?.car_uuid) return
    setCalling(true)
    try {
      const { data } = await requestCallToken(thread.car_uuid)
      setActiveCall(data)
    } catch {
      toast.error('Could not start call.')
    } finally {
      setCalling(false)
    }
  }

  async function handleBlockToggle() {
    if (!threadId || !thread) return
    try {
      if (thread.blocked_by_me) {
        await unblockUser(threadId)
        toast.success('User unblocked')
      } else {
        if (!confirm('Block this user? They will no longer be able to message or call you.')) return
        await blockUser(threadId)
        toast.success('User blocked')
      }
      await refreshThread()
    } catch {
      toast.error('Action failed')
    }
  }

  if (loading) return <div className="flex justify-center py-20"><Spinner size="lg" /></div>

  const expiresIn = thread?.expires_at
    ? Math.max(0, Math.round((new Date(thread.expires_at).getTime() - Date.now()) / 3600000))
    : null

  return (
    <>
      {activeCall && (
        <CallOverlay
          mode="outgoing"
          channelId={activeCall.channel_id}
          token={activeCall.token}
          appId={import.meta.env.VITE_AGORA_APP_ID ?? ''}
          carNickname={thread?.car_nickname ?? ''}
          onClose={() => setActiveCall(null)}
        />
      )}

      <div className="flex flex-col h-[calc(100vh-140px)]">
        {/* Header */}
        <div className="flex items-center justify-between pb-3 border-b border-gray-100 mb-2">
          <div>
            <p className="font-semibold text-text-primary">{thread?.car_nickname || 'Chat'}</p>
            {expiresIn !== null && !thread?.is_blocked && (
              <p className="text-xs text-gray-400">Chat disappears in ~{expiresIn}h</p>
            )}
          </div>
          <div className="flex items-center gap-4">
            {thread?.car_uuid && !thread.is_blocked && (
              <button
                onClick={handleCall}
                disabled={calling}
                className="flex items-center gap-1 text-primary text-sm font-medium disabled:opacity-50"
              >
                {calling ? <Spinner size="sm" /> : '📞'} Call
              </button>
            )}
            <button
              onClick={handleBlockToggle}
              className={`text-sm font-medium ${thread?.blocked_by_me ? 'text-primary' : 'text-red-500'}`}
            >
              {thread?.blocked_by_me ? 'Unblock' : 'Block'}
            </button>
          </div>
        </div>

        {/* Blocked banner */}
        {thread?.is_blocked && (
          <div className="bg-red-50 text-red-600 text-sm text-center rounded-xl py-2 px-4 mb-2">
            {thread.blocked_by_me
              ? 'You blocked this user. Unblock to resume the conversation.'
              : 'You cannot contact this user.'}
          </div>
        )}

        <div className="flex-1 overflow-y-auto flex flex-col gap-2 pb-4">
          {messages.map((msg) => {
            if (msg.is_system) {
              return (
                <div key={msg.uuid} className="flex justify-center">
                  <span className="text-xs text-gray-400 bg-gray-100 rounded-full px-3 py-1">{msg.content}</span>
                </div>
              )
            }
            const isMe = msg.sender_label === 'Visitor' || msg.sender_label === 'You'
            return (
              <div key={msg.uuid} className={`flex ${isMe ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[70%] rounded-2xl px-4 py-2 ${isMe ? 'bg-primary text-white' : 'bg-white shadow-sm'}`}>
                  <p className={`text-xs mb-1 font-semibold ${isMe ? 'text-blue-100' : 'text-text-secondary'}`}>
                    {msg.sender_label}
                  </p>
                  <p className="text-sm">{msg.content}</p>
                  <p className={`text-xs mt-1 ${isMe ? 'text-blue-200' : 'text-gray-400'}`}>
                    {new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </p>
                </div>
              </div>
            )
          })}
          <div ref={bottomRef} />
        </div>

        <form onSubmit={handleSend} className="flex gap-2 pt-3 border-t border-gray-100">
          <input
            value={input} onChange={(e) => setInput(e.target.value)}
            placeholder={thread?.is_blocked ? 'Messaging unavailable' : 'Type a message...'}
            disabled={thread?.is_blocked}
            className="flex-1 border border-gray-200 rounded-xl px-4 py-2 text-sm focus:outline-none focus:border-primary disabled:bg-gray-50"
          />
          <button
            type="submit"
            disabled={thread?.is_blocked}
            className="bg-primary text-white rounded-xl px-4 py-2 text-sm font-medium disabled:opacity-50"
          >
            Send
          </button>
        </form>
      </div>
    </>
  )
}
