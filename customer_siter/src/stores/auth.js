import { defineStore } from 'pinia'
import { ref } from 'vue'
import { customerAuth } from '../services/customerAuth'

export const useAuthStore = defineStore('auth', () => {
  const customer = ref(null)
  const pendingEmail = ref('')
  const loading = ref(false)
  const error = ref('')

  function initialize() {
    pendingEmail.value = customerAuth.getPendingEmail()
    if (customerAuth.isAuthenticated()) {
      customer.value = customerAuth.getCustomer()
    }
  }

  async function register(data) {
    loading.value = true
    error.value = ''
    try {
      const registration = await customerAuth.register(data)
      pendingEmail.value = registration.email
      return registration
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function verifyRegistration(otp) {
    loading.value = true
    error.value = ''
    try {
      customer.value = await customerAuth.verifyRegistration(otp)
      pendingEmail.value = ''
      return customer.value
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function resendRegistrationCode() {
    loading.value = true
    error.value = ''
    try {
      return await customerAuth.resendRegistrationCode()
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
    pendingEmail,
    loading,
    error,
    initialize,
    register,
    verifyRegistration,
    resendRegistrationCode,
    login,
    logout,
    refreshProfile,
    updateProfile,
  }
})
