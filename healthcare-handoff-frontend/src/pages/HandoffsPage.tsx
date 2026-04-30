import React, { useState, useEffect } from 'react'
import { Navbar } from '../components/common/Navbar'
import { Button } from '../components/common/Button'
import { Modal } from '../components/common/Modal'
import { HandoffCard } from '../components/handoffs/HandoffCard'
import { HandoffForm } from '../components/handoffs/HandoffForm'
import { useToast } from '../hooks/useToast'
import { Plus } from 'lucide-react'
import { Handoff } from '../types'

export const HandoffsPage: React.FC = () => {
  const [showForm, setShowForm] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const { addToast } = useToast()

  const handleHandoffCreated = () => {
    setShowForm(false)
  }

  return (
    <>
      <Navbar />
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="flex items-center justify-between mb-8">
          <h1 className="text-3xl font-bold">Handoffs</h1>
          <Button
            variant="primary"
            onClick={() => setShowForm(true)}
            className="flex items-center gap-2"
          >
            <Plus size={20} /> New Handoff
          </Button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div className="text-center py-12 bg-white rounded-lg col-span-full">
            <p className="text-gray-600 mb-4">No handoffs yet</p>
            <Button variant="primary" onClick={() => setShowForm(true)}>
              Create First Handoff
            </Button>
          </div>
        </div>

        <Modal
          isOpen={showForm}
          onClose={() => setShowForm(false)}
          title="Create New Handoff"
          size="lg"
        >
          <HandoffForm
            onSuccess={handleHandoffCreated}
            onCancel={() => setShowForm(false)}
          />
        </Modal>
      </div>
    </>
  )
}