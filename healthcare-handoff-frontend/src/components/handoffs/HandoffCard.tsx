import React from 'react'
import { Handoff } from '../../types'
import { Clock, AlertCircle, CheckCircle } from 'lucide-react'

interface HandoffCardProps {
  handoff: Handoff
  onClick?: () => void
}

export const HandoffCard: React.FC<HandoffCardProps> = ({ handoff, onClick }) => {
  const statusColors = {
    DRAFT: 'badge-info',
    PENDING_REVIEW: 'badge-warning',
    ACCEPTED: 'badge-success',
    COMPLETED: 'badge-success',
    ESCALATED: 'badge-error',
  }

  const priorityColors = {
    LOW: 'text-green-600',
    MEDIUM: 'text-yellow-600',
    HIGH: 'text-orange-600',
    CRITICAL: 'text-red-600 font-bold',
  }

  return (
    <div onClick={onClick} className="card cursor-pointer">
      <div className="flex items-start justify-between mb-3">
        <div>
          <h3 className="text-lg font-semibold">Patient Handoff</h3>
          <p className="text-gray-600 text-sm">ID: {handoff.id.slice(0, 8)}</p>
        </div>
        <span className={statusColors[handoff.status]}>
          {handoff.status.replace('_', ' ')}
        </span>
      </div>

      <p className="text-gray-700 mb-2">{handoff.diagnosis_summary}</p>

      <div className="space-y-2 text-sm">
        <div className="flex items-center gap-2">
          <span className={`font-medium ${priorityColors[handoff.priority]}`}>
            {handoff.priority}
          </span>
          <span className="text-gray-600">Priority</span>
        </div>

        <div className="flex items-center gap-2">
          <Clock size={16} className="text-gray-600" />
          <span className="text-gray-600">
            Due: {new Date(handoff.follow_up_deadline).toLocaleDateString()}
          </span>
        </div>

        {handoff.is_ready && (
          <div className="flex items-center gap-2">
            <CheckCircle size={16} className="text-green-600" />
            <span className="text-green-600">Ready for acceptance</span>
          </div>
        )}
      </div>

      {handoff.status === 'ESCALATED' && (
        <div className="mt-3 p-2 bg-red-50 rounded border border-red-200 flex items-center gap-2">
          <AlertCircle size={16} className="text-red-600" />
          <span className="text-sm text-red-600">Escalated</span>
        </div>
      )}
    </div>
  )
}