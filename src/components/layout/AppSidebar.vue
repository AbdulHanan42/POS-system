<script setup>
import { LogOut } from 'lucide-vue-next'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth.js'

const auth = useAuthStore()
const router = useRouter()

async function signOut() {
  await auth.logout()
  await router.replace('/login')
}
</script>

<template>
  <aside class="app-sidebar" aria-label="Main navigation">
    <div class="brand">
      <span class="brand-mark" aria-hidden="true">RP</span>
      <span class="brand-copy">
        <strong>RestoPilot</strong>
        <small>Restaurant operations</small>
      </span>
    </div>

    <nav class="navigation">
      <p class="nav-label">Workspace</p>
      <RouterLink v-if="auth.can('dashboard:read')" class="nav-item" to="/dashboard">
        <span class="nav-icon" aria-hidden="true">DB</span>
        <span>Dashboard</span>
      </RouterLink>
      <RouterLink v-if="auth.can('pos:use')" class="nav-item nav-item--accent" to="/pos">
        <span class="nav-icon" aria-hidden="true">$</span>
        <span>Point of Sale</span>
        <span class="nav-shortcut">Ctrl P</span>
      </RouterLink>

      <p class="nav-label nav-label--spaced">Management</p>
      <RouterLink v-if="auth.can('tables:read')" class="nav-item" to="/tables">
        <span class="nav-icon" aria-hidden="true">TB</span>
        <span>Tables</span>
      </RouterLink>
      <div v-if="auth.can('catalog:manage')" class="menu-group">
        <p class="nav-label nav-label--inline">Menu</p>
        <RouterLink class="nav-subitem" to="/menu/products">Products</RouterLink>
        <RouterLink class="nav-subitem" to="/menu/categories">Categories</RouterLink>
        <RouterLink class="nav-subitem" to="/menu/modifiers">Modifiers</RouterLink>
      </div>
      <RouterLink v-if="auth.can('orders:read')" class="nav-item" to="/orders">
        <span class="nav-icon" aria-hidden="true">OR</span>
        <span>Orders</span>
      </RouterLink>
      <RouterLink v-if="auth.can('kitchen:read')" class="nav-item" to="/kitchen">
        <span class="nav-icon" aria-hidden="true">KT</span>
        <span>Kitchen</span>
        <span class="status-dot" aria-label="Kitchen has active orders"></span>
      </RouterLink>
      <RouterLink v-if="auth.can('customers:manage')" class="nav-item" to="/customers">
        <span class="nav-icon" aria-hidden="true">CU</span>
        <span>Customers</span>
      </RouterLink>
      <RouterLink v-if="auth.can('inventory:read')" class="nav-item" to="/inventory">
        <span class="nav-icon" aria-hidden="true">IN</span>
        <span>Inventory</span>
      </RouterLink>
      <RouterLink v-if="auth.can('purchases:manage')" class="nav-item" to="/purchases">
        <span class="nav-icon" aria-hidden="true">PU</span>
        <span>Purchases</span>
      </RouterLink>
      <RouterLink v-if="auth.can('reports:read')" class="nav-item" to="/reports">
        <span class="nav-icon" aria-hidden="true">RE</span>
        <span>Reports</span>
      </RouterLink>
      <RouterLink v-if="auth.can('staff:manage')" class="nav-item" to="/staff">
        <span class="nav-icon" aria-hidden="true">ST</span>
        <span>Staff</span>
      </RouterLink>
      <RouterLink v-if="auth.can('settings:manage')" class="nav-item" to="/settings">
        <span class="nav-icon" aria-hidden="true">SE</span>
        <span>Settings</span>
      </RouterLink>
    </nav>

    <div class="sidebar-footer">
      <div class="shift-status">
        <span class="status-dot" aria-hidden="true"></span>
        <span>
          <strong>{{ auth.user?.tenantName }}</strong>
          <small>{{ auth.user?.role }}</small>
        </span>
      </div>
      <div class="account">
        <span class="avatar">{{ auth.user?.name?.split(' ').map((part) => part[0]).slice(0, 2).join('').toUpperCase() }}</span>
        <span class="account-copy">
          <strong>{{ auth.user?.name }}</strong>
          <small>{{ auth.user?.email }}</small>
        </span>
        <button type="button" class="account-menu" aria-label="Sign out" title="Sign out" @click="signOut"><LogOut :size="16" aria-hidden="true" /></button>
      </div>
    </div>
  </aside>
</template>

<style scoped>
.app-sidebar {
  display: flex;
  flex-direction: column;
  width: 16.5rem;
  min-height: 100vh;
  padding: 1.5rem 1rem 1rem;
  color: #e7edf5;
  background: #14202b;
  border-right: 1px solid #263645;
}

