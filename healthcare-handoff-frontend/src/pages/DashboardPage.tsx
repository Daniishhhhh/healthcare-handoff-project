import React, { useState, useEffect } from 'react'
import { Navbar } from '../components/common/Navbar'
import { useAuth } from '../hooks/useAuth'
import { useToast } from '../hooks/useToast'
import apiClient from '../api/client'
import { Handoff, Patient } from '../types'
import { HandoffCard } from '../components/handoffs/HandoffCard'
import { Users, ClipboardList, AlertCircle } from 'lucide-react'

export const DashboardPage: React.FC = () => {
  const { user } = useAuth()
  const { addToast } = useToast()
  const [stats, setStats] = useState({
    totalPatients: 0,
    totalHandoffs: 0,
    readyHandoffs: 0,
    escalatedHandoffs: 0,
  })
  const [recentHandoffs, setRecentHandoffs] = useState<Handoff[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    loadDashboardData()
  }, [])

  const loadDashboardData = async () => {
    try {
      const patients = await apiClient.listPatients()
      setStats((prev) => ({ ...prev, totalPatients: patients.length }))
    } catch (error: any) {
      addToast('Failed to load dashboard', 'error')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <>
      <Navbar />
      <div className="max-w-7xl mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-8">Welcome, {user?.email}!</h1>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Total Patients</p>
                <p className="text-3xl font-bold">{stats.totalPatients}</p>
              </div>
              <Users className="text-blue-600" size={32} />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Total Handoffs</p>
                <p className="text-3xl font-bold">{stats.totalHandoffs}</p>
              </div>
              <ClipboardList className="text-green-600" size={32} />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Ready for Review</p>
                <p className="text-3xl font-bold">{stats.readyHandoffs}</p>
              </div>
              <ClipboardList className="text-orange-600" size={32} />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Escalated</p>
                <p className="text-3xl font-bold">{stats.escalatedHandoffs}</p>
              </div>
              <AlertCircle className="text-red-600" size={32} />
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <h2 className="text-xl font-bold mb-4">Quick Stats</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-blue-50 p-4 rounded">
              <p className="text-sm text-gray-600">Your Role</p>
              <p className="text-lg font-semibold text-blue-600">{user?.role.toUpperCase()}</p>
            </div>
            <div className="bg-green-50 p-4 rounded">
              <p className="text-sm text-gray-600">Member Since</p>
              <p className="text-lg font-semibold text-green-600">
                {new Date().toLocaleDateString()}
              </p>
            </div>
            <div className="bg-purple-50 p-4 rounded">
              <p className="text-sm text-gray-600">System Status</p>
              <p className="text-lg font-semibold text-purple-600">Operational</p>
            </div>
          </div>
        </div>

        {/* Info Box */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h3 className="font-semibold text-blue-900 mb-2">Getting Started</h3>
          <ul className="text-sm text-blue-800 space-y-1">
            <li>• Create patients and manage their medical records</li>
            <li>• Create handoffs to transfer care responsibilities</li>
            <li>• Add tasks and set follow-up deadlines</li>
            <li>• Check readiness before accepting handoffs</li>
            <li>• Escalate when urgent intervention is needed</li>
          </ul>
        </div>
      </div>
    </>
  )
}