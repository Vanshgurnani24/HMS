import axios from 'axios'

// Create axios instance with base configuration
const api = axios.create({
  baseURL: 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Flag to prevent multiple refresh attempts
let isRefreshing = false
let failedQueue = []

const processQueue = (error, token = null) => {
  failedQueue.forEach(prom => {
    if (error) {
      prom.reject(error)
    } else {
      prom.resolve(token)
    }
  })

  failedQueue = []
}

// Response interceptor to handle errors and token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    if (error.response?.status === 401) {
      // Don't try to refresh on login, refresh, or if already retried
      const isLoginRequest = originalRequest?.url?.includes('/auth/login')
      const isRefreshRequest = originalRequest?.url?.includes('/auth/refresh')

      if (isLoginRequest || isRefreshRequest) {
        return Promise.reject(error)
      }

      if (originalRequest._retry) {
        // Already tried refreshing, logout user
        localStorage.removeItem('token')
        localStorage.removeItem('refreshToken')
        localStorage.removeItem('user')
        window.location.href = '/login'
        return Promise.reject(error)
      }

      if (isRefreshing) {
        // Queue this request while refresh is in progress
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject })
        })
          .then(token => {
            originalRequest.headers.Authorization = `Bearer ${token}`
            return api(originalRequest)
          })
          .catch(err => {
            return Promise.reject(err)
          })
      }

      originalRequest._retry = true
      isRefreshing = true

      const refreshToken = localStorage.getItem('refreshToken')

      // Check for missing, null, or "undefined" string (from legacy users)
      if (!refreshToken || refreshToken === 'undefined') {
        // No valid refresh token, logout
        localStorage.removeItem('token')
        localStorage.removeItem('refreshToken')
        localStorage.removeItem('user')
        window.location.href = '/login'
        return Promise.reject(error)
      }

      try {
        // Try to refresh the token
        const response = await api.post('/auth/refresh', null, {
          params: { refresh_token: refreshToken }
        })

        const { access_token, refresh_token: new_refresh_token } = response.data

        localStorage.setItem('token', access_token)
        localStorage.setItem('refreshToken', new_refresh_token)

        // Update authorization header
        api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`
        originalRequest.headers.Authorization = `Bearer ${access_token}`

        processQueue(null, access_token)
        isRefreshing = false

        // Retry the original request
        return api(originalRequest)
      } catch (refreshError) {
        processQueue(refreshError, null)
        isRefreshing = false

        // Refresh failed, logout user
        localStorage.removeItem('token')
        localStorage.removeItem('refreshToken')
        localStorage.removeItem('user')
        window.location.href = '/login'
        return Promise.reject(refreshError)
      }
    }

    return Promise.reject(error)
  }
)

// API endpoints
export const authAPI = {
  login: (credentials) => api.post('/auth/login', credentials, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
  }),
  register: (userData) => api.post('/auth/register', userData),
  getCurrentUser: () => api.get('/auth/me'),
}

export const roomsAPI = {
  getRooms: (params) => api.get('/rooms/', { params }),
  getRoom: (id) => api.get(`/rooms/${id}`),
  createRoom: (data) => api.post('/rooms/', data),
  updateRoom: (id, data) => api.put(`/rooms/${id}`, data),
  updateRoomStatus: (id, status) => api.patch(`/rooms/${id}/status`, { status }),
  deleteRoom: (id) => api.delete(`/rooms/${id}`),
  getAvailableRooms: (params) => api.get('/rooms/available/check', { params }),
  getRoomsByType: (type, params) => api.get(`/rooms/type/${type}`, { params }),
}

export const customersAPI = {
  getCustomers: (params) => api.get('/customers/', { params }),
  getCustomer: (id) => api.get(`/customers/${id}`),
  createCustomer: (data) => {
    const formData = new FormData()
    Object.keys(data).forEach(key => {
      if (data[key] !== null && data[key] !== undefined) {
        formData.append(key, data[key])
      }
    })
    return api.post('/customers/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },
  updateCustomer: (id, data) => {
    const formData = new FormData()
    Object.keys(data).forEach(key => {
      if (data[key] !== null && data[key] !== undefined) {
        formData.append(key, data[key])
      }
    })
    return api.put(`/customers/${id}`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },
  deleteCustomer: (id) => api.delete(`/customers/${id}`),
  searchCustomers: (query) => api.get('/customers/search', { params: { query } }),
  getCustomerByEmail: (email) => api.get(`/customers/email/${email}`),
  getCustomerByPhone: (phone) => api.get(`/customers/phone/${phone}`),
}

export const bookingsAPI = {
  getBookings: (params) => api.get('/bookings/', { params }),
  getBooking: (id) => api.get(`/bookings/${id}`),
  createBooking: (data) => api.post('/bookings/', data),
  updateBooking: (id, data) => api.put(`/bookings/${id}`, data),
  updateBookingStatus: (id, status) => api.patch(`/bookings/${id}/status`, { status }),
  deleteBooking: (id) => api.delete(`/bookings/${id}`),
  checkIn: (id) => api.patch(`/bookings/${id}/status`, { status: 'checked_in' }), // FIXED: Use status endpoint
  checkOut: (id) => api.patch(`/bookings/${id}/status`, { status: 'checked_out' }), // FIXED: Use status endpoint
  cancelBooking: (id) => api.post(`/bookings/${id}/cancel`),
  getBookingsByCustomer: (customerId) => api.get(`/bookings/customer/${customerId}`),
  getBookingsByRoom: (roomId) => api.get(`/bookings/room/${roomId}`),
}

export const paymentsAPI = {
  getPayments: (params) => api.get('/payments/', { params }),
  getPayment: (id) => api.get(`/payments/${id}`),
  createPayment: (data) => api.post('/payments/', data),
  updatePaymentStatus: (id, status, data) => api.patch(`/payments/${id}/status`, { payment_status: status, ...data }),
  refundPayment: (id) => api.post(`/payments/${id}/refund`),
  getPaymentsByBooking: (bookingId) => api.get(`/payments/booking/${bookingId}`),
  getPaymentSummary: (bookingId) => api.get(`/payments/booking/${bookingId}/summary`),
  getPaymentHistory: (bookingId) => api.get(`/payments/booking/${bookingId}/history`),
  getInvoiceByPayment: (paymentId) => api.get(`/payments/invoices/payment/${paymentId}`),
  getInvoiceByBooking: (bookingId) => api.get(`/payments/invoices/booking/${bookingId}`),
}

export const reportsAPI = {
  getReport: (reportType, dateRange) => api.get('/reports/', {
    params: {
      report_type: reportType,
      date_range: dateRange
    }
  }),
  getOccupancy: () => api.get('/reports/occupancy'),
  getDailyRevenue: (date) => api.get('/reports/revenue/daily', { params: { target_date: date } }),
  getRevenueRange: (startDate, endDate) => api.get('/reports/revenue/range', {
    params: { start_date: startDate, end_date: endDate }
  }),
  getBookingHistory: (params) => api.get('/reports/bookings/history', { params }),
  getUpcomingBookings: (days = 7) => api.get('/reports/bookings/upcoming', { params: { days } }),
  getDashboard: () => api.get('/reports/dashboard'),
  getTopCustomers: (reportType = 'by_revenue', limit = 10) => api.get('/reports/customers/top', {
    params: { report_type: reportType, limit }
  }),
}

export const settingsAPI = {
  getHotelSettings: () => api.get('/settings/hotel'),
  updateHotelSettings: (data) => api.put('/settings/hotel', data),
}

export const roomTypesAPI = {
  getRoomTypes: (includeInactive = false) => api.get('/room-types/', { params: { include_inactive: includeInactive } }),
  getRoomType: (id) => api.get(`/room-types/${id}`),
  createRoomType: (data) => api.post('/room-types/', data),
  updateRoomType: (id, data) => api.put(`/room-types/${id}`, data),
  deleteRoomType: (id) => api.delete(`/room-types/${id}`),
}

export default api