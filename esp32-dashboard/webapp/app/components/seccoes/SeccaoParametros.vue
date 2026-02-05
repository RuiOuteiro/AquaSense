<!--
  Componente: SeccaoParametros
  Descrição: Secção que agrupa os cartões de sensores
  
  @ficheiro components/seccoes/SeccaoParametros.vue
  @autor AquaSense Team
-->
<template>
  <section class="parameters-section">
    <h2 class="section-title">
      <span class="material-icons-outlined">analytics</span>
      Parâmetros
    </h2>
    
    <div class="sensors-grid">
      <CartaoSensor
        tipo="temperatura"
        :valor="temperaturaAgua"
        :limite-temp-alto="limiteTempAlto"
        :limite-temp-baixo="limiteTempBaixo"
      />
      
      <CartaoSensor
        tipo="ph"
        :valor="ph"
        :tensao="tensaoPH"
      />
      
      <CartaoSensor
        tipo="turbidez"
        :valor="turbidez"
        :tensao="tensaoTurbidez"
      />
      
      <CartaoSensor
        tipo="ambiente"
        :valor="temperaturaAmbiente"
      />
      
      <CartaoSensor
        tipo="humidade"
        :valor="humidade"
      />
    </div>
  </section>
</template>

<script setup lang="ts">
import CartaoSensor from '~/components/cartoes/CartaoSensor.vue'

/**
 * Props do componente
 */
defineProps<{
  temperaturaAgua: number | null
  temperaturaAmbiente: number | null
  ph: number | null
  tensaoPH?: number | null
  turbidez: number | null
  tensaoTurbidez?: number | null
  humidade: number | null
  limiteTempAlto: number
  limiteTempBaixo: number
}>()
</script>

<style scoped>
/* Estilos herdados do dashboard.css */
</style>
