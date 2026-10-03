import { apiRequest } from './api.js'

export const tableService = {
  list: () => apiRequest('/tables'),
  create: (table) => apiRequest('/tables', { method: 'POST', body: JSON.stringify(table) }),
  update: (id, table) => apiRequest(`/tables/${id}`, { method: 'PUT', body: JSON.stringify(table) }),
  remove: (id) => apiRequest(`/tables/${id}`, { method: 'DELETE' }),
}
