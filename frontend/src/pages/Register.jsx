import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { apiPost } from '../api/client'
import { useAuth } from '../context/AuthContext'

// ── Constants ─────────────────────────────────────────────────────────────────
const BLOOD_TYPES = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
const GENDERS     = [{ value: 'M', label: 'Male' }, { value: 'F', label: 'Female' }, { value: 'Other', label: 'Other' }]
const LANGUAGES   = ['English', 'French', 'Swahili', 'Kinyarwanda', 'Luganda', 'Amharic', 'Arabic', 'Lingala', 'Other']

const STEPS = [
  { id: 1, title: 'Account',  icon: '👤', desc: 'Basic info & PIN' },
  { id: 2, title: 'Personal', icon: '🏠', desc: 'Personal details' },
  { id: 3, title: 'Medical',  icon: '🩺', desc: 'Health information' },
]

// ── Progress bar ──────────────────────────────────────────────────────────────
function StepIndicator({ current }) {
  return (
    <div className="step-indicator">
      {STEPS.map((s, i) => (
        <div key={s.id} className="step-item">
          <div className={`step-circle ${current === s.id ? 'step-active' : current > s.id ? 'step-done' : ''}`}>
            {current > s.id
              ? <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="3"><polyline points="20 6 9 17 4 12"/></svg>
              : s.icon}
          </div>
          <span className={`step-label ${current === s.id ? 'step-label-active' : ''}`}>{s.title}</span>
          {i < STEPS.length - 1 && <div className={`step-line ${current > s.id ? 'step-line-done' : ''}`} />}
        </div>
      ))}
    </div>
  )
}

