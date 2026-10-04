import { apiRequest } from './api.js'

export const purchaseService = {
  list: () => apiRequest('/purchases'),
  create: (purchase) => apiRequest('/purchases', {
    method: 'POST',
    body: JSON.stringify(purchase),
  }),
  receive: (id) => apiRequest(`/purchases/${id}/receive`, { method: 'POST' }),
}