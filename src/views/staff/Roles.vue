<template>
  <section class="roles-view">
    <div class="header">
      <h1>Roles and Permissions</h1>
      <p class="subtitle">Manage access levels for different staff roles in your restaurant</p>
    </div>

    <div class="roles-grid">
      <div v-for="role in roles" :key="role.name" class="role-card" :class="role.name.toLowerCase()">
        <div class="role-header">
          <div class="role-icon">{{ role.icon }}</div>
          <div>
            <h2>{{ role.name }}</h2>
            <p class="role-description">{{ role.description }}</p>
          </div>
        </div>
        <div class="permissions-list">
          <h3>Permissions</h3>
          <div class="permissions">
            <span v-for="permission in role.permissions" :key="permission" class="permission-badge">
              {{ permission }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <div class="info-section">
      <h3>Permission Legend</h3>
      <div class="legend-grid">
        <div class="legend-item">
          <strong>*</strong>
          <span>Full access to all features</span>
        </div>
        <div class="legend-item">
          <strong>pos:use</strong>
          <span>Access to POS interface</span>
        </div>
        <div class="legend-item">
          <strong>catalog:read</strong>
          <span>View product catalog</span>
        </div>
        <div class="legend-item">
          <strong>orders:read</strong>
          <span>View orders</span>
        </div>
        <div class="legend-item">
          <strong>orders:create</strong>
          <span>Create new orders</span>
        </div>
        <div class="legend-item">
          <strong>orders:payment</strong>
          <span>Process payments</span>
        </div>
        <div class="legend-item">
          <strong>kitchen:read</strong>
          <span>View kitchen display</span>
        </div>
        <div class="legend-item">
          <strong>kitchen:update</strong>
          <span>Update kitchen order status</span>
        </div>
        <div class="legend-item">
          <strong>inventory:read</strong>
          <span>View inventory levels</span>
        </div>
        <div class="legend-item">
          <strong>tables:read</strong>
          <span>View table status</span>
        </div>
        <div class="legend-item">
          <strong>tables:update</strong>
          <span>Update table status</span>
        </div>
        <div class="legend-item">
          <strong>customers:manage</strong>
          <span>Manage customer information</span>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref } from 'vue'

const roles = ref([
  {
    name: 'Administrator',
    icon: '👑',
    description: 'Full access to all system features and settings',
    permissions: ['*']
  },
  {
    name: 'Manager',
    icon: '👔',
    description: 'Full access to all operational features',
    permissions: ['*']
  },
  {
    name: 'Cashier',
    icon: '💰',
    description: 'Handle sales, payments, and customer orders',
    permissions: ['pos:use', 'catalog:read', 'orders:read', 'orders:create', 'orders:payment', 'inventory:read', 'customers:manage']
  },
  {
    name: 'Chef',
    icon: '👨‍🍳',
    description: 'Manage kitchen operations and order preparation',
    permissions: ['kitchen:read', 'kitchen:update', 'orders:read']
  },
  {
    name: 'Waiter',
    icon: '🍽️',
    description: 'Take orders, manage tables, and assist customers',
    permissions: ['pos:use', 'catalog:read', 'orders:read', 'orders:create', 'inventory:read', 'tables:read', 'tables:update', 'customers:manage']
  }
])
</script>

<style scoped>
.roles-view {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

.header {
  margin-bottom: 2rem;
}

.header h1 {
  font-size: 2rem;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 0.5rem;
}

.subtitle {
  color: #6b7280;
  font-size: 1rem;
}

.roles-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 1.5rem;
  margin-bottom: 3rem;
}

.role-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  border: 2px solid transparent;
  transition: all 0.2s;
}

.role-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
}

.role-card.administrator {
  border-color: #f59e0b;
}

.role-card.manager {
  border-color: #3b82f6;
}

.role-card.cashier {
  border-color: #10b981;
}

.role-card.chef {
  border-color: #ef4444;
}

.role-card.waiter {
  border-color: #8b5cf6;
}

.role-header {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.role-icon {
  font-size: 2.5rem;
  line-height: 1;
}

.role-header h2 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 0.25rem;
}

.role-description {
  color: #6b7280;
  font-size: 0.875rem;
  line-height: 1.4;
}

.permissions-list h3 {
  font-size: 0.875rem;
  font-weight: 600;
  color: #374151;
  margin-bottom: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.permissions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.permission-badge {
  background: #f3f4f6;
  color: #374151;
  padding: 0.375rem 0.75rem;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 500;
  font-family: monospace;
}

.info-section {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.info-section h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 1rem;
}

.legend-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 0.75rem;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem;
  border-radius: 6px;
  background: #f9fafb;
}

.legend-item strong {
  font-family: monospace;
  font-size: 0.875rem;
  color: #4b5563;
  min-width: 140px;
}

.legend-item span {
  color: #6b7280;
  font-size: 0.875rem;
}
</style>
