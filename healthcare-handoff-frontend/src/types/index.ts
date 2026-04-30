// User & Auth
export interface User {
  id: string
  email: string
  role: 'intern' | 'nurse' | 'doctor' | 'admin'
  created_at: string
}

export interface LoginRequest {
  email: string
  password: string
}

export interface SignupRequest {
  email: string
  password: string
  role: 'intern' | 'nurse' | 'doctor' | 'admin'
}

export interface AuthResponse {
  access_token: string
  token_type: string
}

// Patient
export interface Patient {
  id: string
  mrn: string
  name: string
  date_of_birth: string
  created_by: string
  created_at: string
  updated_at: string
}

export interface CreatePatientRequest {
  mrn: string
  name: string
  date_of_birth: string
}

// Handoff Item
export interface HandoffItem {
  id: string
  handoff_id: string
  title: string
  description?: string
  item_type: 'FOLLOW_UP' | 'MEDICATION' | 'LAB_TEST' | 'NOTE'
  assigned_to: string
  due_date?: string
  status: 'OPEN' | 'IN_PROGRESS' | 'COMPLETED'
  created_at: string
  updated_at: string
  completed_at?: string
}

export interface CreateItemRequest {
  title: string
  description?: string
  item_type: 'FOLLOW_UP' | 'MEDICATION' | 'LAB_TEST' | 'NOTE'
  assigned_to: string
  due_date?: string
}

// Handoff
export interface Handoff {
  id: string
  patient_id: string
  created_by: string
  assigned_to: string
  status: 'DRAFT' | 'PENDING_REVIEW' | 'ACCEPTED' | 'COMPLETED' | 'ESCALATED'
  priority: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL'
  is_ready: boolean
  diagnosis_summary: string
  pending_tests?: string
  medication_changes?: string
  follow_up_deadline: string
  additional_notes?: string
  created_at: string
  updated_at: string
  accepted_at?: string
  completed_at?: string
}

export interface CreateHandoffRequest {
  patient_id: string
  assigned_to: string
  priority: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL'
  diagnosis_summary: string
  follow_up_deadline: string
  pending_tests?: string
  medication_changes?: string
  additional_notes?: string
}

// Readiness Check
export interface ReadinessCheck {
  handoff_id: string
  patient_id: string
  status: string
  is_ready: boolean
  total_items: number
  items_by_status: {
    open: number
    in_progress: number
    completed: number
  }
  failures: string[]
  warnings: string[]
  checked_at: string
}

// Escalation
export interface EscalationEvent {
  id: string
  handoff_id: string
  triggered_by: 'MANUAL' | 'AUTO'
  reason: string
  action_taken?: string
  created_at: string
}

// API Error
export interface ApiError {
  error: string
  message: string
  details?: Record<string, string>
}

// Toast
export interface Toast {
  id: string
  type: 'success' | 'error' | 'warning' | 'info'
  message: string
  duration?: number
}