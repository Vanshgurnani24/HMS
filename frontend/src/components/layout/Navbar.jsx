import { AppBar, Toolbar, Typography, IconButton, Menu, MenuItem, Avatar, Box } from '@mui/material'
import { AccountCircle, Logout, Person } from '@mui/icons-material'
import { useState } from 'react'
import { useAuth } from '../../context/AuthContext'
import { useNavigate } from 'react-router-dom'
import UpcomingCheckinNotifications from './UpcomingCheckinNotifications'

const Navbar = () => {
  console.log('🔵 Navbar: Component rendering...')
  
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [anchorEl, setAnchorEl] = useState(null)

  console.log('🔵 Navbar: User data:', user)

  const handleMenu = (event) => {
    setAnchorEl(event.currentTarget)
  }

  const handleClose = () => {
    setAnchorEl(null)
  }

  const handleLogout = () => {
    logout()
    navigate('/login')
    handleClose()
  }

  console.log('🔵 Navbar: About to render...')

  return (
    <AppBar
      position="sticky"
      sx={{
        backgroundColor: 'white',
        color: 'text.primary',
        boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
      }}
    >
      <Toolbar>
        {console.log('🔵 Navbar: Inside Toolbar')}
        
        <Typography variant="h6" component="div" sx={{ flexGrow: 1, color: '#1976d2' }}>
          Hotel Management System
        </Typography>
        {console.log('🔵 Navbar: Title rendered')}

        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          {console.log('🔵 Navbar: ⚡ About to render UpcomingCheckinNotifications...')}
          
          {/* ==================== NOTIFICATION BELL ==================== */}
          <UpcomingCheckinNotifications />
          {/* ========================================================== */}
          
          {console.log('🔵 Navbar: ✅ Notification component rendered')}

          <Typography variant="body2" sx={{ mr: 1 }}>
            {user?.full_name}
          </Typography>
          
          <IconButton
            size="large"
            aria-label="account of current user"
            aria-controls="menu-appbar"
            aria-haspopup="true"
            onClick={handleMenu}
            color="primary"
          >
            <AccountCircle />
          </IconButton>
          
          <Menu
            id="menu-appbar"
            anchorEl={anchorEl}
            anchorOrigin={{
              vertical: 'bottom',
              horizontal: 'right',
            }}
            keepMounted
            transformOrigin={{
              vertical: 'top',
              horizontal: 'right',
            }}
            open={Boolean(anchorEl)}
            onClose={handleClose}
          >
            <MenuItem disabled>
              <Person sx={{ mr: 1 }} />
              {user?.role?.toUpperCase()}
            </MenuItem>
            <MenuItem onClick={handleLogout}>
              <Logout sx={{ mr: 1 }} />
              Logout
            </MenuItem>
          </Menu>
        </Box>
      </Toolbar>
    </AppBar>
  )
}

console.log('🔵 Navbar: Component definition complete')

export default Navbar