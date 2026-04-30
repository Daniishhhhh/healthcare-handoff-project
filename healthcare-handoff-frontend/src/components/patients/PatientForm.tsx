import React, { useState } from 'react'
import { Button } from '../common/Button'
import { useToast } from '../../hooks/useToast'
import apiClient from '../../api/client'
import { CreatePatientRequest } from '../../types'

interface PatientFormProps {
  onSuccess?: () => void
  onCancel?: () => void
}

export const PatientForm: React.FC<PatientFormProps> = ({ onSuccess, onCancel }) => {
  const [formData, setFormData] = useState<CreatePatientRequest>({
    mrn: '',
    name: '',
    date_of_birth: '',
  })
  const [isLoading, setIsLoading] = useState(false)
  const { addToast } = useToast()

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setFormData((prev) => ({ ...prev, [name]: value }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)

    try {
      await apiClient.createPatient(formData)
      addToast('Patient created successfully', 'success')
      setFormData({ mrn: '', name: '', date_of_birth: '' })
      onSuccess?.()
    } catch (error: any) {
      addToast(error.response?.data?.message || 'Failed to create patient', 'error')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="block text-sm font-medium mb-1">MRN (Medical Record Number)</label>
        <input
          type="text"
          name="mrn"
          value={formData.mrn}
          onChange={handleChange}
          className="input-base"
          required
        />
      </div>

      <div>
        <label className="block text-sm font-medium mb-1">Full Name</label>
        <input
          type="text"
          name="name"
          value={formData.name}
          onChange={handleChange}
          className="input-base"
          required
        />
      </div>

      <div>
        <label className="block text-sm font-medium mb-1">Date of Birth</label>
        <input
          type="date"
          name="date_of_birth"
          value={formData.date_of_birth}
          onChange={handleChange}
          className="input-base"
          required
        />
      </div>

      <div className="flex gap-2">
        <Button variant="primary" type="submit" isLoading={isLoading} className="flex-1">
          Create Patient
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