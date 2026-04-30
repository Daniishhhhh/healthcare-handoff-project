import React from 'react'
import { Link } from 'react-router-dom'
import { LoginForm } from '../components/auth/LoginForm'
import { ClipboardList } from 'lucide-react'

export const LoginPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-xl p-8 w-full max-w-md">
        <div className="flex items-center justify-center gap-2 mb-8">
          <ClipboardList className="text-blue-600" size={32} />
          <h1 className="text-3xl font-bold text-blue-600">HandoffPro</h1>
        </div>

        <h2 className="text-2xl font-bold text-center mb-2">Welcome Back</h2>
        <p className="text-gray-600 text-center mb-8">
          Healthcare Handoff Management System
        </p>

        <LoginForm />

        <div className="mt-6 text-center">
          <p className="text-gray-600">
            Don't have an account?{' '}
            <Link to="/signup" className="text-blue-600 hover:text-blue-700 font-medium">
              Sign up
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}