// ── Step 1: Account ───────────────────────────────────────────────────────────
function Step1({ onDone }) {
  const { login } = useAuth()
  const [form, setForm]     = useState({ first_name: '', last_name: '', phone_number: '', email_address: '', pin: '', confirm_pin: '' })
  const [showPin, setShowPin]     = useState(false)
  const [showConfirm, setShowConfirm] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError]     = useState('')

  const set = (k, v) => setForm(f => ({ ...f, [k]: v }))

  const submit = async (e) => {
    e.preventDefault()
    setError('')
    if (form.pin.length < 6)   { setError('PIN must be at least 6 digits.'); return }
    if (form.pin !== form.confirm_pin) { setError('PINs do not match.'); return }
    setLoading(true)
    try {
      const data = await apiPost('/auth/register', {
        first_name: form.first_name,
        last_name:  form.last_name,
        phone_number: form.phone_number,
        email_address: form.email_address || null,
        pin: form.pin,
        confirm_pin: form.confirm_pin,
      })
      login(data.access_token, {
        patientId:   data.patient_id,
        firstName:   data.first_name,
        lastName:    data.last_name,
        phoneNumber: data.phone_number,
        hasPersonalInfo: data.has_personal_info,
        hasMedicalInfo:  data.has_medical_info,
      })
      onDone()
    } catch (err) {
      setError(err.message || 'Registration failed.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <form className="reg-form" onSubmit={submit}>
      <div className="reg-row">
        <div className="form-group">
          <label className="form-label">First Name *</label>
          <input className="form-input" placeholder="John" value={form.first_name}
            onChange={e => set('first_name', e.target.value)} required disabled={loading} />
        </div>
        <div className="form-group">
          <label className="form-label">Last Name *</label>
          <input className="form-input" placeholder="Doe" value={form.last_name}
            onChange={e => set('last_name', e.target.value)} required disabled={loading} />
        </div>
      </div>

      <div className="form-group">
        <label className="form-label">Phone Number *</label>
        <input className="form-input" type="tel" placeholder="+250 7XX XXX XXX"
          value={form.phone_number} onChange={e => set('phone_number', e.target.value)}
          required disabled={loading} />
      </div>

      <div className="form-group">
        <label className="form-label">Email Address <span className="optional">(optional)</span></label>
        <input className="form-input" type="email" placeholder="john@example.com"
          value={form.email_address} onChange={e => set('email_address', e.target.value)} disabled={loading} />
      </div>

      <div className="reg-row">
        <div className="form-group">
          <label className="form-label">PIN * <span className="optional">(min 6 digits)</span></label>
          <div className="input-wrapper">
            <input className="form-input" type={showPin ? 'text' : 'password'}
              placeholder="••••••" inputMode="numeric" maxLength={8}
              value={form.pin} onChange={e => set('pin', e.target.value)} required disabled={loading} />
            <button type="button" className="input-eye" onClick={() => setShowPin(v => !v)}>
              {showPin ? <EyeOff /> : <Eye />}
            </button>
          </div>
        </div>
        <div className="form-group">
          <label className="form-label">Confirm PIN *</label>
          <div className="input-wrapper">
            <input className="form-input" type={showConfirm ? 'text' : 'password'}
              placeholder="••••••" inputMode="numeric" maxLength={8}
              value={form.confirm_pin} onChange={e => set('confirm_pin', e.target.value)} required disabled={loading} />
            <button type="button" className="input-eye" onClick={() => setShowConfirm(v => !v)}>
              {showConfirm ? <EyeOff /> : <Eye />}
            </button>
          </div>
        </div>
      </div>

      {error && <div className="alert alert-error"><ErrIcon />{error}</div>}

      <button className="btn btn-primary btn-full" type="submit" disabled={loading}>
        {loading ? <><span className="spinner"/>Creating account…</> : 'Create Account & Continue →'}
      </button>
    </form>
  )
}

// ── Step 2: Personal Info ─────────────────────────────────────────────────────
function Step2({ onDone }) {
  const [form, setForm] = useState({
    age: '', gender: '', nationality: '', country_of_residence: '', city_of_residence: '',
    address: '', next_of_kin: '', next_of_kin_phone_number: '', patient_next_relationship: '', preferred_language: ''
  })
  const [loading, setLoading] = useState(false)
  const [error, setError]     = useState('')
  const set = (k, v) => setForm(f => ({ ...f, [k]: v }))

  const submit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await apiPost('/auth/register/personal', {
        ...form,
        age: parseInt(form.age, 10),
        next_of_kin: form.next_of_kin || null,
        next_of_kin_phone_number: form.next_of_kin_phone_number || null,
        patient_next_relationship: form.patient_next_relationship || null,
      })
      onDone()
    } catch (err) {
      setError(err.message || 'Failed to save personal info.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <form className="reg-form" onSubmit={submit}>
      <div className="reg-row">
        <div className="form-group">
          <label className="form-label">Age *</label>
          <input className="form-input" type="number" placeholder="25" min={1} max={120}
            value={form.age} onChange={e => set('age', e.target.value)} required disabled={loading} />
        </div>
        <div className="form-group">
          <label className="form-label">Gender *</label>
          <select className="form-input form-select" value={form.gender}
            onChange={e => set('gender', e.target.value)} required disabled={loading}>
            <option value="">Select gender</option>
            {GENDERS.map(g => <option key={g.value} value={g.value}>{g.label}</option>)}
          </select>
        </div>
      </div>

      <div className="reg-row">
        <div className="form-group">
          <label className="form-label">Nationality *</label>
          <input className="form-input" placeholder="Rwandan" value={form.nationality}
            onChange={e => set('nationality', e.target.value)} required disabled={loading} />
        </div>
        <div className="form-group">
          <label className="form-label">Preferred Language *</label>
          <select className="form-input form-select" value={form.preferred_language}
            onChange={e => set('preferred_language', e.target.value)} required disabled={loading}>
            <option value="">Select language</option>
            {LANGUAGES.map(l => <option key={l} value={l}>{l}</option>)}
          </select>
        </div>
      </div>

      <div className="reg-row">
        <div className="form-group">
          <label className="form-label">Country of Residence *</label>
          <input className="form-input" placeholder="Rwanda" value={form.country_of_residence}
            onChange={e => set('country_of_residence', e.target.value)} required disabled={loading} />
        </div>
        <div className="form-group">
          <label className="form-label">City *</label>
          <input className="form-input" placeholder="Kigali" value={form.city_of_residence}
            onChange={e => set('city_of_residence', e.target.value)} required disabled={loading} />
        </div>
      </div>

      <div className="form-group">
        <label className="form-label">Full Address *</label>
        <input className="form-input" placeholder="KG 123 St, Kigali" value={form.address}
          onChange={e => set('address', e.target.value)} required disabled={loading} />
      </div>

      <div className="reg-section-title">Next of Kin <span className="optional">(optional)</span></div>

      <div className="reg-row">
        <div className="form-group">
          <label className="form-label">Full Name</label>
          <input className="form-input" placeholder="Jane Doe" value={form.next_of_kin}
            onChange={e => set('next_of_kin', e.target.value)} disabled={loading} />
        </div>
        <div className="form-group">
          <label className="form-label">Relationship</label>
          <input className="form-input" placeholder="Sister" value={form.patient_next_relationship}
            onChange={e => set('patient_next_relationship', e.target.value)} disabled={loading} />
        </div>
      </div>

      <div className="form-group">
        <label className="form-label">Next of Kin Phone</label>
        <input className="form-input" type="tel" placeholder="0789 XXX XXX" value={form.next_of_kin_phone_number}
          onChange={e => set('next_of_kin_phone_number', e.target.value)} disabled={loading} />
      </div>

      {error && <div className="alert alert-error"><ErrIcon />{error}</div>}

      <div className="reg-actions">
        <button type="submit" className="btn btn-primary" disabled={loading}>
          {loading ? <><span className="spinner"/>Saving…</> : 'Save & Continue →'}
        </button>
      </div>
    </form>
  )
}

// ── Step 3: Medical Info ──────────────────────────────────────────────────────
function Step3({ onDone }) {
  const [form, setForm] = useState({ blood_type: '', allergies: '', chronic_illness: '', recent_vaccination: '' })
  const [loading, setLoading] = useState(false)
  const [error, setError]     = useState('')
  const set = (k, v) => setForm(f => ({ ...f, [k]: v }))

  const submit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await apiPost('/auth/register/medical', {
        blood_type: form.blood_type,
        allergies: form.allergies || null,
        chronic_illness: form.chronic_illness || null,
        recent_vaccination: form.recent_vaccination || null,
      })
      onDone()
    } catch (err) {
      setError(err.message || 'Failed to save medical info.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <form className="reg-form" onSubmit={submit}>
      <div className="form-group">
        <label className="form-label">Blood Type *</label>
        <div className="blood-type-grid">
          {BLOOD_TYPES.map(bt => (
            <button key={bt} type="button"
              className={`blood-btn ${form.blood_type === bt ? 'blood-btn-active' : ''}`}
              onClick={() => set('blood_type', bt)} disabled={loading}>
              {bt}
            </button>
          ))}
        </div>
      </div>

      <div className="form-group">
        <label className="form-label">Allergies <span className="optional">(optional)</span></label>
        <textarea className="form-input form-textarea" rows={2}
          placeholder="e.g. Penicillin, Peanuts, Latex…"
          value={form.allergies} onChange={e => set('allergies', e.target.value)} disabled={loading} />
      </div>

      <div className="form-group">
        <label className="form-label">Chronic Illnesses <span className="optional">(optional)</span></label>
        <textarea className="form-input form-textarea" rows={2}
          placeholder="e.g. Diabetes, Hypertension, Asthma…"
          value={form.chronic_illness} onChange={e => set('chronic_illness', e.target.value)} disabled={loading} />
      </div>

      <div className="form-group">
        <label className="form-label">Recent Vaccinations <span className="optional">(optional)</span></label>
        <textarea className="form-input form-textarea" rows={2}
          placeholder="e.g. COVID-19 (2023), Yellow Fever (2022)…"
          value={form.recent_vaccination} onChange={e => set('recent_vaccination', e.target.value)} disabled={loading} />
      </div>

      {error && <div className="alert alert-error"><ErrIcon />{error}</div>}

      <div className="reg-actions">
        <button type="submit" className="btn btn-primary" disabled={loading || !form.blood_type}>
          {loading ? <><span className="spinner"/>Saving…</> : 'Complete Registration ✓'}
        </button>
      </div>
    </form>
  )
}

// ── Small icon components ─────────────────────────────────────────────────────
const Eye    = () => <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
const EyeOff = () => <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M17.94 17.94A10.07 10.07 0 0112 20c-7 0-11-8-11-8a18.45 18.45 0 015.06-5.94M9.9 4.24A9.12 9.12 0 0112 4c7 0 11 8 11 8a18.5 18.5 0 01-2.16 3.19m-6.72-1.07a3 3 0 11-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/></svg>
const ErrIcon = () => <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>

// ── Main Register page ─────────────────────────────────────────────────────────
export default function Register() {
  const navigate  = useNavigate()
  const { updateUser } = useAuth()
  const [step, setStep] = useState(1)

  const finishStep1 = () => setStep(2)
  const finishStep2 = () => { updateUser({ hasPersonalInfo: true }); setStep(3) }
  const finishStep3 = () => { updateUser({ hasMedicalInfo: true }); navigate('/chat') }

  return (
    <div className="login-container">
      <div className="login-card reg-card">
        <div className="login-logo" style={{ marginBottom: 20 }}>
          <div className="logo-icon">
            <svg width="40" height="40" viewBox="0 0 40 40" fill="none">
              <rect width="40" height="40" rx="12" fill="#1a73e8"/>
              <path d="M20 8v24M8 20h24" stroke="white" strokeWidth="4" strokeLinecap="round"/>
            </svg>
          </div>
          <h1 className="login-title">Create Account</h1>
          <p className="login-subtitle">Join MedCall in 3 easy steps</p>
        </div>

        <StepIndicator current={step} />

        <div className="step-header">
          <h2 className="step-title">{STEPS[step-1].icon} {STEPS[step-1].title}</h2>
          <p className="step-desc">{STEPS[step-1].desc}</p>
        </div>

        {step === 1 && <Step1 onDone={finishStep1} />}
        {step === 2 && <Step2 onDone={finishStep2} />}
        {step === 3 && <Step3 onDone={finishStep3} />}

        {step === 1 && (
          <p className="login-footer" style={{ marginTop: 16 }}>
            Already have an account?{' '}
            <Link to="/login" className="link">Sign in</Link>
          </p>
        )}
      </div>
    </div>
  )
}
