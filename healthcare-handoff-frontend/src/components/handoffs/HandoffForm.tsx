import React, { useState, useEffect } from 'react'
import { Button } from '../common/Button'
import { useToast } from '../../hooks/useToast'
import apiClient from '../../api/client'
import { CreateHandoffRequest, Patient } from '../../types'

interface HandoffFormProps {
  patientId?: string
  onSuccess?: () => void
  onCancel?: () => void
}

export const HandoffForm: React.FC<HandoffFormProps> = ({
  patientId,
  onSuccess,
  onCancel,
}) => {
  const [formData, setFormData] = useState<CreateHandoffRequest>({
    patient_id: patientId || '',
    assigned_to: '',
    priority: 'MEDIUM',
    diagnosis_summary: '',
    follow_up_deadline: '',
    pending_tests: '',
    medication_changes: '',
    additional_notes: '',
  })
  const [patients, setPatients] = useState<Patient[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const { addToast } = useToast()

  useEffect(() => {
    if (!patientId) {
      loadPatients()
    }
  }, [patientId])

  const loadPatients = async () => {
    try {
      const list = await apiClient.listPatients()
      setPatients(list)
    } catch (error: any) {
      addToast('Failed to load patients', 'error')
    }
  }

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>
  ) => {
    const { name, value } = e.target
    setFormData((prev) => ({ ...prev, [name]: value }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!formData.patient_id || !formData.assigned_to) {
      addToast('Please fill in all required fields', 'error')
      return
    }

    setIsLoading(true)

    try {
      await apiClient.createHandoff(formData)
      addToast('Handoff created successfully', 'success')
      setFormData({
        patient_id: '',
        assigned_to: '',
        priority: 'MEDIUM',
        diagnosis_summary: '',
        follow_up_deadline: '',
        pending_tests: '',
        medication_changes: '',
        additional_notes: '',
      })
      onSuccess?.()
    } catch (error: any) {
      addToast(error.response?.data?.message || 'Failed to create handoff', 'error')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {!patientId && (
        <div>
          <label className="block text-sm font-medium mb-1">Patient *</label>
          <select
            name="patient_id"
            value={formData.patient_id}
            onChange={handleChange}
            className="input-base"
            required
          >
            <option value="">Select a patient</option>
            {patients.map((patient) => (
              <option key={patient.id} value={patient.id}>
                {patient.name} (MRN: {patient.mrn})
              </option>
            ))}
          </select>
        </div>
      )}

      <div>
        <label className="block text-sm font-medium mb-1">Assigned To (User ID) *</label>
        <input
          type="text"
          name="assigned_to"
          value={formData.assigned_to}
          onChange={handleChange}
          className="input-base"
          placeholder="Recipient's user ID"
          required
        />
      </div>

      <div>
        <label className="block text-sm font-medium mb-1">Priority *</label>
        <select
          name="priority"
          value={formData.priority}
          onChange={handleChange}
          className="input-base"
          required
        >
          <option value="LOW">Low</option>
          <option value="MEDIUM">Medium</option>
          <option value="HIGH">High</option>
          <option value="CRITICAL">Critical</option>
        </select>
      </div>

      <div>
        <label className="block text-sm font-medium mb-1">Diagnosis Summary *</label>
        <textarea
          name="diagnosis_summary"
          value={formData.diagnosis_summary}
          onChange={handleChange}
          className="input-base"
          rows={3}
          required
          maxLength={500}
        />
        <p className="text-xs text-gray-500 mt-1">
          {formData.diagnosis_summary.length}/500
        </p>
      </div>

      <div>
        <label className="block text-sm font-medium mb-1">Follow-up Deadline *</label>
        <input
          type="datetime-local"
          name="follow_up_deadline"
          value={formData.follow_up_deadline}
          onChange={handleChange}
          className="input-base"
          required
        />
      </div>

      <div>
        <label className="block text-sm font-medium mb-1">Pending Tests</label>
        <textarea
          name="pending_tests"
          value={formData.pending_tests}
          onChange={handleChange}
          className="input-base"
          rows={2}
        />
      </div>

      <div>
        <label className="block text-sm font-medium mb-1">Medication Changes</label>
        <textarea
          name="medication_changes"
          value={formData.medication_changes}
          onChange={handleChange}
          className="input-base"
          rows={2}
        />
      </div>

      <div>
        <label className="block text-sm font-medium mb-1">Additional Notes</label>
        <textarea
          name="additional_notes"
          value={formData.additional_notes}
          onChange={handleChange}
          className="input-base"
          rows={2}
        />
      </div>

      <div className="flex gap-2">
        <Button variant="primary" type="submit" isLoading={isLoading} className="flex-1">
          Create Handoff
        </Button>
        {onCancel && (
          <Button variant="secondary" type="button" onClick={onCancel}>
            Cancel
          </Button>
        )}
      </div>
    </form>
  )
}