import { apiRequest } from './api.js'

export const orderService = {
  list: async () => await apiRequest('/orders'),
  get: async (id) => await apiRequest(`/orders/${id}`),
  create: async (order) => await apiRequest('/orders', { method: 'POST', body: JSON.stringify(order) }),
  createKitchenOrder: async (order) => await apiRequest('/orders/kitchen', { method: 'POST', body: JSON.stringify(order) }),
  completeKitchenPayment: async (id, paymentMethod) => await apiRequest(`/orders/${id}/payment`, {
    method: 'PATCH',
    body: JSON.stringify({ paymentMethod }),
  }),
  updateStatus: async (id, status) => await apiRequest(`/orders/${id}/status`, {
    method: 'PATCH',
    body: JSON.stringify({ status }),
  }),
  updateKitchenStatus: async (id, kitchenStatus) => await apiRequest(`/orders/${id}/kitchen-status`, {
    method: 'PATCH',
    body: JSON.stringify({ kitchenStatus }),
  }),
}
