<template>
  <footer class="app-footer">
    <div class="footer-inner">
      <div class="footer-brand">
        <img src="/images/logonegro.jpeg" alt="Logo" class="footer-logo" />
        <div>
          <div class="footer-name">Nexo Postural: Kyene'is Pondyam</div>
          <div class="footer-org">Universidad Politécnica de Chiapas</div>
        </div>
      </div>
      <div class="footer-copy">&copy; 2026 · Todos los derechos reservados</div>
    </div>
  </footer>
</template>

<style scoped>
.app-footer {
  background: var(--surface);
  border-top: 1px solid var(--border);
  margin-top: auto;
}
.footer-inner {
  max-width: 1024px;
  margin: 0 auto;
  padding: 1rem 1.5rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 0.75rem;
}
.footer-brand {
  display: flex;
  align-items: center;
  gap: 8px;
}
.footer-logo {
  height: 22px;
  width: 22px;
  object-fit: cover;
  border-radius: 6px;
  border: 1px solid var(--border);
}
.footer-name { font-size: 0.75rem; font-weight: 700; color: var(--text-base); }
.footer-org  { font-size: 0.65rem; color: var(--text-subtle); margin-top: 1px; }
.footer-copy { font-size: 0.7rem; color: var(--text-subtle); }
</style>
