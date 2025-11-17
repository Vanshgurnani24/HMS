import React from 'react'
import { AppBar, Toolbar, Typography, Button, Box } from '@mui/material'
import { useNavigate } from 'react-router-dom'
import { Hotel, ExitToApp } from '@mui/icons-material'
import UpcomingCheckinNotifications from './UpcomingCheckinNotifications'

const Header = () => {
  console.log('====================================')
  console.log('🏠 Header: Component START')
  console.log('====================================')
  
  const navigate = useNavigate()
  const user = JSON.parse(localStorage.getItem('user') || '{}')

  console.log('🏠 Header: User data loaded:', user)

  const handleLogout = () => {
    console.log('🏠 Header: Logout clicked')
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    navigate('/login')
  }

  console.log('🏠 Header: About to render JSX')

  return (
    <AppBar position="fixed" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}>
      <Toolbar>
        {console.log('🏠 Header: Inside Toolbar - rendering children...')}
        
        {/* Logo and Title */}
        <Hotel sx={{ mr: 2 }} />
        {console.log('🏠 Header: Hotel icon rendered')}
        
        <Typography variant="h6" component="div" sx={{ flexGrow: 0, mr: 4 }}>
          Hotel Management System
        </Typography>
        {console.log('🏠 Header: Title rendered')}

        {/* Spacer */}
        <Box sx={{ flexGrow: 1 }} />
        {console.log('🏠 Header: Spacer rendered')}

        {/* ==================== NOTIFICATION BELL ==================== */}
        {console.log('🏠 Header: ⚡ About to render UpcomingCheckinNotifications...')}
        <UpcomingCheckinNotifications />
        {console.log('🏠 Header: ✅ UpcomingCheckinNotifications rendered (or attempted)')}
        {/* ========================================================== */}

        {/* User Info */}
        {console.log('🏠 Header: Rendering user info...')}
        <Typography variant="body1" sx={{ mr: 2 }}>
          {user.username || 'User'}
        </Typography>
        {console.log('🏠 Header: User info rendered')}

        {/* Logout Button */}
        {console.log('🏠 Header: Rendering logout button...')}
        <Button
          color="inherit"
          startIcon={<ExitToApp />}
          onClick={handleLogout}
        >
          Logout
        </Button>
        {console.log('🏠 Header: Logout button rendered')}
      </Toolbar>
      {console.log('🏠 Header: Toolbar complete')}
    </AppBar>
  )
}

console.log('🏠 Header: Component definition complete, exporting...')

export default Header