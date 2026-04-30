import React from 'react'
import { Patient } from '../../types'
import { Calendar, User } from 'lucide-react'

interface PatientCardProps {
  patient: Patient
  onClick?: () => void
}

export const PatientCard: React.FC<PatientCardProps> = ({ patient, onClick }) => {
  return (
    <div
      onClick={onClick}
      className="card cursor-pointer"
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <h3 className="text-lg font-semibold flex items-center gap-2">
            <User size={20} className="text-blue-600" />
            {patient.name}
          </h3>
          <p className="text-gray-600 text-sm mt-2">MRN: {patient.mrn}</p>
          <p className="text-gray-600 text-sm flex items-center gap-2 mt-2">
            <Calendar size={16} />
            DOB: {patient.date_of_birth}
          </p>
        </div>
      </div>
      <p className="text-gray-500 text-xs mt-4">
        Created: {new Date(patient.created_at).toLocaleDateString()}
      </p>
    </div>
  )
}