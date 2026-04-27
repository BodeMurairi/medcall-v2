import { useState, useRef, useEffect, useCallback } from 'react'
import { apiPost, apiGet } from '../api/client'
import { useAuth } from '../context/AuthContext'

const STORAGE_KEY = 'medcall_thread_id'

const STICKER_CATEGORIES = [
  {
    label: 'Pain',
    icon: '🤕',
    stickers: [
      { emoji: '😣', label: 'In pain' },
      { emoji: '😖', label: 'Very painful' },
      { emoji: '😫', label: 'Exhausted from pain' },
      { emoji: '🤕', label: 'Head hurts' },
      { emoji: '😵', label: 'Dizzy' },
      { emoji: '😵‍💫', label: 'Very dizzy' },
      { emoji: '🤯', label: 'Severe headache' },
      { emoji: '😤', label: 'Struggling to breathe' },
    ],
  },
  {
    label: 'Sick',
    icon: '🤒',
    stickers: [
      { emoji: '🤒', label: 'Feeling sick' },
      { emoji: '🤢', label: 'Nauseous' },
      { emoji: '🤮', label: 'Vomiting' },
      { emoji: '🥵', label: 'Fever / hot' },
      { emoji: '🥶', label: 'Chills / cold' },
      { emoji: '😰', label: 'Cold sweat' },
      { emoji: '😓', label: 'Sweating' },
      { emoji: '🫠', label: 'Feeling weak' },
    ],
  },
  {
    label: 'Mood',
    icon: '😔',
    stickers: [
      { emoji: '😔', label: 'Sad' },
      { emoji: '😟', label: 'Worried' },
      { emoji: '😨', label: 'Scared' },
      { emoji: '😱', label: 'Very scared' },
      { emoji: '😢', label: 'Crying' },
      { emoji: '😭', label: 'Very distressed' },
      { emoji: '😥', label: 'Upset' },
      { emoji: '🥺', label: 'Anxious' },
    ],
  },
  {
    label: 'Energy',
    icon: '😴',
    stickers: [
      { emoji: '😴', label: 'Very tired' },
      { emoji: '😪', label: 'Sleepy' },
      { emoji: '🥱', label: 'Yawning / fatigued' },
      { emoji: '😩', label: 'Drained' },
      { emoji: '😞', label: 'Low energy' },
      { emoji: '🫥', label: 'Feeling empty' },
      { emoji: '💤', label: 'Need rest' },
      { emoji: '🪫', label: 'Completely drained' },
    ],
  },
  {
    label: 'Better',
    icon: '😊',
    stickers: [
      { emoji: '😊', label: 'Feeling better' },
      { emoji: '😌', label: 'Relieved' },
      { emoji: '🙂', label: 'A little better' },
      { emoji: '😃', label: 'Much better' },
      { emoji: '💪', label: 'Getting stronger' },
      { emoji: '🙌', label: 'Great improvement' },
      { emoji: '👍', label: 'Doing okay' },
      { emoji: '😎', label: 'Feeling good' },
    ],
  },
]

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
  const isStickerOnly = /^\p{Extended_Pictographic}(\s*\p{Extended_Pictographic})*$/u.test(msg.content.trim()) && msg.content.trim().length <= 4
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
      <div className={`message-bubble ${isUser ? 'bubble-user' : 'bubble-ai'} ${isStickerOnly ? 'bubble-sticker' : ''}`}>
        <p className={`message-text ${isStickerOnly ? 'sticker-text' : ''}`}>{msg.content}</p>
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

