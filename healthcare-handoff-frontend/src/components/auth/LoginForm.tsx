import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Button } from '../common/Button'
import { useAuth } from '../../hooks/useAuth'
import { useToast } from '../../hooks/useToast'
import apiClient from '../../api/client'
import { LoginRequest, User } from '../../types'

export const LoginForm: React.FC = () => {
  const [formData, setFormData] = useState<LoginRequest>({
    email: '',
    password: '',
  })
  const [isLoading, setIsLoading] = useState(false)
  const { login } = useAuth()
  const { addToast } = useToast()
  const navigate = useNavigate()

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setFormData((prev) => ({ ...prev, [name]: value }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)

    try {
      const response = await apiClient.login(formData)
      
      // Extract user info from token
      const tokenParts = response.access_token.split('.')
      const payload = JSON.parse(atob(tokenParts[1]))
      
      const user: User = {
        id: payload.sub,
        email: payload.email,
        role: payload.role,
        created_at: new Date().toISOString(),
      }

      login(response.access_token, user)
      addToast('Login successful!', 'success')
      navigate('/')
    } catch (error: any) {
      addToast(error.response?.data?.message || 'Login failed', 'error')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="block text-sm font-medium mb-1">Email</label>
        <input
          type="email"
          name="email"
          value={formData.email}
          onChange={handleChange}
          className="input-base"
          required
        />
      </div>

      <div>
        <label className="block text-sm font-medium mb-1">Password</label>
        <input
          type="password"
          name="password"
          value={formData.password}
          onChange={handleChange}
          className="input-base"
          required
        />
      </div>

      <Button variant="primary" type="submit" isLoading={isLoading} className="w-full">
        Login
      </Button>
    </form>
  )
}