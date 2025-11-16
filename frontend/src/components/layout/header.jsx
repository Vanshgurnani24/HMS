import React from 'react'
import { AppBar, Toolbar, Typography, Button, Box } from '@mui/material'
import { useNavigate } from 'react-router-dom'
import { Hotel, ExitToApp } from '@mui/icons-material'
import UpcomingCheckinNotifications from './UpcomingCheckinNotifications'

const Header = () => {
  const navigate = useNavigate()
  const user = JSON.parse(localStorage.getItem('user') || '{}')

  const handleLogout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    navigate('/login')
  }

  return (
    <AppBar position="fixed" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}>
      <Toolbar>
        {/* Logo and Title */}
        <Hotel sx={{ mr: 2 }} />
        <Typography variant="h6" component="div" sx={{ flexGrow: 0, mr: 4 }}>
          Hotel Management System
        </Typography>

        {/* Spacer */}
        <Box sx={{ flexGrow: 1 }} />

        {/* ✅ NEW: Notification Bell */}
        <UpcomingCheckinNotifications />

        {/* User Info */}
        <Typography variant="body1" sx={{ mr: 2 }}>
          {user.username || 'User'}
        </Typography>

        {/* Logout Button */}
        <Button
          color="inherit"
          startIcon={<ExitToApp />}
          onClick={handleLogout}
        >
          Logout
        </Button>
      </Toolbar>
    </AppBar>
  )
}

export default Header