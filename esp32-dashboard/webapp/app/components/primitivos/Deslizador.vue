<!--
  Componente: Deslizador
  Descrição: Slider para selecção de valores numéricos
  
  @ficheiro components/primitivos/Deslizador.vue
  @autor AquaSense Team
-->
<template>
  <div class="deslizador-contentor">
    <input
      type="range"
      class="deslizador"
      :value="modelValue"
      :min="min"
      :max="max"
      :step="passo"
      :disabled="desactivado"
      @input="aoAlterar"
      @change="aoFinalizar"
    />
    <div v-if="mostrarValor" class="deslizador-valor">
      {{ modelValue }}{{ sufixo }}
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * Props do componente
 */
const props = withDefaults(defineProps<{
  /** Valor actual (v-model) */
  modelValue: number
  /** Valor mínimo */
  min?: number
  /** Valor máximo */
  max?: number
  /** Incremento */
  passo?: number
  /** Sufixo para o valor (ex: %, °C) */
  sufixo?: string
  /** Mostrar valor actual */
  mostrarValor?: boolean
  /** Estado desactivado */
  desactivado?: boolean
}>(), {
  min: 0,
  max: 100,
  passo: 1,
  sufixo: '',
  mostrarValor: true,
  desactivado: false
})

/**
 * Eventos emitidos
 */
const emit = defineEmits<{
  'update:modelValue': [value: number]
  'change': [value: number]
}>()

/**
 * Ao alterar o valor (durante arrasto)
 */
function aoAlterar(evento: Event) {
  const input = evento.target as HTMLInputElement
  emit('update:modelValue', Number(input.value))
}

/**
 * Ao finalizar alteração (soltar)
 */
function aoFinalizar(evento: Event) {
  const input = evento.target as HTMLInputElement
  emit('change', Number(input.value))
}
</script>

<style scoped>
.deslizador-contentor {
  display: flex;
  flex-direction: column;
  gap: 8px;
  width: 100%;
}

.deslizador {
  -webkit-appearance: none;
  appearance: none;
  width: 100%;
  height: 6px;
  background: var(--fundo-hover, rgba(51, 65, 85, 0.5));
  border-radius: 3px;
  cursor: pointer;
}

.deslizador:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.deslizador::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 18px;
  height: 18px;
  background: var(--cor-primaria, #3b82f6);
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.15s ease;
}

.deslizador::-webkit-slider-thumb:hover {
  transform: scale(1.1);
  box-shadow: 0 0 10px var(--cor-primaria, #3b82f6);
}

.deslizador::-moz-range-thumb {
  width: 18px;
  height: 18px;
  background: var(--cor-primaria, #3b82f6);
  border-radius: 50%;
  cursor: pointer;
  border: none;
}

.deslizador-valor {
  text-align: center;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--cor-primaria-clara, #60a5fa);
}
</style>
