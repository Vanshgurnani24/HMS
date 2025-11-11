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
} from '@mui/material'
import { Add, Edit, Delete, Refresh } from '@mui/icons-material'
import { roomsAPI } from '../api/axios'
import { ROOM_TYPES, ROOM_STATUS, ROOM_TYPE_LABELS, ROOM_STATUS_LABELS, STATUS_COLORS } from '../utils/constants'
import LoadingSpinner from '../components/common/LoadingSpinner'

const Rooms = () => {
  const [rooms, setRooms] = useState([])
  const [loading, setLoading] = useState(true)
  const [openDialog, setOpenDialog] = useState(false)
  const [selectedRoom, setSelectedRoom] = useState(null)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [formData, setFormData] = useState({
    room_number: '',
    room_type: ROOM_TYPES.SINGLE,
    price_per_night: '',
    floor: '',
    capacity: '',
    description: '',
    amenities: '',
  })

  useEffect(() => {
    fetchRooms()
  }, [])

  const fetchRooms = async () => {
    try {
      setLoading(true)
      const response = await roomsAPI.getRooms()
      setRooms(response.data.rooms || [])
    } catch (error) {
      console.error('Error fetching rooms:', error)
      setError('Failed to load rooms')
    } finally {
      setLoading(false)
    }
  }

  const handleOpenDialog = (room = null) => {
    if (room) {
      setSelectedRoom(room)
      setFormData({
        room_number: room.room_number,
        room_type: room.room_type,
        price_per_night: room.price_per_night,
        floor: room.floor,
        capacity: room.capacity,
        description: room.description || '',
        amenities: room.amenities || '',
      })
    } else {
      setSelectedRoom(null)
      setFormData({
        room_number: '',
        room_type: ROOM_TYPES.SINGLE,
        price_per_night: '',
        floor: '',
        capacity: '',
        description: '',
        amenities: '',
      })
    }
    setOpenDialog(true)
    setError('')
    setSuccess('')
  }

  const handleCloseDialog = () => {
    setOpenDialog(false)
    setSelectedRoom(null)
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
        price_per_night: parseFloat(formData.price_per_night),
        floor: parseInt(formData.floor),
        capacity: parseInt(formData.capacity),
      }

      if (selectedRoom) {
        await roomsAPI.updateRoom(selectedRoom.id, submitData)
        setSuccess('Room updated successfully!')
      } else {
        await roomsAPI.createRoom(submitData)
        setSuccess('Room created successfully!')
      }

      handleCloseDialog()
      fetchRooms()
    } catch (error) {
      console.error('Error saving room:', error)
      setError(error.response?.data?.detail || 'Failed to save room')
    }
  }

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this room?')) {
      try {
        await roomsAPI.deleteRoom(id)
        setSuccess('Room deleted successfully!')
        fetchRooms()
      } catch (error) {
        console.error('Error deleting room:', error)
        setError(error.response?.data?.detail || 'Failed to delete room')
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
          Room Management
        </Typography>
        <Box>
          <Button
            variant="outlined"
            startIcon={<Refresh />}
            onClick={fetchRooms}
            sx={{ mr: 2 }}
          >
            Refresh
          </Button>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={() => handleOpenDialog()}
          >
            Add Room
          </Button>
        </Box>
      </Box>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
      {success && <Alert severity="success" sx={{ mb: 2 }}>{success}</Alert>}

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell><strong>Room Number</strong></TableCell>
              <TableCell><strong>Type</strong></TableCell>
              <TableCell><strong>Status</strong></TableCell>
              <TableCell><strong>Price/Night</strong></TableCell>
              <TableCell><strong>Floor</strong></TableCell>
              <TableCell><strong>Capacity</strong></TableCell>
              <TableCell><strong>Actions</strong></TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {rooms.length === 0 ? (
              <TableRow>
                <TableCell colSpan={7} align="center">
                  <Typography variant="body2" color="text.secondary">
                    No rooms found. Add your first room!
                  </Typography>
                </TableCell>
              </TableRow>
            ) : (
              rooms.map((room) => (
                <TableRow key={room.id}>
                  <TableCell>{room.room_number}</TableCell>
                  <TableCell>{ROOM_TYPE_LABELS[room.room_type]}</TableCell>
                  <TableCell>
                    <Chip
                      label={ROOM_STATUS_LABELS[room.status]}
                      color={STATUS_COLORS[room.status]}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>₹{room.price_per_night}</TableCell>
                  <TableCell>{room.floor}</TableCell>
                  <TableCell>{room.capacity}</TableCell>
                  <TableCell>
                    <IconButton
                      size="small"
                      color="primary"
                      onClick={() => handleOpenDialog(room)}
                    >
                      <Edit />
                    </IconButton>
                    <IconButton
                      size="small"
                      color="error"
                      onClick={() => handleDelete(room.id)}
                    >
                      <Delete />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Add/Edit Room Dialog */}
      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
        <DialogTitle>
          {selectedRoom ? 'Edit Room' : 'Add New Room'}
        </DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2, display: 'flex', flexDirection: 'column', gap: 2 }}>
            <TextField
              label="Room Number"
              name="room_number"
              value={formData.room_number}
              onChange={handleChange}
              required
              fullWidth
            />
            <TextField
              select
              label="Room Type"
              name="room_type"
              value={formData.room_type}
              onChange={handleChange}
              required
              fullWidth
            >
              {Object.entries(ROOM_TYPE_LABELS).map(([value, label]) => (
                <MenuItem key={value} value={value}>
                  {label}
                </MenuItem>
              ))}
            </TextField>
            <TextField
              label="Price per Night"
              name="price_per_night"
              type="number"
              value={formData.price_per_night}
              onChange={handleChange}
              required
              fullWidth
            />
            <TextField
              label="Floor"
              name="floor"
              type="number"
              value={formData.floor}
              onChange={handleChange}
              required
              fullWidth
            />
            <TextField
              label="Capacity"
              name="capacity"
              type="number"
              value={formData.capacity}
              onChange={handleChange}
              required
              fullWidth
            />
            <TextField
              label="Description"
              name="description"
              value={formData.description}
              onChange={handleChange}
              multiline
              rows={3}
              fullWidth
            />
            <TextField
              label="Amenities (comma separated)"
              name="amenities"
              value={formData.amenities}
              onChange={handleChange}
              fullWidth
              placeholder="WiFi, AC, TV, etc."
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button onClick={handleSubmit} variant="contained">
            {selectedRoom ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}

export default Rooms