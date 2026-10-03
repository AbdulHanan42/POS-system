import { apiRequest } from './api.js'

export const modifierService = {
  list: () => apiRequest('/modifiers'),
  create: (group) => apiRequest('/modifiers', { method: 'POST', body: JSON.stringify(group) }),
  update: (id, group) => apiRequest(`/modifiers/${id}`, { method: 'PUT', body: JSON.stringify(group) }),
  remove: (id) => apiRequest(`/modifiers/${id}`, { method: 'DELETE' }),
}