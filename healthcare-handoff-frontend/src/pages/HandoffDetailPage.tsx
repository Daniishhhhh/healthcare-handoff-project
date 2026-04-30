import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Navbar } from '../components/common/Navbar'
import { Button } from '../components/common/Button'
import { ItemList } from '../components/handoffs/ItemList'
import { ReadinessModal } from '../components/handoffs/ReadinessModal'
import { useToast } from '../hooks/useToast'
import apiClient from '../api/client'
import { Handoff } from '../types'
import { ArrowLeft, AlertCircle, CheckCircle } from 'lucide-react'

export const HandoffDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { addToast } = useToast()
  const [handoff, setHandoff] = useState<Handoff | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [showReadinessModal, setShowReadinessModal] = useState(false)

  useEffect(() => {
    loadHandoff()
  }, [id])

  const loadHandoff = async () => {
    if (!id) return
    try {
      const data = await apiClient.getHandoff(id)
      setHandoff(data)
    } catch (error: any) {
      addToast('Failed to load handoff', 'error')
      navigate('/handoffs')
    } finally {
      setIsLoading(false)
    }
  }

  const handleEscalate = async () => {
    if (!handoff) return
    try {
      await apiClient.escalateHandoff(handoff.id, 'Manual escalation requested')
      addToast('Handoff escalated', 'warning')
      loadHandoff()
    } catch (error: any) {
      addToast('Failed to escalate', 'error')
    }
  }

  const handleComplete = async () => {
    if (!handoff) return
    try {
      await apiClient.completeHandoff(handoff.id)
      addToast('Handoff completed', 'success')
      loadHandoff()
    } catch (error: any) {
      addToast('Failed to complete', 'error')
    }
  }

  if (isLoading) {
    return (
      <>
        <Navbar />
        <div className="max-w-4xl mx-auto px-4 py-8 text-center">
          <p className="text-gray-600">Loading...</p>
        </div>
      </>
    )
  }

  if (!handoff) {
    return (
      <>
        <Navbar />
        <div className="max-w-4xl mx-auto px-4 py-8 text-center">
          <p className="text-gray-600">Handoff not found</p>
        </div>
      </>
    )
  }

  const statusColors = {
    DRAFT: 'bg-blue-50 text-blue-700 border-blue-200',
    PENDING_REVIEW: 'bg-yellow-50 text-yellow-700 border-yellow-200',
    ACCEPTED: 'bg-green-50 text-green-700 border-green-200',
    COMPLETED: 'bg-gray-50 text-gray-700 border-gray-200',
    ESCALATED: 'bg-red-50 text-red-700 border-red-200',
  }

  return (
    <>
      <Navbar />
      <div className="max-w-4xl mx-auto px-4 py-8">
        <button
          onClick={() => navigate('/handoffs')}
          className="flex items-center gap-2 text-blue-600 hover:text-blue-700 mb-6"
        >
          <ArrowLeft size={20} /> Back to Handoffs
        </button>

        {/* Status Header */}
        <div className={`border rounded-lg p-6 mb-6 ${statusColors[handoff.status]}`}>
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold">Patient Handoff</h1>
              <p className="text-sm opacity-75 mt-1">ID: {handoff.id}</p>
            </div>
            <div className="text-right">
              <p className="text-sm opacity-75">Status</p>
              <p className="text-xl font-bold">{handoff.status.replace('_', ' ')}</p>
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-6">
            {/* Diagnosis */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-bold mb-4">Diagnosis & Information</h2>
              <p className="text-gray-700 mb-4">{handoff.diagnosis_summary}</p>

              {handoff.pending_tests && (
                <div className="mb-4">
                  <h3 className="font-semibold text-sm mb-2">Pending Tests</h3>
                  <p className="text-gray-600 text-sm">{handoff.pending_tests}</p>
                </div>
              )}

              {handoff.medication_changes && (
                <div className="mb-4">
                  <h3 className="font-semibold text-sm mb-2">Medication Changes</h3>
                  <p className="text-gray-600 text-sm">{handoff.medication_changes}</p>
                </div>
              )}

              {handoff.additional_notes && (
                <div>
                  <h3 className="font-semibold text-sm mb-2">Additional Notes</h3>
                  <p className="text-gray-600 text-sm">{handoff.additional_notes}</p>
                </div>
              )}
            </div>

            {/* Items */}
            <div className="bg-white rounded-lg shadow p-6">
              <ItemList handoffId={handoff.id} readOnly={handoff.status === 'COMPLETED'} />
            </div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Details */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="font-bold mb-4">Details</h3>
              <div className="space-y-3 text-sm">
                <div>
                  <span className="text-gray-600">Priority</span>
                  <p className={`font-semibold ${
                    handoff.priority === 'CRITICAL' ? 'text-red-600' : 'text-orange-600'
                  }`}>
                    {handoff.priority}
                  </p>
                </div>
                <div>
                  <span className="text-gray-600">Due</span>
                  <p className="font-semibold">
                    {new Date(handoff.follow_up_deadline).toLocaleDateString()}
                  </p>
                </div>
                <div>
                  <span className="text-gray-600">Created</span>
                  <p className="font-semibold">
                    {new Date(handoff.created_at).toLocaleDateString()}
                  </p>
                </div>
              </div>
            </div>

            {/* Readiness */}
            {handoff.status === 'DRAFT' && (
              <Button
                variant="success"
                onClick={() => setShowReadinessModal(true)}
                className="w-full"
              >
                Check Readiness
              </Button>
            )}

            {/* Actions */}
            {handoff.status === 'ACCEPTED' && (
              <Button
                variant="success"
                onClick={handleComplete}
                className="w-full"
              >
                Complete Handoff
              </Button>
            )}

            {handoff.status !== 'COMPLETED' && handoff.status !== 'ESCALATED' && (
              <Button
                variant="danger"
                onClick={handleEscalate}
                className="w-full"
              >
                Escalate
              </Button>
            )}
          </div>
        </div>

        <ReadinessModal
          isOpen={showReadinessModal}
          onClose={() => setShowReadinessModal(false)}
          handoffId={handoff.id}
          onAccept={loadHandoff}
        />
      </div>
    </>
  )
}