import { useEffect, useRef, useState, FormEvent } from 'react'
import { useParams } from 'react-router-dom'
import { getMessages, getThreads, requestCallToken } from '../api'
import Spinner from '../components/Spinner'
import CallOverlay from '../components/CallOverlay'
import type { Message, CallToken } from '../types'

export default function ChatThreadPage() {
  const { threadId } = useParams<{ threadId: string }>()
  const [messages, setMessages] = useState<Message[]>([])
  const [loading, setLoading] = useState(true)
  const [input, setInput] = useState('')
  const [carUuid, setCarUuid] = useState<string | null>(null)
  const [carNickname, setCarNickname] = useState('')
  const [activeCall, setActiveCall] = useState<CallToken | null>(null)
  const [calling, setCalling] = useState(false)
  const wsRef = useRef<WebSocket | null>(null)
  const bottomRef = useRef<HTMLDivElement>(null)

  // Fetch thread metadata to get car UUID for calls
  useEffect(() => {
    getThreads().then((r) => {
      const thread = (r.data as Array<Record<string, string>>).find((t) => t.uuid === threadId)
      if (thread) {
        setCarUuid(thread.car_uuid ?? null)
        setCarNickname(thread.car_nickname ?? '')
      }
    }).catch(() => {})
  }, [threadId])

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
      const data = JSON.parse(e.data) as Message
      setMessages((prev) => [...prev, data])
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
    if (!carUuid) return
    setCalling(true)
    try {
      const { data } = await requestCallToken(carUuid)
      setActiveCall(data)
    } catch {
      // silently ignore — user will see no overlay
    } finally {
      setCalling(false)
    }
  }

  if (loading) return <div className="flex justify-center py-20"><Spinner size="lg" /></div>

  return (
    <>
      {activeCall && (
        <CallOverlay
          mode="outgoing"
          channelId={activeCall.channel_id}
          token={activeCall.token}
          appId={import.meta.env.VITE_AGORA_APP_ID ?? ''}
          carNickname={carNickname}
          onClose={() => setActiveCall(null)}
        />
      )}

      <div className="flex flex-col h-[calc(100vh-140px)]">
        {/* Header with call button */}
        <div className="flex items-center justify-between pb-3 border-b border-gray-100 mb-2">
          <p className="font-semibold text-text-primary">{carNickname || 'Chat'}</p>
          {carUuid && (
            <button
              onClick={handleCall}
              disabled={calling}
              className="flex items-center gap-1 text-primary text-sm font-medium disabled:opacity-50"
            >
              {calling ? <Spinner size="sm" /> : '📞'} Call
            </button>
          )}
        </div>

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
            placeholder="Type a message..."
            className="flex-1 border border-gray-200 rounded-xl px-4 py-2 text-sm focus:outline-none focus:border-primary"
          />
          <button type="submit" className="bg-primary text-white rounded-xl px-4 py-2 text-sm font-medium">Send</button>
        </form>
      </div>
    </>
  )
}
