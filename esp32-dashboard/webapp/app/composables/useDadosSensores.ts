/**
 * Composable para gestão dos dados dos sensores
 * 
 * Obtém e processa leituras do ESP32, mantendo estado
 * actualizado de todos os sensores e dispositivos.
 * 
 * @ficheiro composables/useDadosSensores.ts
 * @autor AquaSense Team
 */

import type { LeituraSensor } from '~/types'
import { TIMEOUT_CONEXAO } from '~/utils/constantes'
import { useConsola } from './useConsola'

// Estado global partilhado
const leituras = ref<LeituraSensor[]>([])
const ultimaActualizacao = ref('')

// Temperatura
const temperaturaAgua = ref<number | null>(null)
const temperaturaAguaTempo = ref<string | null>(null)
const temperaturaAmbiente = ref<number | null>(null)

// Qualidade da água
const ph = ref<number | null>(null)
const phTempo = ref<string | null>(null)
const tensaoPH = ref<number | null>(null)
const turbidez = ref<number | null>(null)
const tensaoTurbidez = ref<number | null>(null)

// Ambiente
const humidade = ref<number | null>(null)

// Estado dos dispositivos
const ventoinhaLigada = ref(false)
const ventoinhaTempoEstado = ref<string | null>(null)
const luzBrancaLigada = ref(false)
const luzBrancaTempoLigada = ref<number | null>(null)
const luzNoturnaLigada = ref(false)
const brilhoLuz = ref(0)

// Estado de ligação
const ligado = ref(false)
const ultimoContactoMs = ref<number | null>(null)

export function useDadosSensores() {
  const { adicionarRegisto } = useConsola()

  /**
   * Obtém dados dos sensores da API
   */
  async function obterDados(): Promise<void> {
    try {
      const res = await $fetch<{ success: boolean; data: LeituraSensor[] }>(
        '/api/sensor?limit=100'
      )
      
      if (!res.success || !res.data.length) return
      
      adicionarRegisto(`Recebidos ${res.data.length} registos de sensores`, 'success')
      
      // Processar leituras
      leituras.value = res.data.map(l => ({
        ...l,
        value: parseFloat(String(l.value))
      }))
      
      // Verificar ligação
      const ultimaLeitura = res.data[0]
      if (ultimaLeitura) {
        const tempoUltima = new Date(ultimaLeitura.created_at).getTime()
        ultimoContactoMs.value = Number.isFinite(tempoUltima) ? tempoUltima : Date.now()
        ligado.value = Date.now() - (ultimoContactoMs.value ?? Date.now()) < TIMEOUT_CONEXAO
      } else {
        ligado.value = Date.now() - (ultimoContactoMs.value ?? 0) < TIMEOUT_CONEXAO
      }
      
      // Extrair valores por tipo
      extrairValoresPorTipo(res.data)
      
      // Actualizar timestamp
      ultimaActualizacao.value = new Date().toLocaleTimeString('pt-PT')
      
    } catch (erro) {
      console.error('[Sensores] Erro ao obter dados:', erro)
      adicionarRegisto(`Erro ao obter dados: ${erro}`, 'error')
      ligado.value = Date.now() - (ultimoContactoMs.value ?? 0) < TIMEOUT_CONEXAO
    }
  }

  /**
   * Extrai valores de cada tipo de sensor
   */
  function extrairValoresPorTipo(dados: LeituraSensor[]): void {
    // Temperatura água
    const temp = dados.find(d => d.sensor_type === 'temperature')
    if (temp) {
      temperaturaAgua.value = parseFloat(String(temp.value))
      temperaturaAguaTempo.value = temp.created_at
    }
    
    // pH
    const phLeitura = dados.find(d => d.sensor_type === 'pH')
    if (phLeitura) {
      ph.value = parseFloat(String(phLeitura.value))
      phTempo.value = phLeitura.created_at
    }
    
    const phV = dados.find(d => d.sensor_type === 'pH_voltage')
    if (phV) tensaoPH.value = parseFloat(String(phV.value))
    
    // Turbidez
    const turb = dados.find(d => d.sensor_type === 'turbidity')
    if (turb) turbidez.value = parseFloat(String(turb.value))
    
    const turbV = dados.find(d => d.sensor_type === 'turbidity_voltage')
    if (turbV) tensaoTurbidez.value = parseFloat(String(turbV.value))
    
    // Ambiente
    const ambient = dados.find(d => d.sensor_type === 'ambient_temp')
    if (ambient) temperaturaAmbiente.value = parseFloat(String(ambient.value))
    
    const hum = dados.find(d => d.sensor_type === 'humidity')
    if (hum) humidade.value = parseFloat(String(hum.value))
    
    // Ventoinha
    const fan = dados.find(d => d.sensor_type === 'fan_status')
    if (fan) {
      ventoinhaLigada.value = parseFloat(String(fan.value)) >= 1
      ventoinhaTempoEstado.value = fan.created_at
    }
    
    // Luz branca
    const luz = dados.find(d => d.sensor_type === 'light_status')
    if (luz) {
      const estaLigada = parseFloat(String(luz.value)) >= 1
      const estavaDeligada = !luzBrancaLigada.value
      luzBrancaLigada.value = estaLigada
      
      if (estaLigada && estavaDeligada) {
        luzBrancaTempoLigada.value = Date.now()
      } else if (!estaLigada) {
        luzBrancaTempoLigada.value = null
      }
    }
    
    // Luz noturna
    const luzN = dados.find(d => d.sensor_type === 'night_light_status')
    if (luzN) luzNoturnaLigada.value = parseFloat(String(luzN.value)) >= 1
    
    // Brilho
    const brilho = dados.find(d => d.sensor_type === 'light_brightness')
    if (brilho) brilhoLuz.value = parseFloat(String(brilho.value))
  }

  return {
    // Leituras
    leituras: readonly(leituras),
    ultimaActualizacao: readonly(ultimaActualizacao),
    
    // Sensores
    temperaturaAgua: readonly(temperaturaAgua),
    temperaturaAguaTempo: readonly(temperaturaAguaTempo),
    temperaturaAmbiente: readonly(temperaturaAmbiente),
    ph: readonly(ph),
    phTempo: readonly(phTempo),
    tensaoPH: readonly(tensaoPH),
    turbidez: readonly(turbidez),
    tensaoTurbidez: readonly(tensaoTurbidez),
    humidade: readonly(humidade),
    
    // Dispositivos
    ventoinhaLigada: readonly(ventoinhaLigada),
    ventoinhaTempoEstado: readonly(ventoinhaTempoEstado),
    luzBrancaLigada,
    luzBrancaTempoLigada,
    luzNoturnaLigada,
    brilhoLuz: readonly(brilhoLuz),
    
    // Ligação
    ligado: readonly(ligado),
    
    // Acções
    obterDados
  }
}
