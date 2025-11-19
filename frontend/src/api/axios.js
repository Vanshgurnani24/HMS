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

// Response interceptor to handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Don't redirect if the error is from the login endpoint itself
      const isLoginRequest = error.config?.url?.includes('/auth/login')

      if (!isLoginRequest) {
        // Unauthorized - clear token and redirect to login
        localStorage.removeItem('token')
        localStorage.removeItem('user')
        window.location.href = '/login'
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
  getInvoiceByPayment: (paymentId) => api.get(`/payments/invoices/payment/${paymentId}`),
  getInvoiceByBooking: (bookingId) => api.get(`/payments/invoices/booking/${bookingId}`),
}

export default api