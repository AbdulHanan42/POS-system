<template>
  <aside class="app-sidebar" aria-label="Main navigation">
    <strong>Restaurant POS</strong>
    <nav>
      <RouterLink to="/dashboard">Dashboard</RouterLink>
      <RouterLink to="/pos">POS</RouterLink>
      <RouterLink to="/tables">Tables</RouterLink>
      <RouterLink to="/kitchen">Kitchen</RouterLink>
    </nav>
  </aside>
</template>

<style scoped>
.app-sidebar {
  display: grid;
  align-content: start;
  gap: 2rem;
  width: 15rem;
  min-height: 100vh;
  padding: 1.5rem;
  color: white;
  background: #172033;
}

nav {
  display: grid;
  gap: 0.75rem;
}

nav a {
  color: #cbd5e1;
  text-decoration: none;
}

nav a.router-link-active {
  color: white;
}
</style>
