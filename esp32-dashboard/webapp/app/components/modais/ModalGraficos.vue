<!--
  Componente: ModalGraficos
  Descrição: Modal com gráficos de histórico dos sensores
  
  @ficheiro components/modais/ModalGraficos.vue
  @autor AquaSense Team
-->
<template>
  <ModalBase
    :visivel="visivel"
    titulo="Gráficos"
    icone="bar_chart"
    classe-extra="charts-modal"
    @fechar="$emit('fechar')"
  >
    <!-- Seletor de Período -->
    <div class="periodo-selector">
      <button
        v-for="p in periodos"
        :key="p.valor"
        class="periodo-botao"
        :class="{ activo: periodo === p.valor }"
        @click="$emit('alterarPeriodo', p.valor)"
      >
        {{ p.etiqueta }}
      </button>
    </div>
    
    <!-- Carregamento -->
    <div v-if="aCarregar" class="loading-state">
      <span class="material-icons-outlined loading-spinner">autorenew</span>
      <span>A carregar dados...</span>
    </div>
    
    <!-- Gráficos -->
    <div v-else class="graficos-grelha">
      <!-- Temperatura -->
      <div class="grafico-cartao">
        <h3 class="chart-title"><span class="material-icons-outlined">device_thermostat</span> Temperatura</h3>
        <ClientOnly>
          <apexchart
            type="area"
            height="200"
            :options="opcoesTemperatura"
            :series="seriesTemperatura"
          />
        </ClientOnly>
      </div>
      
      <!-- pH -->
      <div class="grafico-cartao">
        <h3 class="chart-title"><span class="material-icons-outlined">science</span> pH</h3>
        <ClientOnly>
          <apexchart
            type="line"
            height="200"
            :options="opcoesPH"
            :series="seriesPH"
          />
        </ClientOnly>
      </div>
      
      <!-- Turbidez -->
      <div class="grafico-cartao">
        <h3 class="chart-title"><span class="material-icons-outlined">blur_on</span> Turbidez</h3>
        <ClientOnly>
          <apexchart
            type="area"
            height="200"
            :options="opcoesTurbidez"
            :series="seriesTurbidez"
          />
        </ClientOnly>
      </div>
      
      <!-- Luz Branca -->
      <div class="grafico-cartao">
        <h3 class="chart-title"><span class="material-icons-outlined">wb_sunny</span> Luz Branca (horas/dia)</h3>
        <ClientOnly>
          <apexchart
            type="bar"
            height="200"
            :options="opcoesLuzBranca"
            :series="seriesLuzBranca"
          />
        </ClientOnly>
      </div>
      
      <!-- Luz Noturna -->
      <div class="grafico-cartao">
        <h3 class="chart-title"><span class="material-icons-outlined">nightlight</span> Luz Noturna (horas/dia)</h3>
        <ClientOnly>
          <apexchart
            type="bar"
            height="200"
            :options="opcoesLuzNoturna"
            :series="seriesLuzNoturna"
          />
        </ClientOnly>
      </div>
    </div>
  </ModalBase>
</template>

<script setup lang="ts">
import ModalBase from './ModalBase.vue'
import { PERIODOS_GRAFICO } from '~/utils/constantes'

/**
 * Props do componente
 */
defineProps<{
  visivel: boolean
  periodo: number
  aCarregar: boolean
  opcoesTemperatura: any
  seriesTemperatura: any
  opcoesPH: any
  seriesPH: any
  opcoesTurbidez: any
  seriesTurbidez: any
  opcoesLuzBranca: any
  seriesLuzBranca: any
  opcoesLuzNoturna: any
  seriesLuzNoturna: any
}>()

/**
 * Eventos emitidos
 */
defineEmits<{
  'fechar': []
  'alterarPeriodo': [horas: number]
}>()

const periodos = PERIODOS_GRAFICO
</script>

<style scoped>
.periodo-selector {
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.periodo-botao {
  padding: 8px 16px;
  background: rgba(51, 65, 85, 0.5);
  border: none;
  border-radius: 8px;
  color: #94a3b8;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.15s ease;
}

.periodo-botao:hover {
  background: rgba(71, 85, 105, 0.6);
}

.periodo-botao.activo {
  background: linear-gradient(135deg, #3b82f6, #6366f1);
  color: white;
}

.carregamento {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 40px;
  color: #94a3b8;
}

.carregamento-spinner {
  font-size: 1.5rem;
  animation: rodar 1s linear infinite;
}

.graficos-grelha {
  display: grid;
  gap: 16px;
}

.grafico-cartao {
  background: rgba(30, 41, 59, 0.5);
  border-radius: 12px;
  padding: 16px;
}

.grafico-titulo {
  font-size: 0.875rem;
  font-weight: 600;
  color: #e2e8f0;
  margin-bottom: 12px;
}

@keyframes rodar {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>
