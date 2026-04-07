import { useState, useEffect } from 'react'
import { apiGet } from '../api/client'
import { useAuth } from '../context/AuthContext'

function RiskBadge({ level }) {
  const map = {
    high: { label: 'High Risk', cls: 'badge-danger' },
    moderate: { label: 'Moderate', cls: 'badge-warning' },
    low: { label: 'Low Risk', cls: 'badge-success' },
  }
  const cfg = map[(level || '').toLowerCase()] || { label: level || 'Unknown', cls: 'badge-neutral' }
  return <span className={`badge ${cfg.cls}`}>{cfg.label}</span>
}

function UrgencyBadge({ level }) {
  const map = {
    high: { label: 'High Urgency', cls: 'badge-danger' },
    medium: { label: 'Medium Urgency', cls: 'badge-warning' },
    low: { label: 'Low Urgency', cls: 'badge-success' },
  }
  const cfg = map[(level || '').toLowerCase()] || { label: level || 'Unknown', cls: 'badge-neutral' }
  return <span className={`badge ${cfg.cls}`}>{cfg.label}</span>
}

function ActionBadge({ action }) {
  const map = {
    emergency: { label: '🚨 Emergency', cls: 'badge-danger' },
    visit_clinic: { label: '🏥 Visit Clinic', cls: 'badge-warning' },
    self_care: { label: '🏠 Self Care', cls: 'badge-success' },
  }
  const cfg = map[(action || '').toLowerCase()] || { label: action, cls: 'badge-neutral' }
  return <span className={`badge ${cfg.cls}`}>{cfg.label}</span>
}

function formatDate(iso) {
  if (!iso) return '—'
  return new Date(iso).toLocaleString([], {
    month: 'short', day: 'numeric', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
  })
}

function MessageThread({ messages }) {
  return (
    <div className="history-messages">
      {messages.map((m, i) => (
        <div key={i} className={`hist-msg ${m.message_type === 'user' ? 'hist-msg-user' : 'hist-msg-ai'}`}>
          <span className="hist-msg-label">
            {m.message_type === 'user' ? 'You' : 'Dr. Mshauri'}
          </span>
          <p className="hist-msg-content">{m.content}</p>
          {m.timestamp && (
            <span className="hist-msg-time">{formatDate(m.timestamp)}</span>
          )}
        </div>
      ))}
    </div>
  )
}

