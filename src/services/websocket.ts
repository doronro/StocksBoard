import type { Quote, Order } from '@types'

type MessageHandler<T> = (data: T) => void
type ConnectionHandler = () => void

interface WebSocketMessage {
  type: 'quote' | 'order' | 'trade' | 'error' | 'authenticate' | 'auth_failed' | 'auth_success'
  data: any
  timestamp: number
}

class WebSocketManager {
  private ws: WebSocket | null = null
  private url: string
  private reconnectAttempts: number = 0
  private maxReconnectAttempts: number = 10
  private reconnectDelay: number = 1000
  private subscriptions: Map<string, Set<MessageHandler<any>>> = new Map()
  private connectionHandlers: Set<ConnectionHandler> = new Set()
  private disconnectionHandlers: Set<ConnectionHandler> = new Set()
  private isManualClose: boolean = false
  private authToken: string | null = null
  private isAuthenticating: boolean = false
  private messageRateLimiter = {
    lastMessageTime: 0,
    messageCount: 0,
    resetTime: Date.now(),
    maxMessagesPerSecond: 10
  }
  private reconnectingHandlers: Set<(info: { attempt: number; nextAttemptIn: number }) => void> = new Set()
  private connectionFailedHandlers: Set<(error: { message: string; severity: string }) => void> = new Set()

  constructor(url?: string) {
    this.url =
      url || `${process.env.VITE_WS_URL || 'ws://localhost:3001/ws'}`
  }

  connect(token?: string): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        this.isManualClose = false
        if (token) {
          this.authToken = token
        }

        // Include token in query parameters (will be validated on backend)
        const wsUrl = this.authToken
          ? `${this.url}?token=${encodeURIComponent(this.authToken)}`
          : this.url

        this.ws = new WebSocket(wsUrl)

        this.ws.onopen = () => {
          console.log('[WebSocket] Connected')
          this.isAuthenticating = true

          // Send authentication message immediately if we have a token
          if (this.authToken) {
            this.sendAuthMessage()
          } else {
            this.isAuthenticating = false
            this.reconnectAttempts = 0
            this.connectionHandlers.forEach((handler) => handler())
            resolve()
          }
        }

        this.ws.onmessage = (event) => {
          try {
            const message: WebSocketMessage = JSON.parse(event.data)

            // Handle authentication response
            if (message.type === 'auth_success') {
              this.isAuthenticating = false
              this.reconnectAttempts = 0
              this.connectionHandlers.forEach((handler) => handler())
              resolve()
              return
            }

            if (message.type === 'auth_failed') {
              this.isAuthenticating = false
              console.error('[WebSocket] Authentication failed')
              this.ws?.close(4001)
              this.emitError('authError', message)
              reject(new Error('WebSocket authentication failed'))
              return
            }

            this.handleMessage(message)
          } catch (error) {
            console.error('[WebSocket] Failed to parse message:', error)
          }
        }

        this.ws.onerror = (error) => {
          console.error('[WebSocket] Error:', error)
          if (this.isAuthenticating) {
            reject(error)
          }
        }

