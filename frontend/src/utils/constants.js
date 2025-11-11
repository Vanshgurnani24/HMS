export const ROOM_TYPES = {
  SINGLE: 'single',
  DOUBLE: 'double',
  SUITE: 'suite',
  DELUXE: 'deluxe',
}

export const ROOM_STATUS = {
  AVAILABLE: 'available',
  OCCUPIED: 'occupied',
  MAINTENANCE: 'maintenance',
  RESERVED: 'reserved',
}

export const BOOKING_STATUS = {
  PENDING: 'pending',
  CONFIRMED: 'confirmed',
  CHECKED_IN: 'checked_in',
  CHECKED_OUT: 'checked_out',
  CANCELLED: 'cancelled',
}

export const PAYMENT_METHODS = {
  CASH: 'cash',
  CREDIT_CARD: 'credit_card',
  DEBIT_CARD: 'debit_card',
  UPI: 'upi',
  NET_BANKING: 'net_banking',
  WALLET: 'wallet',
}

export const PAYMENT_STATUS = {
  PENDING: 'pending',
  COMPLETED: 'completed',
  FAILED: 'failed',
  REFUNDED: 'refunded',
}

export const USER_ROLES = {
  ADMIN: 'admin',
  STAFF: 'staff',
}

export const ROOM_TYPE_LABELS = {
  [ROOM_TYPES.SINGLE]: 'Single',
  [ROOM_TYPES.DOUBLE]: 'Double',
  [ROOM_TYPES.SUITE]: 'Suite',
  [ROOM_TYPES.DELUXE]: 'Deluxe',
}

export const ROOM_STATUS_LABELS = {
  [ROOM_STATUS.AVAILABLE]: 'Available',
  [ROOM_STATUS.OCCUPIED]: 'Occupied',
  [ROOM_STATUS.MAINTENANCE]: 'Maintenance',
  [ROOM_STATUS.RESERVED]: 'Reserved',
}

export const BOOKING_STATUS_LABELS = {
  [BOOKING_STATUS.PENDING]: 'Pending',
  [BOOKING_STATUS.CONFIRMED]: 'Confirmed',
  [BOOKING_STATUS.CHECKED_IN]: 'Checked In',
  [BOOKING_STATUS.CHECKED_OUT]: 'Checked Out',
  [BOOKING_STATUS.CANCELLED]: 'Cancelled',
}

export const PAYMENT_METHOD_LABELS = {
  [PAYMENT_METHODS.CASH]: 'Cash',
  [PAYMENT_METHODS.CREDIT_CARD]: 'Credit Card',
  [PAYMENT_METHODS.DEBIT_CARD]: 'Debit Card',
  [PAYMENT_METHODS.UPI]: 'UPI',
  [PAYMENT_METHODS.NET_BANKING]: 'Net Banking',
  [PAYMENT_METHODS.WALLET]: 'Wallet',
}

export const PAYMENT_STATUS_LABELS = {
  [PAYMENT_STATUS.PENDING]: 'Pending',
  [PAYMENT_STATUS.COMPLETED]: 'Completed',
  [PAYMENT_STATUS.FAILED]: 'Failed',
  [PAYMENT_STATUS.REFUNDED]: 'Refunded',
}

export const STATUS_COLORS = {
  // Room Status
  available: 'success',
  occupied: 'error',
  maintenance: 'warning',
  reserved: 'info',
  
  // Booking Status
  pending: 'warning',
  confirmed: 'info',
  checked_in: 'success',
  checked_out: 'default',
  cancelled: 'error',
  
  // Payment Status
  completed: 'success',
  failed: 'error',
  refunded: 'warning',
}