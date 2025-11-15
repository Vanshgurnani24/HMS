import { useState, useEffect } from 'react'
import {
  Box,
  Button,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  IconButton,
  Alert,
} from '@mui/material'
import { Add, Refresh, Edit, Delete, Upload, AttachFile } from '@mui/icons-material'
import { customersAPI } from '../api/axios'
import LoadingSpinner from '../components/common/LoadingSpinner'

const Customers = () => {
  const [customers, setCustomers] = useState([])
  const [loading, setLoading] = useState(true)
  const [openDialog, setOpenDialog] = useState(false)
  const [selectedCustomer, setSelectedCustomer] = useState(null)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [selectedFile, setSelectedFile] = useState(null)
  const [fileName, setFileName] = useState('')
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
    address: '',
    city: '',
    state: '',
    country: '',
    zip_code: '',
    id_type: '',
    id_number: '',
    date_of_birth: '',
  })

  useEffect(() => {
    fetchCustomers()
  }, [])

  const fetchCustomers = async () => {
    try {
      setLoading(true)
      const response = await customersAPI.getCustomers()
      setCustomers(response.data.customers || [])
    } catch (error) {
      console.error('Error fetching customers:', error)
      setError('Failed to load customers')
    } finally {
      setLoading(false)
    }
  }

  const handleOpenDialog = (customer = null) => {
    if (customer) {
      setSelectedCustomer(customer)
      setFormData({
        first_name: customer.first_name || '',
        last_name: customer.last_name || '',
        email: customer.email || '',
        phone: customer.phone || '',
        address: customer.address || '',
        city: customer.city || '',
        state: customer.state || '',
        country: customer.country || '',
        zip_code: customer.zip_code || '',
        id_type: customer.id_type || '',
        id_number: customer.id_number || '',
        date_of_birth: customer.date_of_birth || '',
      })
    } else {
      setSelectedCustomer(null)
      setFormData({
        first_name: '',
        last_name: '',
        email: '',
        phone: '',
        address: '',
        city: '',
        state: '',
        country: '',
        zip_code: '',
        id_type: '',
        id_number: '',
        date_of_birth: '',
      })
    }
    setSelectedFile(null)
    setFileName('')
    setOpenDialog(true)
    setError('')
    setSuccess('')
  }

  const handleCloseDialog = () => {
    setOpenDialog(false)
    setSelectedCustomer(null)
    setSelectedFile(null)
    setFileName('')
  }

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    })
  }

  const handleFileChange = (e) => {
    const file = e.target.files[0]
    if (file) {
      // Validate file type
      const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'application/pdf']
      if (!allowedTypes.includes(file.type)) {
        setError('Invalid file type. Please upload JPG, PNG, or PDF only.')
        return
      }
      
      // Validate file size (5MB max)
      const maxSize = 5 * 1024 * 1024 // 5MB in bytes
      if (file.size > maxSize) {
        setError('File size must be less than 5MB')
        return
      }
      
      setSelectedFile(file)
      setFileName(file.name)
      setError('')
    }
  }

  const handleSubmit = async () => {
    try {
      // Prepare form data with file upload
      const submitData = {
        ...formData,
      }

      // Add file if selected
      if (selectedFile) {
        submitData.id_proof = selectedFile
      }

      if (selectedCustomer) {
        await customersAPI.updateCustomer(selectedCustomer.id, submitData)
        setSuccess('Customer updated successfully!')
      } else {
        await customersAPI.createCustomer(submitData)
        setSuccess('Customer created successfully!')
      }

      handleCloseDialog()
      fetchCustomers()
    } catch (error) {
      console.error('Error saving customer:', error)
      setError(error.response?.data?.detail || 'Failed to save customer')
    }
  }

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this customer?')) {
      try {
        await customersAPI.deleteCustomer(id)
        setSuccess('Customer deleted successfully!')
        fetchCustomers()
      } catch (error) {
        console.error('Error deleting customer:', error)
        setError(error.response?.data?.detail || 'Failed to delete customer')
      }
    }
  }

  if (loading) {
    return <LoadingSpinner />
  }

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" sx={{ fontWeight: 600 }}>
          Customer Management
        </Typography>
        <Box>
          <Button
            variant="outlined"
            startIcon={<Refresh />}
            onClick={fetchCustomers}
            sx={{ mr: 2 }}
          >
            Refresh
          </Button>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={() => handleOpenDialog()}
          >
            Add Customer
          </Button>
        </Box>
      </Box>

      {error && <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>{error}</Alert>}
      {success && <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess('')}>{success}</Alert>}

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell><strong>Name</strong></TableCell>
              <TableCell><strong>Email</strong></TableCell>
              <TableCell><strong>Phone</strong></TableCell>
              <TableCell><strong>City</strong></TableCell>
              <TableCell><strong>Country</strong></TableCell>
              <TableCell><strong>Actions</strong></TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {customers.length === 0 ? (
              <TableRow>
                <TableCell colSpan={6} align="center">
                  <Typography variant="body2" color="text.secondary">
                    No customers found. Add your first customer!
                  </Typography>
                </TableCell>
              </TableRow>
            ) : (
              customers.map((customer) => (
                <TableRow key={customer.id}>
                  <TableCell>{`${customer.first_name} ${customer.last_name}`}</TableCell>
                  <TableCell>{customer.email}</TableCell>
                  <TableCell>{customer.phone}</TableCell>
                  <TableCell>{customer.city || '-'}</TableCell>
                  <TableCell>{customer.country || '-'}</TableCell>
                  <TableCell>
                    <IconButton
                      size="small"
                      color="primary"
                      onClick={() => handleOpenDialog(customer)}
                    >
                      <Edit />
                    </IconButton>
                    <IconButton
                      size="small"
                      color="error"
                      onClick={() => handleDelete(customer.id)}
                    >
                      <Delete />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Add/Edit Customer Dialog */}
      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="md" fullWidth>
        <DialogTitle>
          {selectedCustomer ? 'Edit Customer' : 'Add New Customer'}
        </DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2, display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 2 }}>
            <TextField
              label="First Name"
              name="first_name"
              value={formData.first_name}
              onChange={handleChange}
              required
              fullWidth
            />
            <TextField
              label="Last Name"
              name="last_name"
              value={formData.last_name}
              onChange={handleChange}
              required
              fullWidth
            />
            <TextField
              label="Email"
              name="email"
              type="email"
              value={formData.email}
              onChange={handleChange}
              required
              fullWidth
            />
            <TextField
              label="Phone"
              name="phone"
              value={formData.phone}
              onChange={handleChange}
              required
              fullWidth
            />
            <TextField
              label="Address"
              name="address"
              value={formData.address}
              onChange={handleChange}
              fullWidth
              sx={{ gridColumn: '1 / -1' }}
            />
            <TextField
              label="City"
              name="city"
              value={formData.city}
              onChange={handleChange}
              fullWidth
            />
            <TextField
              label="State"
              name="state"
              value={formData.state}
              onChange={handleChange}
              fullWidth
            />
            <TextField
              label="Country"
              name="country"
              value={formData.country}
              onChange={handleChange}
              fullWidth
            />
            <TextField
              label="Zip Code"
              name="zip_code"
              value={formData.zip_code}
              onChange={handleChange}
              fullWidth
            />
            <TextField
              label="ID Type"
              name="id_type"
              value={formData.id_type}
              onChange={handleChange}
              fullWidth
              placeholder="e.g., Passport, Aadhaar, Driver's License"
            />
            <TextField
              label="ID Number"
              name="id_number"
              value={formData.id_number}
              onChange={handleChange}
              fullWidth
            />
            <TextField
              label="Date of Birth"
              name="date_of_birth"
              type="date"
              value={formData.date_of_birth}
              onChange={handleChange}
              fullWidth
              InputLabelProps={{ shrink: true }}
            />
            
            {/* NEW: ID Proof File Upload */}
            <Box sx={{ gridColumn: '1 / -1', mt: 1 }}>
              <Typography variant="subtitle2" gutterBottom>
                ID Proof Document (Optional)
              </Typography>
              <Typography variant="caption" color="text.secondary" display="block" gutterBottom>
                Upload JPG, PNG, or PDF (Max 5MB)
              </Typography>
              <Button
                variant="outlined"
                component="label"
                startIcon={<Upload />}
                sx={{ mt: 1 }}
              >
                Upload ID Proof
                <input
                  type="file"
                  hidden
                  accept=".jpg,.jpeg,.png,.pdf"
                  onChange={handleFileChange}
                />
              </Button>
              {fileName && (
                <Box sx={{ display: 'flex', alignItems: 'center', mt: 1, gap: 1 }}>
                  <AttachFile fontSize="small" color="primary" />
                  <Typography variant="body2" color="primary">
                    {fileName}
                  </Typography>
                </Box>
              )}
            </Box>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button onClick={handleSubmit} variant="contained">
            {selectedCustomer ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}

export default Customers