import { apiRequest } from './api.js'

export const inventoryService = {
  list: () => apiRequest('/inventory'),
  movements: (productId) => apiRequest(`/inventory/movements${productId ? `?productId=${productId}` : ''}`),
  adjust: (adjustment) => apiRequest('/inventory/adjustments', {
    method: 'POST',
    body: JSON.stringify(adjustment),
  }),
  updateReorderLevel: (productId, reorderLevel) => apiRequest(
    `/inventory/products/${productId}/reorder-level`,
    { method: 'PATCH', body: JSON.stringify({ reorderLevel }) },
  ),
}