import { useState, useEffect, useRef, Fragment } from 'react'
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
  InputAdornment,
} from '@mui/material'
import { Add, Refresh, Receipt as ReceiptIcon, CheckCircle, Print, Search, History } from '@mui/icons-material'
import { paymentsAPI, bookingsAPI, settingsAPI } from '../api/axios'
import { PAYMENT_METHOD_LABELS, PAYMENT_STATUS_LABELS, STATUS_COLORS, PAYMENT_METHODS } from '../utils/constants'
import LoadingSpinner from '../components/common/LoadingSpinner'
import { formatDate } from '../utils/dateUtils'
import ReceiptComponent from '../components/common/Receipt'
import { useReactToPrint } from 'react-to-print'

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
    amount: '',
    payment_method: PAYMENT_METHODS.CASH,
    reference_number: '',
    notes: '',
  })
  const [receiptDialog, setReceiptDialog] = useState(false)
  const [paymentSummary, setPaymentSummary] = useState(null)
  const [historyDialog, setHistoryDialog] = useState(false)
  const [historyData, setHistoryData] = useState({ payments: [], summary: null, booking: null })
  const [invoiceData, setInvoiceData] = useState(null)
  const [receiptLoading, setReceiptLoading] = useState(false)
  const receiptRef = useRef()
  const [searchQuery, setSearchQuery] = useState('')
  const [currentPage, setCurrentPage] = useState(1)
  const itemsPerPage = 50 // Increased for day-wise view
  const [hotelName, setHotelName] = useState('My Hotel')
  const [methodFilter, setMethodFilter] = useState('all')
  const [statusFilter, setStatusFilter] = useState('all')

  useEffect(() => {
    fetchData()
    fetchHotelSettings()
  }, [])

  const fetchHotelSettings = async () => {
    try {
      const response = await settingsAPI.getHotelSettings()
      setHotelName(response.data.hotel_name || 'My Hotel')
    } catch (err) {
      console.error('Error fetching hotel settings:', err)
    }
  }

  const fetchData = async () => {
    try {
      setLoading(true)
      const [paymentsRes, bookingsRes] = await Promise.all([
        paymentsAPI.getPayments(),
        bookingsAPI.getBookings(),
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
      amount: '',
      payment_method: PAYMENT_METHODS.CASH,
      reference_number: '',
      notes: '',
    })
    setPaymentSummary(null)
    setOpenDialog(true)
    setError('')
    setSuccess('')

    // Fetch payment summary if booking is pre-selected
    if (booking?.id) {
      fetchPaymentSummary(booking.id)
    }
  }

  const fetchPaymentSummary = async (bookingId) => {
    try {
      const response = await paymentsAPI.getPaymentSummary(bookingId)
      setPaymentSummary(response.data)
      // Auto-fill with balance due
      setFormData(prev => ({
        ...prev,
        amount: response.data.balance_due > 0 ? response.data.balance_due : ''
      }))
    } catch (err) {
      console.error('Error fetching payment summary:', err)
      // If no payments yet, use the booking's final amount
      const booking = bookings.find(b => b.id === bookingId)
      if (booking) {
        setPaymentSummary({
          total_amount: booking.final_amount,
          total_paid: 0,
          balance_due: booking.final_amount
        })
        setFormData(prev => ({
          ...prev,
          amount: booking.final_amount
        }))
      }
    }
  }

  const handleCloseDialog = () => {
    setOpenDialog(false)
    setSelectedBooking(null)
  }

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData({
      ...formData,
      [name]: value,
    })

    // Fetch payment summary when booking changes
    if (name === 'booking_id' && value) {
      fetchPaymentSummary(parseInt(value))
    }
  }

  const handleSubmit = async () => {
    try {
      if (!formData.booking_id) {
        setError('Please select a booking')
        return
      }

      if (!formData.amount || parseFloat(formData.amount) <= 0) {
        setError('Please enter a valid payment amount')
        return
      }

      const submitData = {
        booking_id: parseInt(formData.booking_id),
        amount: parseFloat(formData.amount),
        payment_method: formData.payment_method,
        reference_number: formData.reference_number || null,
        notes: formData.notes || null,
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

  const handleViewReceipt = async (paymentId) => {
    try {
      setReceiptLoading(true)
      setReceiptDialog(true)
      const response = await paymentsAPI.getInvoiceByPayment(paymentId)
      setInvoiceData(response.data)
    } catch (error) {
      console.error('Error fetching invoice:', error)
      setError(error.response?.data?.detail || 'Failed to load receipt')
      setReceiptDialog(false)
    } finally {
      setReceiptLoading(false)
    }
  }

  const handlePrint = useReactToPrint({
    content: () => receiptRef.current,
    documentTitle: `Receipt-${invoiceData?.invoice_no || 'Invoice'}`,
    pageStyle: `
      @page {
        size: A4;
        margin: 0;
      }
      @media print {
        body {
          -webkit-print-color-adjust: exact;
          print-color-adjust: exact;
        }
      }
    `,
  })

  const handleCloseReceipt = () => {
    setReceiptDialog(false)
    setInvoiceData(null)
  }

  const handleViewHistory = async (bookingId) => {
    try {
      const [historyRes, summaryRes] = await Promise.all([
        paymentsAPI.getPaymentHistory(bookingId),
        paymentsAPI.getPaymentSummary(bookingId)
      ])
      const booking = bookings.find(b => b.id === bookingId)
      setHistoryData({
        payments: historyRes.data.payments || [],
        summary: summaryRes.data,
        booking
      })
      setHistoryDialog(true)
    } catch (err) {
      console.error('Error fetching payment history:', err)
      setError('Failed to load payment history')
    }
  }

  const handleCloseHistory = () => {
    setHistoryDialog(false)
    setHistoryData({ payments: [], summary: null, booking: null })
  }

  if (loading) {
    return <LoadingSpinner />
  }

  // Get bookings that need payment (including partially paid)
  const bookingsWithBalance = bookings.filter(b => {
    if (b.status === 'cancelled') return false
    if (!['confirmed', 'checked_in', 'checked_out'].includes(b.status)) return false

    // Calculate total paid for this booking
    const bookingPayments = payments.filter(p => p.booking_id === b.id)
    const totalPaid = bookingPayments
      .filter(p => p.payment_status === 'completed')
      .reduce((sum, p) => sum + p.amount, 0)
    const totalPending = bookingPayments
      .filter(p => p.payment_status === 'pending')
      .reduce((sum, p) => sum + p.amount, 0)

    // Show if there's balance due (accounting for pending payments)
    return (b.final_amount - totalPaid - totalPending) > 0.01
  }).map(b => {
    // Add calculated balance to booking object for display
    const bookingPayments = payments.filter(p => p.booking_id === b.id)
    const totalPaid = bookingPayments
      .filter(p => p.payment_status === 'completed')
      .reduce((sum, p) => sum + p.amount, 0)
    const totalPending = bookingPayments
      .filter(p => p.payment_status === 'pending')
      .reduce((sum, p) => sum + p.amount, 0)
    return {
      ...b,
      totalPaid,
      totalPending,
      balanceDue: b.final_amount - totalPaid - totalPending
    }
  })

  // Filter payments based on search query, method, and status
  const filteredPayments = payments.filter(payment => {
    // Method filter
    if (methodFilter !== 'all' && payment.payment_method !== methodFilter) {
      return false
    }

    // Status filter
    if (statusFilter !== 'all' && payment.payment_status !== statusFilter) {
      return false
    }

    // Search query filter
    if (searchQuery) {
      const query = searchQuery.toLowerCase()
      const customerName = payment.booking?.customer
        ? `${payment.booking.customer.first_name} ${payment.booking.customer.last_name}`.toLowerCase()
        : ''
      const bookingRef = payment.booking?.booking_reference?.toLowerCase() || ''
      if (!customerName.includes(query) && !bookingRef.includes(query)) {
        return false
      }
    }

    return true
  })

  // Pagination logic
  const totalPages = Math.ceil(filteredPayments.length / itemsPerPage)
  const startIndex = (currentPage - 1) * itemsPerPage
  const endIndex = startIndex + itemsPerPage
  const paginatedPayments = filteredPayments.slice(startIndex, endIndex)

  // Group payments by date for day-wise view
  const groupPaymentsByDate = (paymentsList) => {
    const groups = {}
    paymentsList.forEach(payment => {
      const date = new Date(payment.created_at).toLocaleDateString('en-GB', {
        day: '2-digit',
        month: 'short',
        year: 'numeric'
      })
      if (!groups[date]) {
        groups[date] = []
      }
      groups[date].push(payment)
    })
    return groups
  }

  const groupedPayments = groupPaymentsByDate(paginatedPayments)
  const sortedDates = Object.keys(groupedPayments).sort((a, b) => {
    return new Date(b.split(' ').reverse().join(' ')) - new Date(a.split(' ').reverse().join(' '))
  })

  // Calculate daily totals
  const getDayStats = (dayPayments) => {
    const completed = dayPayments.filter(p => p.payment_status === 'completed')
    return {
      count: dayPayments.length,
      total: completed.reduce((sum, p) => sum + p.amount, 0)
    }
  }

  // Handle page change
  const handlePageChange = (event) => {
    setCurrentPage(Number(event.target.value))
  }

  // Reset to page 1 when search query changes
  const handleSearchChange = (event) => {
    setSearchQuery(event.target.value)
    setCurrentPage(1)
  }

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

      {error && <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>{error}</Alert>}
      {success && <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess('')}>{success}</Alert>}

      {/* Stats Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Revenue
              </Typography>
              <Typography variant="h4">
                ₹{stats.totalRevenue.toFixed(2)}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Completed Payments
              </Typography>
              <Typography variant="h4">
                {stats.completedPayments}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Pending Payments
              </Typography>
              <Typography variant="h4">
                {stats.pendingPayments}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Search and Filter Controls */}
      <Box sx={{ mb: 3, display: 'flex', flexWrap: 'wrap', gap: 2, alignItems: 'center' }}>
        <TextField
          placeholder="Search by customer name or booking reference..."
          value={searchQuery}
          onChange={handleSearchChange}
          size="small"
          sx={{ flexGrow: 1, minWidth: 250, maxWidth: 400 }}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <Search />
              </InputAdornment>
            ),
          }}
        />
        <TextField
          select
          size="small"
          value={methodFilter}
          onChange={(e) => { setMethodFilter(e.target.value); setCurrentPage(1) }}
          sx={{ minWidth: 150 }}
          label="Payment Method"
        >
          <MenuItem value="all">All Methods</MenuItem>
          {Object.entries(PAYMENT_METHOD_LABELS).map(([value, label]) => (
            <MenuItem key={value} value={value}>{label}</MenuItem>
          ))}
        </TextField>
        <TextField
          select
          size="small"
          value={statusFilter}
          onChange={(e) => { setStatusFilter(e.target.value); setCurrentPage(1) }}
          sx={{ minWidth: 130 }}
          label="Status"
        >
          <MenuItem value="all">All Status</MenuItem>
          {Object.entries(PAYMENT_STATUS_LABELS).map(([value, label]) => (
            <MenuItem key={value} value={value}>{label}</MenuItem>
          ))}
        </TextField>
        {totalPages > 1 && (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, ml: 'auto' }}>
            <Typography variant="body2" color="text.secondary">
              Page {currentPage} of {totalPages}
            </Typography>
            <TextField
              select
              size="small"
              value={currentPage}
              onChange={handlePageChange}
              sx={{ minWidth: 70 }}
            >
              {Array.from({ length: totalPages }, (_, i) => i + 1).map((page) => (
                <MenuItem key={page} value={page}>{page}</MenuItem>
              ))}
            </TextField>
          </Box>
        )}
      </Box>

      {/* Results summary */}
      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
        Showing {filteredPayments.length} payments
        {methodFilter !== 'all' && ` • ${PAYMENT_METHOD_LABELS[methodFilter]}`}
        {statusFilter !== 'all' && ` • ${PAYMENT_STATUS_LABELS[statusFilter]}`}
      </Typography>

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
            {paginatedPayments.length === 0 ? (
              <TableRow>
                <TableCell colSpan={8} align="center">
                  <Typography variant="body2" color="text.secondary">
                    {searchQuery ? 'No payments found matching your search.' : 'No payments recorded yet. Record your first payment!'}
                  </Typography>
                </TableCell>
              </TableRow>
            ) : (
              sortedDates.map((date, dateIndex) => {
                const dayPayments = groupedPayments[date]
                const dayStats = getDayStats(dayPayments)
                return (
                  <Fragment key={date}>
                    {/* Day Header Row */}
                    <TableRow sx={{ bgcolor: '#e3f2fd' }}>
                      <TableCell colSpan={8}>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <Typography variant="subtitle2" fontWeight="bold" color="primary">
                            {date}
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            {dayStats.count} payment{dayStats.count !== 1 ? 's' : ''} • Total: ₹{dayStats.total.toFixed(2)}
                          </Typography>
                        </Box>
                      </TableCell>
                    </TableRow>
                    {/* Day's Payments */}
                    {dayPayments.map((payment, paymentIndex) => (
                      <TableRow
                        key={payment.id}
                        sx={{
                          bgcolor: paymentIndex === dayPayments.length - 1 && dateIndex < sortedDates.length - 1
                            ? 'transparent'
                            : 'transparent'
                        }}
                      >
                        <TableCell>{payment.transaction_id}</TableCell>
                        <TableCell>{payment.booking?.booking_reference || 'N/A'}</TableCell>
                        <TableCell>
                          {payment.booking?.customer ?
                            `${payment.booking.customer.first_name} ${payment.booking.customer.last_name}` :
                            'N/A'}
                        </TableCell>
                        <TableCell>₹{payment.amount?.toFixed(2)}</TableCell>
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
                            formatDate(payment.payment_date) :
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
                              onClick={() => handleViewReceipt(payment.id)}
                            >
                              <ReceiptIcon />
                            </IconButton>
                          )}
                          <IconButton
                            size="small"
                            color="info"
                            title="Payment History"
                            onClick={() => handleViewHistory(payment.booking_id)}
                          >
                            <History />
                          </IconButton>
                        </TableCell>
                      </TableRow>
                    ))}
                    {/* Day Separator Line */}
                    {dateIndex < sortedDates.length - 1 && (
                      <TableRow>
                        <TableCell colSpan={8} sx={{ p: 0, borderBottom: '3px solid #1976d2' }} />
                      </TableRow>
                    )}
                  </Fragment>
                )
              })
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
              {bookingsWithBalance.length === 0 ? (
                <MenuItem disabled>No bookings with balance due</MenuItem>
              ) : (
                bookingsWithBalance.map((booking) => (
                  <MenuItem key={booking.id} value={booking.id}>
                    {booking.booking_reference} - {booking.customer?.first_name} {booking.customer?.last_name}
                    {' '}(Balance: ₹{booking.balanceDue.toFixed(2)})
                  </MenuItem>
                ))
              )}
            </TextField>

            {/* Payment Summary Info */}
            {paymentSummary && (
              <Box sx={{ p: 2, bgcolor: 'grey.100', borderRadius: 1 }}>
                <Typography variant="body2" color="text.secondary">
                  Total Amount: ₹{paymentSummary.total_amount?.toFixed(2)}
                </Typography>
                <Typography variant="body2" color="success.main">
                  Paid: ₹{paymentSummary.total_paid?.toFixed(2)}
                </Typography>
                <Typography variant="body2" color="primary.main" fontWeight="bold">
                  Balance Due: ₹{paymentSummary.balance_due?.toFixed(2)}
                </Typography>
              </Box>
            )}

            <TextField
              label="Payment Amount"
              name="amount"
              type="number"
              value={formData.amount}
              onChange={handleChange}
              required
              fullWidth
              InputProps={{
                startAdornment: <InputAdornment position="start">₹</InputAdornment>,
              }}
              helperText={paymentSummary ? `Max: ₹${paymentSummary.balance_due?.toFixed(2)}` : ''}
            />

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

      {/* Receipt Dialog */}
      <Dialog open={receiptDialog} onClose={handleCloseReceipt} maxWidth="md" fullWidth>
        <DialogTitle>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="h6">Payment Receipt</Typography>
            <Button
              startIcon={<Print />}
              variant="contained"
              onClick={handlePrint}
              disabled={receiptLoading || !invoiceData}
            >
              Print Receipt
            </Button>
          </Box>
        </DialogTitle>
        <DialogContent>
          {receiptLoading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
              <LoadingSpinner />
            </Box>
          ) : (
            <ReceiptComponent ref={receiptRef} invoiceData={invoiceData} hotelName={hotelName} />
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseReceipt}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* Payment History Dialog */}
      <Dialog open={historyDialog} onClose={handleCloseHistory} maxWidth="md" fullWidth>
        <DialogTitle>
          <Typography variant="h6">
            Payment History - {historyData.booking?.booking_reference}
          </Typography>
        </DialogTitle>
        <DialogContent>
          {historyData.summary && (
            <Box sx={{ mb: 3, p: 2, bgcolor: 'grey.100', borderRadius: 1 }}>
              <Grid container spacing={2}>
                <Grid item xs={6} md={3}>
                  <Typography variant="body2" color="text.secondary">Total Amount</Typography>
                  <Typography variant="h6">₹{historyData.summary.total_amount?.toFixed(2)}</Typography>
                </Grid>
                <Grid item xs={6} md={3}>
                  <Typography variant="body2" color="text.secondary">Total Paid</Typography>
                  <Typography variant="h6" color="success.main">₹{historyData.summary.total_paid?.toFixed(2)}</Typography>
                </Grid>
                <Grid item xs={6} md={3}>
                  <Typography variant="body2" color="text.secondary">Pending</Typography>
                  <Typography variant="h6" color="warning.main">₹{historyData.summary.total_pending?.toFixed(2)}</Typography>
                </Grid>
                <Grid item xs={6} md={3}>
                  <Typography variant="body2" color="text.secondary">Balance Due</Typography>
                  <Typography variant="h6" color="error.main">₹{historyData.summary.balance_due?.toFixed(2)}</Typography>
                </Grid>
              </Grid>
            </Box>
          )}

          <TableContainer component={Paper}>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Date</TableCell>
                  <TableCell>Amount</TableCell>
                  <TableCell>Method</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Reference</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {historyData.payments.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={5} align="center">No payments recorded yet</TableCell>
                  </TableRow>
                ) : (
                  historyData.payments.map((payment) => (
                    <TableRow key={payment.id}>
                      <TableCell>{formatDate(payment.created_at)}</TableCell>
                      <TableCell>₹{payment.amount?.toFixed(2)}</TableCell>
                      <TableCell>{PAYMENT_METHOD_LABELS[payment.payment_method] || payment.payment_method}</TableCell>
                      <TableCell>
                        <Chip
                          label={PAYMENT_STATUS_LABELS[payment.payment_status] || payment.payment_status}
                          color={STATUS_COLORS[payment.payment_status] || 'default'}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>{payment.reference_number || '-'}</TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </TableContainer>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseHistory}>Close</Button>
          {historyData.summary?.balance_due > 0 && (
            <Button
              variant="contained"
              onClick={() => {
                handleCloseHistory()
                handleOpenDialog(historyData.booking)
              }}
            >
              Record Payment
            </Button>
          )}
        </DialogActions>
      </Dialog>
    </Box>
  )
}

export default Billing