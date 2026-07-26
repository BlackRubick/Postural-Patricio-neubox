<template>
  <div class="usuarios-shell">

    <!-- Header -->
    <div class="usuarios-header">
      <div>
        <h1 class="usuarios-title">Gestión de Usuarios</h1>
        <p class="usuarios-subtitle">Administra las cuentas con acceso a la plataforma</p>
      </div>
      <button class="btn-primary" @click="openCreate">
        <svg width="14" height="14" fill="none" viewBox="0 0 24 24">
          <path d="M12 5v14M5 12h14" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
        </svg>
        Nuevo usuario
      </button>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="usuarios-loading">
      <div class="spinner"></div>
      <span>Cargando usuarios...</span>
    </div>

    <!-- Lista -->
    <div v-else-if="users.length" class="usuarios-grid">
      <div v-for="u in users" :key="u.id" class="user-card">
        <div class="user-avatar-big">{{ initials(u.name || u.email) }}</div>
        <div class="user-info">
          <div class="user-name">{{ u.name || '—' }}</div>
          <div class="user-email">{{ u.email }}</div>
          <div class="user-meta">
            <span class="role-badge" :class="u.role === 'admin' ? 'role-admin' : 'role-doctor'">
              {{ u.role === 'admin' ? 'Administrador' : 'Doctor' }}
            </span>
            <span class="user-date">Desde {{ formatDate(u.createdAt) }}</span>
          </div>
        </div>
        <div class="user-actions">
          <button class="btn-icon" title="Editar" @click="openEdit(u)">
            <svg width="14" height="14" fill="none" viewBox="0 0 24 24">
              <path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              <path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>
          </button>
          <button
            class="btn-icon btn-icon-danger"
            title="Eliminar"
            :disabled="u.id === currentUser?.id"
            @click="handleDelete(u)"
          >
            <svg width="14" height="14" fill="none" viewBox="0 0 24 24">
              <polyline points="3 6 5 6 21 6" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              <path d="M19 6l-1 14a2 2 0 01-2 2H8a2 2 0 01-2-2L5 6M10 11v6M14 11v6M9 6V4a1 1 0 011-1h4a1 1 0 011 1v2" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>
          </button>
        </div>
      </div>
    </div>

    <!-- Empty -->
    <div v-else class="usuarios-empty">
      <svg width="40" height="40" fill="none" viewBox="0 0 24 24" class="empty-icon">
        <path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2M9 11a4 4 0 100-8 4 4 0 000 8zM23 21v-2a4 4 0 00-3-3.87M16 3.13a4 4 0 010 7.75" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
      </svg>
      <p>No hay usuarios registrados</p>
    </div>

  </div>

  <!-- Modal crear / editar -->
  <Teleport to="body">
    <div v-if="modalOpen" class="modal-overlay" @click.self="closeModal">
      <div class="modal-box animate-fade-in-up">

        <div class="modal-header">
          <h3>{{ editing ? 'Editar usuario' : 'Nuevo usuario' }}</h3>
          <button class="modal-close" @click="closeModal">
            <svg width="14" height="14" fill="none" viewBox="0 0 24 24">
              <path d="M18 6L6 18M6 6l12 12" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
            </svg>
          </button>
        </div>

        <form @submit.prevent="handleSave" class="modal-form">
          <!-- Nombre -->
          <div class="field">
            <label class="field-label">Nombre completo <span class="field-optional">— opcional</span></label>
            <input v-model="form.name" type="text" placeholder="Ej. Dr. Juan García" class="field-input" />
          </div>

          <!-- Email -->
          <div class="field">
            <label class="field-label">Correo electrónico <span class="field-required">*</span></label>
            <input v-model="form.email" type="email" required placeholder="doctor@ejemplo.com" class="field-input" />
          </div>

          <!-- Contraseña -->
          <div class="field">
            <label class="field-label">
              Contraseña
              <span v-if="editing" class="field-optional">— dejar en blanco para no cambiar</span>
              <span v-else class="field-required">*</span>
            </label>
            <div class="password-wrap">
              <input
                v-model="form.password"
                :type="showPwd ? 'text' : 'password'"
                :required="!editing"
                placeholder="Mínimo 6 caracteres"
                class="field-input"
                style="padding-right:2.8rem"
              />
              <button type="button" class="pwd-toggle" @click="showPwd = !showPwd">
                <svg v-if="!showPwd" width="15" height="15" fill="none" viewBox="0 0 24 24">
                  <path d="M1 12s4-7 11-7 11 7 11 7-4 7-11 7S1 12 1 12z" stroke="currentColor" stroke-width="2"/>
                  <circle cx="12" cy="12" r="3" stroke="currentColor" stroke-width="2"/>
                </svg>
                <svg v-else width="15" height="15" fill="none" viewBox="0 0 24 24">
                  <path d="M17.94 17.94A10.07 10.07 0 0112 20c-7 0-11-8-11-8a18.45 18.45 0 015.06-5.94M9.9 4.24A9.12 9.12 0 0112 4c7 0 11 8 11 8a18.5 18.5 0 01-2.16 3.19m-6.72-1.07a3 3 0 11-4.24-4.24M1 1l22 22" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                </svg>
              </button>
            </div>
          </div>

          <!-- Rol -->
          <div class="field">
            <label class="field-label">Rol <span class="field-required">*</span></label>
            <select v-model="form.role" required class="field-input">
              <option value="doctor">Doctor</option>
              <option value="admin">Administrador</option>
            </select>
          </div>

          <!-- Error -->
          <div v-if="formError" class="form-error">
            <svg width="14" height="14" fill="none" viewBox="0 0 24 24">
              <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
              <path d="M12 8v4M12 16h.01" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>
            {{ formError }}
          </div>

          <div class="modal-actions">
            <button type="button" class="btn-secondary" @click="closeModal">Cancelar</button>
            <button type="submit" class="btn-primary" :disabled="saving">
              <div v-if="saving" class="spinner" style="width:14px;height:14px;border-width:2px"></div>
              {{ saving ? 'Guardando...' : (editing ? 'Guardar cambios' : 'Crear usuario') }}
            </button>
          </div>
        </form>

      </div>
    </div>
  </Teleport>
