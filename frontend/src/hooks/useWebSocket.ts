import { useEffect, useRef, useState } from 'react'

export function useWebSocket(url: string | null, onMessage: (data: unknown) => void) {
  const [connected, setConnected] = useState(false)
  const onMessageRef = useRef(onMessage)

  useEffect(() => {
    onMessageRef.current = onMessage
  })

  useEffect(() => {
    if (!url) return

    const socket = new WebSocket(url)

    socket.onopen = () => setConnected(true)
    socket.onclose = () => setConnected(false)
    socket.onmessage = (event) => {
      onMessageRef.current(JSON.parse(event.data))
    }

    return () => {
      socket.close()
    }
  }, [url])

  return { connected }
}
