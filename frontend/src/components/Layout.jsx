import { useState } from 'react'
import { Outlet, NavLink } from 'react-router-dom'
import medcallIcon from '../assets/medcall-icon.svg'
import medcallLogo from '../assets/medcall-logo.svg'
import { useAuth } from '../context/AuthContext'
import { useToast } from '../context/ToastContext'
import ChangePasswordModal from './ChangePasswordModal'
import NotificationBell   from './NotificationBell'

function ProfileMenu({ user, onChangePwd, onLogout }) {
  const [open, setOpen] = useState(false)
  return (
    <div className="profile-menu-wrapper">
      <button className="sidebar-user" onClick={() => setOpen(v => !v)}>
        <div className="user-avatar">
          {user?.firstName?.[0]}{user?.lastName?.[0]}
        </div>
        <div className="user-info">
          <p className="user-name">{user?.firstName} {user?.lastName}</p>
          <p className="user-phone">{user?.phoneNumber}</p>
        </div>
        <svg className={`profile-chevron ${open ? 'profile-chevron-up' : ''}`}
          width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
          <polyline points="6 9 12 15 18 9"/>
        </svg>
      </button>

      {open && (
        <div className="profile-dropdown">
          <div className="profile-dropdown-header">
            <p className="profile-dropdown-name">{user?.firstName} {user?.lastName}</p>
            <p className="profile-dropdown-phone">{user?.phoneNumber}</p>
          </div>
          <div className="profile-dropdown-divider" />
          <button className="profile-dropdown-item" onClick={() => { setOpen(false); onChangePwd() }}>
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
              <path d="M7 11V7a5 5 0 0110 0v4"/>
            </svg>
            Change PIN
          </button>
          <div className="profile-dropdown-divider" />
          <button className="profile-dropdown-item profile-dropdown-logout" onClick={() => { setOpen(false); onLogout() }}>
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4"/>
              <polyline points="16 17 21 12 16 7"/>
              <line x1="21" y1="12" x2="9" y2="12"/>
            </svg>
            Sign Out
          </button>
        </div>
      )}
    </div>
  )
}

export default function Layout() {
  const { user, logout } = useAuth()
  const { show }         = useToast()
  const [showChangePwd, setShowChangePwd] = useState(false)

  const handleLogout = () => {
    logout()                            // clears localStorage synchronously
    show('You have been signed out successfully.', 'info', 3000)
    // Brief delay so the toast renders before the hard reload destroys the DOM
    setTimeout(() => window.location.replace('/login'), 400)
  }

  return (
    <div className="app-shell">
      {/* ── Sidebar (desktop) ── */}
      <aside className="sidebar">
        <div className="sidebar-logo">
          <img src={medcallLogo} alt="MedCall" className="sidebar-logo-img" />
        </div>

        <nav className="sidebar-nav">
          <NavLink to="/chat"    className={({ isActive }) => `nav-item ${isActive ? 'nav-item-active' : ''}`}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/>
            </svg>
            <span>Consultation</span>
          </NavLink>
          <NavLink to="/history" className={({ isActive }) => `nav-item ${isActive ? 'nav-item-active' : ''}`}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M12 8v4l3 3"/><circle cx="12" cy="12" r="10"/>
            </svg>
            <span>History</span>
          </NavLink>
        </nav>

        <div className="sidebar-bottom">
          <NotificationBell />
          <ProfileMenu user={user} onChangePwd={() => setShowChangePwd(true)} onLogout={handleLogout} />
        </div>
      </aside>

      {/* ── Main content ── */}
      <main className="main-content">
        <Outlet />
      </main>

      {/* ── Bottom nav (mobile) ── */}
      <nav className="bottom-nav">
        <NavLink to="/chat"    className={({ isActive }) => `bottom-nav-item ${isActive ? 'bottom-nav-active' : ''}`}>
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/>
          </svg>
          <span>Chat</span>
        </NavLink>
        <NavLink to="/history" className={({ isActive }) => `bottom-nav-item ${isActive ? 'bottom-nav-active' : ''}`}>
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M12 8v4l3 3"/><circle cx="12" cy="12" r="10"/>
          </svg>
          <span>History</span>
        </NavLink>
        <div className="bottom-nav-item bottom-notif-wrap">
          <NotificationBell />
          <span>Alerts</span>
        </div>
        <button className="bottom-nav-item" onClick={() => setShowChangePwd(true)}>
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
            <path d="M7 11V7a5 5 0 0110 0v4"/>
          </svg>
          <span>PIN</span>
        </button>
        <button className="bottom-nav-item" onClick={handleLogout}>
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4"/>
            <polyline points="16 17 21 12 16 7"/>
            <line x1="21" y1="12" x2="9" y2="12"/>
          </svg>
          <span>Logout</span>
        </button>
      </nav>

      {showChangePwd && <ChangePasswordModal onClose={() => setShowChangePwd(false)} />}
    </div>
  )
}
