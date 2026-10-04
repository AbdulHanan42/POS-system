import { apiRequest } from './api.js'

export const staffService = {
  list: () => apiRequest('/staff'),
  create: (staffMember) => apiRequest('/staff', {
    method: 'POST',
    body: JSON.stringify(staffMember),
  }),
  update: (id, staffMember) => apiRequest(`/staff/${id}`, {
    method: 'PUT',
    body: JSON.stringify(staffMember),
  }),
  remove: (id) => apiRequest(`/staff/${id}`, { method: 'DELETE' }),
}