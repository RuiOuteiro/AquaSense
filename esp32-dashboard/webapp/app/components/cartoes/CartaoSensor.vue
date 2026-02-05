<!--
  Componente: CartaoSensor
  Descrição: Cartão reutilizável para exibição de valores de sensores
  
  @ficheiro components/cartoes/CartaoSensor.vue
  @autor AquaSense Team
-->
<template>
  <div class="sensor-card">
    <div class="sensor-header">
      <div class="sensor-icon" :class="tipo">
        <span class="material-icons-outlined">{{ icone }}</span>
      </div>
      <div class="sensor-info">
        <h3>{{ titulo }}</h3>
        <span>{{ subtitulo }}</span>
      </div>
    </div>
    <div class="sensor-value">
      <span class="value" :class="classeValor">{{ valorNumerico }}</span>
      <span class="unit">{{ unidade }}</span>
    </div>
    <div class="sensor-footer" v-if="tipo === 'temperatura'">
      <div class="threshold">
        <span class="material-icons-outlined">arrow_upward</span>
        Liga: {{ limiteTempAlto }}°C
      </div>
      <div class="threshold">
        <span class="material-icons-outlined">arrow_downward</span>
        Desliga: {{ limiteTempBaixo }}°C
      </div>
    </div>
    <div class="ph-scale" v-if="tipo === 'ph'">
      <div class="scale-bar"></div>
      <div class="scale-labels">
        <span>Ácido</span>
        <span>Neutro</span>
        <span>Alcalino</span>
      </div>
    </div>
    <div class="turbidity-scale" v-if="tipo === 'turbidez'">
      <div class="scale-bar turbidity-bar"></div>
      <div class="scale-labels">
        <span>Limpa</span>
        <span>Turva</span>
      </div>
    </div>
    <div class="sensor-voltage" v-if="tensao != null">
      <span class="material-icons-outlined">electric_bolt</span>
      {{ tensao?.toFixed(tipo === 'ph' ? 3 : 2) }}V
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { 
  obterClasseTemperatura, 
  obterClassePH, 
  obterClasseTurbidez 
} from '~/utils/conversores'

/**
 * Props do componente
 */
const props = defineProps<{
  /** Tipo de sensor */
  tipo: 'temperatura' | 'ph' | 'turbidez' | 'humidade' | 'ambiente'
  /** Valor actual */
  valor: number | null
  /** Tensão do sensor (opcional) */
  tensao?: number | null
  /** Limites para temperatura */
  limiteTempAlto?: number
  limiteTempBaixo?: number
}>()

/**
 * Ícone baseado no tipo
 */
const icone = computed(() => {
  const icones: Record<string, string> = {
    temperatura: 'device_thermostat',
    ph: 'science',
    turbidez: 'blur_on',
    humidade: 'water_drop',
    ambiente: 'thermostat_auto'
  }
  return icones[props.tipo] || 'sensors'
})

/**
 * Título baseado no tipo
 */
const titulo = computed(() => {
  const titulos: Record<string, string> = {
    temperatura: 'Temperatura',
    ph: 'pH',
    turbidez: 'Turbidez',
    humidade: 'Humidade Ambiente',
    ambiente: 'Temperatura Ambiente'
  }
  return titulos[props.tipo] || 'Sensor'
})

/**
 * Subtítulo baseado no tipo
 */
const subtitulo = computed(() => {
  const subtitulos: Record<string, string> = {
    temperatura: 'Água do Aquário',
    ph: 'Acidez da Água',
    turbidez: 'Claridade da Água',
    humidade: '',
    ambiente: ''
  }
  return subtitulos[props.tipo] || ''
})

/**
 * Valor numérico formatado
 */
const valorNumerico = computed(() => {
  if (props.valor === null) return '--'
  
  switch (props.tipo) {
    case 'temperatura':
    case 'ambiente':
      return props.valor.toFixed(1)
    case 'ph':
      return props.valor.toFixed(2)
    case 'turbidez':
    case 'humidade':
      return props.valor.toFixed(0)
    default:
      return `${props.valor}`
  }
})

/**
 * Unidade de medida
 */
const unidade = computed(() => {
  const unidades: Record<string, string> = {
    temperatura: '°C',
    ph: '',
    turbidez: '%',
    humidade: '%',
    ambiente: '°C'
  }
  return unidades[props.tipo] || ''
})

/**
 * Classe CSS baseada no valor
 */
const classeValor = computed(() => {
  if (props.valor === null) return ''
  
  switch (props.tipo) {
    case 'temperatura':
    case 'ambiente':
      return obterClasseTemperatura(
        props.valor,
        props.limiteTempAlto ?? 28,
        props.limiteTempBaixo ?? 22
      )
    case 'ph':
      return obterClassePH(props.valor)
    case 'turbidez':
      return obterClasseTurbidez(props.valor)
    default:
      return ''
  }
})
</script>

<style scoped>
/* Estilos herdados do dashboard.css */
.sensor-icon.temperatura { background: linear-gradient(135deg, #f97316, #ef4444); }
.sensor-icon.ph { background: linear-gradient(135deg, #8b5cf6, #a855f7); }
.sensor-icon.turbidez { background: linear-gradient(135deg, #14b8a6, #06b6d4); }
.sensor-icon.humidade { background: linear-gradient(135deg, #3b82f6, #6366f1); }
.sensor-icon.ambiente { background: linear-gradient(135deg, #06b6d4, #0891b2); }
</style>
