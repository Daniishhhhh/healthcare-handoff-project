import React from 'react'
import { Link } from 'react-router-dom'
import { Button } from '../components/common/Button'
import { AlertCircle } from 'lucide-react'

export const NotFoundPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <div className="text-center">
        <AlertCircle className="mx-auto mb-4 text-gray-400" size={64} />
        <h1 className="text-4xl font-bold mb-2">404</h1>
        <p className="text-gray-600 mb-8">Page not found</p>
        <Link to="/">
          <Button variant="primary">Go Home</Button>
        </Link>
      </div>
    </div>
  )
}