</template>

<script setup>
definePageMeta({ middleware: 'auth' })

import Swal from 'sweetalert2'

const { user: currentUser } = useAuth()

const users = ref([])
const loading = ref(true)
const modalOpen = ref(false)
const editing = ref(null)
const saving = ref(false)
const showPwd = ref(false)
const formError = ref('')

const form = ref({ name: '', email: '', password: '', role: 'doctor' })

function initials(str) {
  return str.split(' ').slice(0, 2).map(s => s[0]?.toUpperCase() || '').join('') || '?'
}

function formatDate(dateStr) {
  return new Date(dateStr).toLocaleDateString('es-MX', { year: 'numeric', month: 'short' })
}

async function fetchUsers() {
  loading.value = true
  try {
    users.value = await $fetch('/api/users')
  } catch {
    Swal.fire({ icon: 'error', title: 'Error', text: 'No se pudieron cargar los usuarios.' })
  } finally {
    loading.value = false
  }
}

function openCreate() {
  editing.value = null
  form.value = { name: '', email: '', password: '', role: 'doctor' }
  formError.value = ''
  showPwd.value = false
  modalOpen.value = true
}

function openEdit(u) {
  editing.value = u
  form.value = { name: u.name || '', email: u.email, password: '', role: u.role }
  formError.value = ''
  showPwd.value = false
  modalOpen.value = true
}

function closeModal() {
  modalOpen.value = false
  editing.value = null
}

async function handleSave() {
  formError.value = ''
  if (!editing.value && form.value.password.length < 6) {
    formError.value = 'La contraseña debe tener al menos 6 caracteres'
    return
  }
  saving.value = true
  try {
    if (editing.value) {
      const updated = await $fetch(`/api/users/${editing.value.id}`, {
        method: 'PUT',
        body: {
          name: form.value.name,
          email: form.value.email,
          role: form.value.role,
          password: form.value.password || undefined,
        },
      })
      const idx = users.value.findIndex(u => u.id === editing.value.id)
      if (idx !== -1) users.value[idx] = updated
    } else {
      const created = await $fetch('/api/users', {
        method: 'POST',
        body: { ...form.value },
      })
      users.value.unshift(created)
    }
    closeModal()
    Swal.fire({
      icon: 'success',
      title: editing.value ? 'Usuario actualizado' : 'Usuario creado',
      timer: 1400,
      showConfirmButton: false,
    })
  } catch (e) {
    formError.value = e?.data?.message || 'Ocurrió un error al guardar'
  } finally {
    saving.value = false
  }
}

async function handleDelete(u) {
  const result = await Swal.fire({
    icon: 'warning',
    title: '¿Eliminar usuario?',
    text: `Se eliminará la cuenta de ${u.email}. Esta acción no se puede deshacer.`,
    showCancelButton: true,
    confirmButtonText: 'Sí, eliminar',
    cancelButtonText: 'Cancelar',
    reverseButtons: true,
  })
  if (!result.isConfirmed) return
  try {
    await $fetch(`/api/users/${u.id}`, { method: 'DELETE' })
    users.value = users.value.filter(x => x.id !== u.id)
    Swal.fire({ icon: 'success', title: 'Usuario eliminado', timer: 1200, showConfirmButton: false })
  } catch (e) {
    Swal.fire({ icon: 'error', title: 'Error', text: e?.data?.message || 'No se pudo eliminar el usuario' })
  }
}

