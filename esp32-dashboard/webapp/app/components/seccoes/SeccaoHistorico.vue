<!--
  Componente: SeccaoHistorico
  Descrição: Secção com tabela de histórico de leituras
  
  @ficheiro components/seccoes/SeccaoHistorico.vue
  @autor AquaSense Team
-->
<template>
  <section class="history">
    <div class="history-header">
      <h2>
        <span class="material-icons-outlined">history</span>
        Histórico de Leituras
      </h2>
      <span class="badge">{{ leituras.length }} registos</span>
    </div>
    <div class="history-table" v-if="leituras.length > 0">
      <table>
        <thead>
          <tr>
            <th>Data/Hora</th>
            <th>Sensor</th>
            <th>Valor</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="leitura in leiturasVisiveis" :key="leitura.id">
            <td>{{ formatarData(leitura.created_at) }}</td>
            <td>
              <span class="sensor-badge" :class="leitura.sensor_type">
                {{ traduzirTipo(leitura.sensor_type) }}
              </span>
            </td>
            <td class="value-cell">{{ formatarValor(leitura) }}</td>
          </tr>
        </tbody>
      </table>
    </div>
    <div class="empty-state" v-else>
      <span class="material-icons-outlined">hourglass_empty</span>
      <p>A aguardar dados...</p>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { LeituraSensor } from '~/types'
import { traduzirTipoSensor } from '~/utils/conversores'
import { formatarData, formatarValorSensor } from '~/utils/formatadores'

/**
 * Props do componente
 */
const props = defineProps<{
  /** Lista de leituras */
  leituras: LeituraSensor[]
  /** Número máximo de leituras a mostrar */
  limite?: number
}>()

/**
 * Leituras limitadas
 */
const leiturasVisiveis = computed(() => {
  return props.leituras.slice(0, props.limite ?? 10)
})

/**
 * Traduz tipo de sensor
 */
function traduzirTipo(tipo: string): string {
  return traduzirTipoSensor(tipo)
}

/**
 * Formata valor da leitura
 */
function formatarValor(leitura: LeituraSensor): string {
  return formatarValorSensor(leitura)
}
</script>

<style scoped>
/* Estilos herdados do dashboard.css */
</style>
