import { apiRequest } from './api.js'

export const dashboardService = {
  get: async (range = 'today') => await apiRequest(`/dashboard?range=${encodeURIComponent(range)}`),
}