.brand {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0 0.625rem 2rem;
}

.brand-mark,
.avatar {
  display: grid;
  place-items: center;
  flex: 0 0 auto;
  border-radius: 9px;
  font-size: 0.7rem;
  font-weight: 800;
}

.brand-mark {
  width: 2.25rem;
  height: 2.25rem;
  color: #fff7ed;
  background: #e16b2f;
  box-shadow: 0 5px 14px rgb(225 107 47 / 25%);
}

.brand-copy,
.account-copy,
.shift-status span:last-child {
  display: grid;
  gap: 0.15rem;
}

.brand-copy strong {
  color: #f8fafc;
  font-size: 0.95rem;
}

.brand-copy small,
.account-copy small,
.shift-status small {
  color: #8293a5;
  font-size: 0.68rem;
}

.navigation {
  display: grid;
  gap: 0.3rem;
}

.nav-label {
  margin: 0 0.75rem 0.45rem;
  color: #718397;
  font-size: 0.65rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

.nav-label--spaced {
  margin-top: 1.25rem;
}

.nav-label--inline {
  margin-top: 0.85rem;
  margin-bottom: 0.25rem;
}

.nav-subitem {
  display: block;
  margin-left: 2.15rem;
  padding: 0.38rem 0.75rem;
  color: #8fa0b1;
  border-left: 1px solid #3a4b5b;
  font-size: 0.75rem;
  text-decoration: none;
}

.nav-subitem:hover,
.nav-subitem.router-link-active {
  color: #fff7ed;
}

.nav-subitem.router-link-active {
  border-left-color: #e16b2f;
}

.nav-item,
.account {
  display: flex;
  align-items: center;
  min-height: 2.75rem;
  color: #aebdcb;
  text-decoration: none;
  border-radius: 7px;
  transition: color 160ms ease, background-color 160ms ease;
}

.nav-item {
  gap: 0.75rem;
  padding: 0 0.75rem;
  font-size: 0.82rem;
  font-weight: 600;
}

.nav-item:hover,
.account:hover {
  color: #f8fafc;
  background: #1d2c3a;
}

.nav-item.router-link-active {
  color: #fff7ed;
  background: #a94b23;
  box-shadow: inset 3px 0 #ffc49d;
}

.nav-item--accent:not(.router-link-active) {
  color: #f2c0a3;
}

.nav-icon {
  display: grid;
  place-items: center;
  width: 1.4rem;
  height: 1.4rem;
  color: #8598aa;
  border: 1px solid #425364;
  border-radius: 4px;
  font-size: 0.52rem;
  font-weight: 800;
}

.router-link-active .nav-icon {
  color: #fff7ed;
  border-color: rgb(255 247 237 / 45%);
}

.nav-shortcut {
  margin-left: auto;
  color: #8293a5;
  font-size: 0.62rem;
  font-weight: 500;
}

.status-dot {
  width: 0.42rem;
  height: 0.42rem;
  margin-left: auto;
  border-radius: 50%;
  background: #55c58a;
  box-shadow: 0 0 0 3px rgb(85 197 138 / 12%);
}

.sidebar-footer {
  display: grid;
  gap: 1rem;
  margin-top: auto;
  padding-top: 1.25rem;
}

.shift-status {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  padding: 0.8rem 0.75rem;
  background: #1b2a38;
  border: 1px solid #2b3d4d;
  border-radius: 7px;
  font-size: 0.73rem;
}

.shift-status .status-dot {
  margin: 0;
}

.shift-status strong {
  color: #d9e4ed;
  font-size: 0.73rem;
}

.account {
  gap: 0.65rem;
  padding: 0.5rem 0.35rem;
}

.avatar {
  width: 2rem;
  height: 2rem;
  color: #173225;
  background: #9ed9b7;
  font-size: 0.6rem;
}

.account-copy strong {
  color: #e8eef4;
  font-size: 0.75rem;
}

.account-menu {
  margin-left: auto;
  color: #8293a5;
  font-weight: 700;
  letter-spacing: 0.12em;
}

@media (max-width: 700px) {
  .app-sidebar {
    width: 4.5rem;
    padding-inline: 0.5rem;
  }

  .brand,
  .nav-item,
  .account {
    justify-content: center;
  }

  .brand-copy,
  .nav-label,
  .nav-subitem,
  .nav-item > span:not(.nav-icon),
  .sidebar-footer .shift-status,
  .account-copy,
  .account-menu {
    display: none;
  }

  .brand {
    padding-inline: 0;
  }

  .nav-item {
    padding-inline: 0;
  }

  .nav-item .status-dot {
    position: absolute;
    margin: -1rem 0 0 1.2rem;
  }
}
</style>
