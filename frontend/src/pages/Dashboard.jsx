import { useState, useEffect } from 'react'
import {
  Box,
  Grid,
  Paper,
  Typography,
  Card,
  CardContent,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
  Divider,
  Avatar,
} from '@mui/material'
import {
  Hotel,
  People,
  EventNote,
  TrendingUp,
  BookOnline,
  Payment,
  Login as CheckInIcon,
  Logout as CheckOutIcon,
  Person,
  MeetingRoom,
} from '@mui/icons-material'
import { roomsAPI, customersAPI, bookingsAPI, paymentsAPI } from '../api/axios'
import LoadingSpinner from '../components/common/LoadingSpinner'
import { formatDate } from '../utils/dateUtils'

const Dashboard = () => {
  const [stats, setStats] = useState({
    totalRooms: 0,
    availableRooms: 0,
    totalCustomers: 0,
    totalBookings: 0,
    activeBookings: 0,
    revenue: 0,
  })
  const [recentBookings, setRecentBookings] = useState([])
  const [recentPayments, setRecentPayments] = useState([])
  const [todayCheckins, setTodayCheckins] = useState([])
  const [todayCheckouts, setTodayCheckouts] = useState([])
  const [tomorrowCheckins, setTomorrowCheckins] = useState([])
  const [currentlyCheckedIn, setCurrentlyCheckedIn] = useState([])
  const [checkedOutToday, setCheckedOutToday] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchDashboardData()
  }, [])

  const fetchDashboardData = async () => {
    try {
      const [roomsRes, customersRes, bookingsRes, paymentsRes] = await Promise.all([
        roomsAPI.getRooms(),
        customersAPI.getCustomers(),
        bookingsAPI.getBookings(),
        paymentsAPI.getPayments(),
      ])

      const rooms = roomsRes.data.rooms || []
      const customers = customersRes.data.customers || []
      const bookings = bookingsRes.data.bookings || []
      const payments = paymentsRes.data.payments || []

      const availableRooms = rooms.filter(r => r.status === 'available').length
      const activeBookings = bookings.filter(
        b => b.status === 'confirmed' || b.status === 'checked_in'
      ).length

      const completedPayments = payments.filter(p => p.payment_status === 'completed')
      const revenue = completedPayments.reduce((sum, p) => sum + p.amount, 0)

      setStats({
        totalRooms: rooms.length,
        availableRooms,
        totalCustomers: customers.length,
        totalBookings: bookings.length,
        activeBookings,
        revenue,
      })

      // Get recent bookings (last 5, sorted by created_at)
      const sortedBookings = [...bookings].sort(
        (a, b) => new Date(b.created_at) - new Date(a.created_at)
      )
      setRecentBookings(sortedBookings.slice(0, 5))

      // Get recent payments (last 5, sorted by created_at)
      const sortedPayments = [...payments].sort(
        (a, b) => new Date(b.created_at) - new Date(a.created_at)
      )
      setRecentPayments(sortedPayments.slice(0, 5))

      // Get today's check-ins and check-outs
      const today = new Date().toISOString().split('T')[0]
      const tomorrow = new Date(Date.now() + 86400000).toISOString().split('T')[0]

      const todayArrivals = bookings.filter(
        b => b.check_in_date === today && (b.status === 'confirmed' || b.status === 'checked_in')
      )
      // Today's checkouts - those who need to check out today (still checked in)
      const todayDepartures = bookings.filter(
        b => b.check_out_date === today && b.status === 'checked_in'
      )
      // Already checked out today
      const alreadyCheckedOut = bookings.filter(
        b => b.check_out_date === today && b.status === 'checked_out'
      )
      const tomorrowArrivals = bookings.filter(
        b => b.check_in_date === tomorrow && b.status === 'confirmed'
      )

      setTodayCheckins(todayArrivals)
      setTodayCheckouts(todayDepartures)
      setTomorrowCheckins(tomorrowArrivals)
      setCheckedOutToday(alreadyCheckedOut)

      // Get all currently checked-in customers
      const checkedInBookings = bookings.filter(b => b.status === 'checked_in')
      setCurrentlyCheckedIn(checkedInBookings)

    } catch (error) {
      console.error('Error fetching dashboard data:', error)
    } finally {
      setLoading(false)
    }
  }

  const getStatusColor = (status) => {
    const colors = {
      pending: 'warning',
      confirmed: 'info',
      checked_in: 'success',
      checked_out: 'default',
      cancelled: 'error',
    }
    return colors[status] || 'default'
  }

  const getPaymentStatusColor = (status) => {
    const colors = {
      pending: 'warning',
      completed: 'success',
      failed: 'error',
      refunded: 'info',
    }
    return colors[status] || 'default'
  }

  const formatTimeAgo = (dateString) => {
    const date = new Date(dateString)
    const now = new Date()
    const diffMs = now - date
    const diffMins = Math.floor(diffMs / 60000)
    const diffHours = Math.floor(diffMs / 3600000)
    const diffDays = Math.floor(diffMs / 86400000)

    if (diffMins < 1) return 'Just now'
    if (diffMins < 60) return `${diffMins} min ago`
    if (diffHours < 24) return `${diffHours} hr ago`
    if (diffDays < 7) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`
    return formatDate(dateString)
  }

  if (loading) {
    return <LoadingSpinner />
  }

  const statCards = [
    {
      title: 'Total Rooms',
      value: stats.totalRooms,
      subtitle: `${stats.availableRooms} Available`,
      icon: <Hotel sx={{ fontSize: 40, color: '#1976d2' }} />,
      color: '#e3f2fd',
    },
    {
      title: 'Total Customers',
      value: stats.totalCustomers,
      subtitle: 'Registered',
      icon: <People sx={{ fontSize: 40, color: '#2e7d32' }} />,
      color: '#e8f5e9',
    },
    {
      title: 'Active Bookings',
      value: stats.activeBookings,
      subtitle: `${stats.totalBookings} Total`,
      icon: <EventNote sx={{ fontSize: 40, color: '#ed6c02' }} />,
      color: '#fff3e0',
    },
    {
      title: 'Revenue',
      value: `₹${stats.revenue.toLocaleString()}`,
      subtitle: 'Total Collected',
      icon: <TrendingUp sx={{ fontSize: 40, color: '#9c27b0' }} />,
      color: '#f3e5f5',
    },
  ]

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" sx={{ mb: 3, fontWeight: 600 }}>
        Dashboard
      </Typography>

      {/* Stat Cards */}
      <Grid container spacing={3}>
        {statCards.map((card, index) => (
          <Grid item xs={12} sm={6} md={3} key={index}>
            <Card
              sx={{
                height: '100%',
                backgroundColor: card.color,
                transition: 'transform 0.2s',
                '&:hover': {
                  transform: 'translateY(-4px)',
                  boxShadow: 3,
                },
              }}
            >
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                  <Box>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      {card.title}
                    </Typography>
                    <Typography variant="h4" sx={{ fontWeight: 700 }}>
                      {card.value}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {card.subtitle}
                    </Typography>
                  </Box>
                  <Box>{card.icon}</Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Today's Overview */}
      <Grid container spacing={3} sx={{ mt: 2 }}>
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3, height: '100%' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
              <CheckInIcon color="success" />
              <Typography variant="h6">Today's Check-ins</Typography>
              <Chip label={todayCheckins.length} size="small" color="success" />
            </Box>
            {todayCheckins.length === 0 ? (
              <Typography variant="body2" color="text.secondary">
                No check-ins scheduled for today
              </Typography>
            ) : (
              <List dense>
                {todayCheckins.slice(0, 3).map((booking) => (
                  <ListItem key={booking.id} sx={{ px: 0 }}>
                    <ListItemIcon sx={{ minWidth: 40 }}>
                      <Avatar sx={{ width: 32, height: 32, bgcolor: 'success.light' }}>
                        <Person fontSize="small" />
                      </Avatar>
                    </ListItemIcon>
                    <ListItemText
                      primary={booking.customer?.first_name + ' ' + booking.customer?.last_name}
                      secondary={`Room ${booking.room?.room_number} • ${booking.number_of_guests} guest(s)`}
                    />
                  </ListItem>
                ))}
                {todayCheckins.length > 3 && (
                  <Typography variant="caption" color="text.secondary" sx={{ pl: 1 }}>
                    +{todayCheckins.length - 3} more
                  </Typography>
                )}
              </List>
            )}
          </Paper>
        </Grid>

        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3, height: '100%' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
              <CheckOutIcon color="warning" />
              <Typography variant="h6">Today's Check-outs</Typography>
              <Chip label={todayCheckouts.length} size="small" color="warning" />
            </Box>
            {todayCheckouts.length === 0 ? (
              <Typography variant="body2" color="text.secondary">
                No check-outs scheduled for today
              </Typography>
            ) : (
              <List dense sx={{ maxHeight: 200, overflow: 'auto' }}>
                {todayCheckouts.map((booking) => (
                  <ListItem key={booking.id} sx={{ px: 0 }}>
                    <ListItemIcon sx={{ minWidth: 40 }}>
                      <Avatar sx={{ width: 32, height: 32, bgcolor: 'warning.light' }}>
                        <Person fontSize="small" />
                      </Avatar>
                    </ListItemIcon>
                    <ListItemText
                      primary={booking.customer?.first_name + ' ' + booking.customer?.last_name}
                      secondary={`Room ${booking.room?.room_number}`}
                    />
                  </ListItem>
                ))}
              </List>
            )}
          </Paper>
        </Grid>

        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3, height: '100%' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
              <CheckInIcon color="info" />
              <Typography variant="h6">Tomorrow's Check-ins</Typography>
              <Chip label={tomorrowCheckins.length} size="small" color="info" />
            </Box>
            {tomorrowCheckins.length === 0 ? (
              <Typography variant="body2" color="text.secondary">
                No check-ins scheduled for tomorrow
              </Typography>
            ) : (
              <List dense>
                {tomorrowCheckins.slice(0, 3).map((booking) => (
                  <ListItem key={booking.id} sx={{ px: 0 }}>
                    <ListItemIcon sx={{ minWidth: 40 }}>
                      <Avatar sx={{ width: 32, height: 32, bgcolor: 'info.light' }}>
                        <Person fontSize="small" />
                      </Avatar>
                    </ListItemIcon>
                    <ListItemText
                      primary={booking.customer?.first_name + ' ' + booking.customer?.last_name}
                      secondary={`Room ${booking.room?.room_number} • ${booking.number_of_guests} guest(s)`}
                    />
                  </ListItem>
                ))}
                {tomorrowCheckins.length > 3 && (
                  <Typography variant="caption" color="text.secondary" sx={{ pl: 1 }}>
                    +{tomorrowCheckins.length - 3} more
                  </Typography>
                )}
              </List>
            )}
          </Paper>
        </Grid>
      </Grid>

      {/* Currently Checked-In Customers */}
      <Grid container spacing={3} sx={{ mt: 2 }}>
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
              <CheckInIcon color="primary" />
              <Typography variant="h6">Currently Checked-In Guests</Typography>
              <Chip label={currentlyCheckedIn.length} size="small" color="primary" />
            </Box>
            {currentlyCheckedIn.length === 0 ? (
              <Typography variant="body2" color="text.secondary">
                No guests currently checked in
              </Typography>
            ) : (
              <List dense sx={{ '& .MuiListItem-root': { px: 0 } }}>
                {currentlyCheckedIn.map((booking, index) => (
                  <Box key={booking.id}>
                    <ListItem>
                      <ListItemIcon sx={{ minWidth: 40 }}>
                        <Avatar sx={{ width: 36, height: 36, bgcolor: 'primary.main' }}>
                          <Person fontSize="small" />
                        </Avatar>
                      </ListItemIcon>
                      <ListItemText
                        primary={
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Typography variant="body1" fontWeight={500}>
                              {booking.customer?.first_name} {booking.customer?.last_name}
                            </Typography>
                            <Chip
                              label={booking.status.replace('_', ' ')}
                              size="small"
                              color="success"
                              sx={{ height: 20, fontSize: '0.7rem' }}
                            />
                          </Box>
                        }
                        secondary={
                          <Box>
                            <Typography variant="body2" color="text.secondary" display="inline">
                              Room {booking.room?.room_number} • {booking.room?.room_type}
                            </Typography>
                            <Typography variant="body2" color="text.secondary" display="block">
                              {booking.number_of_guests} guest(s) • Check-out: {formatDate(booking.check_out_date)}
                            </Typography>
                            <Typography variant="caption" color="text.secondary" display="block">
                              Booking Ref: {booking.booking_reference}
                            </Typography>
                          </Box>
                        }
                      />
                    </ListItem>
                    {index < currentlyCheckedIn.length - 1 && <Divider />}
                  </Box>
                ))}
              </List>
            )}
          </Paper>
        </Grid>
      </Grid>

      {/* Checked Out Today */}
      <Grid container spacing={3} sx={{ mt: 2 }}>
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
              <CheckOutIcon color="success" />
              <Typography variant="h6">Checked Out Today</Typography>
              <Chip label={checkedOutToday.length} size="small" color="success" />
            </Box>
            {checkedOutToday.length === 0 ? (
              <Typography variant="body2" color="text.secondary">
                No guests have checked out today yet
              </Typography>
            ) : (
              <List dense sx={{ '& .MuiListItem-root': { px: 0 } }}>
                {checkedOutToday.map((booking, index) => (
                  <Box key={booking.id}>
                    <ListItem>
                      <ListItemIcon sx={{ minWidth: 40 }}>
                        <Avatar sx={{ width: 36, height: 36, bgcolor: 'success.light' }}>
                          <Person fontSize="small" />
                        </Avatar>
                      </ListItemIcon>
                      <ListItemText
                        primary={
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Typography variant="body1" fontWeight={500}>
                              {booking.customer?.first_name} {booking.customer?.last_name}
                            </Typography>
                            <Chip
                              label={booking.status.replace('_', ' ')}
                              size="small"
                              color="default"
                              sx={{ height: 20, fontSize: '0.7rem' }}
                            />
                          </Box>
                        }
                        secondary={
                          <Box>
                            <Typography variant="body2" color="text.secondary" display="inline">
                              Room {booking.room?.room_number} • {booking.room?.room_type}
                            </Typography>
                            <Typography variant="body2" color="text.secondary" display="block">
                              Stay: {formatDate(booking.check_in_date)} - {formatDate(booking.check_out_date)}
                            </Typography>
                            <Typography variant="caption" color="text.secondary" display="block">
                              Booking Ref: {booking.booking_reference}
                            </Typography>
                          </Box>
                        }
                      />
                    </ListItem>
                    {index < checkedOutToday.length - 1 && <Divider />}
                  </Box>
                ))}
              </List>
            )}
          </Paper>
        </Grid>
      </Grid>

      {/* Recent Activity */}
      <Grid container spacing={3} sx={{ mt: 2 }}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
              <BookOnline color="primary" />
              <Typography variant="h6">Recent Bookings</Typography>
            </Box>
            {recentBookings.length === 0 ? (
              <Typography variant="body2" color="text.secondary">
                No bookings yet
              </Typography>
            ) : (
              <List dense sx={{ '& .MuiListItem-root': { px: 0 } }}>
                {recentBookings.map((booking, index) => (
                  <Box key={booking.id}>
                    <ListItem>
                      <ListItemIcon sx={{ minWidth: 40 }}>
                        <Avatar sx={{ width: 32, height: 32, bgcolor: 'primary.light' }}>
                          <MeetingRoom fontSize="small" />
                        </Avatar>
                      </ListItemIcon>
                      <ListItemText
                        primary={
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Typography variant="body2" fontWeight={500}>
                              {booking.booking_reference}
                            </Typography>
                            <Chip
                              label={booking.status.replace('_', ' ')}
                              size="small"
                              color={getStatusColor(booking.status)}
                              sx={{ height: 20, fontSize: '0.7rem' }}
                            />
                          </Box>
                        }
                        secondary={
                          <Box>
                            <Typography variant="caption" color="text.secondary" display="block">
                              {booking.customer?.first_name} {booking.customer?.last_name} • Room {booking.room?.room_number}
                            </Typography>
                            <Typography variant="caption" color="text.secondary" display="block">
                              {formatDate(booking.check_in_date)} → {formatDate(booking.check_out_date)} • {formatTimeAgo(booking.created_at)}
                            </Typography>
                          </Box>
                        }
                      />
                    </ListItem>
                    {index < recentBookings.length - 1 && <Divider />}
                  </Box>
                ))}
              </List>
            )}
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
              <Payment color="success" />
              <Typography variant="h6">Recent Payments</Typography>
            </Box>
            {recentPayments.length === 0 ? (
              <Typography variant="body2" color="text.secondary">
                No payments yet
              </Typography>
            ) : (
              <List dense sx={{ '& .MuiListItem-root': { px: 0 } }}>
                {recentPayments.map((payment, index) => (
                  <Box key={payment.id}>
                    <ListItem>
                      <ListItemIcon sx={{ minWidth: 40 }}>
                        <Avatar sx={{ width: 32, height: 32, bgcolor: 'success.light' }}>
                          ₹
                        </Avatar>
                      </ListItemIcon>
                      <ListItemText
                        primary={
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Typography variant="body2" fontWeight={600} color="success.main">
                              ₹{payment.amount.toLocaleString()}
                            </Typography>
                            <Chip
                              label={payment.payment_status}
                              size="small"
                              color={getPaymentStatusColor(payment.payment_status)}
                              sx={{ height: 20, fontSize: '0.7rem' }}
                            />
                          </Box>
                        }
                        secondary={
                          <Typography variant="caption" color="text.secondary">
                            {payment.payment_method?.replace('_', ' ')} • {payment.transaction_id?.slice(0, 15)}... • {formatTimeAgo(payment.created_at)}
                          </Typography>
                        }
                      />
                    </ListItem>
                    {index < recentPayments.length - 1 && <Divider />}
                  </Box>
                ))}
              </List>
            )}
          </Paper>
        </Grid>
      </Grid>

      {/* Quick Stats */}
      <Grid container spacing={3} sx={{ mt: 2 }}>
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Quick Stats
            </Typography>
            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid item xs={6} sm={2.4}>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h4" fontWeight="bold" color="primary">
                    {stats.totalRooms > 0
                      ? `${Math.round(((stats.totalRooms - stats.availableRooms) / stats.totalRooms) * 100)}%`
                      : '0%'}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Occupancy Rate
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={6} sm={2.4}>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h4" fontWeight="bold" color="secondary.main">
                    ₹{stats.totalBookings > 0 ? Math.round(stats.revenue / stats.totalBookings).toLocaleString() : 0}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Avg. Revenue/Booking
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={6} sm={2.4}>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h4" fontWeight="bold" color="success.main">
                    {todayCheckins.length}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Arrivals Today
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={6} sm={2.4}>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h4" fontWeight="bold" color="warning.main">
                    {todayCheckouts.length}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Departures Today
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={6} sm={2.4}>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h4" fontWeight="bold" color="info.main">
                    {tomorrowCheckins.length}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Arrivals Tomorrow
                  </Typography>
                </Box>
              </Grid>
            </Grid>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  )
}

export default Dashboard
