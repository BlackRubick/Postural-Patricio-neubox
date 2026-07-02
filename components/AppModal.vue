<template>
  <Teleport to="body">
    <Transition name="modal">
      <div
        v-if="open"
        class="fixed inset-0 z-50 flex items-end sm:items-center justify-center p-4"
        style="background:rgba(15,23,42,0.45);backdrop-filter:blur(4px)"
        @click.self="$emit('close')"
      >
        <div class="modal-box rounded-2xl shadow-2xl w-full max-w-lg flex flex-col max-h-[90vh] overflow-hidden">
          <!-- Header -->
          <div class="modal-header flex items-center justify-between px-6 py-4 flex-shrink-0">
            <h2 v-if="title" class="modal-title text-base font-bold leading-tight pr-4">{{ title }}</h2>
            <button
              class="modal-close-btn w-8 h-8 rounded-lg flex items-center justify-center transition flex-shrink-0 ml-auto"
              @click="$emit('close')"
            >
              <svg width="14" height="14" fill="none" viewBox="0 0 24 24">
                <path d="M18 6L6 18M6 6l12 12" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
              </svg>
            </button>
          </div>

          <!-- Content -->
          <div class="overflow-y-auto flex-1 px-6 py-5">
            <slot />
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
defineProps({
  open: { type: Boolean, default: false },
  title: { type: String, default: '' },
})
defineEmits(['close'])
</script>

<style scoped>
.modal-box {
  background: var(--surface);
  color: var(--text-base);
}
.modal-header {
  border-bottom: 1px solid var(--border);
}
.modal-title {
  color: var(--text-base);
}
.modal-close-btn {
  background: var(--surface-3);
  border: 1px solid var(--border);
  color: var(--text-muted);
}
.modal-close-btn:hover {
  background: var(--surface-2);
  color: var(--text-base);
}
.modal-enter-active, .modal-leave-active {
  transition: opacity 0.2s ease;
}
.modal-enter-active .modal-box, .modal-leave-active .modal-box {
  transition: transform 0.25s cubic-bezier(.4,0,.2,1), opacity 0.2s ease;
}
.modal-enter-from, .modal-leave-to {
  opacity: 0;
}
</style>
