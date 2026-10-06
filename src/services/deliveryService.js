import { apiRequest } from './api.js'

export const deliveryService = {
  getZones: () => apiRequest('/delivery/zones'),
  createZone: (zone) => apiRequest('/delivery/zones', { method: 'POST', body: JSON.stringify(zone) }),
  getZone: (id) => apiRequest(`/delivery/zones/${id}`),
  updateZone: (id, zone) => apiRequest(`/delivery/zones/${id}`, { method: 'PATCH', body: JSON.stringify(zone) }),
  deleteZone: (id) => apiRequest(`/delivery/zones/${id}`, { method: 'DELETE' }),
  getDeliveryOrders: () => apiRequest('/delivery/orders'),
  updateDeliveryStatus: (orderId, statusData) => apiRequest(`/delivery/orders/${orderId}/status`, {
    method: 'PATCH',
    body: JSON.stringify(statusData),
  }),
}
