import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import medcallLogo from '../assets/medcall-logo.svg'
import medcallIcon from '../assets/medcall-icon.svg'

/* ── Shared small components ─────────────────────────────────────────────── */

function NavBar() {
  const { user } = useAuth()
  return (
    <header className="home-nav">
      <div className="home-nav-inner">
        <Link to="/" className="home-nav-logo">
          <img src={medcallLogo} alt="MedCall" className="home-nav-logo-img" />
        </Link>
        <nav className="home-nav-links">
          <a href="#how" className="home-nav-link">How it works</a>
          <a href="#impact" className="home-nav-link">Impact</a>
          <a href="#about" className="home-nav-link">About</a>
        </nav>
        <div className="home-nav-cta">
          {user ? (
            <Link to="/chat" className="btn btn-primary">Open App</Link>
          ) : (
            <>
              <Link to="/login"    className="btn btn-ghost-nav">Sign In</Link>
              <Link to="/register" className="btn btn-primary">Get Started</Link>
            </>
          )}
        </div>
      </div>
    </header>
  )
}

function StatCard({ value, label }) {
  return (
    <div className="stat-card">
      <span className="stat-value">{value}</span>
      <span className="stat-label">{label}</span>
    </div>
  )
}

function FeatureCard({ icon, title, desc }) {
  return (
    <div className="feature-card">
      <div className="feature-icon">{icon}</div>
      <h3 className="feature-title">{title}</h3>
      <p className="feature-desc">{desc}</p>
    </div>
  )
}

function StepCard({ number, title, desc }) {
  return (
    <div className="step-card">
      <div className="step-number">{number}</div>
      <div>
        <h4 className="step-title">{title}</h4>
        <p className="step-desc">{desc}</p>
      </div>
    </div>
  )
}

function ImpactCard({ emoji, title, desc }) {
  return (
    <div className="impact-card">
      <span className="impact-emoji">{emoji}</span>
      <h4 className="impact-title">{title}</h4>
      <p className="impact-desc">{desc}</p>
    </div>
  )
}

function UserCard({ emoji, title, desc }) {
  return (
    <div className="user-card">
      <span className="user-card-emoji">{emoji}</span>
      <h4 className="user-card-title">{title}</h4>
      <p className="user-card-desc">{desc}</p>
    </div>
  )
}

