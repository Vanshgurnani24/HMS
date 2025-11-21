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
  const [anchorEl, setAnchorEl] = useState(null)
  const [notifications, setNotifications] = useState([])
  const [urgentCheckouts, setUrgentCheckouts] = useState([])
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  // Fetch upcoming check-ins and urgent checkouts
  const fetchUpcomingCheckins = async () => {
    setLoading(true)
    try {
      const response = await api.get('/bookings/alerts/upcoming-checkins')
      setNotifications(response.data.bookings || [])
      setUrgentCheckouts(response.data.urgent_checkouts || [])
    } catch (error) {
      console.error('Error fetching notifications:', error)
    } finally {
      setLoading(false)
    }
  }

  // Fetch on component mount and every 5 minutes for auto-refresh
  useEffect(() => {
    fetchUpcomingCheckins()

    // Refresh every 5 minutes (300000 ms)
    const interval = setInterval(() => {
      fetchUpcomingCheckins()
    }, 300000)

    return () => clearInterval(interval)
  }, [])

  const handleClick = (event) => {
    setAnchorEl(event.currentTarget)
    // Refresh when opening popover
    fetchUpcomingCheckins()
  }

  const handleClose = () => {
    setAnchorEl(null)
  }

  const handleViewBooking = () => {
    navigate(`/bookings`)
    handleClose()
  }

  const open = Boolean(anchorEl)
  const notificationCount = notifications.length + urgentCheckouts.length

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
        <Box sx={{ width: 420, maxHeight: 550, overflow: 'auto' }}>
          {/* Header */}
          <Box sx={{ p: 2, bgcolor: 'primary.main', color: 'white' }}>
            <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Warning />
              Booking Alerts
            </Typography>
            <Typography variant="body2" sx={{ mt: 0.5, opacity: 0.9 }}>
              {notificationCount} alert(s) require attention
            </Typography>
          </Box>

          {/* Loading State */}
          {loading ? (
            <Box sx={{ p: 3, textAlign: 'center' }}>
              <Typography color="text.secondary">Loading...</Typography>
            </Box>
          ) : notificationCount === 0 ? (
            <Box sx={{ p: 3, textAlign: 'center' }}>
              <Typography color="text.secondary">
                No alerts at this time
              </Typography>
            </Box>
          ) : (
            <>
              {/* URGENT CHECKOUTS SECTION */}
              {urgentCheckouts.length > 0 && (
                <>
                  <Box sx={{ p: 1.5, bgcolor: 'error.light', color: 'error.contrastText' }}>
                    <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                      URGENT: Guests Must Checkout Today ({urgentCheckouts.length})
                    </Typography>
                    <Typography variant="caption">
                      These rooms have new bookings starting tomorrow
                    </Typography>
                  </Box>
                  <List sx={{ p: 0, bgcolor: 'error.50' }}>
                    {urgentCheckouts.map((booking, index) => (
                      <React.Fragment key={`urgent-${booking.id}`}>
                        <ListItem
                          sx={{
                            flexDirection: 'column',
                            alignItems: 'flex-start',
                            bgcolor: 'rgba(211, 47, 47, 0.08)',
                            '&:hover': {
                              bgcolor: 'rgba(211, 47, 47, 0.15)',
                              cursor: 'pointer',
                            },
                          }}
                          onClick={handleViewBooking}
                        >
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1, width: '100%' }}>
                            <Hotel color="error" fontSize="small" />
                            <Typography variant="subtitle1" sx={{ fontWeight: 600, color: 'error.main' }}>
                              Room {booking.room?.room_number || 'N/A'}
                            </Typography>
                            <Chip
                              label="CHECKOUT TODAY"
                              size="small"
                              color="error"
                            />
                          </Box>
                          <ListItemText
                            primary={
                              <Typography variant="body2" color="text.primary">
                                <strong>Current Guest:</strong>{' '}
                                {booking.customer
                                  ? `${booking.customer.first_name} ${booking.customer.last_name}`
                                  : 'N/A'}
                              </Typography>
                            }
                            secondary={
                              <Typography variant="body2" color="error.main" sx={{ mt: 0.5 }}>
                                Must vacate for new guest arriving tomorrow
                              </Typography>
                            }
                          />
                        </ListItem>
                        {index < urgentCheckouts.length - 1 && <Divider />}
                      </React.Fragment>
                    ))}
                  </List>
                  <Divider />
                </>
              )}

              {/* UPCOMING CHECK-INS SECTION */}
              {notifications.length > 0 && (
                <>
                  <Box sx={{ p: 1.5, bgcolor: 'info.light', color: 'info.contrastText' }}>
                    <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                      Check-ins Tomorrow ({notifications.length})
                    </Typography>
                    <Typography variant="caption">
                      Do not allocate these rooms
                    </Typography>
                  </Box>
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
                          onClick={handleViewBooking}
                        >
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
                              </Box>
                            }
                          />
                        </ListItem>
                        {index < notifications.length - 1 && <Divider />}
                      </React.Fragment>
                    ))}
                  </List>
                </>
              )}
            </>
          )}

          {/* Footer */}
          {notificationCount > 0 && (
            <>
              <Divider />
              <Box sx={{ p: 2, textAlign: 'center' }}>
                <Button
                  fullWidth
                  variant="outlined"
                  onClick={handleViewBooking}
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