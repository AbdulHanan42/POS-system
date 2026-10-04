import { defineStore } from 'pinia'
import { ref } from 'vue'
import { authService } from '../services/authService.js'

const TOKEN_KEY = 'restopilot.accessToken'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem(TOKEN_KEY) || '')
  const initialized = ref(false)
  const loading = ref(false)
  const error = ref('')

  function clearSession() {
    localStorage.removeItem(TOKEN_KEY)
    token.value = ''
    user.value = null
    initialized.value = true
  }

  function acceptSession(session) {
    token.value = session.accessToken
    user.value = session.user
    localStorage.setItem(TOKEN_KEY, session.accessToken)
    initialized.value = true
    error.value = ''
  }

  async function initialize() {
    if (initialized.value) return Boolean(user.value)
    if (!token.value) {
      initialized.value = true
      return false
    }
    loading.value = true
    try {
      user.value = await authService.me()
      return true
    } catch {
      clearSession()
      return false
    } finally {
      loading.value = false
      initialized.value = true
    }
  }

  async function login(credentials) {
    loading.value = true
    error.value = ''
    try {
      acceptSession(await authService.login(credentials))
      return user.value
    } catch (requestError) {
      error.value = requestError.message
      throw requestError
    } finally {
      loading.value = false
    }
  }

  async function signup(details) {
    loading.value = true
    error.value = ''
    try {
      acceptSession(await authService.signup(details))
      return user.value
    } catch (requestError) {
      error.value = requestError.message
      throw requestError
    } finally {
      loading.value = false
    }
  }

  async function logout() {
    try {
      if (token.value) await authService.logout()
    } finally {
      clearSession()
    }
  }

  function can(permission) {
    const permissions = user.value?.permissions || []
    return permissions.includes('*') || permissions.includes(permission)
  }

  return { user, token, initialized, loading, error, initialize, login, signup, logout, can }
})
