import { apiRequest } from './api.js'

export const orderService = {
  create: (order) => apiRequest('/orders', { method: 'POST', body: JSON.stringify(order) }),
}
