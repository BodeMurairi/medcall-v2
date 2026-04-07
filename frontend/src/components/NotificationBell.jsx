import { useState, useEffect, useRef, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { apiGet } from '../api/client'
import { useToast } from '../context/ToastContext'

const SEEN_KEY = 'medcall_seen_notifications'
const POLL_INTERVAL = 30_000   // 30 seconds

function getSeen() {
  try { return new Set(JSON.parse(localStorage.getItem(SEEN_KEY) || '[]')) }
  catch { return new Set() }
}
function saveSeen(set) {
  localStorage.setItem(SEEN_KEY, JSON.stringify([...set]))
}

function urgencyColor(urgency) {
  if (!urgency) return 'notif-neutral'
  const u = urgency.toLowerCase()
  if (u === 'high')   return 'notif-danger'
  if (u === 'medium') return 'notif-warning'
  return 'notif-success'
}

function actionLabel(action) {
  const map = { emergency: '🚨 Emergency', visit_clinic: '🏥 Visit clinic', self_care: '🏠 Self-care' }
  return map[(action || '').toLowerCase()] || action || '—'
}

function formatRelative(iso) {
  if (!iso) return ''
  const diff = Date.now() - new Date(iso).getTime()
  const mins  = Math.floor(diff / 60_000)
  const hours = Math.floor(diff / 3_600_000)
  const days  = Math.floor(diff / 86_400_000)
  if (mins  < 1)  return 'just now'
  if (mins  < 60) return `${mins}m ago`
  if (hours < 24) return `${hours}h ago`
  return `${days}d ago`
}

export default function NotificationBell() {
  const navigate = useNavigate()
  const { show }  = useToast()
  const [items,   setItems]   = useState([])
  const [open,    setOpen]    = useState(false)
  const [seen,    setSeen]    = useState(getSeen)
  const panelRef = useRef(null)
  const prevIdsRef = useRef(new Set())

  const unread = items.filter(n => !seen.has(n.id)).length

  const fetchNotifications = useCallback(async () => {
    try {
      const data = await apiGet('/notifications')
      const incoming = Array.isArray(data) ? data : []
      setItems(incoming)

      // Fire toast for newly arrived results the user hasn't seen yet
      const newItems = incoming.filter(n => !prevIdsRef.current.has(n.id) && !seen.has(n.id))
      newItems.forEach(n => {
        const label = n.urgency ? ` — ${n.urgency.toUpperCase()} urgency` : ''
        show(`Your consultation results are ready${label}. Check your history.`, 'info', 6000)
      })
      // Update previous-ids tracking
      prevIdsRef.current = new Set(incoming.map(n => n.id))
    } catch {
      // Silently fail — network issues shouldn't break the UI
    }
  }, [show, seen])

  // Initial load + polling
  useEffect(() => {
    fetchNotifications()
    const timer = setInterval(fetchNotifications, POLL_INTERVAL)
    return () => clearInterval(timer)
  }, [fetchNotifications])

  // Close panel on outside click
  useEffect(() => {
    function handleClick(e) {
      if (panelRef.current && !panelRef.current.contains(e.target)) setOpen(false)
    }
    if (open) document.addEventListener('mousedown', handleClick)
    return () => document.removeEventListener('mousedown', handleClick)
  }, [open])

  const markAllRead = () => {
    const next = new Set([...seen, ...items.map(n => n.id)])
    setSeen(next)
    saveSeen(next)
  }

  const handleItemClick = (n) => {
    const next = new Set([...seen, n.id])
    setSeen(next)
    saveSeen(next)
    setOpen(false)
    navigate('/history')
  }

  const handleOpen = () => {
    setOpen(v => !v)
  }

  return (
    <div className="notif-wrapper" ref={panelRef}>
      <button className={`notif-bell ${open ? 'notif-bell-open' : ''}`} onClick={handleOpen} aria-label="Notifications">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M18 8A6 6 0 006 8c0 7-3 9-3 9h18s-3-2-3-9"/>
          <path d="M13.73 21a2 2 0 01-3.46 0"/>
        </svg>
        {unread > 0 && (
          <span className="notif-badge">{unread > 9 ? '9+' : unread}</span>
        )}
      </button>

      {open && (
        <div className="notif-panel">
          <div className="notif-panel-header">
            <h3 className="notif-panel-title">Notifications</h3>
            {unread > 0 && (
              <button className="notif-mark-all" onClick={markAllRead}>Mark all read</button>
            )}
          </div>

          <div className="notif-list">
            {items.length === 0 ? (
              <div className="notif-empty">
                <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#cbd5e1" strokeWidth="1.5">
                  <path d="M18 8A6 6 0 006 8c0 7-3 9-3 9h18s-3-2-3-9"/>
                  <path d="M13.73 21a2 2 0 01-3.46 0"/>
                </svg>
                <p>No notifications yet</p>
              </div>
            ) : (
              items.map(n => {
                const isUnread = !seen.has(n.id)
                return (
                  <button key={n.id} className={`notif-item ${isUnread ? 'notif-item-unread' : ''}`} onClick={() => handleItemClick(n)}>
                    <div className={`notif-dot ${isUnread ? 'notif-dot-active' : ''}`} />
                    <div className="notif-item-body">
                      <div className="notif-item-header">
                        <span className="notif-item-title">Results ready</span>
                        <span className="notif-item-time">{formatRelative(n.last_updated)}</span>
                      </div>
                      <p className="notif-item-sub">
                        {n.has_decision
                          ? <>Recommendation: <strong>{actionLabel(n.action)}</strong></>
                          : 'Analysis complete — view your report'}
                      </p>
                      {n.urgency && (
                        <span className={`notif-urgency-tag ${urgencyColor(n.urgency)}`}>
                          {n.urgency.toUpperCase()} URGENCY
                        </span>
                      )}
                    </div>
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#94a3b8" strokeWidth="2">
                      <polyline points="9 18 15 12 9 6"/>
                    </svg>
                  </button>
                )
              })
            )}
          </div>

          {items.length > 0 && (
            <div className="notif-panel-footer">
              <button className="notif-view-all" onClick={() => { setOpen(false); navigate('/history') }}>
                View all in History →
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
