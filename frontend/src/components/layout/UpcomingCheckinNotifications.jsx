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
import api from '../../utils/api'

const UpcomingCheckinNotifications = () => {
  const [anchorEl, setAnchorEl] = useState(null)
  const [notifications, setNotifications] = useState([])
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  // Fetch upcoming check-ins
  const fetchUpcomingCheckins = async () => {
    setLoading(true)
    try {
      const response = await api.get('/bookings/alerts/upcoming-checkins')
      setNotifications(response.data.bookings || [])
    } catch (error) {
      console.error('Error fetching upcoming check-ins:', error)
    } finally {
      setLoading(false)
    }
  }

  // Fetch on component mount and every hour
  useEffect(() => {
    fetchUpcomingCheckins()
    
    // Refresh every hour (3600000 ms)
    const interval = setInterval(fetchUpcomingCheckins, 3600000)
    
    return () => clearInterval(interval)
  }, [])

  const handleClick = (event) => {
    setAnchorEl(event.currentTarget)
  }

  const handleClose = () => {
    setAnchorEl(null)
  }

  const handleViewBooking = (bookingId) => {
    navigate(`/bookings`)
    handleClose()
  }

  const open = Boolean(anchorEl)
  const notificationCount = notifications.length

  return (
    <>
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
                            {new Date(booking.check_in_date).toLocaleDateString()}
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