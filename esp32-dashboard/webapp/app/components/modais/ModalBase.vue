<!--
  Componente: ModalBase
  Descrição: Estrutura base reutilizável para modais
  
  @ficheiro components/modais/ModalBase.vue
  @autor AquaSense Team
-->
<template>
  <Teleport to="body">
    <Transition name="modal-fade">
      <div v-if="visivel" class="modal-overlay" @click.self="fechar">
        <div class="modal-container" :class="classeExtra">
          <!-- Cabeçalho -->
          <div class="modal-header">
            <h2>
              <span v-if="icone" class="material-icons-outlined">{{ icone }}</span>
              {{ titulo }}
            </h2>
            <button class="close-btn" @click="fechar" title="Fechar">
              <span class="material-icons-outlined">close</span>
            </button>
          </div>
          
          <!-- Corpo -->
          <div class="modal-content custom-scroll">
            <slot />
          </div>
          
          <!-- Rodapé (opcional) -->
          <div v-if="$slots.rodape" class="modal-footer">
            <slot name="rodape" />
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
/**
 * Props do componente
 */
const props = defineProps<{
  /** Modal está visível */
  visivel: boolean
  /** Título do modal */
  titulo: string
  /** Ícone (Material Icon name) */
  icone?: string
  /** Classe CSS extra para o container */
  classeExtra?: string
}>()

/**
 * Classe extra computed (para compatibilidade)
 */
const classeExtra = computed(() => props.classeExtra || '')

/**
 * Eventos emitidos
 */
const emit = defineEmits<{
  'fechar': []
}>()

/**
 * Fecha o modal
 */
function fechar() {
  emit('fechar')
}

/**
 * Fechar com tecla Escape
 */
onMounted(() => {
  const handleEscape = (e: KeyboardEvent) => {
    if (e.key === 'Escape' && props.visivel) {
      fechar()
    }
  }
  document.addEventListener('keydown', handleEscape)
  onUnmounted(() => {
    document.removeEventListener('keydown', handleEscape)
  })
})

/**
 * Controlar scroll do body
 */
watch(() => props.visivel, (visivel) => {
  document.body.style.overflow = visivel ? 'hidden' : ''
})
</script>

<!-- Estilos em dashboard.css -->
