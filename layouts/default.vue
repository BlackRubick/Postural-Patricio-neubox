<template>
  <div class="app-shell">
    <AppNavbar />
    <main class="app-main animate-fade-in">
      <slot />
    </main>
    <AppFooter />
  </div>
</template>

<style>
.app-shell {
  min-height: 100svh;
  display: flex;
  flex-direction: column;
  background: var(--surface-2);
  /* subtle diagonal grid pattern */
  background-image:
    linear-gradient(var(--border) 1px, transparent 1px),
    linear-gradient(90deg, var(--border) 1px, transparent 1px);
  background-size: 40px 40px;
  background-attachment: fixed;
}
.app-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  width: 100%;
  max-width: 1024px;
  margin: 0 auto;
  padding-bottom: 3rem;
}
</style>
