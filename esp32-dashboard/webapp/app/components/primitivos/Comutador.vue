<!--
  Componente: Comutador
  Descrição: Toggle switch para ligar/desligar opções
  
  @ficheiro components/primitivos/Comutador.vue
  @autor AquaSense Team
-->
<template>
  <label class="comutador" :class="{ desactivado }">
    <input
      type="checkbox"
      class="comutador-entrada"
      :checked="modelValue"
      :disabled="desactivado"
      @change="alternar"
    />
    <span class="comutador-fundo"></span>
    <span class="comutador-bola"></span>
  </label>
</template>

<script setup lang="ts">
/**
 * Props do componente
 */
const props = defineProps<{
  /** Valor actual (v-model) */
  modelValue: boolean
  /** Estado desactivado */
  desactivado?: boolean
}>()

/**
 * Eventos emitidos
 */
const emit = defineEmits<{
  'update:modelValue': [value: boolean]
}>()

/**
 * Alterna o estado do comutador
 */
function alternar(evento: Event) {
  const input = evento.target as HTMLInputElement
  emit('update:modelValue', input.checked)
}
</script>

<style scoped>
.comutador {
  position: relative;
  width: 48px;
  height: 26px;
  cursor: pointer;
  display: inline-block;
}

.comutador.desactivado {
  opacity: 0.5;
  cursor: not-allowed;
}

.comutador-entrada {
  opacity: 0;
  width: 0;
  height: 0;
  position: absolute;
}

.comutador-fundo {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: var(--fundo-hover, rgba(51, 65, 85, 0.5));
  border-radius: 13px;
  transition: all 0.2s ease;
}

.comutador-entrada:checked + .comutador-fundo {
  background: var(--cor-sucesso, #10b981);
}

.comutador-bola {
  position: absolute;
  width: 22px;
  height: 22px;
  left: 2px;
  top: 2px;
  background: white;
  border-radius: 50%;
  transition: all 0.2s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.comutador-entrada:checked ~ .comutador-bola {
  transform: translateX(22px);
}

.comutador:hover:not(.desactivado) .comutador-fundo {
  background: rgba(71, 85, 105, 0.6);
}

.comutador:hover:not(.desactivado) .comutador-entrada:checked + .comutador-fundo {
  background: #059669;
}
</style>
