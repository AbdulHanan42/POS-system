import { apiRequest } from './api.js'

export const categoryService = {
  list: () => apiRequest('/categories'),
  create: (category) => apiRequest('/categories', { method: 'POST', body: JSON.stringify(category) }),
  update: (id, category) => apiRequest(`/categories/${id}`, { method: 'PUT', body: JSON.stringify(category) }),
  remove: (id) => apiRequest(`/categories/${id}`, { method: 'DELETE' }),
}