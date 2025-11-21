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
} from '@mui/material'
import { Save, Business } from '@mui/icons-material'
import { settingsAPI } from '../api/axios'

const Settings = () => {
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

  useEffect(() => {
    fetchSettings()
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

      <Paper sx={{ p: 3, maxWidth: 600 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <Business sx={{ mr: 1, color: 'primary.main' }} />
          <Typography variant="h6">Hotel Information</Typography>
        </Box>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
          Configure your hotel details. The hotel name will appear on all receipts and reports.
        </Typography>

        <Divider sx={{ mb: 3 }} />

        {success && (
          <Alert severity="success" sx={{ mb: 2 }}>
            {success}
          </Alert>
        )}

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

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
    </Box>
  )
}

export default Settings
