<template>
  <Teleport to="body">
    <Transition name="alert-slide">
      <div v-if="visible" class="alert-container" :class="alertType">
        <div class="alert-content">
          <div class="alert-icon">
            <span class="material-icons-outlined">{{ icon }}</span>
          </div>
          <div class="alert-body">
            <h4 class="alert-title">{{ title }}</h4>
            <p class="alert-message">{{ message }}</p>
          </div>
          <button class="alert-close" @click="close">
            <span class="material-icons-outlined">close</span>
          </button>
        </div>
        <div class="alert-progress" :style="{ animationDuration: `${duration}ms` }"></div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
interface Props {
  visible: boolean
  type?: 'warning' | 'danger' | 'info' | 'success'
  title: string
  message: string
  duration?: number
  autoClose?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  type: 'warning',
  duration: 5000,
  autoClose: true
})

const emit = defineEmits<{
  (e: 'close'): void
}>()

const alertType = computed(() => `alert-${props.type}`)

const icon = computed(() => {
  switch (props.type) {
    case 'danger': return 'error'
    case 'warning': return 'warning'
    case 'success': return 'check_circle'
    case 'info': return 'info'
    default: return 'warning'
  }
})

let timer: ReturnType<typeof setTimeout> | null = null

watch(() => props.visible, (val) => {
  if (val && props.autoClose) {
    timer = setTimeout(() => emit('close'), props.duration)
  } else if (timer) {
    clearTimeout(timer)
  }
})

function close() {
  if (timer) clearTimeout(timer)
  emit('close')
}

onUnmounted(() => {
  if (timer) clearTimeout(timer)
})
</script>

<style scoped>
.alert-container {
  position: fixed;
  top: 20px;
  right: 20px;
  min-width: 320px;
  max-width: 420px;
  background: rgba(30, 41, 59, 0.95);
  backdrop-filter: blur(12px);
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.4);
  z-index: 9999;
  overflow: hidden;
  border: 1px solid rgba(148, 163, 184, 0.1);
  font-family: 'Inter', sans-serif;
}

.alert-content {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px;
}

.alert-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.alert-icon .material-icons-outlined {
  font-size: 24px;
}

.alert-warning .alert-icon {
  background: rgba(251, 191, 36, 0.15);
  color: #fbbf24;
}

.alert-danger .alert-icon {
  background: rgba(239, 68, 68, 0.15);
  color: #ef4444;
}

.alert-success .alert-icon {
  background: rgba(16, 185, 129, 0.15);
  color: #10b981;
}

.alert-info .alert-icon {
  background: rgba(6, 182, 212, 0.15);
  color: #06b6d4;
}

.alert-body {
  flex: 1;
  min-width: 0;
}

.alert-title {
  color: #f1f5f9;
  font-size: 14px;
  font-weight: 600;
  margin: 0 0 4px;
}

.alert-message {
  color: #94a3b8;
  font-size: 13px;
  margin: 0;
  line-height: 1.4;
}

.alert-close {
  background: none;
  border: none;
  padding: 4px;
  cursor: pointer;
  color: #64748b;
  transition: color 0.2s;
  flex-shrink: 0;
}

.alert-close:hover {
  color: #f1f5f9;
}

.alert-close .material-icons-outlined {
  font-size: 20px;
}

.alert-progress {
  height: 3px;
  background: currentColor;
  opacity: 0.3;
  animation: progress linear forwards;
}

.alert-warning .alert-progress { color: #fbbf24; }
.alert-danger .alert-progress { color: #ef4444; }
.alert-success .alert-progress { color: #10b981; }
.alert-info .alert-progress { color: #06b6d4; }

@keyframes progress {
  from { width: 100%; }
  to { width: 0%; }
}

.alert-slide-enter-active {
  animation: slideIn 0.3s ease-out;
}

.alert-slide-leave-active {
  animation: slideOut 0.2s ease-in;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateX(100px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@keyframes slideOut {
  from {
    opacity: 1;
    transform: translateX(0);
  }
  to {
    opacity: 0;
    transform: translateX(100px);
  }
}

@media (max-width: 480px) {
  .alert-container {
    left: 10px;
    right: 10px;
    min-width: auto;
    max-width: none;
  }
}
</style>
