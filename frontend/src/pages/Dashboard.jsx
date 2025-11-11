import { useState, useEffect } from 'react'
import {
  Box,
  Grid,
  Paper,
  Typography,
  Card,
  CardContent,
} from '@mui/material'
import {
  Hotel,
  People,
  EventNote,
  TrendingUp,
} from '@mui/icons-material'
import { roomsAPI, customersAPI, bookingsAPI, paymentsAPI } from '../api/axios'
import LoadingSpinner from '../components/common/LoadingSpinner'

const Dashboard = () => {
  const [stats, setStats] = useState({
    totalRooms: 0,
    availableRooms: 0,
    totalCustomers: 0,
    totalBookings: 0,
    activeBookings: 0,
    revenue: 0,
  })
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
    } catch (error) {
      console.error('Error fetching dashboard data:', error)
    } finally {
      setLoading(false)
    }
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

      <Grid container spacing={3} sx={{ mt: 2 }}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Quick Stats
            </Typography>
            <Box sx={{ mt: 2 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                <Typography>Occupancy Rate</Typography>
                <Typography fontWeight="bold">
                  {stats.totalRooms > 0
                    ? `${Math.round(((stats.totalRooms - stats.availableRooms) / stats.totalRooms) * 100)}%`
                    : '0%'}
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                <Typography>Average Revenue per Booking</Typography>
                <Typography fontWeight="bold">
                  ₹{stats.totalBookings > 0 ? Math.round(stats.revenue / stats.totalBookings) : 0}
                </Typography>
              </Box>
            </Box>
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Recent Activity
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
              System is operational. All services running normally.
            </Typography>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  )
}

export default Dashboard