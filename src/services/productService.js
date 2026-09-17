import { apiRequest } from './api.js'

export const productService = {
  list: () => apiRequest('/products'),
}
