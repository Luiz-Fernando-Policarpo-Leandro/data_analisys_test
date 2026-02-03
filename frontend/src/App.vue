<template>
  <div class="container">
    <header>
      <h1>Operadoras ANS</h1>

      <nav>
        <RouterLink to="/">Operadoras</RouterLink>
        <RouterLink to="/estatisticas">Estatísticas</RouterLink>
      </nav>
    </header>

    <main>
      <RouterView />
    </main>
  </div>
</template>

<script setup lang="ts">
import { RouterView, RouterLink } from 'vue-router'
</script>

<style scoped>
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 16px;
}

header {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 24px;
}

nav {
  display: flex;
  gap: 16px;
}

nav a {
  text-decoration: none;
  color: #42b883;
  font-weight: bold;
}

nav a.router-link-active {
  text-decoration: underline;
}
</style>
