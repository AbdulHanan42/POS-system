import { apiRequest } from './api.js'

export const productService = {
  list: async () => await apiRequest('/products'),
  create: async (product) => await apiRequest('/products', { method: 'POST', body: JSON.stringify(product) }),
  update: async (id, product) => await apiRequest(`/products/${id}`, { method: 'PUT', body: JSON.stringify(product) }),
  remove: async (id) => await apiRequest(`/products/${id}`, { method: 'DELETE' }),
}
