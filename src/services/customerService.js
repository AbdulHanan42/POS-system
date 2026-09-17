import { apiRequest } from './api.js'

export const customerService = {
  list: () => apiRequest('/customers'),
  create: (customer) => apiRequest('/customers', { method: 'POST', body: JSON.stringify(customer) }),
  update: (id, customer) => apiRequest(`/customers/${id}`, { method: 'PUT', body: JSON.stringify(customer) }),
  remove: (id) => apiRequest(`/customers/${id}`, { method: 'DELETE' }),
}
