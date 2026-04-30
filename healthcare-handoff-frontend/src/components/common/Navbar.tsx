import React from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { LogOut, Home, Users, ClipboardList } from 'lucide-react'
import { useAuth } from '../../hooks/useAuth'

export const Navbar: React.FC = () => {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  if (!user) return null

  return (
    <nav className="bg-white shadow-md sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-2">
          <ClipboardList className="text-blue-600" size={32} />
          <span className="text-2xl font-bold text-blue-600">HandoffPro</span>
        </Link>

        <div className="flex items-center gap-6">
          <Link
            to="/"
            className="flex items-center gap-1 text-gray-700 hover:text-blue-600"
          >
            <Home size={20} /> Dashboard
          </Link>
          <Link
            to="/patients"
            className="flex items-center gap-1 text-gray-700 hover:text-blue-600"
          >
            <Users size={20} /> Patients
          </Link>
          <Link
            to="/handoffs"
            className="flex items-center gap-1 text-gray-700 hover:text-blue-600"
          >
            <ClipboardList size={20} /> Handoffs
          </Link>
        </div>

        <div className="flex items-center gap-4">
          <span className="text-sm text-gray-700">
            {user.email} <span className="badge-info">{user.role}</span>
          </span>
          <button
            onClick={handleLogout}
            className="flex items-center gap-1 text-red-600 hover:text-red-700"
          >
            <LogOut size={20} /> Logout
          </button>
        </div>
      </div>
    </nav>
  )
}