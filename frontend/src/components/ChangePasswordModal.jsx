import { useState } from 'react'
import { apiPost } from '../api/client'

export default function ChangePasswordModal({ onClose }) {
  const [form, setForm] = useState({ current_pin: '', new_pin: '', confirm_new_pin: '' })
  const [show, setShow]     = useState({ current: false, new: false, confirm: false })
  const [loading, setLoading] = useState(false)
  const [error,   setError]   = useState('')
  const [success, setSuccess] = useState(false)

  const set = (k, v) => setForm(f => ({ ...f, [k]: v }))
  const toggleShow = (k) => setShow(s => ({ ...s, [k]: !s[k] }))

  const submit = async (e) => {
    e.preventDefault()
    setError('')

    if (form.new_pin.length < 6)              { setError('New PIN must be at least 6 digits.'); return }
    if (form.new_pin !== form.confirm_new_pin) { setError('New PINs do not match.'); return }
    if (form.new_pin === form.current_pin)     { setError('New PIN must differ from the current PIN.'); return }

    setLoading(true)
    try {
      await apiPost('/auth/change-password', form)
      setSuccess(true)
      setTimeout(onClose, 1800)
    } catch (err) {
      setError(err.message || 'Failed to update PIN.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="modal-overlay" onClick={e => e.target === e.currentTarget && onClose()}>
      <div className="modal-card">
        {/* Header */}
        <div className="modal-header">
          <div className="modal-title-row">
            <div className="modal-icon">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2">
                <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
                <path d="M7 11V7a5 5 0 0110 0v4"/>
              </svg>
            </div>
            <div>
              <h2 className="modal-title">Change PIN</h2>
              <p className="modal-subtitle">Update your MedCall PIN</p>
            </div>
          </div>
          <button className="modal-close" onClick={onClose} aria-label="Close">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>

        {success ? (
          <div className="modal-success">
            <div className="success-icon">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#34a853" strokeWidth="2.5">
                <path d="M22 11.08V12a10 10 0 11-5.93-9.14"/>
                <polyline points="22 4 12 14.01 9 11.01"/>
              </svg>
            </div>
            <h3>PIN Updated!</h3>
            <p>Your PIN has been changed successfully.</p>
          </div>
        ) : (
          <form className="modal-body" onSubmit={submit}>
            {[
              { key: 'current', label: 'Current PIN', field: 'current_pin', placeholder: '••••••' },
              { key: 'new',     label: 'New PIN',     field: 'new_pin',     placeholder: '•••••• (min 6 digits)' },
              { key: 'confirm', label: 'Confirm New PIN', field: 'confirm_new_pin', placeholder: '••••••' },
            ].map(({ key, label, field, placeholder }) => (
              <div className="form-group" key={field}>
                <label className="form-label">{label}</label>
                <div className="input-wrapper">
                  <span className="input-icon">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
                      <path d="M7 11V7a5 5 0 0110 0v4"/>
                    </svg>
                  </span>
                  <input
                    className="form-input pin-input"
                    type={show[key] ? 'text' : 'password'}
                    placeholder={placeholder}
                    inputMode="numeric"
                    maxLength={8}
                    value={form[field]}
                    onChange={e => set(field, e.target.value)}
                    required
                    disabled={loading}
                  />
                  <button type="button" className="input-eye" onClick={() => toggleShow(key)}>
                    {show[key]
                      ? <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M17.94 17.94A10.07 10.07 0 0112 20c-7 0-11-8-11-8a18.45 18.45 0 015.06-5.94M9.9 4.24A9.12 9.12 0 0112 4c7 0 11 8 11 8a18.5 18.5 0 01-2.16 3.19m-6.72-1.07a3 3 0 11-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/></svg>
                      : <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
                    }
                  </button>
                </div>
              </div>
            ))}

            {error && (
              <div className="alert alert-error">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/>
                </svg>
                {error}
              </div>
            )}

            <div className="modal-actions">
              <button type="button" className="btn btn-ghost" onClick={onClose} disabled={loading}>Cancel</button>
              <button type="submit" className="btn btn-primary" disabled={loading}>
                {loading ? <><span className="spinner"/>Updating…</> : 'Update PIN'}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  )
}
