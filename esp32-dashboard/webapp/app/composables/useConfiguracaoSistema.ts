/**
 * Composable para gestão da configuração do sistema
 * 
 * Gere todas as configurações de ventoinha, luzes e IA,
 * incluindo comunicação com a API.
 * 
 * @ficheiro composables/useConfiguracaoSistema.ts
 * @autor AquaSense Team
 */

import type { ConfiguracaoSistema, ModoLuz, ModoLuzNoturna, SugestaoIA } from '~/types'
import { useConsola } from './useConsola'
import { useDadosSensores } from './useDadosSensores'

// Estado global partilhado
const config = reactive<ConfiguracaoSistema>({
  // Ventoinha
  modoManual: false,
  ventoinhaManual: false,
  tempLigar: 14.0,
  tempDesligar: 13.0,
  
  // Luz branca
  luzManual: false,
  luzEstado: false,
  luzModo: 'horario',
  luzCicloHoras: 8,
  luzCicloInicio: null,
  luzHoraLigar: 8,
  luzMinutoLigar: 0,
  luzHoraDesligar: 20,
  luzMinutoDesligar: 0,
  luzIntensidade: 100,
  luzFadeSpeed: 10,
  
  // Luz noturna
  luzNoturnaManual: false,
  luzNoturnaEstado: false,
  luzNoturnaModo: 'horario',
  luzNoturnaCicloHoras: 8,
  luzNoturnaCicloInicio: null,
  luzNoturnaHoraLigar: 20,
  luzNoturnaMinutoLigar: 0,
  luzNoturnaHoraDesligar: 8,
  luzNoturnaMinutoDesligar: 0,
  
  // IA
  aiAjusteFotoperiodo: false,
  aiFotoperiodoSugerido: null
})

// Sugestão da IA
const sugestaoIA = ref<SugestaoIA | null>(null)

