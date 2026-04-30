import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

class ApiClient {
  private token: string | null = localStorage.getItem('token')

  constructor() {
    axios.defaults.baseURL = API_BASE_URL

    // Request interceptor to add token
    axios.interceptors.request.use((config) => {
      const token = localStorage.getItem('token')
      if (token) {
        config.headers.Authorization = `Bearer ${token}`
      }
      return config
    })

    // Response interceptor for 401 handling
    axios.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          localStorage.removeItem('token')
          window.location.href = '/login'
        }
        return Promise.reject(error)
      }
    )
  }

  // Auth endpoints
  login(data: { email: string; password: string }) {
    return axios.post('/auth/login', data).then((res) => res.data)
  }

  signup(data: { email: string; password: string; role: string }) {
    return axios.post('/auth/signup', data).then((res) => res.data)
  }

  // Patient endpoints
  listPatients() {
    return axios.get('/patients').then((res) => res.data)
  }

  createPatient(data: any) {
    return axios.post('/patients', data).then((res) => res.data)
  }

  getPatient(id: string) {
    return axios.get(`/patients/${id}`).then((res) => res.data)
  }

  // Handoff endpoints
  listHandoffs() {
    return axios.get('/handoffs').then((res) => res.data)
  }

  createHandoff(data: any) {
    return axios.post('/handoffs', data).then((res) => res.data)
  }

  getHandoff(id: string) {
    return axios.get(`/handoffs/${id}`).then((res) => res.data)
  }

  checkReadiness(handoffId: string) {
    return axios
      .post(`/handoffs/${handoffId}/readiness-check`, {})
      .then((res) => res.data)
  }

  acceptHandoff(handoffId: string) {
    return axios.post(`/handoffs/${handoffId}/accept`, {}).then((res) => res.data)
  }

  completeHandoff(handoffId: string) {
    return axios.post(`/handoffs/${handoffId}/complete`, {}).then((res) => res.data)
  }

  escalateHandoff(handoffId: string, reason: string) {
    return axios
      .post(`/handoffs/${handoffId}/escalate`, { reason })
      .then((res) => res.data)
  }

  // Item endpoints
  addItem(handoffId: string, data: any) {
    return axios
      .post(`/handoffs/${handoffId}/items`, data)
      .then((res) => res.data)
  }

  listItems(handoffId: string) {
    return axios.get(`/handoffs/${handoffId}/items`).then((res) => res.data)
  }

  getItem(handoffId: string, itemId: string) {
    return axios
      .get(`/handoffs/${handoffId}/items/${itemId}`)
      .then((res) => res.data)
  }

  updateItemStatus(handoffId: string, itemId: string, status: string) {
    return axios
      .patch(`/handoffs/${handoffId}/items/${itemId}`, { status })
      .then((res) => res.data)
  }

  setToken(token: string) {
    this.token = token
    localStorage.setItem('token', token)
    axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
  }

  getToken() {
    return this.token || localStorage.getItem('token')
  }

  clearToken() {
    this.token = null
    localStorage.removeItem('token')
    delete axios.defaults.headers.common['Authorization']
  }
}

export default new ApiClient()