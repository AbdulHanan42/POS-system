import { apiRequest } from './api.js'

export const reportService = {
  sales: (params = '') => apiRequest(`/reports/sales${params}`),
}
