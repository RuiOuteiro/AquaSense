<!--
  Componente: CartaoVentoinha
  Descrição: Cartão de estado e controlo da ventoinha
  
  @ficheiro components/cartoes/CartaoVentoinha.vue
  @autor AquaSense Team
-->
<template>
  <div class="fan-card" :class="{ active: ligada }">
    <div class="fan-header">
      <div class="fan-icon" :class="{ active: ligada }">
        <span class="material-icons-outlined">air</span>
      </div>
      <div class="fan-info">
        <h3>Ventoinha de Arrefecimento</h3>
        <span class="fan-mode">{{ modoManual ? 'Modo Manual' : 'Modo Automático' }}</span>
      </div>
      <div class="fan-status-indicator">
        <span class="fan-status-text" :class="{ on: ligada }">
          {{ ligada ? 'LIGADA' : 'DESLIGADA' }}
        </span>
      </div>
    </div>
    
    <div class="fan-controls">
      <div class="auto-info" v-if="!modoManual">
        <div class="temp-threshold">
          <span class="material-icons-outlined">arrow_upward</span>
          <span>Liga: <strong>{{ tempLigar }}°C</strong></span>
        </div>
        <div class="temp-threshold">
          <span class="material-icons-outlined">arrow_downward</span>
          <span>Desliga: <strong>{{ tempDesligar }}°C</strong></span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * Props do componente
 */
defineProps<{
  /** Ventoinha está ligada */
  ligada: boolean
  /** Modo manual activo */
  modoManual: boolean
  /** Temperatura para ligar (automático) */
  tempLigar: number
  /** Temperatura para desligar (automático) */
  tempDesligar: number
}>()
</script>

<style scoped>
/* Estilos herdados do dashboard.css */
</style>
