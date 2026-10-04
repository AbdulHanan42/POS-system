import { apiRequest } from './api.js'

export const settingsService = {
  get: () => apiRequest('/settings'),
  update: (settings) => apiRequest('/settings', {
    method: 'PUT',
    body: JSON.stringify(settings),
  }),
}