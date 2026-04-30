import React, { useState, useEffect } from 'react'
import { Modal } from '../common/Modal'
import { Button } from '../common/Button'
import { ReadinessCheck } from '../../types'
import { AlertCircle, CheckCircle, AlertTriangle } from 'lucide-react'
import apiClient from '../../api/client'
import { useToast } from '../../hooks/useToast'

interface ReadinessModalProps {
  isOpen: boolean
  onClose: () => void
  handoffId: string
  onAccept?: () => void
}

export const ReadinessModal: React.FC<ReadinessModalProps> = ({
  isOpen,
  onClose,
  handoffId,
  onAccept,
}) => {
  const [readiness, setReadiness] = useState<ReadinessCheck | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [isAccepting, setIsAccepting] = useState(false)
  const { addToast } = useToast()

  useEffect(() => {
    if (isOpen) {
      checkReadiness()
    }
  }, [isOpen, handoffId])

  const checkReadiness = async () => {
    setIsLoading(true)
    try {
      const result = await apiClient.checkReadiness(handoffId)
      setReadiness(result)
    } catch (error: any) {
      addToast('Failed to check readiness', 'error')
      onClose()
    } finally {
      setIsLoading(false)
    }
  }

  const handleAccept = async () => {
    setIsAccepting(true)
    try {
      await apiClient.acceptHandoff(handoffId)
      addToast('Handoff accepted successfully', 'success')
      onAccept?.()
      onClose()
    } catch (error: any) {
      addToast(error.response?.data?.message || 'Failed to accept handoff', 'error')
    } finally {
      setIsAccepting(false)
    }
  }

  if (!readiness) {
    return (
      <Modal isOpen={isOpen} onClose={onClose} title="Readiness Check">
        <div className="text-center py-8">
          {isLoading ? '...' : 'Failed to load readiness check'}
        </div>
      </Modal>
    )
  }

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Readiness Check" size="lg">
      <div className="space-y-4">
        {/* Status */}
        <div className={`p-4 rounded-lg ${readiness.is_ready ? 'bg-green-50' : 'bg-red-50'}`}>
          <div className="flex items-center gap-2">
            {readiness.is_ready ? (
              <>
                <CheckCircle className="text-green-600" size={24} />
                <span className="text-lg font-semibold text-green-700">Ready for Acceptance</span>
              </>
            ) : (
              <>
                <AlertCircle className="text-red-600" size={24} />
                <span className="text-lg font-semibold text-red-700">Not Ready</span>
              </>
            )}
          </div>
        </div>

        {/* Item Status */}
        <div className="bg-gray-50 p-4 rounded-lg">
          <h4 className="font-semibold mb-2">Items Status</h4>
          <div className="grid grid-cols-3 gap-2 text-sm">
            <div>
              <span className="text-gray-600">Open</span>
              <p className="text-lg font-semibold">{readiness.items_by_status.open}</p>
            </div>
            <div>
              <span className="text-gray-600">In Progress</span>
              <p className="text-lg font-semibold">{readiness.items_by_status.in_progress}</p>
            </div>
            <div>
              <span className="text-gray-600">Completed</span>
              <p className="text-lg font-semibold">{readiness.items_by_status.completed}</p>
            </div>
          </div>
        </div>

        {/* Failures */}
        {readiness.failures.length > 0 && (
          <div className="bg-red-50 border border-red-200 p-4 rounded-lg">
            <div className="flex items-center gap-2 mb-2">
              <AlertCircle className="text-red-600" size={20} />
              <h4 className="font-semibold text-red-700">Issues to Fix</h4>
            </div>
            <ul className="space-y-1">
              {readiness.failures.map((failure, idx) => (
                <li key={idx} className="text-sm text-red-700">• {failure}</li>
              ))}
            </ul>
          </div>
        )}

        {/* Warnings */}
        {readiness.warnings.length > 0 && (
          <div className="bg-yellow-50 border border-yellow-200 p-4 rounded-lg">
            <div className="flex items-center gap-2 mb-2">
              <AlertTriangle className="text-yellow-600" size={20} />
              <h4 className="font-semibold text-yellow-700">Warnings</h4>
            </div>
            <ul className="space-y-1">
              {readiness.warnings.map((warning, idx) => (
                <li key={idx} className="text-sm text-yellow-700">• {warning}</li>
              ))}
            </ul>
          </div>
        )}

        {/* Actions */}
        <div className="flex gap-2 pt-4">
          {readiness.is_ready && (
            <Button
              variant="success"
              onClick={handleAccept}
              isLoading={isAccepting}
              className="flex-1"
            >
              Accept Handoff
            </Button>
          )}
          <Button variant="secondary" onClick={onClose} className="flex-1">
            {readiness.is_ready ? 'Maybe Later' : 'Close'}
          </Button>
        </div>
      </div>
    </Modal>
  )
}