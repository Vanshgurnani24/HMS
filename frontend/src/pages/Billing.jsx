import { useState, useEffect } from 'react'
import {
  Box,
  Button,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  MenuItem,
  Chip,
  IconButton,
  Alert,
  Card,
  CardContent,
  Grid,
} from '@mui/material'
import { Add, Refresh, Receipt, CheckCircle } from '@mui/icons-material'
import { paymentsAPI, bookingsAPI } from '../api/axios'
import { PAYMENT_METHOD_LABELS, PAYMENT_STATUS_LABELS, STATUS_COLORS, PAYMENT_METHODS } from '../utils/constants'
import LoadingSpinner from '../components/common/LoadingSpinner'

const Billing = () => {
  const [payments, setPayments] = useState([])
  const [bookings, setBookings] = useState([])
  const [loading, setLoading] = useState(true)
  const [openDialog, setOpenDialog] = useState(false)
  const [selectedBooking, setSelectedBooking] = useState(null)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [stats, setStats] = useState({
    totalRevenue: 0,
    pendingPayments: 0,
    completedPayments: 0,
  })
  const [formData, setFormData] = useState({
    booking_id: '',
    payment_method: PAYMENT_METHODS.CASH,
    reference_number: '',
    notes: '',
  })

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      setLoading(true)
      const [paymentsRes, bookingsRes] = await Promise.all([
        paymentsAPI.getPayments({ limit: 1000 }),
        bookingsAPI.getBookings({ limit: 1000 }),
      ])
      
      const paymentsData = paymentsRes.data.payments || []
      setPayments(paymentsData)
      setBookings(bookingsRes.data.bookings || [])

      // Calculate stats
      const completed = paymentsData.filter(p => p.payment_status === 'completed')
      const pending = paymentsData.filter(p => p.payment_status === 'pending')
      const totalRevenue = completed.reduce((sum, p) => sum + p.amount, 0)

      setStats({
        totalRevenue,
        pendingPayments: pending.length,
        completedPayments: completed.length,
      })
    } catch (error) {
      console.error('Error fetching data:', error)
      setError('Failed to load data')
    } finally {
      setLoading(false)
    }
  }

  const handleOpenDialog = (booking = null) => {
    setSelectedBooking(booking)
    setFormData({
      booking_id: booking?.id || '',
      payment_method: PAYMENT_METHODS.CASH,
      reference_number: '',
      notes: '',
    })
    setOpenDialog(true)
    setError('')
    setSuccess('')
  }

  const handleCloseDialog = () => {
    setOpenDialog(false)
    setSelectedBooking(null)
  }

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    })
  }

  const handleSubmit = async () => {
    try {
      const submitData = {
        ...formData,
        booking_id: parseInt(formData.booking_id),
      }

      await paymentsAPI.createPayment(submitData)
      setSuccess('Payment recorded successfully!')
      handleCloseDialog()
      fetchData()
    } catch (error) {
      console.error('Error creating payment:', error)
      setError(error.response?.data?.detail || 'Failed to record payment')
    }
  }

  const handleCompletePayment = async (paymentId) => {
    try {
      await paymentsAPI.updatePaymentStatus(paymentId, 'completed', {
        payment_date: new Date().toISOString(),
      })
      setSuccess('Payment marked as completed!')
      fetchData()
    } catch (error) {
      console.error('Error completing payment:', error)
      setError(error.response?.data?.detail || 'Failed to complete payment')
    }
  }

  if (loading) {
    return <LoadingSpinner />
  }

  // Get bookings that need payment
  const unpaidBookings = bookings.filter(b => 
    (b.status === 'confirmed' || b.status === 'checked_in' || b.status === 'checked_out') &&
    !payments.some(p => p.booking_id === b.id && p.payment_status === 'completed')
  )

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" sx={{ fontWeight: 600 }}>
          Billing & Payments
        </Typography>
        <Box>
          <Button
            variant="outlined"
            startIcon={<Refresh />}
            onClick={fetchData}
            sx={{ mr: 2 }}
          >
            Refresh
          </Button>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={() => handleOpenDialog()}
          >
            Record Payment
          </Button>
        </Box>
      </Box>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
      {success && <Alert severity="success" sx={{ mb: 2 }}>{success}</Alert>}

      {/* Stats Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={4}>
          <Card sx={{ backgroundColor: '#e8f5e9' }}>
            <CardContent>
              <Typography variant="body2" color="text.secondary">
                Total Revenue
              </Typography>
              <Typography variant="h4" sx={{ fontWeight: 700, color: '#2e7d32' }}>
                ₹{stats.totalRevenue.toLocaleString()}
              </Typography>
              <Typography variant="caption">
                {stats.completedPayments} completed payments
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card sx={{ backgroundColor: '#fff3e0' }}>
            <CardContent>
              <Typography variant="body2" color="text.secondary">
                Pending Payments
              </Typography>
              <Typography variant="h4" sx={{ fontWeight: 700, color: '#ed6c02' }}>
                {stats.pendingPayments}
              </Typography>
              <Typography variant="caption">
                Awaiting confirmation
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card sx={{ backgroundColor: '#e3f2fd' }}>
            <CardContent>
              <Typography variant="body2" color="text.secondary">
                Unpaid Bookings
              </Typography>
              <Typography variant="h4" sx={{ fontWeight: 700, color: '#1976d2' }}>
                {unpaidBookings.length}
              </Typography>
              <Typography variant="caption">
                Need payment processing
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell><strong>Transaction ID</strong></TableCell>
              <TableCell><strong>Booking Ref</strong></TableCell>
              <TableCell><strong>Customer</strong></TableCell>
              <TableCell><strong>Amount</strong></TableCell>
              <TableCell><strong>Method</strong></TableCell>
              <TableCell><strong>Status</strong></TableCell>
              <TableCell><strong>Date</strong></TableCell>
              <TableCell><strong>Actions</strong></TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {payments.length === 0 ? (
              <TableRow>
                <TableCell colSpan={8} align="center">
                  <Typography variant="body2" color="text.secondary">
                    No payments recorded yet. Record your first payment!
                  </Typography>
                </TableCell>
              </TableRow>
            ) : (
              payments.map((payment) => (
                <TableRow key={payment.id}>
                  <TableCell>{payment.transaction_id}</TableCell>
                  <TableCell>{payment.booking?.booking_reference || 'N/A'}</TableCell>
                  <TableCell>
                    {payment.booking?.customer ? 
                      `${payment.booking.customer.first_name} ${payment.booking.customer.last_name}` : 
                      'N/A'}
                  </TableCell>
                  <TableCell>₹{payment.amount}</TableCell>
                  <TableCell>{PAYMENT_METHOD_LABELS[payment.payment_method]}</TableCell>
                  <TableCell>
                    <Chip
                      label={PAYMENT_STATUS_LABELS[payment.payment_status]}
                      color={STATUS_COLORS[payment.payment_status]}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    {payment.payment_date ? 
                      new Date(payment.payment_date).toLocaleDateString() : 
                      'Pending'}
                  </TableCell>
                  <TableCell>
                    {payment.payment_status === 'pending' && (
                      <IconButton
                        size="small"
                        color="success"
                        onClick={() => handleCompletePayment(payment.id)}
                        title="Mark as Completed"
                      >
                        <CheckCircle />
                      </IconButton>
                    )}
                    {payment.payment_status === 'completed' && (
                      <IconButton
                        size="small"
                        color="primary"
                        title="View Receipt"
                      >
                        <Receipt />
                      </IconButton>
                    )}
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Record Payment Dialog */}
      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
        <DialogTitle>Record Payment</DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2, display: 'flex', flexDirection: 'column', gap: 2 }}>
            <TextField
              select
              label="Select Booking"
              name="booking_id"
              value={formData.booking_id}
              onChange={handleChange}
              required
              fullWidth
            >
              {unpaidBookings.length === 0 ? (
                <MenuItem disabled>No unpaid bookings available</MenuItem>
              ) : (
                unpaidBookings.map((booking) => (
                  <MenuItem key={booking.id} value={booking.id}>
                    {booking.booking_reference} - {booking.customer?.first_name} {booking.customer?.last_name} 
                    {' '}(₹{booking.final_amount})
                  </MenuItem>
                ))
              )}
            </TextField>
            <TextField
              select
              label="Payment Method"
              name="payment_method"
              value={formData.payment_method}
              onChange={handleChange}
              required
              fullWidth
            >
              {Object.entries(PAYMENT_METHOD_LABELS).map(([value, label]) => (
                <MenuItem key={value} value={value}>
                  {label}
                </MenuItem>
              ))}
            </TextField>
            <TextField
              label="Reference Number"
              name="reference_number"
              value={formData.reference_number}
              onChange={handleChange}
              fullWidth
              placeholder="Transaction/Check number"
            />
            <TextField
              label="Notes"
              name="notes"
              value={formData.notes}
              onChange={handleChange}
              multiline
              rows={3}
              fullWidth
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button onClick={handleSubmit} variant="contained" disabled={!formData.booking_id}>
            Record Payment
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}

export default Billing