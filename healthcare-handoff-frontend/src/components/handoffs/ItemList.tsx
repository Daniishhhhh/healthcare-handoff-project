import React, { useState, useEffect } from 'react'
import { HandoffItem, CreateItemRequest } from '../../types'
import { Button } from '../common/Button'
import { Modal } from '../common/Modal'
import { Plus, Trash2 } from 'lucide-react'
import apiClient from '../../api/client'
import { useToast } from '../../hooks/useToast'

interface ItemListProps {
  handoffId: string
  readOnly?: boolean
}

export const ItemList: React.FC<ItemListProps> = ({ handoffId, readOnly = false }) => {
  const [items, setItems] = useState<HandoffItem[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [showAddForm, setShowAddForm] = useState(false)
  const [newItem, setNewItem] = useState<CreateItemRequest>({
    title: '',
    description: '',
    item_type: 'FOLLOW_UP',
    assigned_to: '',
    due_date: '',
  })
  const { addToast } = useToast()

  useEffect(() => {
    loadItems()
  }, [handoffId])

  const loadItems = async () => {
    try {
      const data = await apiClient.listItems(handoffId)
      setItems(data)
    } catch (error: any) {
      addToast('Failed to load items', 'error')
    } finally {
      setIsLoading(false)
    }
  }

  const handleAddItem = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      const item = await apiClient.addItem(handoffId, newItem)
      setItems([...items, item])
      setNewItem({
        title: '',
        description: '',
        item_type: 'FOLLOW_UP',
        assigned_to: '',
        due_date: '',
      })
      setShowAddForm(false)
      addToast('Item added successfully', 'success')
    } catch (error: any) {
      addToast('Failed to add item', 'error')
    }
  }

  const handleUpdateStatus = async (itemId: string, newStatus: string) => {
    try {
      const updated = await apiClient.updateItemStatus(handoffId, itemId, newStatus)
      setItems(items.map((i) => (i.id === itemId ? updated : i)))
      addToast('Item updated', 'success')
    } catch (error: any) {
      addToast('Failed to update item', 'error')
    }
  }

  const statusOptions = ['OPEN', 'IN_PROGRESS', 'COMPLETED']

  if (isLoading) {
    return <div className="text-center py-4">Loading items...</div>
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">Tasks ({items.length})</h3>
        {!readOnly && (
          <Button
            variant="primary"
            size="sm"
            onClick={() => setShowAddForm(true)}
            className="flex items-center gap-2"
          >
            <Plus size={16} /> Add Item
          </Button>
        )}
      </div>

      {items.length === 0 ? (
        <p className="text-gray-500 text-center py-4">No items yet</p>
      ) : (
        <div className="space-y-2">
          {items.map((item) => (
            <div key={item.id} className="bg-gray-50 p-4 rounded-lg">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <h4 className="font-medium">{item.title}</h4>
                  {item.description && (
                    <p className="text-sm text-gray-600 mt-1">{item.description}</p>
                  )}
                  <div className="flex gap-2 mt-2 text-xs">
                    <span className="badge-info">{item.item_type}</span>
                    {item.due_date && (
                      <span className="text-gray-600">
                        Due: {new Date(item.due_date).toLocaleDateString()}
                      </span>
                    )}
                  </div>
                </div>
                {!readOnly && (
                  <select
                    value={item.status}
                    onChange={(e) => handleUpdateStatus(item.id, e.target.value)}
                    className="input-base text-sm p-1"
                  >
                    {statusOptions.map((status) => (
                      <option key={status} value={status}>
                        {status}
                      </option>
                    ))}
                  </select>
                )}
                {readOnly && (
                  <span className={`px-2 py-1 rounded text-xs font-medium ${
                    item.status === 'COMPLETED' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                  }`}>
                    {item.status}
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      <Modal
        isOpen={showAddForm}
        onClose={() => setShowAddForm(false)}
        title="Add Task Item"
      >
        <form onSubmit={handleAddItem} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">Title *</label>
            <input
              type="text"
              value={newItem.title}
              onChange={(e) => setNewItem({ ...newItem, title: e.target.value })}
              className="input-base"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Description</label>
            <textarea
              value={newItem.description}
              onChange={(e) => setNewItem({ ...newItem, description: e.target.value })}
              className="input-base"
              rows={2}
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Type *</label>
            <select
              value={newItem.item_type}
              onChange={(e) => setNewItem({ ...newItem, item_type: e.target.value as any })}
              className="input-base"
              required
            >
              <option value="FOLLOW_UP">Follow-up</option>
              <option value="MEDICATION">Medication</option>
              <option value="LAB_TEST">Lab Test</option>
              <option value="NOTE">Note</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Assigned To (User ID) *</label>
            <input
              type="text"
              value={newItem.assigned_to}
              onChange={(e) => setNewItem({ ...newItem, assigned_to: e.target.value })}
              className="input-base"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Due Date</label>
            <input
              type="datetime-local"
              value={newItem.due_date}
              onChange={(e) => setNewItem({ ...newItem, due_date: e.target.value })}
              className="input-base"
            />
          </div>

          <div className="flex gap-2">
            <Button variant="primary" type="submit" className="flex-1">
              Add Item
            </Button>
            <Button variant="secondary" onClick={() => setShowAddForm(false)}>
              Cancel
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  )
}