/* ── Main Page ───────────────────────────────────────────────────────────── */
export default function Home() {
  return (
    <div className="home-page">
      <NavBar />

      {/* ══ HERO ══════════════════════════════════════════════════════════ */}
      <section className="home-hero">
        <div className="home-hero-bg" aria-hidden="true" />
        <div className="home-container">
          <div className="hero-badge">
            <span className="hero-badge-dot" />
            AI-Powered Clinical Assistant
          </div>
          <h1 className="hero-title">
            Healthcare Intelligence<br/>
            <span className="hero-title-accent">for Africa</span>
          </h1>
          <p className="hero-subtitle">
            A telemedicine platform that works on basic phones via USSD &amp; SMS — no smartphone
            or internet required. MedCall connects rural and low-income patients across Africa
            to AI-powered consultations, early symptom detection, and qualified health facilities.
          </p>
          <div className="hero-actions">
            <Link to="/register" className="btn btn-hero-primary">
              Get Started Free
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                <line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/>
              </svg>
            </Link>
            <a href="#how" className="btn btn-hero-ghost">
              See How It Works
            </a>
          </div>
          <div className="hero-stats">
            <StatCard value="80%+" label="Lagos residents &gt;5km from care*" />
            <StatCard value="97.9%" label="Uninsured in urban Lagos*" />
            <StatCard value="USSD + Web" label="Works on any phone" />
            <StatCard value="8 Countries" label="East Africa covered" />
          </div>
        </div>
      </section>

      {/* ══ PROBLEM ═══════════════════════════════════════════════════════ */}
      <section className="pds-section" id="problem">
        <div className="home-container">

          {/* Header */}
          <div className="pds-header">
            <div className="pds-label">The Problem</div>
            <h2 className="pds-title">Millions across Africa cannot access basic healthcare</h2>
            <p className="pds-lead">
              Across sub-Saharan Africa, rural communities face a healthcare crisis rooted in broken
              infrastructure, chronic shortages of medical professionals, and deep inequalities in
              access. In Lagos, millions face this reality every day — and it repeats across the continent.
            </p>
          </div>

          {/* Stat spotlight row */}
          <div className="pds-stats">
            <div className="pds-stat">
              <span className="pds-stat-num">80%+</span>
              <span className="pds-stat-text">of Lagos residents travel 6–10 km to reach the nearest healthcare facility</span>
              <span className="pds-stat-src">piph.org</span>
            </div>
            <div className="pds-stat-sep" />
            <div className="pds-stat">
              <span className="pds-stat-num">97.9%</span>
              <span className="pds-stat-text">of urban Lagos residents have no health insurance coverage</span>
              <span className="pds-stat-src">piph.org</span>
            </div>
            <div className="pds-stat-sep" />
            <div className="pds-stat">
              <span className="pds-stat-num">1B+</span>
              <span className="pds-stat-text">people across sub-Saharan Africa without adequate healthcare access</span>
              <span className="pds-stat-src">WHO Global Health Observatory</span>
            </div>
          </div>

          {/* Narrative */}
          <div className="pds-narrative">
            <p>
              Countries like Nigeria, Ethiopia, Tanzania, and Sudan face critical shortages of
              medical professionals — leaving <strong>hundreds of millions</strong> without timely
              access to qualified care.
            </p>
            <p>
              Without accessible medical guidance, communities turn to{' '}
              <strong>self-medication and traditional medicine</strong> — practices that are often
              unreliable, ineffective at early detection, and unable to manage chronic or acute
              conditions safely. The cost is measured in <strong>preventable deaths</strong>,
              late-stage diagnoses, and lives diminished by conditions that could have been caught early.
            </p>
            <p>
              Existing digital health solutions worsen the gap: they require high-speed internet,
              smartphones, and advanced digital literacy —{' '}
              <strong>placing them entirely out of reach</strong> for the populations that need
              them most.
            </p>
          </div>

          {/* Problem cards */}
          <div className="pds-grid">
            {[
              {
                num: '01', color: '#ef4444',
                title: 'Inaccessible facilities',
                desc: 'Over 80% of Lagos residents travel 6–10 km to reach a healthcare facility. Long distances and inadequate transport make in-person care unreachable for millions.',
              },
              {
                num: '02', color: '#f59e0b',
                title: 'Critical doctor shortage',
                desc: 'With 97.9% of Lagos residents uninsured and 46.8% spending over 20% of their income on healthcare, cost remains a decisive barrier to seeking care.',
              },
              {
                num: '03', color: '#f97316',
                title: 'Dangerous self-medication',
                desc: 'In the absence of professional guidance, families rely on unregulated drugs and informal remedies, leading to misdiagnosis, treatment delays, and preventable deaths.',
              },
              {
                num: '04', color: '#6366f1',
                title: 'Digital solutions fall short',
                desc: 'Most health apps require smartphones and reliable internet. In rural Africa, where feature phones and USSD are the norm, these platforms are functionally inaccessible.',
              },
            ].map(card => (
              <div key={card.title} className="pds-card" style={{ '--card-accent': card.color }}>
                <span className="pds-card-num">{card.num}</span>
                <h4 className="pds-card-title">{card.title}</h4>
                <p className="pds-card-desc">{card.desc}</p>
              </div>
            ))}
          </div>

          {/* Callout */}
          <div className="pds-callout">
            <div className="pds-callout-bar" />
            <div className="pds-callout-body">
              <p className="pds-callout-heading">There is an urgent need</p>
              <p className="pds-callout-text">
                Accessible, affordable systems that empower rural and low-to-middle-income populations
                to identify early symptoms, receive medical guidance, and connect with qualified
                doctors — quickly, easily, and <strong>without needing a smartphone or internet</strong>.
              </p>
            </div>
          </div>

          <p className="pds-sources">
            Sources: GRID3 (2022); MexicoHistorico.com (2025); WHO Global Health Observatory.
          </p>
        </div>
      </section>

      {/* ══ SOLUTION ══════════════════════════════════════════════════════ */}
      <section className="home-section" id="solution">
        <div className="home-container">
          <div className="section-label">The Solution</div>
          <h2 className="section-title">Meet MedCall</h2>
          <p className="section-sub">
            A telemedicine platform built for Africa — accessible via <strong>USSD and SMS on
            any basic phone</strong>, with a full web app for those who have internet. No smartphone,
            no data plan, no advanced digital skills required.
          </p>
          <div className="solution-channels">
            <div className="channel-card channel-ussd">
              <div className="channel-icon">📟</div>
              <h4>USSD &amp; SMS</h4>
              <p>Dial <strong>*384*41992#</strong> on any mobile phone. No internet, no app, no smartphone needed. Works anywhere there is a mobile signal.</p>
              <span className="channel-tag">Primary channel</span>
            </div>
            <div className="channel-card channel-web">
              <div className="channel-icon">🌐</div>
              <h4>Web App</h4>
              <p>A full-featured web platform for patients and providers with internet access — with AI chat, consultation history, and health reports.</p>
              <span className="channel-tag">You are here</span>
            </div>
          </div>
          <div className="features-grid" style={{ marginTop: '32px' }}>
            <FeatureCard icon="🩺" title="AI-Guided Consultations"   desc="Patients describe their symptoms step-by-step. MedCall's AI collects, structures, and interprets the information just like a trained triage nurse." />
            <FeatureCard icon="🧠" title="Symptom Analysis"          desc="Three specialized AI agents analyze every consultation — detecting possible conditions, risk levels, and recommended exams." />
            <FeatureCard icon="⚡" title="Clinical Decisions"         desc="Receive urgency ratings, recommended actions (self-care, clinic visit, or emergency), and referral guidance in real time." />
            <FeatureCard icon="📍" title="Location-aware Referrals"  desc="MedCall finds the nearest appropriate health facility based on the patient's location across 8 East African countries." />
            <FeatureCard icon="🗂️" title="Full Consultation History"  desc="Every consultation — including AI analysis and clinical decisions — is saved and accessible for continuity of care." />
            <FeatureCard icon="📊" title="Structured Health Data"     desc="Patient data is automatically cleaned and stored, enabling healthcare providers and systems to track trends over time." />
          </div>
        </div>
      </section>

      {/* ══ HOW IT WORKS ══════════════════════════════════════════════════ */}
      <section className="home-section home-section-alt" id="how">
        <div className="home-container">
          <div className="section-label">How It Works</div>
          <h2 className="section-title">From symptom to decision in 5 steps</h2>
          <div className="steps-grid">
            <StepCard number="01" title="Patient submits symptoms"          desc="Via the MedCall app or SMS — no high-end device required." />
            <StepCard number="02" title="MedCall verifies and cleans data"  desc="Patient identity is confirmed and input is structured before analysis." />
            <StepCard number="03" title="AI analyzes the consultation"      desc="Three agents work in parallel: consultation, symptom analysis, and clinical decision." />
            <StepCard number="04" title="Insights and decisions generated" desc="Risk level, possible conditions, recommended exams, and urgency rating — all in one report." />
            <StepCard number="05" title="Data stored for follow-up"         desc="Every consultation is saved with full history, enabling continuity of care over time." />
          </div>
        </div>
      </section>

      {/* ══ IMPACT ════════════════════════════════════════════════════════ */}
      <section className="home-section" id="impact">
        <div className="home-container">
          <div className="section-label">Impact</div>
          <h2 className="section-title">Built to transform healthcare delivery</h2>
          <div className="impact-grid">
            <ImpactCard emoji="🏥" title="Higher efficiency"         desc="Reduce time spent per consultation, freeing providers to see more patients without sacrificing quality." />
            <ImpactCard emoji="🌐" title="Expanded reach"            desc="SMS-based access brings clinical intelligence to rural and underserved populations with basic phones." />
            <ImpactCard emoji="📉" title="Reduced burnout"           desc="Automating repetitive consultation analysis lets doctors focus on complex cases that truly need their expertise." />
            <ImpactCard emoji="📊" title="Data-driven systems"       desc="Structured health data enables governments and NGOs to identify patterns, allocate resources, and plan interventions." />
            <ImpactCard emoji="👩🏾‍⚕️" title="Better quality of care"  desc="Standardized AI analysis reduces variability in clinical decisions and helps catch conditions earlier." />
            <ImpactCard emoji="🔗" title="Seamless referrals"        desc="Location-aware referral recommendations reduce delays and connect patients to the right level of care faster." />
          </div>
        </div>
      </section>

      {/* ══ WHO IT'S FOR ══════════════════════════════════════════════════ */}
      <section className="home-section home-section-alt">
        <div className="home-container">
          <div className="section-label">Who It's For</div>
          <h2 className="section-title">Built for patients first — and everyone around them</h2>
          <p className="section-sub">
            MedCall's primary beneficiary is the <strong>patient</strong> — particularly those in
            rural and underserved communities who have long been excluded from quality healthcare.
          </p>

          {/* Primary beneficiary — full-width hero card */}
          <div className="primary-user-card">
            <div className="primary-user-badge">Primary Beneficiary</div>
            <div className="primary-user-content">
              <div className="primary-user-left">
                <span className="primary-user-emoji">🧑🏾‍🤝‍🧑🏿</span>
                <h3 className="primary-user-title">Patients — Rural &amp; Low-income Communities</h3>
                <p className="primary-user-desc">
                  MedCall exists for the patient who lives hours from the nearest clinic, cannot
                  afford a doctor's visit, or has never had access to structured medical guidance.
                  Using nothing more than a basic mobile phone, they can describe their symptoms,
                  receive an AI-guided consultation, get a clinical recommendation, and be connected
                  to a nearby health facility — all without a smartphone or internet connection.
                </p>
                <ul className="primary-user-list">
                  <li>✅ Dial <strong>*384*41992#</strong> on any phone — no data or app required</li>
                  <li>✅ Receive symptom guidance and urgency assessment instantly</li>
                  <li>✅ Get referred to the nearest appropriate clinic or hospital</li>
                  <li>✅ Keep a full personal health record accessible at any time</li>
                </ul>
              </div>
            </div>
          </div>

          {/* Secondary beneficiaries */}
          <p className="secondary-users-label">Also serving</p>
          <div className="users-grid">
            <UserCard emoji="🏨" title="Clinics &amp; Hospitals"   desc="Receive pre-structured consultation data and AI triage summaries before the patient even arrives." />
            <UserCard emoji="👩🏾‍⚕️" title="Community Health Workers" desc="Use MedCall in the field to document patient encounters, flag emergencies, and coordinate referrals — with or without internet." />
            <UserCard emoji="❤️" title="Health NGOs"              desc="Deploy MedCall-powered programs for populations in humanitarian or remote settings without digital infrastructure." />
            <UserCard emoji="🏛️" title="Government Health Programs" desc="Aggregate structured health data to inform national policy, resource allocation, and epidemic surveillance." />
          </div>
        </div>
      </section>

      {/* ══ VISION ════════════════════════════════════════════════════════ */}
      <section className="home-vision" id="about">
        <div className="home-container">
          <div className="vision-card">
            <div className="vision-label">Our Vision</div>
            <blockquote className="vision-quote">
              "To become the <strong>AI infrastructure layer for healthcare in Africa</strong> —
              powering how patient consultations are processed, analyzed, and used across the continent."
            </blockquote>
            <p className="vision-sub">
              We believe every patient in Africa deserves the same quality of clinical intelligence
              available in the world's leading hospitals. MedCall is how we get there.
            </p>
            <div className="vision-actions">
              <Link to="/register" className="btn btn-hero-primary">
                Start Your Free Account
              </Link>
              <Link to="/login" className="btn btn-hero-ghost">
                Sign In
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* ══ FOOTER ════════════════════════════════════════════════════════ */}
      <footer className="home-footer">
        <div className="home-container">
          <div className="footer-inner">
            <div className="footer-brand">
              <img src={medcallIcon} alt="MedCall" className="footer-brand-icon" />
              <span>MedCall</span>
            </div>
            <p className="footer-tagline">AI-powered clinical intelligence for Africa.</p>
            <p className="footer-note">
              MedCall is a decision-support tool. It does not replace professional medical advice.
              Always consult a qualified healthcare provider for medical emergencies.
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}