function StickerPicker({ onSelect, onClose }) {
  const [activeCategory, setActiveCategory] = useState(0)
  const pickerRef = useRef(null)

  useEffect(() => {
    function handleClick(e) {
      if (pickerRef.current && !pickerRef.current.contains(e.target)) {
        // Don't close if the click was on the toggle button — that button handles its own toggle
        if (e.target.closest?.('.sticker-toggle-btn')) return
        onClose()
      }
    }
    document.addEventListener('mousedown', handleClick)
    return () => document.removeEventListener('mousedown', handleClick)
  }, [onClose])  // onClose is stable via useCallback in parent

  return (
    <div className="sticker-picker" ref={pickerRef}>
      <div className="sticker-picker-header">
        <span className="sticker-picker-title">How do you feel?</span>
        <button className="sticker-picker-close" onClick={onClose}>✕</button>
      </div>
      <div className="sticker-category-tabs">
        {STICKER_CATEGORIES.map((cat, i) => (
          <button
            key={i}
            className={`sticker-tab ${activeCategory === i ? 'sticker-tab-active' : ''}`}
            onClick={() => setActiveCategory(i)}
            title={cat.label}
          >
            {cat.icon}
          </button>
        ))}
      </div>
      <div className="sticker-grid">
        {STICKER_CATEGORIES[activeCategory].stickers.map((s, i) => (
          <button
            key={i}
            className="sticker-btn"
            onClick={() => onSelect(s.emoji)}
            title={s.label}
          >
            {s.emoji}
          </button>
        ))}
      </div>
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

function toTime(isoString) {
  if (!isoString) return now()
  try {
    return new Date(isoString).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  } catch {
    return now()
  }
}

export default function Chat() {
  const { user } = useAuth()
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [resumeLoading, setResumeLoading] = useState(true)
  const [isComplete, setIsComplete] = useState(false)
  const [threadId, setThreadId] = useState(() => localStorage.getItem(STORAGE_KEY) || '')
  const [showStickers, setShowStickers] = useState(false)
  const closeStickers = useCallback(() => setShowStickers(false), [])
  const bottomRef = useRef(null)
  const inputRef = useRef(null)
  const textareaRef = useRef(null)

  // On mount: check for an unfinished consultation and restore it
  useEffect(() => {
    async function checkActive() {
      try {
        const data = await apiGet('/consultation/active')
        if (data.found && data.messages && data.messages.length > 0) {
          const restored = data.messages.map(m => ({
            role: m.role,
            content: m.content,
            time: toTime(m.timestamp),
          }))
          setMessages(restored)
          if (data.thread_id) {
            setThreadId(data.thread_id)
            localStorage.setItem(STORAGE_KEY, data.thread_id)
          }
        }
      } catch {
        // silently ignore — user just gets the default greeting
      } finally {
        setResumeLoading(false)
      }
    }
    checkActive()
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

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
    setShowStickers(false)

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

  const handleStickerSelect = (emoji) => {
    setInput(prev => prev ? prev + ' ' + emoji : emoji)
    setShowStickers(false)
    setTimeout(() => {
      inputRef.current?.focus()
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto'
        textareaRef.current.style.height = Math.min(textareaRef.current.scrollHeight, 120) + 'px'
      }
    }, 0)
  }

  const handleNewConsultation = () => {
    setIsComplete(false)
    setThreadId('')
    localStorage.removeItem(STORAGE_KEY)
    setMessages([])
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

        {resumeLoading ? (
          <div className="resume-loading">
            <span className="dot" /><span className="dot" /><span className="dot" />
          </div>
        ) : (
          <>
            {messages.length > 1 && threadId && !isComplete && (
              <div className="resume-banner">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <polyline points="1 4 1 10 7 10" />
                  <path d="M3.51 15a9 9 0 1 0 .49-4.95" />
                </svg>
                Consultation resumed from where you left off
              </div>
            )}
            {messages.map((msg, i) => (
              <Message key={i} msg={msg} />
            ))}
            {loading && <TypingIndicator />}
            {isComplete && <ConsultationComplete onNewConsultation={handleNewConsultation} />}
          </>
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
          <div className="input-area-inner">
            {showStickers && (
              <StickerPicker
                onSelect={handleStickerSelect}
                onClose={closeStickers}
              />
            )}
            <div className="input-row">
              <button
                className={`sticker-toggle-btn ${showStickers ? 'sticker-toggle-active' : ''}`}
                onClick={() => setShowStickers(prev => !prev)}
                disabled={loading}
                title="Express how you feel"
                aria-label="Open sticker picker"
              >
                🙂
              </button>
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
          </div>
        )}
        <p className="input-hint">MedCall AI assists but does not replace professional medical advice.</p>
      </div>
    </div>
  )
}
