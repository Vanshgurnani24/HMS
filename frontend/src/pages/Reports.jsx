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
import { reportsAPI, settingsAPI } from '../api/axios'
import LoadingSpinner from '../components/common/LoadingSpinner'
import html2pdf from 'html2pdf.js'

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8']

const Reports = () => {
  const [loading, setLoading] = useState(true)
  const [reportType, setReportType] = useState('overview')
  const [dateRange, setDateRange] = useState('all')
  const [reportData, setReportData] = useState(null)
  const [error, setError] = useState('')
  const [hotelName, setHotelName] = useState('My Hotel')
  const [gstNumber, setGstNumber] = useState('')

  // Fetch hotel settings on mount
  useEffect(() => {
    const fetchHotelSettings = async () => {
      try {
        const response = await settingsAPI.getHotelSettings()
        setHotelName(response.data.hotel_name || 'My Hotel')
        setGstNumber(response.data.gst_number || '')
      } catch (err) {
        console.error('Error fetching hotel settings:', err)
      }
    }
    fetchHotelSettings()
  }, [])

  // Fetch report data whenever reportType or dateRange changes
  useEffect(() => {
    fetchReportData()
  }, [reportType, dateRange])

  const fetchReportData = async () => {
    try {
      setLoading(true)
      setError('')
      const response = await reportsAPI.getReport(reportType, dateRange)
      setReportData(response.data)
    } catch (error) {
      console.error('Error fetching report data:', error)
      setError(error.response?.data?.detail || 'Failed to load report data')
    } finally {
      setLoading(false)
    }
  }

  // PDF Export Function using html2pdf
  const handleExportPDF = () => {
    if (!reportData) return

    const reportTitles = {
      overview: 'Overview Report',
      rooms: 'Room Analysis Report',
      bookings: 'Booking Analysis Report',
      revenue: 'Revenue Analysis Report'
    }

    // Calculate actual date range
    const today = new Date()
    let startDate = null
    let dateRangeText = 'All Time'

    if (dateRange === 'today') {
      startDate = today
      dateRangeText = today.toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' })
    } else if (dateRange === 'week') {
      const dayOfWeek = today.getDay()
      const diff = dayOfWeek === 0 ? 6 : dayOfWeek - 1 // Monday as start of week
      startDate = new Date(today)
      startDate.setDate(today.getDate() - diff)
      dateRangeText = `${startDate.toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' })} to ${today.toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' })}`
    } else if (dateRange === 'month') {
      startDate = new Date(today.getFullYear(), today.getMonth(), 1)
      dateRangeText = `${startDate.toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' })} to ${today.toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' })}`
    } else if (dateRange === 'year') {
      startDate = new Date(today.getFullYear(), 0, 1)
      dateRangeText = `${startDate.toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' })} to ${today.toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' })}`
    }

    // Create HTML content for the PDF
    let htmlContent = `
      <div style="padding: 20px; font-family: Arial, sans-serif;">
        <h1 style="text-align: center; color: #333;">${hotelName}</h1>
        ${gstNumber ? `<p style="text-align: center; color: #999; font-size: 12px; margin-top: -10px;">GST No: ${gstNumber}</p>` : ''}
        <h2 style="text-align: center; color: #666;">${reportTitles[reportType]}</h2>
        <p style="text-align: center; color: #999;">Date Range: ${dateRangeText}</p>
        <p style="text-align: center; color: #999; margin-bottom: 30px;">Generated: ${new Date().toLocaleString()}</p>
    `

    // Add content based on report type
    if (reportType === 'overview') {
      htmlContent += `
        <h3>Key Metrics</h3>
        <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">
          <thead>
            <tr style="background-color: #0088fe; color: white;">
              <th style="border: 1px solid #ddd; padding: 8px;">Metric</th>
              <th style="border: 1px solid #ddd; padding: 8px;">Value</th>
            </tr>
          </thead>
          <tbody>
            <tr><td style="border: 1px solid #ddd; padding: 8px;">Total Rooms</td><td style="border: 1px solid #ddd; padding: 8px;">${reportData.stats.total_rooms}</td></tr>
            <tr><td style="border: 1px solid #ddd; padding: 8px;">Available Rooms</td><td style="border: 1px solid #ddd; padding: 8px;">${reportData.stats.available_rooms}</td></tr>
            <tr><td style="border: 1px solid #ddd; padding: 8px;">Occupancy Rate</td><td style="border: 1px solid #ddd; padding: 8px;">${reportData.stats.occupancy_rate}%</td></tr>
            <tr><td style="border: 1px solid #ddd; padding: 8px;">Total Bookings</td><td style="border: 1px solid #ddd; padding: 8px;">${reportData.stats.total_bookings}</td></tr>
            <tr><td style="border: 1px solid #ddd; padding: 8px;">Active Bookings</td><td style="border: 1px solid #ddd; padding: 8px;">${reportData.stats.active_bookings}</td></tr>
            <tr><td style="border: 1px solid #ddd; padding: 8px;">Total Revenue</td><td style="border: 1px solid #ddd; padding: 8px;">₹${reportData.stats.total_revenue.toLocaleString()}</td></tr>
            <tr><td style="border: 1px solid #ddd; padding: 8px;">Avg Booking Value</td><td style="border: 1px solid #ddd; padding: 8px;">₹${reportData.stats.avg_booking_value}</td></tr>
            <tr><td style="border: 1px solid #ddd; padding: 8px;">Total Customers</td><td style="border: 1px solid #ddd; padding: 8px;">${reportData.stats.total_customers}</td></tr>
          </tbody>
        </table>

        <h3>Room Type Distribution</h3>
        <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">
          <thead>
            <tr style="background-color: #0088fe; color: white;">
              <th style="border: 1px solid #ddd; padding: 8px;">Room Type</th>
              <th style="border: 1px solid #ddd; padding: 8px;">Count</th>
            </tr>
          </thead>
          <tbody>
            ${reportData.charts.room_types.map(rt => `
              <tr><td style="border: 1px solid #ddd; padding: 8px;">${rt.name}</td><td style="border: 1px solid #ddd; padding: 8px;">${rt.value}</td></tr>
            `).join('')}
          </tbody>
        </table>

        <h3>Booking Status Distribution</h3>
        <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">
          <thead>
            <tr style="background-color: #0088fe; color: white;">
              <th style="border: 1px solid #ddd; padding: 8px;">Status</th>
              <th style="border: 1px solid #ddd; padding: 8px;">Count</th>
            </tr>
          </thead>
          <tbody>
            ${reportData.charts.booking_status.map(bs => `
              <tr><td style="border: 1px solid #ddd; padding: 8px;">${bs.name}</td><td style="border: 1px solid #ddd; padding: 8px;">${bs.value}</td></tr>
            `).join('')}
          </tbody>
        </table>

        <h3>Revenue by Month</h3>
        <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">
          <thead>
            <tr style="background-color: #0088fe; color: white;">
              <th style="border: 1px solid #ddd; padding: 8px;">Month</th>
              <th style="border: 1px solid #ddd; padding: 8px;">Revenue (₹)</th>
            </tr>
          </thead>
          <tbody>
            ${reportData.charts.revenue_by_month.map(rm => `
              <tr><td style="border: 1px solid #ddd; padding: 8px;">${rm.month}</td><td style="border: 1px solid #ddd; padding: 8px;">${rm.revenue.toLocaleString()}</td></tr>
            `).join('')}
          </tbody>
        </table>
      `
    } else if (reportType === 'rooms') {
      htmlContent += `
        <h3>Room Statistics</h3>
        <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">
          <thead>
            <tr style="background-color: #0088fe; color: white;">
              <th style="border: 1px solid #ddd; padding: 8px;">Metric</th>
              <th style="border: 1px solid #ddd; padding: 8px;">Value</th>
            </tr>
          </thead>
          <tbody>
            <tr><td style="border: 1px solid #ddd; padding: 8px;">Total Rooms</td><td style="border: 1px solid #ddd; padding: 8px;">${reportData.total_rooms}</td></tr>
            <tr><td style="border: 1px solid #ddd; padding: 8px;">Active Rooms</td><td style="border: 1px solid #ddd; padding: 8px;">${reportData.active_rooms}</td></tr>
            <tr><td style="border: 1px solid #ddd; padding: 8px;">Overall Occupancy Rate</td><td style="border: 1px solid #ddd; padding: 8px;">${reportData.overall_occupancy_rate}%</td></tr>
          </tbody>
        </table>

        <h3>Room Status Distribution</h3>
        <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">
          <thead>
            <tr style="background-color: #0088fe; color: white;">
              <th style="border: 1px solid #ddd; padding: 8px;">Status</th>
              <th style="border: 1px solid #ddd; padding: 8px;">Count</th>
            </tr>
          </thead>
          <tbody>
            ${reportData.by_status.map(s => `
              <tr><td style="border: 1px solid #ddd; padding: 8px;">${s.status.replace('_', ' ').toUpperCase()}</td><td style="border: 1px solid #ddd; padding: 8px;">${s.count}</td></tr>
            `).join('')}
          </tbody>
        </table>

        <h3>Room Type Analysis</h3>
        <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px; font-size: 10px;">
          <thead>
            <tr style="background-color: #0088fe; color: white;">
              <th style="border: 1px solid #ddd; padding: 6px;">Room Type</th>
              <th style="border: 1px solid #ddd; padding: 6px;">Total</th>
              <th style="border: 1px solid #ddd; padding: 6px;">Available</th>
              <th style="border: 1px solid #ddd; padding: 6px;">Occupied</th>
              <th style="border: 1px solid #ddd; padding: 6px;">Reserved</th>
              <th style="border: 1px solid #ddd; padding: 6px;">Maintenance</th>
              <th style="border: 1px solid #ddd; padding: 6px;">Occupancy %</th>
            </tr>
          </thead>
          <tbody>
            ${reportData.by_type.map(t => `
              <tr>
                <td style="border: 1px solid #ddd; padding: 6px;">${t.room_type.toUpperCase()}</td>
                <td style="border: 1px solid #ddd; padding: 6px;">${t.total_rooms}</td>
                <td style="border: 1px solid #ddd; padding: 6px;">${t.available}</td>
                <td style="border: 1px solid #ddd; padding: 6px;">${t.occupied}</td>
                <td style="border: 1px solid #ddd; padding: 6px;">${t.reserved}</td>
                <td style="border: 1px solid #ddd; padding: 6px;">${t.maintenance}</td>
                <td style="border: 1px solid #ddd; padding: 6px;">${t.occupancy_rate}%</td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      `
    } else if (reportType === 'bookings') {
      htmlContent += `
        <h3>Booking Statistics</h3>
        <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">
          <thead>
            <tr style="background-color: #0088fe; color: white;">
              <th style="border: 1px solid #ddd; padding: 8px;">Metric</th>
              <th style="border: 1px solid #ddd; padding: 8px;">Value</th>
            </tr>
          </thead>
          <tbody>
            <tr><td style="border: 1px solid #ddd; padding: 8px;">Total Bookings</td><td style="border: 1px solid #ddd; padding: 8px;">${reportData.total_bookings}</td></tr>
            <tr><td style="border: 1px solid #ddd; padding: 8px;">Average Nights per Booking</td><td style="border: 1px solid #ddd; padding: 8px;">${reportData.avg_nights}</td></tr>
            <tr><td style="border: 1px solid #ddd; padding: 8px;">Average Guests per Booking</td><td style="border: 1px solid #ddd; padding: 8px;">${reportData.avg_guests}</td></tr>
          </tbody>
        </table>

        <h3>Booking Status Breakdown</h3>
        <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">
          <thead>
            <tr style="background-color: #0088fe; color: white;">
              <th style="border: 1px solid #ddd; padding: 8px;">Status</th>
              <th style="border: 1px solid #ddd; padding: 8px;">Count</th>
            </tr>
          </thead>
          <tbody>
            ${reportData.status_breakdown.map(s => `
              <tr><td style="border: 1px solid #ddd; padding: 8px;">${s.status.replace('_', ' ').toUpperCase()}</td><td style="border: 1px solid #ddd; padding: 8px;">${s.count}</td></tr>
            `).join('')}
          </tbody>
        </table>

        <h3>Room Type Preferences</h3>
        <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">
          <thead>
            <tr style="background-color: #0088fe; color: white;">
              <th style="border: 1px solid #ddd; padding: 8px;">Room Type</th>
              <th style="border: 1px solid #ddd; padding: 8px;">Bookings</th>
            </tr>
          </thead>
          <tbody>
            ${reportData.room_preferences.map(r => `
              <tr><td style="border: 1px solid #ddd; padding: 8px;">${r.room_type.toUpperCase()}</td><td style="border: 1px solid #ddd; padding: 8px;">${r.count}</td></tr>
            `).join('')}
          </tbody>
        </table>
      `
    } else if (reportType === 'revenue') {
      htmlContent += `
        <h3>Revenue Statistics</h3>
        <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">
          <thead>
            <tr style="background-color: #0088fe; color: white;">
              <th style="border: 1px solid #ddd; padding: 8px;">Metric</th>
              <th style="border: 1px solid #ddd; padding: 8px;">Value</th>
            </tr>
          </thead>
          <tbody>
            <tr><td style="border: 1px solid #ddd; padding: 8px;">Total Revenue</td><td style="border: 1px solid #ddd; padding: 8px;">₹${reportData.total_revenue.toLocaleString()}</td></tr>
            <tr><td style="border: 1px solid #ddd; padding: 8px;">Total Transactions</td><td style="border: 1px solid #ddd; padding: 8px;">${reportData.payment_count}</td></tr>
            <tr><td style="border: 1px solid #ddd; padding: 8px;">Average Transaction Value</td><td style="border: 1px solid #ddd; padding: 8px;">₹${reportData.avg_transaction_value.toLocaleString()}</td></tr>
          </tbody>
        </table>

        <h3>Revenue by Payment Method</h3>
        <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">
          <thead>
            <tr style="background-color: #0088fe; color: white;">
              <th style="border: 1px solid #ddd; padding: 8px;">Payment Method</th>
              <th style="border: 1px solid #ddd; padding: 8px;">Total Amount (₹)</th>
              <th style="border: 1px solid #ddd; padding: 8px;">Transactions</th>
            </tr>
          </thead>
          <tbody>
            ${reportData.by_payment_method.map(pm => `
              <tr>
                <td style="border: 1px solid #ddd; padding: 8px;">${pm.payment_method.toUpperCase()}</td>
                <td style="border: 1px solid #ddd; padding: 8px;">${pm.total_amount.toLocaleString()}</td>
                <td style="border: 1px solid #ddd; padding: 8px;">${pm.transaction_count}</td>
              </tr>
            `).join('')}
          </tbody>
        </table>

        <h3>Revenue Breakdown</h3>
        <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px; font-size: 10px;">
          <thead>
            <tr style="background-color: #0088fe; color: white;">
              <th style="border: 1px solid #ddd; padding: 6px;">Period</th>
              <th style="border: 1px solid #ddd; padding: 6px;">Revenue (₹)</th>
            </tr>
          </thead>
          <tbody>
            ${reportData.revenue_breakdown.slice(0, 20).map(rb => `
              <tr>
                <td style="border: 1px solid #ddd; padding: 6px;">${rb.period}</td>
                <td style="border: 1px solid #ddd; padding: 6px;">${rb.revenue.toLocaleString()}</td>
              </tr>
            `).join('')}
          </tbody>
        </table>
        ${reportData.revenue_breakdown.length > 20 ? '<p style="font-style: italic; font-size: 10px;">(Showing first 20 entries)</p>' : ''}
      `
    }

    htmlContent += '</div>'

    // Generate PDF using html2pdf
    const dateStr = new Date().toISOString().split('T')[0]
    const filename = `${reportTitles[reportType].replace(/\s+/g, '_')}_${dateRange}_${dateStr}.pdf`

    const opt = {
      margin: 10,
      filename: filename,
      image: { type: 'jpeg', quality: 0.98 },
      html2canvas: { scale: 2 },
      jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' }
    }

    // Create temporary element
    const element = document.createElement('div')
    element.innerHTML = htmlContent
    document.body.appendChild(element)

    // Generate PDF
    html2pdf().set(opt).from(element).save().then(() => {
      document.body.removeChild(element)
    })
  }

  if (loading) {
    return <LoadingSpinner />
  }

  if (error) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="error" onClose={() => setError('')}>
          {error}
        </Alert>
      </Box>
    )
  }

  // Render different report views based on report type
  const renderReportContent = () => {
    if (!reportData) return null

    switch (reportType) {
      case 'overview':
        return renderOverviewReport()
      case 'rooms':
        return renderRoomsReport()
      case 'bookings':
        return renderBookingsReport()
      case 'revenue':
        return renderRevenueReport()
      default:
        return null
    }
  }

  // ============================================
  // OVERVIEW REPORT RENDERER
  // ============================================
  const renderOverviewReport = () => {
    // Safety check: ensure reportData has the correct structure
    if (!reportData || !reportData.stats || !reportData.charts) {
      return <LoadingSpinner />
    }

    const { stats, charts } = reportData

    return (
      <>
        {/* Key Metrics */}
        <Grid container spacing={3} sx={{ mb: 3 }}>
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Typography variant="body2" color="text.secondary">
                  Total Rooms
                </Typography>
                <Typography variant="h4" sx={{ fontWeight: 700 }}>
                  {stats.total_rooms}
                </Typography>
                <Typography variant="caption" color="success.main">
                  {stats.available_rooms} Available
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
                  {stats.occupancy_rate}%
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
                  {stats.total_bookings}
                </Typography>
                <Typography variant="caption" color="info.main">
                  {stats.active_bookings} Active
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
                  ₹{stats.total_revenue.toLocaleString()}
                </Typography>
                <Typography variant="caption">
                  Avg: ₹{stats.avg_booking_value}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Charts */}
        <Grid container spacing={3}>
          <Grid item xs={12} md={4}>
            <Paper sx={{ p: 3, height: '450px', display: 'flex', flexDirection: 'column' }}>
              <Typography variant="h6" gutterBottom>
                Room Type Distribution
              </Typography>
              {charts.room_types.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={charts.room_types}
                      cx="50%"
                      cy="50%"
                      labelLine={true}
                      label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                      outerRadius={100}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {charts.room_types.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              ) : (
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%' }}>
                  <Typography color="text.secondary">No data available</Typography>
                </Box>
              )}
            </Paper>
          </Grid>

          <Grid item xs={12} md={4}>
            <Paper sx={{ p: 3, height: '450px', display: 'flex', flexDirection: 'column' }}>
              <Typography variant="h6" gutterBottom>
                Booking Status Distribution
              </Typography>
              {charts.booking_status.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={charts.booking_status}
                      cx="50%"
                      cy="50%"
                      labelLine={true}
                      label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                      outerRadius={100}
                      fill="#82ca9d"
                      dataKey="value"
                    >
                      {charts.booking_status.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              ) : (
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%' }}>
                  <Typography color="text.secondary">No data available</Typography>
                </Box>
              )}
            </Paper>
          </Grid>

          <Grid item xs={12} md={4}>
            <Paper sx={{ p: 3, height: '450px', display: 'flex', flexDirection: 'column' }}>
              <Typography variant="h6" gutterBottom>
                Revenue Trend
              </Typography>
              {charts.revenue_by_month.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={charts.revenue_by_month}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis
                      dataKey="month"
                      tick={{ fontSize: 12 }}
                      interval={0}
                    />
                    <YAxis
                      tick={{ fontSize: 12 }}
                      label={{ value: 'Revenue (₹)', angle: -90, position: 'insideLeft' }}
                    />
                    <Tooltip />
                    <Legend wrapperStyle={{ fontSize: '14px' }} />
                    <Bar dataKey="revenue" fill="#8884d8" name="Revenue (₹)" />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%' }}>
                  <Typography color="text.secondary">No data available</Typography>
                </Box>
              )}
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
                  <Typography fontWeight="bold">{stats.total_customers}</Typography>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                  <Typography>Average Booking Value</Typography>
                  <Typography fontWeight="bold">₹{stats.avg_booking_value}</Typography>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                  <Typography>Revenue per Room</Typography>
                  <Typography fontWeight="bold">
                    ₹{stats.total_rooms > 0 ? Math.round(stats.total_revenue / stats.total_rooms) : 0}
                  </Typography>
                </Box>
              </Box>
            </Paper>
          </Grid>

          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Report Information
              </Typography>
              <Alert severity="info" sx={{ mt: 2 }}>
                Showing {dateRange === 'all' ? 'all time' : dateRange} data
              </Alert>
              <Typography variant="body2" sx={{ mt: 2 }}>
                Last updated: {new Date().toLocaleString()}
              </Typography>
            </Paper>
          </Grid>
        </Grid>
      </>
    )
  }

  // ============================================
  // ROOMS REPORT RENDERER
  // ============================================
  const renderRoomsReport = () => {
    // Safety check: ensure reportData has the correct structure
    if (!reportData || !reportData.by_type || !reportData.by_status) {
      return <LoadingSpinner />
    }

    const { total_rooms, active_rooms, by_status, by_type, overall_occupancy_rate } = reportData

    return (
      <>
        {/* Room Statistics */}
        <Grid container spacing={3} sx={{ mb: 3 }}>
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="body2" color="text.secondary">
                  Total Rooms
                </Typography>
                <Typography variant="h4" sx={{ fontWeight: 700 }}>
                  {total_rooms}
                </Typography>
                <Typography variant="caption">
                  {active_rooms} Active
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="body2" color="text.secondary">
                  Overall Occupancy Rate
                </Typography>
                <Typography variant="h4" sx={{ fontWeight: 700 }}>
                  {overall_occupancy_rate}%
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="body2" color="text.secondary">
                  Room Types
                </Typography>
                <Typography variant="h4" sx={{ fontWeight: 700 }}>
                  {by_type.length}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Room Status Distribution */}
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 3, height: '400px' }}>
              <Typography variant="h6" gutterBottom>
                Room Status Distribution
              </Typography>
              {by_status.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={by_status.map(s => ({ name: s.status.replace('_', ' ').toUpperCase(), value: s.count }))}
                      cx="50%"
                      cy="50%"
                      labelLine={true}
                      label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                      outerRadius={100}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {by_status.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              ) : (
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%' }}>
                  <Typography color="text.secondary">No data available</Typography>
                </Box>
              )}
            </Paper>
          </Grid>

          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Room Type Analysis
              </Typography>
              <Box sx={{ mt: 2 }}>
                {by_type.map((type, index) => (
                  <Box key={index} sx={{ mb: 3 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                      <Typography variant="subtitle1" fontWeight="bold">
                        {type.room_type.toUpperCase()}
                      </Typography>
                      <Typography variant="subtitle1" color="primary">
                        {type.occupancy_rate}% Occupied
                      </Typography>
                    </Box>
                    <Grid container spacing={2}>
                      <Grid item xs={6}>
                        <Typography variant="body2" color="text.secondary">
                          Total: {type.total_rooms}
                        </Typography>
                      </Grid>
                      <Grid item xs={6}>
                        <Typography variant="body2" color="success.main">
                          Available: {type.available}
                        </Typography>
                      </Grid>
                      <Grid item xs={6}>
                        <Typography variant="body2" color="error.main">
                          Occupied: {type.occupied}
                        </Typography>
                      </Grid>
                      <Grid item xs={6}>
                        <Typography variant="body2" color="warning.main">
                          Reserved: {type.reserved}
                        </Typography>
                      </Grid>
                    </Grid>
                  </Box>
                ))}
              </Box>
            </Paper>
          </Grid>
        </Grid>
      </>
    )
  }

  // ============================================
  // BOOKINGS REPORT RENDERER
  // ============================================
  const renderBookingsReport = () => {
    // Safety check: ensure reportData has the correct structure
    if (!reportData || !reportData.status_breakdown || !reportData.room_preferences) {
      return <LoadingSpinner />
    }

    const { total_bookings, status_breakdown, avg_nights, avg_guests, room_preferences } = reportData

    return (
      <>
        {/* Booking Statistics */}
        <Grid container spacing={3} sx={{ mb: 3 }}>
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Typography variant="body2" color="text.secondary">
                  Total Bookings
                </Typography>
                <Typography variant="h4" sx={{ fontWeight: 700 }}>
                  {total_bookings}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Typography variant="body2" color="text.secondary">
                  Avg Nights per Booking
                </Typography>
                <Typography variant="h4" sx={{ fontWeight: 700 }}>
                  {avg_nights}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Typography variant="body2" color="text.secondary">
                  Avg Guests per Booking
                </Typography>
                <Typography variant="h4" sx={{ fontWeight: 700 }}>
                  {avg_guests}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Typography variant="body2" color="text.secondary">
                  Booking Statuses
                </Typography>
                <Typography variant="h4" sx={{ fontWeight: 700 }}>
                  {status_breakdown.length}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Charts */}
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 3, height: '400px' }}>
              <Typography variant="h6" gutterBottom>
                Booking Status Breakdown
              </Typography>
              {status_breakdown.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={status_breakdown.map(s => ({ name: s.status.replace('_', ' ').toUpperCase(), value: s.count }))}
                      cx="50%"
                      cy="50%"
                      labelLine={true}
                      label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                      outerRadius={100}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {status_breakdown.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              ) : (
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%' }}>
                  <Typography color="text.secondary">No data available</Typography>
                </Box>
              )}
            </Paper>
          </Grid>

          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 3, height: '450px' }}>
              <Typography variant="h6" gutterBottom>
                Room Type Preferences
              </Typography>
              {room_preferences.length > 0 ? (
                <ResponsiveContainer width="100%" height="90%">
                  <BarChart data={room_preferences.map(r => ({ name: r.room_type.toUpperCase(), bookings: r.count }))} margin={{ bottom: 20 }}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Legend wrapperStyle={{ paddingTop: '10px' }} />
                    <Bar dataKey="bookings" fill="#8884d8" name="Bookings" />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%' }}>
                  <Typography color="text.secondary">No data available</Typography>
                </Box>
              )}
            </Paper>
          </Grid>
        </Grid>
      </>
    )
  }

  // ============================================
  // REVENUE REPORT RENDERER
  // ============================================
  const renderRevenueReport = () => {
    // Safety check: ensure reportData has the correct structure
    if (!reportData || !reportData.by_payment_method || !reportData.revenue_breakdown) {
      return <LoadingSpinner />
    }

    const { total_revenue, payment_count, avg_transaction_value, by_payment_method, revenue_breakdown } = reportData

    return (
      <>
        {/* Revenue Statistics */}
        <Grid container spacing={3} sx={{ mb: 3 }}>
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="body2" color="text.secondary">
                  Total Revenue
                </Typography>
                <Typography variant="h4" sx={{ fontWeight: 700 }}>
                  ₹{total_revenue.toLocaleString()}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="body2" color="text.secondary">
                  Total Transactions
                </Typography>
                <Typography variant="h4" sx={{ fontWeight: 700 }}>
                  {payment_count}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="body2" color="text.secondary">
                  Avg Transaction Value
                </Typography>
                <Typography variant="h4" sx={{ fontWeight: 700 }}>
                  ₹{avg_transaction_value.toLocaleString()}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Charts */}
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 3, height: '400px' }}>
              <Typography variant="h6" gutterBottom>
                Revenue by Payment Method
              </Typography>
              {by_payment_method.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={by_payment_method.map(p => ({ name: p.payment_method.toUpperCase(), value: p.total_amount }))}
                      cx="50%"
                      cy="50%"
                      labelLine={true}
                      label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                      outerRadius={100}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {by_payment_method.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value) => `₹${value.toLocaleString()}`} />
                  </PieChart>
                </ResponsiveContainer>
              ) : (
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%' }}>
                  <Typography color="text.secondary">No data available</Typography>
                </Box>
              )}
            </Paper>
          </Grid>

          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 3, height: '450px' }}>
              <Typography variant="h6" gutterBottom>
                Revenue Breakdown
              </Typography>
              {revenue_breakdown.length > 0 ? (
                <ResponsiveContainer width="100%" height="90%">
                  <BarChart data={revenue_breakdown.map(r => ({ period: r.period, revenue: r.revenue }))} margin={{ bottom: 20 }}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis
                      dataKey="period"
                      tick={{ fontSize: 10 }}
                      angle={-45}
                      textAnchor="end"
                      height={80}
                    />
                    <YAxis />
                    <Tooltip formatter={(value) => `₹${value.toLocaleString()}`} />
                    <Legend wrapperStyle={{ paddingTop: '10px' }} />
                    <Bar dataKey="revenue" fill="#82ca9d" name="Revenue (₹)" />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%' }}>
                  <Typography color="text.secondary">No data available</Typography>
                </Box>
              )}
            </Paper>
          </Grid>
        </Grid>

        {/* Payment Method Details */}
        <Grid container spacing={3} sx={{ mt: 2 }}>
          <Grid item xs={12}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Payment Method Details
              </Typography>
              <Grid container spacing={2} sx={{ mt: 1 }}>
                {by_payment_method.map((method, index) => (
                  <Grid item xs={12} md={3} key={index}>
                    <Box sx={{ textAlign: 'center' }}>
                      <Typography variant="subtitle2" color="text.secondary">
                        {method.payment_method.toUpperCase()}
                      </Typography>
                      <Typography variant="h6" color="primary">
                        ₹{method.total_amount.toLocaleString()}
                      </Typography>
                      <Typography variant="caption">
                        {method.transaction_count} transactions
                      </Typography>
                    </Box>
                  </Grid>
                ))}
              </Grid>
            </Paper>
          </Grid>
        </Grid>
      </>
    )
  }

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
            onClick={handleExportPDF}
            disabled={!reportData}
          >
            Export PDF
          </Button>
        </Box>
      </Box>

      {error && <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>{error}</Alert>}

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

      {renderReportContent()}
    </Box>
  )
}

export default Reports
