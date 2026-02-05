/**
 * Composable para gestão dos gráficos
 * 
 * Gere dados e opções dos gráficos ApexCharts,
 * incluindo períodos e estatísticas de luz.
 * 
 * @ficheiro composables/useGraficos.ts
 * @autor AquaSense Team
 */

import type { DadosGrafico, EstatisticasLuz } from '~/types'
import { formatarDataCurta, arredondarParaGrafico } from '~/utils/formatadores'

// Estado global partilhado
const periodo = ref(24)
const dadosGraficos = ref<Record<string, DadosGrafico[]>>({})
const estatisticasLuz = ref<EstatisticasLuz | null>(null)
const aCarregar = ref(false)

export function useGraficos() {
  /**
   * Obtém dados para os gráficos
   */
  async function obterDadosGraficos(): Promise<void> {
    aCarregar.value = true
    try {
      const [sensorRes, lightRes] = await Promise.all([
        $fetch<{ success: boolean; data: Record<string, DadosGrafico[]> }>(
          `/api/sensors/history?hours=${periodo.value}`
        ),
        $fetch<{ success: boolean; data: EstatisticasLuz }>(
          `/api/sensors/light-stats?days=${Math.ceil(periodo.value / 24) || 7}`
        )
      ])
      
      if (sensorRes.success) {
        dadosGraficos.value = sensorRes.data
      }
      if (lightRes.success) {
        estatisticasLuz.value = lightRes.data
      }
    } catch (erro) {
      console.error('[Gráficos] Erro ao obter dados:', erro)
    } finally {
      aCarregar.value = false
    }
  }

  /**
   * Altera período dos gráficos
   */
  async function alterarPeriodo(horas: number): Promise<void> {
    periodo.value = horas
    await obterDadosGraficos()
  }

  // ========== OPÇÕES BASE DOS GRÁFICOS ==========
  const opcoesBase = {
    chart: {
      toolbar: { show: false },
      zoom: { enabled: false },
      background: 'transparent',
      fontFamily: 'Inter, sans-serif'
    },
    theme: { mode: 'dark' as const },
    grid: {
      borderColor: 'rgba(255,255,255,0.1)',
      strokeDashArray: 3
    },
    xaxis: {
      type: 'datetime' as const,
      labels: {
        style: { colors: '#94a3b8', fontSize: '10px' },
        datetimeFormatter: { hour: 'HH:mm', day: 'dd MMM' }
      },
      axisBorder: { show: false },
      axisTicks: { show: false }
    },
    yaxis: {
      labels: { 
        style: { colors: '#94a3b8', fontSize: '10px' },
        formatter: (val: number) => val?.toFixed(1)
      }
    },
    tooltip: {
      theme: 'dark',
      x: { format: 'dd MMM HH:mm' },
      y: { formatter: (val: number) => val?.toFixed(1) }
    },
    stroke: { curve: 'smooth' as const, width: 2 },
    dataLabels: { enabled: false }
  }

  // ========== OPÇÕES ESPECÍFICAS ==========
  const opcoesTemperatura = computed(() => ({
    ...opcoesBase,
    colors: ['#ff6b6b'],
    fill: { 
      type: 'gradient', 
      gradient: { shadeIntensity: 1, opacityFrom: 0.4, opacityTo: 0.1 } 
    },
    yaxis: { 
      ...opcoesBase.yaxis, 
      title: { text: '°C', style: { color: '#94a3b8' } } 
    }
  }))

  const opcoesPH = computed(() => ({
    ...opcoesBase,
    colors: ['#4ecdc4'],
    yaxis: { 
      ...opcoesBase.yaxis, 
      min: 5, 
      max: 10, 
      title: { text: 'pH', style: { color: '#94a3b8' } } 
    }
  }))

  const opcoesTurbidez = computed(() => ({
    ...opcoesBase,
    colors: ['#ffe66d'],
    fill: { 
      type: 'gradient', 
      gradient: { shadeIntensity: 1, opacityFrom: 0.4, opacityTo: 0.1 } 
    },
    yaxis: { 
      ...opcoesBase.yaxis, 
      min: 0, 
      max: 100, 
      title: { text: '%', style: { color: '#94a3b8' } } 
    }
  }))

  const opcoesLuzBranca = computed(() => ({
    chart: { 
      toolbar: { show: false }, 
      background: 'transparent', 
      fontFamily: 'Inter, sans-serif' 
    },
    theme: { mode: 'dark' as const },
    colors: ['#fbbf24'],
    plotOptions: { bar: { borderRadius: 4, columnWidth: '60%' } },
    grid: { borderColor: 'rgba(255,255,255,0.1)', strokeDashArray: 3 },
    xaxis: {
      categories: (estatisticasLuz.value?.whiteLight || []).map(
        (d) => formatarDataCurta(d.date)
      ),
      labels: { style: { colors: '#94a3b8', fontSize: '10px' } },
      axisBorder: { show: false }
    },
    yaxis: { 
      max: 24, 
      labels: { style: { colors: '#94a3b8', fontSize: '10px' } }, 
      title: { text: 'Horas', style: { color: '#94a3b8' } } 
    },
    dataLabels: { enabled: false },
    tooltip: { theme: 'dark' }
  }))

  const opcoesLuzNoturna = computed(() => ({
    chart: { 
      toolbar: { show: false }, 
      background: 'transparent', 
      fontFamily: 'Inter, sans-serif' 
    },
    theme: { mode: 'dark' as const },
    colors: ['#60a5fa'],
    plotOptions: { bar: { borderRadius: 4, columnWidth: '60%' } },
    grid: { borderColor: 'rgba(255,255,255,0.1)', strokeDashArray: 3 },
    xaxis: {
      categories: (estatisticasLuz.value?.blueLight || []).map(
        (d) => formatarDataCurta(d.date)
      ),
      labels: { style: { colors: '#94a3b8', fontSize: '10px' } },
      axisBorder: { show: false }
    },
    yaxis: { 
      max: 24, 
      labels: { style: { colors: '#94a3b8', fontSize: '10px' } }, 
      title: { text: 'Horas', style: { color: '#94a3b8' } } 
    },
    dataLabels: { enabled: false },
    tooltip: { theme: 'dark' }
  }))

  // ========== SÉRIES DOS GRÁFICOS ==========
  const seriesTemperatura = computed(() => [{
    name: 'Temperatura',
    data: (dadosGraficos.value['temperature'] || []).map(d => ({
      x: new Date(d.created_at).getTime(),
      y: arredondarParaGrafico(d.value)
    }))
  }])

  const seriesPH = computed(() => [{
    name: 'pH',
    data: (dadosGraficos.value['pH'] || []).map(d => ({
      x: new Date(d.created_at).getTime(),
      y: arredondarParaGrafico(d.value)
    }))
  }])

  const seriesTurbidez = computed(() => [{
    name: 'Turbidez',
    data: (dadosGraficos.value['turbidity'] || []).map(d => ({
      x: new Date(d.created_at).getTime(),
      y: arredondarParaGrafico(d.value)
    }))
  }])

  const seriesLuzBranca = computed(() => [{
    name: 'Horas',
    data: (estatisticasLuz.value?.whiteLight || []).map(
      d => arredondarParaGrafico(d.hours)
    )
  }])

  const seriesLuzNoturna = computed(() => [{
    name: 'Horas',
    data: (estatisticasLuz.value?.blueLight || []).map(
      d => arredondarParaGrafico(d.hours)
    )
  }])

  return {
    // Estado
    periodo: readonly(periodo),
    dadosGraficos: readonly(dadosGraficos),
    estatisticasLuz: readonly(estatisticasLuz),
    aCarregar: readonly(aCarregar),
    
    // Acções
    obterDadosGraficos,
    alterarPeriodo,
    
    // Opções
    opcoesTemperatura,
    opcoesPH,
    opcoesTurbidez,
    opcoesLuzBranca,
    opcoesLuzNoturna,
    
    // Séries
    seriesTemperatura,
    seriesPH,
    seriesTurbidez,
    seriesLuzBranca,
    seriesLuzNoturna
  }
}
