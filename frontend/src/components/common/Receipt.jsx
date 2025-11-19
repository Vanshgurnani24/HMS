import { forwardRef } from 'react'
import {
  Box,
  Typography,
  Divider,
  Table,
  TableBody,
  TableCell,
  TableRow,
  Paper,
} from '@mui/material'
import { formatDate } from '../../utils/dateUtils'

const Receipt = forwardRef(({ invoiceData }, ref) => {
  if (!invoiceData) return null

  return (
    <Box
      ref={ref}
      sx={{
        p: 4,
        maxWidth: '800px',
        margin: '0 auto',
        backgroundColor: 'white',
        '@media print': {
          p: '20mm',
          margin: 0,
          maxWidth: '210mm',
          width: '210mm',
          minHeight: '297mm',
          boxShadow: 'none',
          '@page': {
            size: 'A4',
            margin: '0',
          },
        },
      }}
    >
      {/* Header */}
      <Box sx={{ textAlign: 'center', mb: 4 }}>
        <Typography variant="h3" sx={{ fontWeight: 700, color: '#1976d2', mb: 1 }}>
          Ajanta Rooms
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Thank you for choosing our services
        </Typography>
      </Box>

      <Divider sx={{ mb: 3 }} />

      {/* Invoice Info */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="h5" sx={{ fontWeight: 600, mb: 2 }}>
          Payment Receipt
        </Typography>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', flexWrap: 'wrap', gap: 2 }}>
          <Box>
            <Typography variant="body2" color="text.secondary">
              Invoice Number
            </Typography>
            <Typography variant="body1" sx={{ fontWeight: 600 }}>
              {invoiceData.invoice_no}
            </Typography>
          </Box>
          <Box>
            <Typography variant="body2" color="text.secondary">
              Booking Reference
            </Typography>
            <Typography variant="body1" sx={{ fontWeight: 600 }}>
              {invoiceData.booking_reference}
            </Typography>
          </Box>
          <Box>
            <Typography variant="body2" color="text.secondary">
              Date Issued
            </Typography>
            <Typography variant="body1" sx={{ fontWeight: 600 }}>
              {formatDate(invoiceData.created_at)}
            </Typography>
          </Box>
        </Box>
      </Box>

      <Divider sx={{ mb: 3 }} />

      {/* Customer Details */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>
          Customer Information
        </Typography>
        <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 2 }}>
          <Box>
            <Typography variant="body2" color="text.secondary">
              Name
            </Typography>
            <Typography variant="body1" sx={{ fontWeight: 500 }}>
              {invoiceData.customer_name}
            </Typography>
          </Box>
          <Box>
            <Typography variant="body2" color="text.secondary">
              Email
            </Typography>
            <Typography variant="body1" sx={{ fontWeight: 500 }}>
              {invoiceData.customer_email}
            </Typography>
          </Box>
          <Box>
            <Typography variant="body2" color="text.secondary">
              Phone
            </Typography>
            <Typography variant="body1" sx={{ fontWeight: 500 }}>
              {invoiceData.customer_phone}
            </Typography>
          </Box>
          <Box>
            <Typography variant="body2" color="text.secondary">
              Room Number
            </Typography>
            <Typography variant="body1" sx={{ fontWeight: 500 }}>
              {invoiceData.room_number}
            </Typography>
          </Box>
        </Box>
      </Box>

      <Divider sx={{ mb: 3 }} />

      {/* Booking Details */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>
          Booking Details
        </Typography>
        <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 2 }}>
          <Box>
            <Typography variant="body2" color="text.secondary">
              Check-In Date
            </Typography>
            <Typography variant="body1" sx={{ fontWeight: 500 }}>
              {formatDate(invoiceData.check_in_date)}
            </Typography>
          </Box>
          <Box>
            <Typography variant="body2" color="text.secondary">
              Check-Out Date
            </Typography>
            <Typography variant="body1" sx={{ fontWeight: 500 }}>
              {formatDate(invoiceData.check_out_date)}
            </Typography>
          </Box>
          <Box>
            <Typography variant="body2" color="text.secondary">
              Number of Nights
            </Typography>
            <Typography variant="body1" sx={{ fontWeight: 500 }}>
              {invoiceData.number_of_nights}
            </Typography>
          </Box>
        </Box>
      </Box>

      <Divider sx={{ mb: 3 }} />

      {/* Itemized Charges */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>
          Charges
        </Typography>
        <Paper variant="outlined" sx={{ overflow: 'hidden' }}>
          <Table>
            <TableBody>
              <TableRow>
                <TableCell sx={{ fontWeight: 600 }}>Description</TableCell>
                <TableCell align="center" sx={{ fontWeight: 600 }}>Quantity</TableCell>
                <TableCell align="right" sx={{ fontWeight: 600 }}>Unit Price</TableCell>
                <TableCell align="right" sx={{ fontWeight: 600 }}>Amount</TableCell>
              </TableRow>
              {invoiceData.items?.map((item, index) => (
                <TableRow key={index}>
                  <TableCell>{item.description}</TableCell>
                  <TableCell align="center">{item.quantity}</TableCell>
                  <TableCell align="right">₹{item.unit_price.toFixed(2)}</TableCell>
                  <TableCell align="right">₹{item.amount.toFixed(2)}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </Paper>
      </Box>

      {/* Totals */}
      <Box sx={{ mb: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 1 }}>
          <Box sx={{ width: '300px' }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
              <Typography variant="body1">Subtotal:</Typography>
              <Typography variant="body1">₹{invoiceData.subtotal.toFixed(2)}</Typography>
            </Box>
            {invoiceData.discount > 0 && (
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography variant="body1" color="success.main">Discount:</Typography>
                <Typography variant="body1" color="success.main">-₹{invoiceData.discount.toFixed(2)}</Typography>
              </Box>
            )}
            {invoiceData.tax > 0 && (
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography variant="body1">Tax:</Typography>
                <Typography variant="body1">₹{invoiceData.tax.toFixed(2)}</Typography>
              </Box>
            )}
            <Divider sx={{ my: 1 }} />
            <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
              <Typography variant="h6" sx={{ fontWeight: 700 }}>Total Amount:</Typography>
              <Typography variant="h6" sx={{ fontWeight: 700, color: '#1976d2' }}>
                ₹{invoiceData.total_amount.toFixed(2)}
              </Typography>
            </Box>
          </Box>
        </Box>
      </Box>

      <Divider sx={{ mb: 3 }} />

      {/* Payment Details */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>
          Payment Information
        </Typography>
        <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 2 }}>
          <Box>
            <Typography variant="body2" color="text.secondary">
              Payment Status
            </Typography>
            <Typography
              variant="body1"
              sx={{
                fontWeight: 600,
                color: invoiceData.payment_status === 'completed' ? 'success.main' : 'warning.main'
              }}
            >
              {invoiceData.payment_status.charAt(0).toUpperCase() + invoiceData.payment_status.slice(1)}
            </Typography>
          </Box>
          <Box>
            <Typography variant="body2" color="text.secondary">
              Payment Method
            </Typography>
            <Typography variant="body1" sx={{ fontWeight: 500 }}>
              {invoiceData.payment_method.replace('_', ' ').split(' ').map(w =>
                w.charAt(0).toUpperCase() + w.slice(1)
              ).join(' ')}
            </Typography>
          </Box>
          {invoiceData.payment_date && (
            <Box>
              <Typography variant="body2" color="text.secondary">
                Payment Date
              </Typography>
              <Typography variant="body1" sx={{ fontWeight: 500 }}>
                {formatDate(invoiceData.payment_date)}
              </Typography>
            </Box>
          )}
        </Box>
      </Box>

      <Divider sx={{ mb: 3 }} />

      {/* Footer */}
      <Box sx={{ textAlign: 'center', mt: 4 }}>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
          This is a computer-generated receipt and does not require a signature.
        </Typography>
        <Typography variant="body2" color="text.secondary">
          For any queries, please contact our front desk.
        </Typography>
        <Typography variant="body2" sx={{ mt: 2, fontWeight: 600 }}>
          Thank you for your business!
        </Typography>
      </Box>
    </Box>
  )
})

Receipt.displayName = 'Receipt'

export default Receipt
