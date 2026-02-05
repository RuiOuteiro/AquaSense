<!--
  Componente: PainelConsola
  Descrição: Painel flutuante com logs do sistema e ESP32
  
  @ficheiro components/layout/PainelConsola.vue
  @autor AquaSense Team
-->
<template>
  <div v-if="visivel" class="console-panel">
    <div class="console-header">
      <h3>
        <span class="material-icons-outlined">terminal</span>
        Consola ESP32
      </h3>
      <div class="console-actions">
        <button @click="$emit('limpar')" title="Limpar">
          <span class="material-icons-outlined">delete</span>
        </button>
        <button @click="$emit('fechar')" title="Fechar">
          <span class="material-icons-outlined">close</span>
        </button>
      </div>
    </div>
    
    <div ref="corpoConsola" class="console-body">
      <div 
        v-for="(registo, index) in registos" 
        :key="index"
        class="console-line"
        :class="registo.tipo"
      >
        <span class="log-time">{{ registo.hora }}</span>
        <span class="log-msg">{{ registo.mensagem }}</span>
      </div>
      
      <div v-if="registos.length === 0" class="console-empty">
        A aguardar mensagens do ESP32...
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { RegistoConsola } from '~/types'

/**
 * Props do componente
 */
defineProps<{
  /** Painel está visível */
  visivel: boolean
  /** Lista de registos */
  registos: RegistoConsola[]
}>()

/**
 * Eventos emitidos
 */
defineEmits<{
  'fechar': []
  'limpar': []
}>()

/**
 * Referência ao corpo da consola para auto-scroll
 */
const corpoConsola = ref<HTMLElement | null>(null)

/**
 * Expor referência para uso externo
 */
defineExpose({
  corpoConsola
})
</script>

<style scoped>
/* Estilos herdados do dashboard.css - classes originais */
</style>
