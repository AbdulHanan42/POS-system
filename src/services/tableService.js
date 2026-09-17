import { apiRequest } from './api.js'

export const tableService = {
  list: () => apiRequest('/tables'),
}
