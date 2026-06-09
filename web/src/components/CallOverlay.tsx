import { useEffect, useRef, useState } from 'react'
import AgoraRTC, { IAgoraRTCClient, IMicrophoneAudioTrack } from 'agora-rtc-sdk-ng'
import { updateCallStatus } from '../api'

type Mode = 'outgoing' | 'active' | 'incoming'

interface Props {
  mode: Mode
  channelId: string
  token: string
  appId: string
  carNickname: string
  onClose: () => void
}

export default function CallOverlay({ mode: initialMode, channelId, token, appId, carNickname, onClose }: Props) {
  const [mode, setMode] = useState<Mode>(initialMode)
  const [muted, setMuted] = useState(false)
  const [seconds, setSeconds] = useState(0)
  const [micError, setMicError] = useState(false)
  const clientRef = useRef<IAgoraRTCClient | null>(null)
  const trackRef = useRef<IMicrophoneAudioTrack | null>(null)
  const timerRef = useRef<number | null>(null)

  async function joinChannel() {
    try {
      const client = AgoraRTC.createClient({ mode: 'rtc', codec: 'vp8' })
      clientRef.current = client
      await client.join(appId, channelId, token, null)
      const track = await AgoraRTC.createMicrophoneAudioTrack()
      trackRef.current = track
      await client.publish([track])
      setMode('active')
      timerRef.current = window.setInterval(() => setSeconds((s) => s + 1), 1000)
    } catch {
      setMicError(true)
    }
  }

  useEffect(() => {
    if (initialMode === 'outgoing' || initialMode === 'active') {
      joinChannel()
    }
    return () => {
      if (timerRef.current) clearInterval(timerRef.current)
      trackRef.current?.close()
      clientRef.current?.leave()
    }
  }, [])

  async function endCall() {
    if (timerRef.current) clearInterval(timerRef.current)
    trackRef.current?.close()
    await clientRef.current?.leave()
    await updateCallStatus(channelId, 'ended', seconds)
    onClose()
  }

  async function acceptCall() {
    await joinChannel()
  }

  async function declineCall() {
    await updateCallStatus(channelId, 'declined')
    onClose()
  }

  const duration = `${String(Math.floor(seconds / 60)).padStart(2, '0')}:${String(seconds % 60).padStart(2, '0')}`

  return (
    <div className="fixed inset-0 bg-gray-900 flex flex-col items-center justify-center z-50 text-white">
      <div className="text-6xl mb-4">🚗</div>
      <p className="text-xl font-bold mb-1">{carNickname}</p>

      {mode === 'outgoing' && <p className="text-gray-400 text-sm mb-8">Calling car owner...</p>}
      {mode === 'active' && <p className="text-gray-400 text-sm mb-8">{duration}</p>}
      {mode === 'incoming' && <p className="text-gray-400 text-sm mb-8">Visitor is calling about this car</p>}

      {micError && (
        <p className="text-red-400 text-sm mb-4">Microphone permission denied. Check browser settings.</p>
      )}

      {mode === 'active' && (
        <div className="flex gap-8 mb-8">
          <button onClick={() => {
            if (trackRef.current) {
              trackRef.current.setMuted(!muted)
              setMuted(!muted)
            }
          }} className="flex flex-col items-center gap-1">
            <div className="w-14 h-14 rounded-full bg-gray-700 flex items-center justify-center text-xl">
              {muted ? '🔇' : '🎙'}
            </div>
            <span className="text-xs text-gray-400">{muted ? 'Unmute' : 'Mute'}</span>
          </button>
          <button onClick={endCall} className="flex flex-col items-center gap-1">
            <div className="w-14 h-14 rounded-full bg-red-600 flex items-center justify-center text-2xl">📵</div>
            <span className="text-xs text-gray-400">End</span>
          </button>
        </div>
      )}

      {mode === 'outgoing' && (
        <button onClick={endCall} className="w-14 h-14 rounded-full bg-red-600 flex items-center justify-center text-2xl">📵</button>
      )}

      {mode === 'incoming' && (
        <div className="flex gap-8">
          <button onClick={declineCall} className="flex flex-col items-center gap-1">
            <div className="w-14 h-14 rounded-full bg-red-600 flex items-center justify-center text-2xl">📵</div>
            <span className="text-xs text-gray-400">Decline</span>
          </button>
          <button onClick={acceptCall} className="flex flex-col items-center gap-1">
            <div className="w-14 h-14 rounded-full bg-green-600 flex items-center justify-center text-2xl">📞</div>
            <span className="text-xs text-gray-400">Accept</span>
          </button>
        </div>
      )}
    </div>
  )
}
