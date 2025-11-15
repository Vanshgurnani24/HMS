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
  Autocomplete,
} from '@mui/material'
import { Add, Refresh, CheckCircle, Cancel, Login, Logout } from '@mui/icons-material'
import { bookingsAPI, roomsAPI, customersAPI } from '../api/axios'
import { BOOKING_STATUS_LABELS, STATUS_COLORS } from '../utils/constants'
import LoadingSpinner from '../components/common/LoadingSpinner'

const Bookings = () => {
  const [bookings, setBookings] = useState([])
  const [rooms, setRooms] = useState([])
  const [customers, setCustomers] = useState([])
  const [loading, setLoading] = useState(true)
  const [openDialog, setOpenDialog] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [formData, setFormData] = useState({
    customer_id: null,
    room_id: null,
    check_in_date: '',
    check_out_date: '',
    number_of_guests: '',
    special_requests: '',
  })

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      setLoading(true)
      const [bookingsRes, roomsRes, customersRes] = await Promise.all([
        bookingsAPI.getBookings(),
        roomsAPI.getRooms(),
        customersAPI.getCustomers(),
      ])
      setBookings(bookingsRes.data.bookings || [])
      setRooms(roomsRes.data.rooms || [])
      setCustomers(customersRes.data.customers || [])
    } catch (error) {
      console.error('Error fetching data:', error)
      setError('Failed to load data')
    } finally {
      setLoading(false)
    }
  }

  const handleOpenDialog = () => {
    setFormData({
      customer_id: null,
      room_id: null,
      check_in_date: '',
      check_out_date: '',
      number_of_guests: '',
      special_requests: '',
    })
    setOpenDialog(true)
    setError('')
    setSuccess('')
  }

  const handleCloseDialog = () => {
    setOpenDialog(false)
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
        customer_id: formData.customer_id?.id || formData.customer_id,
        room_id: formData.room_id?.id || formData.room_id,
        number_of_guests: parseInt(formData.number_of_guests),
      }

      await bookingsAPI.createBooking(submitData)
      setSuccess('Booking created successfully!')
      handleCloseDialog()
      fetchData()
    } catch (error) {
      console.error('Error creating booking:', error)
      setError(error.response?.data?.detail || 'Failed to create booking')
    }
  }

  const handleCheckIn = async (id) => {
    try {
      await bookingsAPI.checkIn(id)
      setSuccess('Checked in successfully!')
      fetchData()
    } catch (error) {
      console.error('Error checking in:', error)
      setError(error.response?.data?.detail || 'Failed to check in')
    }
  }

  const handleCheckOut = async (id) => {
    try {
      await bookingsAPI.checkOut(id)
      setSuccess('Checked out successfully!')
      fetchData()
    } catch (error) {
      console.error('Error checking out:', error)
      setError(error.response?.data?.detail || 'Failed to check out')
    }
  }

  const handleCancel = async (id) => {
    if (window.confirm('Are you sure you want to cancel this booking?')) {
      try {
        await bookingsAPI.cancelBooking(id)
        setSuccess('Booking cancelled successfully!')
        fetchData()
      } catch (error) {
        console.error('Error cancelling booking:', error)
        setError(error.response?.data?.detail || 'Failed to cancel booking')
      }
    }
  }

  if (loading) {
    return <LoadingSpinner />
  }

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" sx={{ fontWeight: 600 }}>
          Booking Management
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
            onClick={handleOpenDialog}
          >
            Create Booking
          </Button>
        </Box>
      </Box>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
      {success && <Alert severity="success" sx={{ mb: 2 }}>{success}</Alert>}

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell><strong>Booking Ref</strong></TableCell>
              <TableCell><strong>Customer</strong></TableCell>
              <TableCell><strong>Room</strong></TableCell>
              <TableCell><strong>Check-in</strong></TableCell>
              <TableCell><strong>Check-out</strong></TableCell>
              <TableCell><strong>Nights</strong></TableCell>
              <TableCell><strong>Amount</strong></TableCell>
              <TableCell><strong>Status</strong></TableCell>
              <TableCell><strong>Actions</strong></TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {bookings.length === 0 ? (
              <TableRow>
                <TableCell colSpan={9} align="center">
                  <Typography variant="body2" color="text.secondary">
                    No bookings found. Create your first booking!
                  </Typography>
                </TableCell>
              </TableRow>
            ) : (
              bookings.map((booking) => (
                <TableRow key={booking.id}>
                  <TableCell>{booking.booking_reference}</TableCell>
                  <TableCell>
                    {booking.customer ? 
                      `${booking.customer.first_name} ${booking.customer.last_name}` : 
                      'N/A'}
                  </TableCell>
                  <TableCell>{booking.room?.room_number || 'N/A'}</TableCell>
                  <TableCell>{new Date(booking.check_in_date).toLocaleDateString()}</TableCell>
                  <TableCell>{new Date(booking.check_out_date).toLocaleDateString()}</TableCell>
                  <TableCell>{booking.number_of_nights}</TableCell>
                  <TableCell>₹{booking.final_amount}</TableCell>
                  <TableCell>
                    <Chip
                      label={BOOKING_STATUS_LABELS[booking.status]}
                      color={STATUS_COLORS[booking.status]}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    {booking.status === 'confirmed' && (
                      <IconButton
                        size="small"
                        color="success"
                        onClick={() => handleCheckIn(booking.id)}
                        title="Check In"
                      >
                        <Login />
                      </IconButton>
                    )}
                    {booking.status === 'checked_in' && (
                      <IconButton
                        size="small"
                        color="primary"
                        onClick={() => handleCheckOut(booking.id)}
                        title="Check Out"
                      >
                        <Logout />
                      </IconButton>
                    )}
                    {(booking.status === 'pending' || booking.status === 'confirmed') && (
                      <IconButton
                        size="small"
                        color="error"
                        onClick={() => handleCancel(booking.id)}
                        title="Cancel"
                      >
                        <Cancel />
                      </IconButton>
                    )}
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Create Booking Dialog */}
      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
        <DialogTitle>Create New Booking</DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2, display: 'flex', flexDirection: 'column', gap: 2 }}>
            <Autocomplete
              options={customers}
              getOptionLabel={(option) => `${option.first_name} ${option.last_name} (${option.email})`}
              value={formData.customer_id}
              onChange={(event, newValue) => {
                setFormData({ ...formData, customer_id: newValue })
              }}
              renderInput={(params) => (
                <TextField {...params} label="Select Customer" required />
              )}
            />
            <Autocomplete
              options={rooms.filter(r => r.status === 'available')}
              getOptionLabel={(option) => `${option.room_number} - ${option.room_type} (₹${option.price_per_night}/night)`}
              value={formData.room_id}
              onChange={(event, newValue) => {
                setFormData({ ...formData, room_id: newValue })
              }}
              renderInput={(params) => (
                <TextField {...params} label="Select Room" required />
              )}
            />
            <TextField
              label="Check-in Date"
              name="check_in_date"
              type="date"
              value={formData.check_in_date}
              onChange={handleChange}
              required
              fullWidth
              InputLabelProps={{ shrink: true }}
            />
            <TextField
              label="Check-out Date"
              name="check_out_date"
              type="date"
              value={formData.check_out_date}
              onChange={handleChange}
              required
              fullWidth
              InputLabelProps={{ shrink: true }}
            />
            <TextField
              label="Number of Guests"
              name="number_of_guests"
              type="number"
              value={formData.number_of_guests}
              onChange={handleChange}
              required
              fullWidth
            />
            <TextField
              label="Special Requests"
              name="special_requests"
              value={formData.special_requests}
              onChange={handleChange}
              multiline
              rows={3}
              fullWidth
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button onClick={handleSubmit} variant="contained">
            Create Booking
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}

export default Bookings