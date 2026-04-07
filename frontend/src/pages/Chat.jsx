import { useState, useRef, useEffect, useCallback } from 'react'
import { apiPost } from '../api/client'
import { useAuth } from '../context/AuthContext'

const STORAGE_KEY = 'medcall_thread_id'

function TypingIndicator() {
  return (
    <div className="message-row message-ai">
      <div className="avatar avatar-ai">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2">
          <path d="M12 2a10 10 0 100 20A10 10 0 0012 2z" />
          <path d="M12 8v4l3 3" />
        </svg>
      </div>
      <div className="message-bubble bubble-ai typing-bubble">
        <span className="dot" />
        <span className="dot" />
        <span className="dot" />
      </div>
    </div>
  )
}

function Message({ msg }) {
  const isUser = msg.role === 'user'
  return (
    <div className={`message-row ${isUser ? 'message-user' : 'message-ai'}`}>
      {!isUser && (
        <div className="avatar avatar-ai">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2">
            <path d="M12 2a10 10 0 100 20A10 10 0 0012 2z" />
            <path d="M12 8v4l3 3" />
          </svg>
        </div>
      )}
      <div className={`message-bubble ${isUser ? 'bubble-user' : 'bubble-ai'}`}>
        <p className="message-text">{msg.content}</p>
        <span className="message-time">{msg.time}</span>
      </div>
      {isUser && (
        <div className="avatar avatar-user">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2">
            <path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2" />
            <circle cx="12" cy="7" r="4" />
          </svg>
        </div>
      )}
    </div>
  )
}

function ConsultationComplete({ onNewConsultation }) {
  return (
    <div className="consultation-complete">
      <div className="complete-icon">
        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#34a853" strokeWidth="2">
          <path d="M22 11.08V12a10 10 0 11-5.93-9.14" />
          <polyline points="22 4 12 14.01 9 11.01" />
        </svg>
      </div>
      <h3>Consultation Complete</h3>
      <p>Your symptoms have been recorded and our AI is preparing your health analysis and recommendations. Check your <strong>History</strong> tab soon for the full report.</p>
      <button className="btn btn-primary" onClick={onNewConsultation}>
        Start New Consultation
      </button>
    </div>
  )
}

function now() {
  return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

export default function Chat() {
  const { user } = useAuth()
  const [messages, setMessages] = useState([
    {
      role: 'ai',
      content: `Hello ${user?.firstName || 'there'}! I'm Doctor Mshauri, your AI health assistant. Please describe your symptoms or health concern and I'll guide you through a consultation.`,
      time: now(),
    }
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [isComplete, setIsComplete] = useState(false)
  const [threadId, setThreadId] = useState(() => localStorage.getItem(STORAGE_KEY) || '')
  const bottomRef = useRef(null)
  const inputRef = useRef(null)
  const textareaRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  const handleSend = useCallback(async () => {
    const text = input.trim()
    if (!text || loading || isComplete) return

    const userMsg = { role: 'user', content: text, time: now() }
    setMessages(prev => [...prev, userMsg])
    setInput('')
    setLoading(true)

    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
    }

    try {
      const data = await apiPost('/consultation', {
        phone_number: user.phoneNumber,
        message: text,
        thread_id: threadId || undefined,
      })

      if (data.thread_id) {
        setThreadId(data.thread_id)
        localStorage.setItem(STORAGE_KEY, data.thread_id)
      }

      if (data.message) {
        setMessages(prev => [...prev, { role: 'ai', content: data.message, time: now() }])
      }

      if (data.status === 'complete') {
        setIsComplete(true)
        localStorage.removeItem(STORAGE_KEY)
        setThreadId('')
      }
    } catch (err) {
      setMessages(prev => [
        ...prev,
        {
          role: 'ai',
          content: 'Sorry, I encountered an error. Please try again in a moment.',
          time: now(),
        }
      ])
    } finally {
      setLoading(false)
      setTimeout(() => inputRef.current?.focus(), 0)
    }
  }, [input, loading, isComplete, threadId, user])

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const handleInput = (e) => {
    setInput(e.target.value)
    e.target.style.height = 'auto'
    e.target.style.height = Math.min(e.target.scrollHeight, 120) + 'px'
  }

  const handleNewConsultation = () => {
    setIsComplete(false)
    setThreadId('')
    localStorage.removeItem(STORAGE_KEY)
    setMessages([{
      role: 'ai',
      content: `Hello ${user?.firstName || 'there'}! I'm Doctor Mshauri. What health concern would you like to discuss today?`,
      time: now(),
    }])
  }

  return (
    <div className="chat-container">
      <div className="chat-header">
        <div className="chat-header-info">
          <div className="chat-avatar">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2">
              <path d="M12 2a10 10 0 100 20A10 10 0 0012 2z" />
              <path d="M12 8v4l3 3" />
            </svg>
          </div>
          <div>
            <h2 className="chat-title">Doctor Mshauri</h2>
            <span className={`status-badge ${loading ? 'status-typing' : 'status-online'}`}>
              {loading ? 'Typing...' : 'Online'}
            </span>
          </div>
        </div>
        <div className="chat-header-actions">
          <div className="patient-chip">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2" />
              <circle cx="12" cy="7" r="4" />
            </svg>
            {user?.firstName} {user?.lastName}
          </div>
        </div>
      </div>

      <div className="chat-messages">
        <div className="chat-date-divider">
          <span>{new Date().toLocaleDateString([], { weekday: 'long', month: 'long', day: 'numeric' })}</span>
        </div>

        {messages.map((msg, i) => (
          <Message key={i} msg={msg} />
        ))}

        {loading && <TypingIndicator />}

        {isComplete && (
          <ConsultationComplete onNewConsultation={handleNewConsultation} />
        )}

        <div ref={bottomRef} />
      </div>

      <div className="chat-input-area">
        {isComplete ? (
          <div className="input-disabled-msg">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M22 11.08V12a10 10 0 11-5.93-9.14" />
              <polyline points="22 4 12 14.01 9 11.01" />
            </svg>
            Consultation ended. Start a new one above.
          </div>
        ) : (
          <div className="input-row">
            <textarea
              ref={el => { inputRef.current = el; textareaRef.current = el }}
              className="chat-input"
              placeholder="Describe your symptoms…"
              value={input}
              onChange={handleInput}
              onKeyDown={handleKeyDown}
              rows={1}
              disabled={loading}
            />
            <button
              className={`send-btn ${(!input.trim() || loading) ? 'send-btn-disabled' : ''}`}
              onClick={handleSend}
              disabled={!input.trim() || loading}
              aria-label="Send message"
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                <line x1="22" y1="2" x2="11" y2="13" />
                <polygon points="22 2 15 22 11 13 2 9 22 2" />
              </svg>
            </button>
          </div>
        )}
        <p className="input-hint">MedCall AI assists but does not replace professional medical advice.</p>
      </div>
    </div>
  )
}
