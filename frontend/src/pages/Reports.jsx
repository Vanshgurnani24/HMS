import { useState, useEffect } from 'react'
import {
  Box,
  Paper,
  Typography,
  Grid,
  Card,
  CardContent,
  MenuItem,
  TextField,
  Button,
  Alert,
} from '@mui/material'
import { Download, Refresh } from '@mui/icons-material'
import { BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { roomsAPI, customersAPI, bookingsAPI, paymentsAPI } from '../api/axios'
import LoadingSpinner from '../components/common/LoadingSpinner'

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8']

const Reports = () => {
  const [loading, setLoading] = useState(true)
  const [reportType, setReportType] = useState('overview')
  const [dateRange, setDateRange] = useState('all')
  const [data, setData] = useState({
    rooms: [],
    customers: [],
    bookings: [],
    payments: [],
  })
  const [chartData, setChartData] = useState({
    roomTypes: [],
    bookingStatus: [],
    revenueByMonth: [],
  })

  useEffect(() => {
    fetchReportData()
  }, [dateRange])

  const fetchReportData = async () => {
    try {
      setLoading(true)
      const [roomsRes, customersRes, bookingsRes, paymentsRes] = await Promise.all([
        roomsAPI.getRooms(),
        customersAPI.getCustomers(),
        bookingsAPI.getBookings(),
        paymentsAPI.getPayments(),
      ])

      const fetchedData = {
        rooms: roomsRes.data.rooms || [],
        customers: customersRes.data.customers || [],
        bookings: bookingsRes.data.bookings || [],
        payments: paymentsRes.data.payments || [],
      }

      setData(fetchedData)
      processChartData(fetchedData)
    } catch (error) {
      console.error('Error fetching report data:', error)
    } finally {
      setLoading(false)
    }
  }

  const processChartData = (fetchedData) => {
    // Room types distribution
    const roomTypeCount = {}
    fetchedData.rooms.forEach(room => {
      roomTypeCount[room.room_type] = (roomTypeCount[room.room_type] || 0) + 1
    })
    const roomTypesData = Object.entries(roomTypeCount).map(([type, count]) => ({
      name: type.charAt(0).toUpperCase() + type.slice(1),
      value: count,
    }))

    // Booking status distribution
    const bookingStatusCount = {}
    fetchedData.bookings.forEach(booking => {
      bookingStatusCount[booking.status] = (bookingStatusCount[booking.status] || 0) + 1
    })
    const bookingStatusData = Object.entries(bookingStatusCount).map(([status, count]) => ({
      name: status.replace('_', ' ').split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' '),
      value: count,
    }))

    // Revenue by month (mock data for now)
    const revenueData = [
      { month: 'Jan', revenue: 45000 },
      { month: 'Feb', revenue: 52000 },
      { month: 'Mar', revenue: 48000 },
      { month: 'Apr', revenue: 61000 },
      { month: 'May', revenue: 55000 },
      { month: 'Jun', revenue: 67000 },
    ]

    setChartData({
      roomTypes: roomTypesData,
      bookingStatus: bookingStatusData,
      revenueByMonth: revenueData,
    })
  }

  const calculateStats = () => {
    const totalRooms = data.rooms.length
    const availableRooms = data.rooms.filter(r => r.status === 'available').length
    const occupancyRate = totalRooms > 0 ? ((totalRooms - availableRooms) / totalRooms * 100).toFixed(1) : 0

    const totalBookings = data.bookings.length
    const activeBookings = data.bookings.filter(b => 
      b.status === 'confirmed' || b.status === 'checked_in'
    ).length

    const completedPayments = data.payments.filter(p => p.payment_status === 'completed')
    const totalRevenue = completedPayments.reduce((sum, p) => sum + p.amount, 0)
    const avgBookingValue = totalBookings > 0 ? (totalRevenue / totalBookings).toFixed(0) : 0

    return {
      totalRooms,
      availableRooms,
      occupancyRate,
      totalBookings,
      activeBookings,
      totalRevenue,
      avgBookingValue,
      totalCustomers: data.customers.length,
    }
  }

  if (loading) {
    return <LoadingSpinner />
  }

  const stats = calculateStats()

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" sx={{ fontWeight: 600 }}>
          Reports & Analytics
        </Typography>
        <Box>
          <Button
            variant="outlined"
            startIcon={<Refresh />}
            onClick={fetchReportData}
            sx={{ mr: 2 }}
          >
            Refresh
          </Button>
          <Button
            variant="contained"
            startIcon={<Download />}
          >
            Export PDF
          </Button>
        </Box>
      </Box>

      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12} md={6}>
          <TextField
            select
            label="Report Type"
            value={reportType}
            onChange={(e) => setReportType(e.target.value)}
            fullWidth
          >
            <MenuItem value="overview">Overview</MenuItem>
            <MenuItem value="rooms">Room Analysis</MenuItem>
            <MenuItem value="bookings">Booking Analysis</MenuItem>
            <MenuItem value="revenue">Revenue Analysis</MenuItem>
          </TextField>
        </Grid>
        <Grid item xs={12} md={6}>
          <TextField
            select
            label="Date Range"
            value={dateRange}
            onChange={(e) => setDateRange(e.target.value)}
            fullWidth
          >
            <MenuItem value="all">All Time</MenuItem>
            <MenuItem value="today">Today</MenuItem>
            <MenuItem value="week">This Week</MenuItem>
            <MenuItem value="month">This Month</MenuItem>
            <MenuItem value="year">This Year</MenuItem>
          </TextField>
        </Grid>
      </Grid>

      {/* Key Metrics */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography variant="body2" color="text.secondary">
                Total Rooms
              </Typography>
              <Typography variant="h4" sx={{ fontWeight: 700 }}>
                {stats.totalRooms}
              </Typography>
              <Typography variant="caption" color="success.main">
                {stats.availableRooms} Available
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography variant="body2" color="text.secondary">
                Occupancy Rate
              </Typography>
              <Typography variant="h4" sx={{ fontWeight: 700 }}>
                {stats.occupancyRate}%
              </Typography>
              <Typography variant="caption">
                Current occupancy
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography variant="body2" color="text.secondary">
                Total Bookings
              </Typography>
              <Typography variant="h4" sx={{ fontWeight: 700 }}>
                {stats.totalBookings}
              </Typography>
              <Typography variant="caption" color="info.main">
                {stats.activeBookings} Active
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography variant="body2" color="text.secondary">
                Total Revenue
              </Typography>
              <Typography variant="h4" sx={{ fontWeight: 700 }}>
                ₹{stats.totalRevenue.toLocaleString()}
              </Typography>
              <Typography variant="caption">
                Avg: ₹{stats.avgBookingValue}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Charts */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Room Types Distribution
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={chartData.roomTypes}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {chartData.roomTypes.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Booking Status Distribution
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={chartData.bookingStatus}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#82ca9d"
                  dataKey="value"
                >
                  {chartData.bookingStatus.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Revenue Trend
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={chartData.revenueByMonth}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="revenue" fill="#8884d8" name="Revenue (₹)" />
              </BarChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>
      </Grid>

      {/* Additional Stats */}
      <Grid container spacing={3} sx={{ mt: 2 }}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Quick Statistics
            </Typography>
            <Box sx={{ mt: 2 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                <Typography>Total Customers</Typography>
                <Typography fontWeight="bold">{stats.totalCustomers}</Typography>
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                <Typography>Average Booking Value</Typography>
                <Typography fontWeight="bold">₹{stats.avgBookingValue}</Typography>
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                <Typography>Revenue per Room</Typography>
                <Typography fontWeight="bold">
                  ₹{stats.totalRooms > 0 ? Math.round(stats.totalRevenue / stats.totalRooms) : 0}
                </Typography>
              </Box>
            </Box>
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              System Status
            </Typography>
            <Alert severity="success" sx={{ mt: 2 }}>
              All systems operational
            </Alert>
            <Typography variant="body2" sx={{ mt: 2 }}>
              Last updated: {new Date().toLocaleString()}
            </Typography>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  )
}

export default Reports