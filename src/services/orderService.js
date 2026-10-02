import { apiRequest } from './api.js'

export const orderService = {
  list: async () => await apiRequest('/orders'),
  get: async (id) => await apiRequest(`/orders/${id}`),
  create: async (order) => await apiRequest('/orders', { method: 'POST', body: JSON.stringify(order) }),
  updateStatus: async (id, status) => await apiRequest(`/orders/${id}/status`, {
    method: 'PATCH',
    body: JSON.stringify({ status }),
  }),
}
