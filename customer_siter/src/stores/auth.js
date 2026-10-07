import { defineStore } from 'pinia'
import { ref } from 'vue'
import { customerAuth } from '../services/customerAuth'

export const useAuthStore = defineStore('auth', () => {
  const customer = ref(null)
  const loading = ref(false)
  const error = ref('')

  function initialize() {
    if (customerAuth.isAuthenticated()) {
      customer.value = customerAuth.getCustomer()
    }
  }

  async function register(data) {
    loading.value = true
    error.value = ''
    try {
      customer.value = await customerAuth.register(data)
      return customer.value
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function login(credentials) {
    loading.value = true
    error.value = ''
    try {
      customer.value = await customerAuth.login(credentials)
      return customer.value
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function logout() {
    loading.value = true
    error.value = ''
    try {
      await customerAuth.logout()
      customer.value = null
    } catch (err) {
      error.value = err.message
    } finally {
      loading.value = false
    }
  }

  async function refreshProfile() {
    loading.value = true
    error.value = ''
    try {
      customer.value = await customerAuth.getProfile()
      return customer.value
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function updateProfile(data) {
    loading.value = true
    error.value = ''
    try {
      customer.value = await customerAuth.updateProfile(data)
      return customer.value
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    customer,
    loading,
    error,
    initialize,
    register,
    login,
    logout,
    refreshProfile,
    updateProfile,
  }
})
