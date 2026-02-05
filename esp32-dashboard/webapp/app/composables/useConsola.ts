/**
 * Composable para gestão da consola do ESP32
 * 
 * Gere os registos de logs do sistema e do ESP32,
 * incluindo auto-scroll e limite de registos.
 * 
 * @ficheiro composables/useConsola.ts
 * @autor AquaSense Team
 */

import type { RegistoConsola } from '~/types'
import { MAX_REGISTOS_CONSOLA } from '~/utils/constantes'

// Estado global partilhado
const registos = ref<RegistoConsola[]>([])
const elementoConsola = ref<HTMLElement | null>(null)
let ultimoTimestamp = 0

export function useConsola() {
  /**
   * Adiciona registo à consola
   */
  function adicionarRegisto(
    mensagem: string,
    tipo: RegistoConsola['tipo'] = 'info'
  ): void {
    const agora = new Date()
    const hora = agora.toLocaleTimeString('pt-PT')
    
    registos.value.push({ hora, mensagem, tipo })
    
    // Limitar número de registos
    if (registos.value.length > MAX_REGISTOS_CONSOLA) {
      registos.value.shift()
    }
    
    // Auto-scroll
    nextTick(() => {
      if (elementoConsola.value) {
        elementoConsola.value.scrollTop = elementoConsola.value.scrollHeight
      }
    })
  }

  /**
   * Limpa todos os registos
   */
  function limparConsola(): void {
    registos.value = []
  }

  /**
   * Obtém logs do ESP32
   */
  async function obterLogsESP32(): Promise<void> {
    try {
      const res = await $fetch<{ 
        success: boolean
        logs: any[]
        timestamp: number 
      }>(`/api/logs?since=${ultimoTimestamp}`)
      
      if (res.success && res.logs.length > 0) {
        for (const log of res.logs) {
          registos.value.push({
            hora: log.time,
            mensagem: `[ESP32] ${log.message}`,
            tipo: log.type || 'info'
          })
        }
        
        // Limitar registos
        while (registos.value.length > MAX_REGISTOS_CONSOLA) {
          registos.value.shift()
        }
        
        ultimoTimestamp = res.timestamp
        
        // Auto-scroll
        nextTick(() => {
          if (elementoConsola.value) {
            elementoConsola.value.scrollTop = elementoConsola.value.scrollHeight
          }
        })
      }
    } catch {
      // Silencioso - logs são opcionais
    }
  }

  return {
    registos: readonly(registos),
    elementoConsola,
    adicionarRegisto,
    limparConsola,
    obterLogsESP32
  }
}
