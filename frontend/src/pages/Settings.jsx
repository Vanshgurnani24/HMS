import { useState, useEffect } from 'react'
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  Alert,
  CircularProgress,
  Divider,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Chip,
  Grid,
} from '@mui/material'
import { Save, Business, Add, Edit, Delete, Hotel } from '@mui/icons-material'
import { settingsAPI, roomTypesAPI } from '../api/axios'

const Settings = () => {
  // Hotel settings state
  const [settings, setSettings] = useState({
    hotel_name: '',
    hotel_address: '',
    hotel_phone: '',
    hotel_email: '',
  })
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [success, setSuccess] = useState('')
  const [error, setError] = useState('')

  // Room types state
  const [roomTypes, setRoomTypes] = useState([])
  const [roomTypesLoading, setRoomTypesLoading] = useState(true)
  const [roomTypeDialog, setRoomTypeDialog] = useState(false)
  const [editingRoomType, setEditingRoomType] = useState(null)
  const [roomTypeForm, setRoomTypeForm] = useState({
    name: '',
    display_name: '',
  })
  const [roomTypeError, setRoomTypeError] = useState('')

  useEffect(() => {
    fetchSettings()
    fetchRoomTypes()
  }, [])

  const fetchSettings = async () => {
    try {
      setLoading(true)
      const response = await settingsAPI.getHotelSettings()
      setSettings({
        hotel_name: response.data.hotel_name || '',
        hotel_address: response.data.hotel_address || '',
        hotel_phone: response.data.hotel_phone || '',
        hotel_email: response.data.hotel_email || '',
      })
    } catch (err) {
      setError('Failed to load settings')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const fetchRoomTypes = async () => {
    try {
      setRoomTypesLoading(true)
      const response = await roomTypesAPI.getRoomTypes(true) // Include inactive
      setRoomTypes(response.data.room_types || [])
    } catch (err) {
      console.error('Failed to load room types:', err)
    } finally {
      setRoomTypesLoading(false)
    }
  }

  const handleChange = (field) => (event) => {
    setSettings(prev => ({
      ...prev,
      [field]: event.target.value
    }))
    setSuccess('')
    setError('')
  }

  const handleSave = async () => {
    if (!settings.hotel_name.trim()) {
      setError('Hotel name is required')
      return
    }

    try {
      setSaving(true)
      setError('')
      await settingsAPI.updateHotelSettings(settings)
      setSuccess('Settings saved successfully!')
    } catch (err) {
      setError('Failed to save settings')
      console.error(err)
    } finally {
      setSaving(false)
    }
  }

  // Room Type handlers
  const handleOpenRoomTypeDialog = (roomType = null) => {
    if (roomType) {
      setEditingRoomType(roomType)
      setRoomTypeForm({
        name: roomType.name,
        display_name: roomType.display_name,
      })
    } else {
      setEditingRoomType(null)
      setRoomTypeForm({
        name: '',
        display_name: '',
      })
    }
    setRoomTypeError('')
    setRoomTypeDialog(true)
  }

  const handleCloseRoomTypeDialog = () => {
    setRoomTypeDialog(false)
    setEditingRoomType(null)
    setRoomTypeError('')
  }

  const handleRoomTypeFormChange = (field) => (event) => {
    setRoomTypeForm(prev => ({
      ...prev,
      [field]: event.target.value
    }))
  }

  const handleSaveRoomType = async () => {
    if (!roomTypeForm.display_name.trim()) {
      setRoomTypeError('Display name is required')
      return
    }

    try {
      if (editingRoomType) {
        await roomTypesAPI.updateRoomType(editingRoomType.id, {
          display_name: roomTypeForm.display_name,
        })
      } else {
        const name = roomTypeForm.name.trim() || roomTypeForm.display_name.toLowerCase().replace(/\s+/g, '_')
        await roomTypesAPI.createRoomType({
          name,
          display_name: roomTypeForm.display_name,
        })
      }
      handleCloseRoomTypeDialog()
      fetchRoomTypes()
      setSuccess(editingRoomType ? 'Room type updated!' : 'Room type created!')
    } catch (err) {
      setRoomTypeError(err.response?.data?.detail || 'Failed to save room type')
    }
  }

  const handleToggleRoomTypeStatus = async (roomType) => {
    try {
      await roomTypesAPI.updateRoomType(roomType.id, {
        is_active: !roomType.is_active
      })
      fetchRoomTypes()
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to update room type')
    }
  }

  const handleDeleteRoomType = async (roomType) => {
    if (!window.confirm(`Are you sure you want to delete "${roomType.display_name}"? This action cannot be undone.`)) {
      return
    }

    try {
      await roomTypesAPI.deleteRoomType(roomType.id)
      fetchRoomTypes()
      setSuccess('Room type deleted!')
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to delete room type')
    }
  }

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '50vh' }}>
        <CircularProgress />
      </Box>
    )
  }

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" sx={{ mb: 3, fontWeight: 600 }}>
        Settings
      </Typography>

      {success && (
        <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess('')}>
          {success}
        </Alert>
      )}

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* Hotel Information */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <Business sx={{ mr: 1, color: 'primary.main' }} />
              <Typography variant="h6">Hotel Information</Typography>
            </Box>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
              Configure your hotel details. The hotel name will appear on all receipts and reports.
            </Typography>

            <Divider sx={{ mb: 3 }} />

            <TextField
              fullWidth
              label="Hotel Name"
              value={settings.hotel_name}
              onChange={handleChange('hotel_name')}
              sx={{ mb: 2 }}
              required
              helperText="This name will appear on receipts and reports"
            />

            <TextField
              fullWidth
              label="Hotel Address"
              value={settings.hotel_address}
              onChange={handleChange('hotel_address')}
              sx={{ mb: 2 }}
              multiline
              rows={2}
            />

            <TextField
              fullWidth
              label="Hotel Phone"
              value={settings.hotel_phone}
              onChange={handleChange('hotel_phone')}
              sx={{ mb: 2 }}
            />

            <TextField
              fullWidth
              label="Hotel Email"
              value={settings.hotel_email}
              onChange={handleChange('hotel_email')}
              sx={{ mb: 3 }}
              type="email"
            />

            <Button
              variant="contained"
              startIcon={saving ? <CircularProgress size={20} color="inherit" /> : <Save />}
              onClick={handleSave}
              disabled={saving}
            >
              {saving ? 'Saving...' : 'Save Settings'}
            </Button>
          </Paper>
        </Grid>

        {/* Room Types */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <Hotel sx={{ mr: 1, color: 'primary.main' }} />
                <Typography variant="h6">Room Types</Typography>
              </Box>
              <Button
                variant="contained"
                size="small"
                startIcon={<Add />}
                onClick={() => handleOpenRoomTypeDialog()}
              >
                Add Type
              </Button>
            </Box>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
              Manage the types of rooms available in your hotel.
            </Typography>

            <Divider sx={{ mb: 2 }} />

            {roomTypesLoading ? (
              <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
                <CircularProgress size={30} />
              </Box>
            ) : (
              <TableContainer>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell><strong>Type</strong></TableCell>
                      <TableCell><strong>Status</strong></TableCell>
                      <TableCell><strong>Actions</strong></TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {roomTypes.length === 0 ? (
                      <TableRow>
                        <TableCell colSpan={3} align="center">
                          No room types configured
                        </TableCell>
                      </TableRow>
                    ) : (
                      roomTypes.map((roomType) => (
                        <TableRow key={roomType.id}>
                          <TableCell>
                            <Typography variant="body2" fontWeight="medium">
                              {roomType.display_name}
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                              {roomType.name}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Chip
                              label={roomType.is_active ? 'Active' : 'Inactive'}
                              color={roomType.is_active ? 'success' : 'default'}
                              size="small"
                              onClick={() => handleToggleRoomTypeStatus(roomType)}
                              sx={{ cursor: 'pointer' }}
                            />
                          </TableCell>
                          <TableCell>
                            <IconButton
                              size="small"
                              onClick={() => handleOpenRoomTypeDialog(roomType)}
                              title="Edit"
                            >
                              <Edit fontSize="small" />
                            </IconButton>
                            <IconButton
                              size="small"
                              color="error"
                              onClick={() => handleDeleteRoomType(roomType)}
                              title="Delete"
                            >
                              <Delete fontSize="small" />
                            </IconButton>
                          </TableCell>
                        </TableRow>
                      ))
                    )}
                  </TableBody>
                </Table>
              </TableContainer>
            )}
          </Paper>
        </Grid>
      </Grid>

      {/* Room Type Dialog */}
      <Dialog open={roomTypeDialog} onClose={handleCloseRoomTypeDialog} maxWidth="sm" fullWidth>
        <DialogTitle>
          {editingRoomType ? 'Edit Room Type' : 'Add Room Type'}
        </DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2, display: 'flex', flexDirection: 'column', gap: 2 }}>
            {roomTypeError && (
              <Alert severity="error">{roomTypeError}</Alert>
            )}

            {!editingRoomType && (
              <TextField
                fullWidth
                label="Internal Name"
                value={roomTypeForm.name}
                onChange={handleRoomTypeFormChange('name')}
                helperText="Optional. Auto-generated from display name if empty (e.g., 'executive_suite')"
              />
            )}

            <TextField
              fullWidth
              label="Display Name"
              value={roomTypeForm.display_name}
              onChange={handleRoomTypeFormChange('display_name')}
              required
              helperText="The name shown to users (e.g., 'Executive Suite')"
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseRoomTypeDialog}>Cancel</Button>
          <Button variant="contained" onClick={handleSaveRoomType}>
            {editingRoomType ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}

export default Settings
