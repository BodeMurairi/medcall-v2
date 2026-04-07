import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { apiPost } from '../api/client'
import { useAuth } from '../context/AuthContext'

export default function Login() {
  const { login } = useAuth()
  const navigate  = useNavigate()

  const [phone,   setPhone]   = useState('')
  const [pin,     setPin]     = useState('')
  const [showPin, setShowPin] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error,   setError]   = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')

    if (!phone.trim())    { setError('Please enter your phone number.'); return }
    if (pin.length < 4)   { setError('PIN must be at least 4 digits.'); return }

    setLoading(true)
    try {
      const data = await apiPost('/auth/login', { phone_number: phone.trim(), pin })
      login(data.access_token, {
        patientId:       data.patient_id,
        firstName:       data.first_name,
        lastName:        data.last_name,
        phoneNumber:     data.phone_number,
        hasPersonalInfo: data.has_personal_info,
        hasMedicalInfo:  data.has_medical_info,
      })
      navigate('/chat')
    } catch (err) {
      // 404 → not registered, 401 → wrong PIN
      if (err.message?.includes('not registered') || err.message?.includes('404')) {
        setError('NOT_REGISTERED')
      } else {
        setError(err.message || 'Login failed. Please try again.')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="login-container">
      <div className="login-card">

        <Link to="/" className="login-back-home">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
            <polyline points="15 18 9 12 15 6"/>
          </svg>
          Back to Home
        </Link>

        <div className="login-logo">
          <div className="logo-icon">
            <svg width="40" height="40" viewBox="0 0 40 40" fill="none">
              <rect width="40" height="40" rx="12" fill="#1a73e8"/>
              <path d="M20 8v24M8 20h24" stroke="white" strokeWidth="4" strokeLinecap="round"/>
            </svg>
          </div>
          <h1 className="login-title">MedCall</h1>
          <p className="login-subtitle">Your AI Health Companion</p>
        </div>

        <form className="login-form" onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="phone" className="form-label">Phone Number</label>
            <div className="input-wrapper">
              <span className="input-icon">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M22 16.92v3a2 2 0 01-2.18 2 19.79 19.79 0 01-8.63-3.07A19.5 19.5 0 013.07 8.81a19.79 19.79 0 01-3.07-8.63A2 2 0 012 0h3a2 2 0 012 1.72c.127.96.361 1.903.7 2.81a2 2 0 01-.45 2.11L6.09 7.91a16 16 0 006 6l1.27-1.27a2 2 0 012.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0122 16.92z"/>
                </svg>
              </span>
              <input id="phone" type="tel" className="form-input"
                placeholder="+250 7XX XXX XXX"
                value={phone} onChange={e => setPhone(e.target.value)}
                autoComplete="tel" disabled={loading} />
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="pin" className="form-label">PIN</label>
            <div className="input-wrapper">
              <span className="input-icon">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
                  <path d="M7 11V7a5 5 0 0110 0v4"/>
                </svg>
              </span>
              <input id="pin" type={showPin ? 'text' : 'password'}
                className="form-input pin-input"
                placeholder="Enter your PIN"
                value={pin} onChange={e => setPin(e.target.value)}
                maxLength={8} inputMode="numeric"
                autoComplete="current-password" disabled={loading} />
              <button type="button" className="input-eye" onClick={() => setShowPin(v => !v)}>
                {showPin
                  ? <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M17.94 17.94A10.07 10.07 0 0112 20c-7 0-11-8-11-8a18.45 18.45 0 015.06-5.94M9.9 4.24A9.12 9.12 0 0112 4c7 0 11 8 11 8a18.5 18.5 0 01-2.16 3.19m-6.72-1.07a3 3 0 11-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/></svg>
                  : <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
                }
              </button>
            </div>
          </div>

          {error && error !== 'NOT_REGISTERED' && (
            <div className="alert alert-error">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/>
              </svg>
              {error}
            </div>
          )}

          <button type="submit" className="btn btn-primary btn-full" disabled={loading}>
            {loading ? <><span className="spinner"/>Signing in…</> : 'Sign In'}
          </button>
        </form>

        {error === 'NOT_REGISTERED' && (
          <div className="ussd-card">
            <div className="ussd-header">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#f59e0b" strokeWidth="2">
                <path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/>
                <line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>
              </svg>
              <strong>Phone number not registered</strong>
            </div>
            <p className="ussd-text">You can register directly here or via USSD on your phone:</p>
            <div className="ussd-code">*384*41992#</div>
            <Link to="/register" className="btn btn-primary btn-full" style={{ marginTop: 8 }}>
              Register here instead →
            </Link>
          </div>
        )}

        <div className="login-divider"><span>or</span></div>

        <Link to="/register" className="btn btn-outline btn-full">
          Create a new account
        </Link>

        <p className="login-footer">
          MedCall uses AI to assist with medical consultations.<br/>
          <span className="text-muted">Always consult a real doctor for emergencies.</span>
        </p>
      </div>
    </div>
  )
}
