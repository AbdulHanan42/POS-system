import { useAuthStore } from '../stores/auth.js'

export function usePermissions() {
  const authStore = useAuthStore()

  function can(permission) {
    return authStore.can(permission)
  }

  return { can }
}
