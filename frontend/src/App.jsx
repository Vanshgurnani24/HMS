import { Routes, Route, Navigate } from 'react-router-dom'
import { Box } from '@mui/material'
import { useAuth } from './context/AuthContext'
import PrivateRoute from './components/common/PrivateRoute'
import Navbar from './components/layout/Navbar'
import Sidebar from './components/layout/Sidebar'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Rooms from './pages/Rooms'
import Customers from './pages/Customers'
import Bookings from './pages/Bookings'
import Billing from './pages/Billing'
import Reports from './pages/Reports'
import './App.css'

function App() {
  const { isAuthenticated } = useAuth()

  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      
      <Route
        path="/*"
        element={
          <PrivateRoute>
            <Box sx={{ display: 'flex' }}>
              <Sidebar />
              <Box
                component="main"
                sx={{
                  flexGrow: 1,
                  minHeight: '100vh',
                  backgroundColor: '#f5f5f5',
                }}
              >
                <Navbar />
                <Routes>
                  <Route path="/" element={<Navigate to="/dashboard" />} />
                  <Route path="/dashboard" element={<Dashboard />} />
                  <Route path="/rooms" element={<Rooms />} />
                  <Route path="/customers" element={<Customers />} />
                  <Route path="/bookings" element={<Bookings />} />
                  <Route path="/billing" element={<Billing />} />
                  <Route path="/reports" element={<Reports />} />
                </Routes>
              </Box>
            </Box>
          </PrivateRoute>
        }
      />
    </Routes>
  )
}

export default App