        this.ws.onclose = (event) => {
          console.log('[WebSocket] Disconnected with code:', event.code)
          this.disconnectionHandlers.forEach((handler) => handler())
          if (!this.isManualClose) {
            this.attemptReconnect()
          }
        }
      } catch (error) {
        reject(error)
      }
    })
  }

  private sendAuthMessage(): void {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN || !this.authToken) {
      return
    }

    try {
      this.ws.send(JSON.stringify({
        type: 'authenticate',
        token: this.authToken
      }))
    } catch (error) {
      console.error('[WebSocket] Failed to send auth message:', error)
    }
  }

  private emitError(type: string, data: any): void {
    const handlers = this.subscriptions.get('error')
    if (handlers) {
      handlers.forEach((handler) => {
        try {
          handler({ type, ...data })
        } catch (error) {
          console.error('[WebSocket] Error in error handler:', error)
        }
      })
    }
  }

  private validateMessage(message: any): message is WebSocketMessage {
    // Basic validation of message structure
    if (!message || typeof message !== 'object') {
      console.error('[WebSocket] Invalid message: not an object')
      return false
    }

    if (typeof message.type !== 'string') {
      console.error('[WebSocket] Invalid message: missing type field')
      return false
    }

    // Validate specific message types
    switch (message.type) {
      case 'quote':
        return (
          typeof message.data === 'object' &&
          typeof message.data.symbol === 'string' &&
          typeof message.data.price === 'number' &&
          typeof message.timestamp === 'number'
        )
      case 'order_update':
        return (
          typeof message.data === 'object' &&
          typeof message.data.orderId === 'string' &&
          typeof message.data.status === 'string' &&
          typeof message.timestamp === 'number'
        )
      case 'trade':
        return typeof message.data === 'object' && typeof message.timestamp === 'number'
      case 'error':
        return typeof message.data === 'object'
      case 'authenticate':
      case 'auth_failed':
      case 'auth_success':
        return true
      default:
        console.warn('[WebSocket] Unknown message type:', message.type)
        return false
    }
  }

  private handleMessage(message: WebSocketMessage): void {
    if (!this.validateMessage(message)) {
      console.error('[WebSocket] Message validation failed:', message)
      this.emitError('validationError', { message: 'Invalid message format' })
      return
    }

    const handlers = this.subscriptions.get(message.type)
    if (handlers) {
      handlers.forEach((handler) => {
        try {
          handler(message.data)
        } catch (error) {
          console.error(`[WebSocket] Error in message handler:`, error)
        }
      })
    }
  }

  private attemptReconnect(): void {
    if (this.isManualClose) {
      return
    }

    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('[WebSocket] Max reconnect attempts reached')
      this.emitConnectionFailed({
        message: 'WebSocket disconnected. Prices may be stale. Refresh page to reconnect.',
        severity: 'error'
      })
      return
    }

    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts)
    const maxDelay = 30000  // Don't wait more than 30s
    const actualDelay = Math.min(delay, maxDelay)

    this.reconnectAttempts++

    this.emitReconnecting({
      attempt: this.reconnectAttempts,
      nextAttemptIn: actualDelay / 1000
    })

    console.log(`[WebSocket] Reconnecting in ${actualDelay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})...`)

    setTimeout(() => {
      this.connect(this.authToken || undefined).catch((error) => {
        console.error('[WebSocket] Reconnection failed:', error)
      })
    }, actualDelay)
  }

  private emitReconnecting(info: { attempt: number; nextAttemptIn: number }): void {
    this.reconnectingHandlers.forEach((handler) => {
      try {
        handler(info)
      } catch (error) {
        console.error('[WebSocket] Error in reconnecting handler:', error)
      }
    })
  }

  private emitConnectionFailed(error: { message: string; severity: string }): void {
    this.connectionFailedHandlers.forEach((handler) => {
      try {
        handler(error)
      } catch (error) {
        console.error('[WebSocket] Error in connection failed handler:', error)
      }
    })
  }

  onReconnecting(handler: (info: { attempt: number; nextAttemptIn: number }) => void): () => void {
    this.reconnectingHandlers.add(handler)
    return () => this.reconnectingHandlers.delete(handler)
  }

  onConnectionFailed(handler: (error: { message: string; severity: string }) => void): () => void {
    this.connectionFailedHandlers.add(handler)
    return () => this.connectionFailedHandlers.delete(handler)
  }

  subscribe<T>(type: string, handler: MessageHandler<T>): () => void {
    if (!this.subscriptions.has(type)) {
      this.subscriptions.set(type, new Set())
    }

    const handlers = this.subscriptions.get(type)!
    handlers.add(handler)

    // Return unsubscribe function
    return () => {
      handlers.delete(handler)
      if (handlers.size === 0) {
        this.subscriptions.delete(type)
      }
    }
  }

  onConnect(handler: ConnectionHandler): () => void {
    this.connectionHandlers.add(handler)
    return () => this.connectionHandlers.delete(handler)
  }

  onDisconnect(handler: ConnectionHandler): () => void {
    this.disconnectionHandlers.add(handler)
    return () => this.disconnectionHandlers.delete(handler)
  }

  subscribeToQuotes(symbols: string[]): () => void {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      console.warn('[WebSocket] Not connected')
      return () => {}
    }

    this.send({
      type: 'subscribe',
      channel: 'quotes',
      symbols,
    })

    return () => {
      this.send({
        type: 'unsubscribe',
        channel: 'quotes',
        symbols,
      })
    }
  }

  subscribeToOrderUpdates(): () => void {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      console.warn('[WebSocket] Not connected')
      return () => {}
    }

    this.send({
      type: 'subscribe',
      channel: 'orders',
    })

    return () => {
      this.send({
        type: 'unsubscribe',
        channel: 'orders',
      })
    }
  }

  send(data: any): void {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      console.warn('[WebSocket] Not connected')
      return
    }

    // Rate limit: max 10 messages per second
    const now = Date.now()

    if (now - this.messageRateLimiter.resetTime > 1000) {
      // Reset counter every second
      this.messageRateLimiter.messageCount = 0
      this.messageRateLimiter.resetTime = now
    }

    if (this.messageRateLimiter.messageCount >= this.messageRateLimiter.maxMessagesPerSecond) {
      console.warn('[WebSocket] Message rate limit exceeded')
      return  // Drop message
    }

    this.messageRateLimiter.messageCount++

    try {
      this.ws.send(JSON.stringify(data))
    } catch (error) {
      console.error('[WebSocket] Failed to send message:', error)
    }
  }

  disconnect(): void {
    this.isManualClose = true
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
  }

  isConnected(): boolean {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN
  }
}

// Create singleton instance
export const wsManager = new WebSocketManager()

// Export convenience functions
export const subscribeToQuotes = (
  symbols: string[],
  handler: MessageHandler<Quote>
) => {
  wsManager.subscribeToQuotes(symbols)
  return wsManager.subscribe<Quote>('quote', handler)
}

export const subscribeToOrderUpdates = (handler: MessageHandler<Order>) => {
  wsManager.subscribeToOrderUpdates()
  return wsManager.subscribe<Order>('order', handler)
}

export const onWebSocketConnect = (handler: ConnectionHandler) => {
  return wsManager.onConnect(handler)
}

export const onWebSocketDisconnect = (handler: ConnectionHandler) => {
  return wsManager.onDisconnect(handler)
}
