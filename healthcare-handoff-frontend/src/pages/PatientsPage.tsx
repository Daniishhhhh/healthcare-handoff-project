import React, { useState, useEffect } from 'react'
import { Navbar } from '../components/common/Navbar'
import { Button } from '../components/common/Button'
import { Modal } from '../components/common/Modal'
import { PatientCard } from '../components/patients/PatientCard'
import { PatientForm } from '../components/patients/PatientForm'
import { useToast } from '../hooks/useToast'
import apiClient from '../api/client'
import { Patient } from '../types'
import { Plus } from 'lucide-react'

export const PatientsPage: React.FC = () => {
  const [patients, setPatients] = useState<Patient[]>([])
  const [showForm, setShowForm] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const { addToast } = useToast()

  useEffect(() => {
    loadPatients()
  }, [])

  const loadPatients = async () => {
    try {
      const data = await apiClient.listPatients()
      setPatients(data)
    } catch (error: any) {
      addToast('Failed to load patients', 'error')
    } finally {
      setIsLoading(false)
    }
  }

  const handlePatientCreated = () => {
    loadPatients()
    setShowForm(false)
  }

  return (
    <>
      <Navbar />
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="flex items-center justify-between mb-8">
          <h1 className="text-3xl font-bold">Patients</h1>
          <Button
            variant="primary"
            onClick={() => setShowForm(true)}
            className="flex items-center gap-2"
          >
            <Plus size={20} /> New Patient
          </Button>
        </div>

        {isLoading ? (
          <div className="text-center py-12">
            <p className="text-gray-600">Loading patients...</p>
          </div>
        ) : patients.length === 0 ? (
          <div className="text-center py-12 bg-white rounded-lg">
            <p className="text-gray-600 mb-4">No patients found</p>
            <Button variant="primary" onClick={() => setShowForm(true)}>
              Create First Patient
            </Button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {patients.map((patient) => (
              <PatientCard key={patient.id} patient={patient} />
            ))}
          </div>
        )}

        <Modal
          isOpen={showForm}
          onClose={() => setShowForm(false)}
          title="Create New Patient"
        >
          <PatientForm
            onSuccess={handlePatientCreated}
            onCancel={() => setShowForm(false)}
          />
        </Modal>
      </div>
    </>
  )
}