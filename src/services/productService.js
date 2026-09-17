import { apiRequest } from './api.js'

export const productService = {
  list: () => apiRequest('/products'),
  create: (product) => apiRequest('/products', { method: 'POST', body: JSON.stringify(product) }),
  update: (id, product) => apiRequest(`/products/${id}`, { method: 'PUT', body: JSON.stringify(product) }),
  remove: (id) => apiRequest(`/products/${id}`, { method: 'DELETE' }),
}
