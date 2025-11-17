import React from 'react'
import { IconButton, Badge } from '@mui/material'
import { Notifications } from '@mui/icons-material'

const TestBell = () => {
  console.log('🧪 TestBell: Component is rendering!')
  console.log('🧪 TestBell: This proves Header can render child components')
  
  return (
    <IconButton 
      color="inherit" 
      sx={{ mr: 2 }}
      onClick={() => {
        console.log('🧪 TestBell: Bell icon clicked!')
        alert('Test Bell Clicked! This means the component is working.')
      }}
    >
      <Badge badgeContent={99} color="error">
        <Notifications />
      </Badge>
    </IconButton>
  )
}

console.log('🧪 TestBell: Component definition loaded')

export default TestBell