function AnalysisPanel({ analysis }) {
  if (!analysis) return (
    <div className="panel-empty">
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#94a3b8" strokeWidth="2">
        <circle cx="12" cy="12" r="10" />
        <line x1="12" y1="8" x2="12" y2="12" />
        <line x1="12" y1="16" x2="12.01" y2="16" />
      </svg>
      <p>Analysis is still being processed. Check back shortly.</p>
    </div>
  )

  const symptoms = Array.isArray(analysis.detected_symptoms)
    ? analysis.detected_symptoms
    : typeof analysis.detected_symptoms === 'string'
      ? analysis.detected_symptoms.split(',').map(s => s.trim()).filter(Boolean)
      : []

  const conditions = Array.isArray(analysis.possible_conditions)
    ? analysis.possible_conditions
    : []

  const exams = analysis.exams && typeof analysis.exams === 'object' && !Array.isArray(analysis.exams)
    ? Object.entries(analysis.exams)
    : []

  return (
    <div className="analysis-panel">
      <div className="analysis-header">
        <RiskBadge level={analysis.risk_level} />
        {analysis.mark_emergency && (
          <span className="badge badge-danger">⚠ Emergency Flag</span>
        )}
      </div>

      {symptoms.length > 0 && (
        <div className="analysis-section">
          <h4 className="analysis-section-title">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M9 12l2 2 4-4" /><circle cx="12" cy="12" r="10" />
            </svg>
            Detected Symptoms
          </h4>
          <div className="tag-list">
            {symptoms.map((s, i) => (
              <span key={i} className="tag">{s}</span>
            ))}
          </div>
        </div>
      )}

      {conditions.length > 0 && (
        <div className="analysis-section">
          <h4 className="analysis-section-title">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M8 6h13M8 12h13M8 18h13M3 6h.01M3 12h.01M3 18h.01" />
            </svg>
            Possible Conditions
          </h4>
          <div className="conditions-list">
            {conditions.map((c, i) => {
              const name = typeof c === 'object' ? c.name || c.condition || JSON.stringify(c) : c
              const confidence = typeof c === 'object' && c.confidence != null
                ? Math.round(c.confidence * 100)
                : null
              return (
                <div key={i} className="condition-item">
                  <span className="condition-name">{name}</span>
                  {confidence !== null && (
                    <div className="confidence-bar">
                      <div className="confidence-fill" style={{ width: `${confidence}%` }} />
                      <span className="confidence-label">{confidence}%</span>
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        </div>
      )}

      {exams.length > 0 && (
        <div className="analysis-section">
          <h4 className="analysis-section-title">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M9 3H5a2 2 0 00-2 2v4m6-6h10a2 2 0 012 2v4M9 3v18m0 0h10a2 2 0 002-2V9M9 21H5a2 2 0 01-2-2V9m0 0h18" />
            </svg>
            Recommended Exams
          </h4>
          <ul className="exam-list">
            {exams.map(([cond, examList], i) => (
              <li key={i}>
                <strong>{cond}:</strong>{' '}
                {Array.isArray(examList) ? examList.join(', ') : examList}
              </li>
            ))}
          </ul>
        </div>
      )}

      {analysis.reasoning && (
        <div className="analysis-section">
          <h4 className="analysis-section-title">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="10" /><line x1="12" y1="8" x2="12" y2="12" /><line x1="12" y1="16" x2="12.01" y2="16" />
            </svg>
            AI Reasoning
          </h4>
          <p className="reasoning-text">{analysis.reasoning}</p>
        </div>
      )}
    </div>
  )
}

function DecisionPanel({ decision }) {
  if (!decision) return (
    <div className="panel-empty">
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#94a3b8" strokeWidth="2">
        <circle cx="12" cy="12" r="10" />
        <line x1="12" y1="8" x2="12" y2="12" />
        <line x1="12" y1="16" x2="12.01" y2="16" />
      </svg>
      <p>Doctor's recommendation is being prepared. Check back shortly.</p>
    </div>
  )

  return (
    <div className="decision-panel">
      <div className="decision-badges">
        <UrgencyBadge level={decision.urgency} />
        <ActionBadge action={decision.action} />
      </div>

      <div className="decision-message">
        <div className="decision-icon">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#1a73e8" strokeWidth="2">
            <path d="M12 2a10 10 0 100 20A10 10 0 0012 2z" />
            <path d="M12 8v4l3 3" />
          </svg>
        </div>
        <div>
          <h4 className="decision-doctor">Dr. Mshuli's Recommendation</h4>
          <p className="decision-text">{decision.message}</p>
        </div>
      </div>

      {decision.referral_type && (
        <div className="referral-box">
          <h4>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z" />
              <polyline points="9 22 9 12 15 12 15 22" />
            </svg>
            Referral Information
          </h4>
          <p>{decision.referral_type}</p>
        </div>
      )}
    </div>
  )
}

function ConsultationCard({ item, isOpen, onToggle }) {
  const [tab, setTab] = useState('messages')

  return (
    <div className={`history-card ${isOpen ? 'history-card-open' : ''}`}>
      <button className="history-card-header" onClick={onToggle}>
        <div className="history-card-left">
          <div className="history-card-icon">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2">
              <path d="M8 6h13M8 12h13M8 18h13M3 6h.01M3 12h.01M3 18h.01" />
            </svg>
          </div>
          <div>
            <p className="history-card-date">{formatDate(item.start_time)}</p>
            <p className="history-card-id">{item.consultation_id}</p>
          </div>
        </div>
        <div className="history-card-right">
          {item.risk_level && <RiskBadge level={typeof item.risk_level === 'string' ? item.risk_level : JSON.stringify(item.risk_level)} />}
          <span className={`status-pill ${item.status === 'active' ? 'pill-active' : 'pill-complete'}`}>
            {item.status === 'active' ? 'In Progress' : 'Complete'}
          </span>
          <svg
            className={`chevron ${isOpen ? 'chevron-up' : ''}`}
            width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"
          >
            <polyline points="6 9 12 15 18 9" />
          </svg>
        </div>
      </button>

      {isOpen && (
        <div className="history-card-body">
          {item.summary && (
            <div className="history-summary">
              <strong>Summary:</strong> {item.summary}
            </div>
          )}

          <div className="history-tabs">
            {['messages', 'analysis', 'decision'].map(t => (
              <button
                key={t}
                className={`history-tab ${tab === t ? 'history-tab-active' : ''}`}
                onClick={() => setTab(t)}
              >
                {t === 'messages' && (
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z" />
                  </svg>
                )}
                {t === 'analysis' && (
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
                  </svg>
                )}
                {t === 'decision' && (
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M9 12l2 2 4-4" /><circle cx="12" cy="12" r="10" />
                  </svg>
                )}
                {t.charAt(0).toUpperCase() + t.slice(1)}
              </button>
            ))}
          </div>

          <div className="history-tab-content">
            {tab === 'messages' && <MessageThread messages={item.messages} />}
            {tab === 'analysis' && <AnalysisPanel analysis={item.analysis} />}
            {tab === 'decision' && <DecisionPanel decision={item.decision} />}
          </div>
        </div>
      )}
    </div>
  )
}

export default function History() {
  const { user } = useAuth()
  const [consultations, setConsultations] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [openId, setOpenId] = useState(null)

  useEffect(() => {
    async function load() {
      setLoading(true)
      setError('')
      try {
        const data = await apiGet('/history', { phone_number: user.phoneNumber })
        setConsultations(data)
        if (data.length > 0) setOpenId(data[0].id)
      } catch (err) {
        setError('Failed to load consultation history. Please try again.')
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [user.phoneNumber])

  return (
    <div className="history-container">
      <div className="history-header">
        <h1 className="history-title">Consultation History</h1>
        <p className="history-subtitle">
          {consultations.length > 0
            ? `${consultations.length} consultation${consultations.length !== 1 ? 's' : ''} on record`
            : 'Your past consultations will appear here'}
        </p>
      </div>

      {loading && (
        <div className="loading-state">
          <div className="loading-spinner" />
          <p>Loading your consultations…</p>
        </div>
      )}

      {!loading && error && (
        <div className="alert alert-error">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="10" />
            <line x1="15" y1="9" x2="9" y2="15" />
            <line x1="9" y1="9" x2="15" y2="15" />
          </svg>
          {error}
        </div>
      )}

      {!loading && !error && consultations.length === 0 && (
        <div className="empty-state">
          <div className="empty-icon">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#cbd5e1" strokeWidth="1.5">
              <path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z" />
            </svg>
          </div>
          <h3>No consultations yet</h3>
          <p>Start a consultation in the Chat tab and your history will appear here.</p>
        </div>
      )}

      {!loading && !error && consultations.length > 0 && (
        <div className="history-list">
          {consultations.map(item => (
            <ConsultationCard
              key={item.id}
              item={item}
              isOpen={openId === item.id}
              onToggle={() => setOpenId(openId === item.id ? null : item.id)}
            />
          ))}
        </div>
      )}
    </div>
  )
}