onMounted(fetchUsers)
</script>

<style scoped>
.usuarios-shell {
  padding: 2rem 1rem;
  max-width: 720px;
  margin: 0 auto;
}

.usuarios-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 2rem;
}
.usuarios-title {
  font-size: 1.35rem;
  font-weight: 800;
  color: var(--text-base);
  letter-spacing: -0.02em;
}
.usuarios-subtitle {
  font-size: 0.82rem;
  color: var(--text-muted);
  margin-top: 3px;
}

.usuarios-loading {
  display: flex;
  align-items: center;
  gap: 10px;
  color: var(--text-muted);
  font-size: 0.85rem;
  padding: 2rem 0;
}

.usuarios-grid {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.user-card {
  display: flex;
  align-items: center;
  gap: 14px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  padding: 1rem 1.25rem;
  transition: box-shadow 0.15s;
}
.user-card:hover {
  box-shadow: var(--shadow-sm);
}

.user-avatar-big {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: linear-gradient(135deg, #2563eb, #1d4ed8);
  color: #fff;
  font-size: 0.9rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  letter-spacing: 0.02em;
}

.user-info {
  flex: 1;
  min-width: 0;
}
.user-name {
  font-size: 0.9rem;
  font-weight: 700;
  color: var(--text-base);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.user-email {
  font-size: 0.78rem;
  color: var(--text-muted);
  margin-top: 1px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.user-meta {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 6px;
}

.role-badge {
  font-size: 0.7rem;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 99px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
.role-admin {
  background: #fef3c7;
  color: #92400e;
  border: 1px solid #fde68a;
}
.role-doctor {
  background: #eff6ff;
  color: #1d4ed8;
  border: 1px solid #bfdbfe;
}

.user-date {
  font-size: 0.72rem;
  color: var(--text-subtle);
}

.user-actions {
  display: flex;
  gap: 6px;
  flex-shrink: 0;
}

.btn-icon {
  width: 32px;
  height: 32px;
  border-radius: var(--radius-xs);
  background: none;
  border: 1.5px solid var(--border);
  color: var(--text-muted);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s;
}
.btn-icon:hover {
  background: var(--primary-light);
  color: var(--primary);
  border-color: var(--primary);
}
.btn-icon-danger:hover {
  background: rgba(220,38,38,0.08);
  color: var(--error);
  border-color: rgba(220,38,38,0.4);
}
.btn-icon:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.usuarios-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 4rem 0;
  color: var(--text-subtle);
  font-size: 0.9rem;
}
.empty-icon {
  color: var(--text-subtle);
  opacity: 0.5;
}

/* Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.5);
  backdrop-filter: blur(5px);
  z-index: 50;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
}
.modal-box {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-xl);
  padding: 1.75rem;
  width: 100%;
  max-width: 420px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
}
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}
.modal-header h3 {
  font-size: 1rem;
  font-weight: 800;
  color: var(--text-base);
}
.modal-close {
  width: 30px;
  height: 30px;
  border-radius: var(--radius-xs);
  background: var(--surface-3);
  border: 1px solid var(--border);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-muted);
  transition: background 0.15s;
}
.modal-close:hover {
  background: rgba(220,38,38,0.08);
  color: var(--error);
}

.modal-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.field { display: flex; flex-direction: column; gap: 6px; }
.field-label {
  font-size: 0.82rem;
  font-weight: 700;
  color: var(--text-muted);
}
.field-required { color: var(--error); }
.field-optional { font-weight: 400; color: var(--text-subtle); }

.field-input {
  padding: 0.6rem 0.85rem;
  border: 1.5px solid var(--border);
  border-radius: 10px;
  font-size: 0.875rem;
  color: var(--text-base);
  background: var(--surface-3);
  outline: none;
  width: 100%;
  transition: border-color 0.15s, background 0.15s;
}
.field-input:focus {
  border-color: var(--primary);
  background: var(--surface);
  box-shadow: 0 0 0 3px var(--primary-ring);
}

.password-wrap {
  position: relative;
}
.pwd-toggle {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  cursor: pointer;
  color: var(--text-muted);
  display: flex;
  align-items: center;
  padding: 0;
}
.pwd-toggle:hover { color: var(--primary); }

.form-error {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #fff5f5;
  border: 1px solid rgba(220,38,38,0.25);
  color: var(--error);
  border-radius: 8px;
  padding: 0.6rem 0.85rem;
  font-size: 0.8rem;
  font-weight: 600;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding-top: 0.5rem;
}
</style>
