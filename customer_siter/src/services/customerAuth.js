const apiBase = import.meta.env.VITE_API_BASE_URL || '/api'

const TOKEN_KEY = 'restaurant_customer.accessToken'
const CUSTOMER_KEY = 'restaurant_customer.data'

function readResponse(response) {
  const body = response.json().catch(() => ({}))
  if (!response.ok) throw new Error(body.detail || 'The request could not be completed.')
  return body
}

export const customerAuth = {
  getToken() {
    return localStorage.getItem(TOKEN_KEY) || ''
  },

  getCustomer() {
    const data = localStorage.getItem(CUSTOMER_KEY)
    return data ? JSON.parse(data) : null
  },

  setSession(session) {
    localStorage.setItem(TOKEN_KEY, session.accessToken)
    localStorage.setItem(CUSTOMER_KEY, JSON.stringify(session.customer))
  },

  clearSession() {
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(CUSTOMER_KEY)
  },

  isAuthenticated() {
    return !!this.getToken()
  },

  async register(data) {
    const response = await fetch(`${apiBase}/customers/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    })
    const session = await readResponse(response)
    this.setSession(session)
    return session.customer
  },

  async login(credentials) {
    const response = await fetch(`${apiBase}/customers/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(credentials),
    })
    const session = await readResponse(response)
    this.setSession(session)
    return session.customer
  },

  async logout() {
    const token = this.getToken()
    if (token) {
      await fetch(`${apiBase}/customers/logout`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
      }).catch(() => {})
    }
    this.clearSession()
  },

  async getProfile() {
    const token = this.getToken()
    const response = await fetch(`${apiBase}/customers/me`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    })
    const customer = await readResponse(response)
    localStorage.setItem(CUSTOMER_KEY, JSON.stringify(customer))
    return customer
  },

  async updateProfile(data) {
    const token = this.getToken()
    const response = await fetch(`${apiBase}/customers/me`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify(data),
    })
    const customer = await readResponse(response)
    localStorage.setItem(CUSTOMER_KEY, JSON.stringify(customer))
    return customer
  },

  async getAddresses() {
    const token = this.getToken()
    const response = await fetch(`${apiBase}/customers/addresses`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    })
    return readResponse(response)
  },

  async createAddress(data) {
    const token = this.getToken()
    const response = await fetch(`${apiBase}/customers/addresses`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify(data),
    })
    return readResponse(response)
  },

  async updateAddress(id, data) {
    const token = this.getToken()
    const response = await fetch(`${apiBase}/customers/addresses/${id}`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify(data),
    })
    return readResponse(response)
  },

  async deleteAddress(id) {
    const token = this.getToken()
    const response = await fetch(`${apiBase}/customers/addresses/${id}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    })
    if (!response.ok) throw new Error('Failed to delete address')
  },

  async getOrders() {
    const token = this.getToken()
    const response = await fetch(`${apiBase}/customers/orders`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    })
    return readResponse(response)
  },
}
