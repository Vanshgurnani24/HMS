/**
 * Date Utility Functions
 * Formats dates in DD/MM/YYYY format for display in the frontend
 */

/**
 * Format date to DD/MM/YYYY
 * @param {string|Date} date - Date string or Date object
 * @returns {string} Formatted date string in DD/MM/YYYY format
 */
export const formatDate = (date) => {
  if (!date) return '-'
  
  try {
    const d = new Date(date)
    
    // Check if date is valid
    if (isNaN(d.getTime())) return '-'
    
    const day = String(d.getDate()).padStart(2, '0')
    const month = String(d.getMonth() + 1).padStart(2, '0') // Months are 0-indexed
    const year = d.getFullYear()
    
    return `${day}/${month}/${year}`
  } catch (error) {
    console.error('Error formatting date:', error)
    return '-'
  }
}

/**
 * Format datetime to DD/MM/YYYY HH:MM
 * @param {string|Date} datetime - Datetime string or Date object
 * @returns {string} Formatted datetime string in DD/MM/YYYY HH:MM format
 */
export const formatDateTime = (datetime) => {
  if (!datetime) return '-'
  
  try {
    const d = new Date(datetime)
    
    // Check if date is valid
    if (isNaN(d.getTime())) return '-'
    
    const day = String(d.getDate()).padStart(2, '0')
    const month = String(d.getMonth() + 1).padStart(2, '0')
    const year = d.getFullYear()
    const hours = String(d.getHours()).padStart(2, '0')
    const minutes = String(d.getMinutes()).padStart(2, '0')
    
    return `${day}/${month}/${year} ${hours}:${minutes}`
  } catch (error) {
    console.error('Error formatting datetime:', error)
    return '-'
  }
}

/**
 * Get today's date in YYYY-MM-DD format (for input fields)
 * @returns {string} Today's date in YYYY-MM-DD format
 */
export const getTodayInputFormat = () => {
  const today = new Date()
  const year = today.getFullYear()
  const month = String(today.getMonth() + 1).padStart(2, '0')
  const day = String(today.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

/**
 * Convert DD/MM/YYYY to YYYY-MM-DD (for backend)
 * @param {string} dateStr - Date string in DD/MM/YYYY format
 * @returns {string} Date string in YYYY-MM-DD format
 */
export const convertToBackendFormat = (dateStr) => {
  if (!dateStr) return ''
  
  try {
    const [day, month, year] = dateStr.split('/')
    return `${year}-${month}-${day}`
  } catch (error) {
    console.error('Error converting date format:', error)
    return dateStr
  }
}