import React, { useEffect } from 'react'
import { X, AlertCircle, CheckCircle, Info } from 'lucide-react'
import { Toast as ToastType } from '../../types'

interface ToastDisplayProps {
  toast: ToastType
  onClose: () => void
}

export const ToastDisplay: React.FC<ToastDisplayProps> = ({ toast, onClose }) => {
  useEffect(() => {
    if (toast.duration) {
      const timer = setTimeout(onClose, toast.duration)
      return () => clearTimeout(timer)
    }
  }, [toast, onClose])

  const colors = {
    success: 'bg-green-100 text-green-800 border-green-300',
    error: 'bg-red-100 text-red-800 border-red-300',
    warning: 'bg-yellow-100 text-yellow-800 border-yellow-300',
    info: 'bg-blue-100 text-blue-800 border-blue-300',
  }

  const icons = {
    success: <CheckCircle size={20} />,
    error: <AlertCircle size={20} />,
    warning: <AlertCircle size={20} />,
    info: <Info size={20} />,
  }

  return (
    <div className={`border rounded-lg p-4 flex items-center justify-between ${colors[toast.type]}`}>
      <div className="flex items-center gap-3">
        {icons[toast.type]}
        <span>{toast.message}</span>
      </div>
      <button onClick={onClose} className="hover:opacity-70">
        <X size={20} />
      </button>
    </div>
  )
}

export const ToastContainer: React.FC<{ toasts: ToastType[]; removeToast: (id: string) => void }> = ({
  toasts,
  removeToast,
}) => {
  return (
    <div className="fixed bottom-4 right-4 space-y-2 z-50">
      {toasts.map((toast) => (
        <ToastDisplay
          key={toast.id}
          toast={toast}
          onClose={() => removeToast(toast.id)}
        />
      ))}
    </div>
  )
}