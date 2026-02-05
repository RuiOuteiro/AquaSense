<!--
  Componente: CampoHora
  Descrição: Input para selecção de hora
  
  @ficheiro components/primitivos/CampoHora.vue
  @autor AquaSense Team
-->
<template>
  <div class="campo-hora-contentor">
    <label v-if="etiqueta" class="campo-hora-etiqueta">
      {{ etiqueta }}
    </label>
    <input
      type="time"
      class="campo-hora"
      :value="valorFormatado"
      :disabled="desactivado"
      @change="aoAlterar"
    />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

/**
 * Props do componente
 */
const props = defineProps<{
  /** Hora (0-23) */
  hora: number
  /** Minuto (0-59) */
  minuto: number
  /** Etiqueta do campo */
  etiqueta?: string
  /** Estado desactivado */
  desactivado?: boolean
}>()

/**
 * Eventos emitidos
 */
const emit = defineEmits<{
  'update': [hora: number, minuto: number]
}>()

/**
 * Valor formatado para o input
 */
const valorFormatado = computed(() => {
  const h = String(props.hora).padStart(2, '0')
  const m = String(props.minuto).padStart(2, '0')
  return `${h}:${m}`
})

/**
 * Ao alterar a hora
 */
function aoAlterar(evento: Event) {
  const input = evento.target as HTMLInputElement
  const [h, m] = input.value.split(':').map(Number)
  emit('update', h ?? 0, m ?? 0)
}
</script>

<style scoped>
.campo-hora-contentor {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.campo-hora-etiqueta {
  font-size: 0.75rem;
  color: var(--texto-secundario, #94a3b8);
}

.campo-hora {
  padding: 8px 12px;
  background: var(--fundo-input, rgba(30, 41, 59, 0.8));
  border: 1px solid var(--borda-sutil, rgba(148, 163, 184, 0.1));
  border-radius: 8px;
  color: var(--texto-principal, #e2e8f0);
  font-family: inherit;
  font-size: 0.875rem;
  transition: all 0.15s ease;
}

.campo-hora:focus {
  outline: none;
  border-color: var(--cor-primaria, #3b82f6);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2);
}

.campo-hora:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.campo-hora::-webkit-calendar-picker-indicator {
  filter: invert(1);
  cursor: pointer;
}
</style>