export function useConfiguracaoSistema() {
  const { adicionarRegisto } = useConsola()
  const { obterDados, luzBrancaLigada, luzNoturnaLigada } = useDadosSensores()

  /**
   * Carrega configuração do servidor
   */
  async function carregarConfiguracao(): Promise<void> {
    try {
      const res = await $fetch<{ success: boolean; data: any }>('/api/config')
      if (res.success && res.data) {
        config.modoManual = res.data.modo_manual === 1 || res.data.modo_manual === true
        config.ventoinhaManual = res.data.ventoinha_manual === 1 || res.data.ventoinha_manual === true
        config.tempLigar = parseFloat(res.data.temp_ligar)
        config.tempDesligar = parseFloat(res.data.temp_desligar)
        config.luzManual = res.data.luz_manual === 1 || res.data.luz_manual === true
        config.luzEstado = res.data.luz_estado === 1 || res.data.luz_estado === true
        config.luzHoraLigar = res.data.luz_hora_ligar ?? 8
        config.luzMinutoLigar = res.data.luz_minuto_ligar ?? 0
        config.luzHoraDesligar = res.data.luz_hora_desligar ?? 20
        config.luzMinutoDesligar = res.data.luz_minuto_desligar ?? 0
        config.luzIntensidade = res.data.luz_intensidade ?? 100
        config.luzFadeSpeed = res.data.luz_fade_speed ?? 10
        config.luzModo = res.data.luz_modo ?? 'horario'
        config.luzCicloHoras = res.data.luz_ciclo_horas ?? 8
        config.luzCicloInicio = res.data.luz_ciclo_inicio ?? null
        config.luzNoturnaManual = res.data.luz_noturna_manual === 1 || res.data.luz_noturna_manual === true
        config.luzNoturnaEstado = res.data.luz_noturna_estado === 1 || res.data.luz_noturna_estado === true
        config.luzNoturnaModo = res.data.luz_noturna_modo ?? 'horario'
        config.luzNoturnaCicloHoras = res.data.luz_noturna_ciclo_horas ?? 8
        config.luzNoturnaCicloInicio = res.data.luz_noturna_ciclo_inicio ?? null
        config.luzNoturnaHoraLigar = res.data.luz_noturna_hora_ligar ?? 20
        config.luzNoturnaMinutoLigar = res.data.luz_noturna_minuto_ligar ?? 0
        config.luzNoturnaHoraDesligar = res.data.luz_noturna_hora_desligar ?? 8
        config.luzNoturnaMinutoDesligar = res.data.luz_noturna_minuto_desligar ?? 0
        config.aiAjusteFotoperiodo = res.data.ai_ajuste_fotoperiodo === 1 || res.data.ai_ajuste_fotoperiodo === true
        config.aiFotoperiodoSugerido = res.data.ai_fotoperiodo_sugerido ?? null
      }
    } catch (erro) {
      console.error('[Config] Erro ao carregar:', erro)
    }
  }

  /**
   * Guarda configuração no servidor
   */
  async function guardarConfiguracao(): Promise<void> {
    try {
      await $fetch('/api/config', {
        method: 'POST',
        body: {
          modo_manual: config.modoManual,
          ventoinha_manual: config.ventoinhaManual,
          temp_ligar: config.tempLigar,
          temp_desligar: config.tempDesligar,
          luz_manual: config.luzManual,
          luz_estado: config.luzEstado,
          luz_hora_ligar: config.luzHoraLigar,
          luz_minuto_ligar: config.luzMinutoLigar,
          luz_hora_desligar: config.luzHoraDesligar,
          luz_minuto_desligar: config.luzMinutoDesligar,
          luz_intensidade: config.luzIntensidade,
          luz_fade_speed: config.luzFadeSpeed,
          luz_modo: config.luzModo,
          luz_ciclo_horas: config.luzCicloHoras,
          luz_ciclo_inicio: config.luzCicloInicio,
          luz_noturna_manual: config.luzNoturnaManual,
          luz_noturna_estado: config.luzNoturnaEstado,
          luz_noturna_hora_ligar: config.luzNoturnaHoraLigar,
          luz_noturna_minuto_ligar: config.luzNoturnaMinutoLigar,
          luz_noturna_hora_desligar: config.luzNoturnaHoraDesligar,
          luz_noturna_minuto_desligar: config.luzNoturnaMinutoDesligar,
          luz_noturna_modo: config.luzNoturnaModo,
          luz_noturna_ciclo_horas: config.luzNoturnaCicloHoras,
          luz_noturna_ciclo_inicio: config.luzNoturnaCicloInicio,
          ai_ajuste_fotoperiodo: config.aiAjusteFotoperiodo
        }
      })
      await obterDados()
    } catch (erro) {
      console.error('[Config] Erro ao guardar:', erro)
    }
  }

  /**
   * Guarda apenas intensidade (sem recarregar dados)
   */
  async function guardarIntensidade(): Promise<void> {
    try {
      await $fetch('/api/config', {
        method: 'POST',
        body: {
          modo_manual: config.modoManual,
          ventoinha_manual: config.ventoinhaManual,
          temp_ligar: config.tempLigar,
          temp_desligar: config.tempDesligar,
          luz_manual: config.luzManual,
          luz_estado: config.luzEstado,
          luz_hora_ligar: config.luzHoraLigar,
          luz_minuto_ligar: config.luzMinutoLigar,
          luz_hora_desligar: config.luzHoraDesligar,
          luz_minuto_desligar: config.luzMinutoDesligar,
          luz_intensidade: config.luzIntensidade,
          luz_fade_speed: config.luzFadeSpeed,
          luz_noturna_manual: config.luzNoturnaManual,
          luz_noturna_estado: config.luzNoturnaEstado,
          luz_noturna_hora_ligar: config.luzNoturnaHoraLigar,
          luz_noturna_minuto_ligar: config.luzNoturnaMinutoLigar,
          luz_noturna_hora_desligar: config.luzNoturnaHoraDesligar,
          luz_noturna_minuto_desligar: config.luzNoturnaMinutoDesligar
        }
      })
    } catch (erro) {
      console.error('[Config] Erro ao guardar intensidade:', erro)
    }
  }

  // ========== ACÇÕES VENTOINHA ==========
  async function definirModoManualVentoinha(activo: boolean): Promise<void> {
    config.modoManual = activo
    await guardarConfiguracao()
  }

  async function definirEstadoVentoinha(ligada: boolean): Promise<void> {
    config.ventoinhaManual = ligada
    await guardarConfiguracao()
  }

  // ========== ACÇÕES LUZ BRANCA ==========
  async function definirModoLuz(modo: ModoLuz): Promise<void> {
    config.luzModo = modo
    config.luzManual = modo === 'manual'
    
    if (modo === 'ciclo') {
      config.luzCicloHoras = 0
      config.luzCicloInicio = null
    }
    
    if (modo === 'ai') {
      config.luzCicloHoras = 0
      config.luzCicloInicio = null
      config.aiAjusteFotoperiodo = false
      sugestaoIA.value = null
    }
    
    await guardarConfiguracao()
  }

  async function definirEstadoLuzManual(ligada: boolean): Promise<void> {
    config.luzManual = true
    config.luzModo = 'manual'
    config.luzEstado = ligada
    await guardarConfiguracao()
  }

  async function iniciarCicloLuz(horas: number): Promise<void> {
    config.luzModo = 'ciclo'
    config.luzCicloHoras = horas
    config.luzCicloInicio = new Date().toISOString()
    config.luzEstado = true
    config.luzManual = false
    await guardarConfiguracao()
  }

  async function alternarLuzBranca(): Promise<void> {
    config.luzManual = true
    config.luzEstado = !luzBrancaLigada.value
    await guardarConfiguracao()
  }

  async function actualizarHorarioLuzBranca(
    tipo: 'ligar' | 'desligar',
    hora: number,
    minuto: number
  ): Promise<void> {
    if (tipo === 'ligar') {
      config.luzHoraLigar = hora
      config.luzMinutoLigar = minuto
    } else {
      config.luzHoraDesligar = hora
      config.luzMinutoDesligar = minuto
    }
    await guardarConfiguracao()
  }

  // ========== ACÇÕES LUZ NOTURNA ==========
  async function definirModoLuzNoturna(modo: ModoLuzNoturna): Promise<void> {
    config.luzNoturnaModo = modo
    config.luzNoturnaManual = modo === 'manual'
    await guardarConfiguracao()
  }

  async function definirEstadoLuzNoturnaManual(ligada: boolean): Promise<void> {
    config.luzNoturnaManual = true
    config.luzNoturnaModo = 'manual'
    config.luzNoturnaEstado = ligada
    await guardarConfiguracao()
  }

  async function iniciarCicloLuzNoturna(horas: number): Promise<void> {
    config.luzNoturnaModo = 'ciclo'
    config.luzNoturnaCicloHoras = horas
    config.luzNoturnaCicloInicio = new Date().toISOString()
    config.luzNoturnaEstado = true
    config.luzNoturnaManual = false
    await guardarConfiguracao()
  }

  async function alternarLuzNoturna(): Promise<void> {
    config.luzNoturnaManual = true
    config.luzNoturnaEstado = !luzNoturnaLigada.value
    await guardarConfiguracao()
  }

  async function actualizarHorarioLuzNoturna(
    tipo: 'ligar' | 'desligar',
    hora: number,
    minuto: number
  ): Promise<void> {
    if (tipo === 'ligar') {
      config.luzNoturnaHoraLigar = hora
      config.luzNoturnaMinutoLigar = minuto
    } else {
      config.luzNoturnaHoraDesligar = hora
      config.luzNoturnaMinutoDesligar = minuto
    }
    config.luzNoturnaManual = false
    await guardarConfiguracao()
  }

  // ========== IA ==========
  async function obterSugestaoIA(): Promise<void> {
    adicionarRegisto('A obter sugestão da IA...', 'info')
    try {
      const aiHost = window.location.hostname
      const res = await $fetch<any>(`http://${aiHost}:5000/api/ai/photoperiod`)
      sugestaoIA.value = res
      adicionarRegisto(
        `IA: Fotoperíodo ${res.fotoperiodo_sugerido}h, Intensidade ${res.intensidade_sugerida}%`,
        'success'
      )
    } catch (erro) {
      console.error('Erro ao obter sugestão IA:', erro)
      adicionarRegisto(`Erro IA: ${erro}`, 'error')
    }
  }

  async function aplicarSugestaoIA(): Promise<void> {
    if (!sugestaoIA.value) return
    
    adicionarRegisto('A aplicar sugestão da IA...', 'info')
    
    config.luzModo = 'ai'
    config.luzManual = false
    config.luzCicloHoras = sugestaoIA.value.fotoperiodo_sugerido
    config.luzCicloInicio = new Date().toISOString()
    config.luzEstado = true
    config.aiAjusteFotoperiodo = true
    
    if (sugestaoIA.value.intensidade_sugerida !== undefined) {
      config.luzIntensidade = sugestaoIA.value.intensidade_sugerida
    }
    
    // Aplicar sugestão de luz noturna
    if (sugestaoIA.value.luz_noturna) {
      const luzNoturna = sugestaoIA.value.luz_noturna
      if (luzNoturna.accao === 'desligar' || luzNoturna.forcar === false) {
        config.luzNoturnaManual = true
        config.luzNoturnaEstado = false
        luzNoturnaLigada.value = false
        adicionarRegisto('Luz noturna: DESLIGADA (sugestão IA)', 'info')
      } else if (luzNoturna.accao === 'ligar' || luzNoturna.forcar === true) {
        config.luzNoturnaManual = true
        config.luzNoturnaEstado = true
        luzNoturnaLigada.value = true
        adicionarRegisto('Luz noturna: LIGADA (sugestão IA)', 'info')
      }
    }
    
    await guardarConfiguracao()
    luzBrancaLigada.value = true
    adicionarRegisto(
      `Configuração aplicada: ${config.luzCicloHoras}h @ ${config.luzIntensidade}%`,
      'success'
    )
  }

  return {
    // Estado
    config,
    sugestaoIA: readonly(sugestaoIA),
    
    // Carregamento
    carregarConfiguracao,
    guardarConfiguracao,
    guardarIntensidade,
    
    // Ventoinha
    definirModoManualVentoinha,
    definirEstadoVentoinha,
    
    // Luz branca
    definirModoLuz,
    definirEstadoLuzManual,
    iniciarCicloLuz,
    alternarLuzBranca,
    actualizarHorarioLuzBranca,
    
    // Luz noturna
    definirModoLuzNoturna,
    definirEstadoLuzNoturnaManual,
    iniciarCicloLuzNoturna,
    alternarLuzNoturna,
    actualizarHorarioLuzNoturna,
    
    // IA
    obterSugestaoIA,
    aplicarSugestaoIA
  }
}
