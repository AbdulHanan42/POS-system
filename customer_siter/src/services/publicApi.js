const apiBase = import.meta.env.VITE_API_BASE_URL || '/api'
import { customerAuth } from './customerAuth'

export function tenantSlug() {
  return new URLSearchParams(window.location.search).get('tenant')
    || import.meta.env.VITE_RESTAURANT_SLUG
    || 'legacy-workspace'
}

function publicUrl(path) {
  const url = new URL(`${apiBase}/public/${path}`, window.location.origin)
  url.searchParams.set('tenant', tenantSlug())
  return url
}

async function readResponse(response) {
  const body = await response.json().catch(() => ({}))
  if (!response.ok) throw new Error(body.detail || 'The request could not be completed.')
  return body
}

export const publicApi = {
  async getSite() {
    return readResponse(await fetch(publicUrl('site')))
  },
  async getMenu() {
    return readResponse(await fetch(publicUrl('menu')))
  },
  async getDeliveryZones() {
    return readResponse(await fetch(publicUrl('delivery-zones')))
  },
  async createOrder(order) {
    const token = customerAuth.getToken()
    return readResponse(await fetch(publicUrl('orders'), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: JSON.stringify(order),
    }))
  },
  async getOrderStatus(orderId, token) {
    return readResponse(await fetch(publicUrl(`orders/${encodeURIComponent(orderId)}/status`), {
      headers: { 'X-Order-Tracking-Token': token },
    }))
  },
  orderEventsUrl(orderId) {
    const url = new URL(`${apiBase}/ws/public/orders/${encodeURIComponent(orderId)}`, window.location.origin)
    url.searchParams.set('tenant', tenantSlug())
    url.protocol = url.protocol === 'https:' ? 'wss:' : 'ws:'
    return url.toString()
  },
}

export function trackingProtocols(token) {
  return ['order-tracking', `order-token.${token}`]
}