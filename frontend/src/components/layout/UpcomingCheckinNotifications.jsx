import React, { useState, useEffect } from 'react'
import {
  Badge,
  IconButton,
  Popover,
  List,
  ListItem,
  ListItemText,
  Typography,
  Box,
  Chip,
  Divider,
  Button,
} from '@mui/material'
import { Notifications, Hotel, Warning } from '@mui/icons-material'
import { useNavigate } from 'react-router-dom'
import api from '../../api/axios'

const UpcomingCheckinNotifications = () => {
  console.log('🔔 UpcomingCheckinNotifications: Component rendering...')
  
  const [anchorEl, setAnchorEl] = useState(null)
  const [notifications, setNotifications] = useState([])
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  // Fetch upcoming check-ins
  const fetchUpcomingCheckins = async () => {
    console.log('🔍 fetchUpcomingCheckins: Starting API call...')
    setLoading(true)
    try {
      console.log('📡 Making request to: /bookings/alerts/upcoming-checkins')
      const response = await api.get('/bookings/alerts/upcoming-checkins')
      console.log('✅ Response received:', response.data)
      console.log('📊 Total notifications:', response.data.bookings?.length || 0)
      setNotifications(response.data.bookings || [])
    } catch (error) {
      console.error('❌ Error fetching upcoming check-ins:', error)
      console.error('❌ Error details:', error.response?.data)
      console.error('❌ Error status:', error.response?.status)
    } finally {
      setLoading(false)
      console.log('🏁 fetchUpcomingCheckins: Completed')
    }
  }

  // Fetch on component mount and every hour
  useEffect(() => {
    console.log('🔄 useEffect: Running...')
    fetchUpcomingCheckins()
    
    // Refresh every hour (3600000 ms)
    const interval = setInterval(() => {
      console.log('⏰ Auto-refresh: Fetching notifications...')
      fetchUpcomingCheckins()
    }, 3600000)
    
    return () => {
      console.log('🧹 useEffect: Cleanup - clearing interval')
      clearInterval(interval)
    }
  }, [])

  const handleClick = (event) => {
    console.log('🖱️ Bell clicked')
    setAnchorEl(event.currentTarget)
  }

  const handleClose = () => {
    console.log('❌ Popover closed')
    setAnchorEl(null)
  }

  const handleViewBooking = (bookingId) => {
    console.log('👁️ Viewing booking:', bookingId)
    navigate(`/bookings`)
    handleClose()
  }

  const open = Boolean(anchorEl)
  const notificationCount = notifications.length

  console.log('📈 Current state:', {
    notificationCount,
    loading,
    open,
    notificationsLength: notifications.length
  })

  return (
    <>
      {console.log('🎨 Rendering JSX...')}
      {/* Notification Bell Icon with Badge */}
      <IconButton
        color="inherit"
        onClick={handleClick}
        sx={{ mr: 2 }}
      >
        <Badge badgeContent={notificationCount} color="error">
          <Notifications />
        </Badge>
      </IconButton>

      {/* Notification Popover */}
      <Popover
        open={open}
        anchorEl={anchorEl}
        onClose={handleClose}
        anchorOrigin={{
          vertical: 'bottom',
          horizontal: 'right',
        }}
        transformOrigin={{
          vertical: 'top',
          horizontal: 'right',
        }}
      >
        <Box sx={{ width: 400, maxHeight: 500, overflow: 'auto' }}>
          {/* Header */}
          <Box sx={{ p: 2, bgcolor: 'primary.main', color: 'white' }}>
            <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Warning />
              Upcoming Check-ins Tomorrow
            </Typography>
            <Typography variant="body2" sx={{ mt: 0.5, opacity: 0.9 }}>
              {notificationCount} room(s) should NOT be allocated
            </Typography>
          </Box>

          {/* Notification List */}
          {loading ? (
            <Box sx={{ p: 3, textAlign: 'center' }}>
              <Typography color="text.secondary">Loading...</Typography>
            </Box>
          ) : notificationCount === 0 ? (
            <Box sx={{ p: 3, textAlign: 'center' }}>
              <Typography color="text.secondary">
                No check-ins scheduled for tomorrow
              </Typography>
            </Box>
          ) : (
            <List sx={{ p: 0 }}>
              {notifications.map((booking, index) => (
                <React.Fragment key={booking.id}>
                  <ListItem
                    sx={{
                      flexDirection: 'column',
                      alignItems: 'flex-start',
                      '&:hover': {
                        bgcolor: 'action.hover',
                        cursor: 'pointer',
                      },
                    }}
                    onClick={() => handleViewBooking(booking.id)}
                  >
                    {/* Room Info */}
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1, width: '100%' }}>
                      <Hotel color="primary" fontSize="small" />
                      <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                        Room {booking.room?.room_number || 'N/A'}
                      </Typography>
                      <Chip
                        label={booking.room?.room_type || 'N/A'}
                        size="small"
                        color="primary"
                        variant="outlined"
                      />
                    </Box>

                    {/* Customer Info */}
                    <ListItemText
                      primary={
                        <Typography variant="body2" color="text.primary">
                          <strong>Customer:</strong>{' '}
                          {booking.customer
                            ? `${booking.customer.first_name} ${booking.customer.last_name}`
                            : 'N/A'}
                        </Typography>
                      }
                      secondary={
                        <Box component="span" sx={{ display: 'block', mt: 0.5 }}>
                          <Typography variant="body2" color="text.secondary">
                            <strong>Booking:</strong> {booking.booking_reference}
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            <strong>Guests:</strong> {booking.number_of_guests}
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            <strong>Check-in:</strong>{' '}
                            {new Date(booking.check_in_date).toLocaleDateString('en-GB')}
                          </Typography>
                          {booking.special_requests && (
                            <Typography
                              variant="body2"
                              color="warning.main"
                              sx={{ mt: 0.5, fontStyle: 'italic' }}
                            >
                              <strong>Note:</strong> {booking.special_requests}
                            </Typography>
                          )}
                        </Box>
                      }
                    />
                  </ListItem>
                  {index < notificationCount - 1 && <Divider />}
                </React.Fragment>
              ))}
            </List>
          )}

          {/* Footer */}
          {notificationCount > 0 && (
            <>
              <Divider />
              <Box sx={{ p: 2, textAlign: 'center' }}>
                <Button
                  fullWidth
                  variant="outlined"
                  onClick={() => {
                    navigate('/bookings')
                    handleClose()
                  }}
                >
                  View All Bookings
                </Button>
              </Box>
            </>
          )}
        </Box>
      </Popover>
    </>
  )
}

export default UpcomingCheckinNotifications