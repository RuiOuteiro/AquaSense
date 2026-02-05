/**
 * Funções de conversão e tradução
 * 
 * @ficheiro utils/conversores.ts
 * @autor AquaSense Team
 */

import { TRADUCAO_SENSORES } from './constantes'

/**
 * Traduz tipo de sensor para português
 */
export function traduzirTipoSensor(tipo: string): string {
  return TRADUCAO_SENSORES[tipo] || tipo
}

/**
 * Obtém classe CSS baseada na temperatura
 */
export function obterClasseTemperatura(
  temp: number | null,
  limiteAlto: number,
  limiteBaixo: number
): string {
  if (temp === null) return ''
  if (temp >= limiteAlto) return 'high'
  if (temp <= limiteBaixo) return 'low'
  return 'normal'
}

/**
 * Obtém classe CSS baseada no pH
 */
export function obterClassePH(ph: number | null): string {
  if (ph === null) return ''
  if (ph < 6.5) return 'acidic'
  if (ph > 7.5) return 'alkaline'
  return 'neutral'
}

/**
 * Obtém classe CSS baseada na turbidez
 */
export function obterClasseTurbidez(turbidez: number | null): string {
  if (turbidez === null) return ''
  if (turbidez <= 20) return 'clear'
  if (turbidez >= 60) return 'murky'
  return 'moderate'
}

/**
 * Obtém classe de alerta baseada na turbidez
 */
export function obterClasseAlertaTurbidez(turbidez: number): string {
  if (turbidez > 80) return 'critical'
  if (turbidez > 60) return 'warning'
  if (turbidez > 40) return 'moderate'
  return 'ok'
}

/**
 * Obtém classe de alerta baseada na severidade da IA
 */
export function obterClasseAlerta(
  turbidez: number,
  severidade?: string
): string {
  // Prioridade: severidade da IA (inclui pH/temp críticos)
  if (severidade === 'critica') return 'alert-critical'
  if (severidade === 'alta') return 'alert-warning'
  if (severidade === 'moderada') return 'alert-moderate'
  // Fallback para turbidez
  if (turbidez > 80) return 'alert-critical'
  if (turbidez > 60) return 'alert-warning'
  if (turbidez > 40) return 'alert-moderate'
  return 'alert-ok'
}

/**
 * Extrai hora e minuto de um input time
 */
export function extrairHoraMinuto(valor: string): { hora: number; minuto: number } {
  const [h, m] = valor.split(':').map(Number)
  return { hora: h ?? 0, minuto: m ?? 0 }
}

/**
 * Converte timestamp ISO para milissegundos
 */
export function converterParaMs(timestamp: string): number {
  const ms = new Date(timestamp).getTime()
  return Number.isFinite(ms) ? ms : Date.now()
}

/**
 * Verifica se valor é número válido
 */
export function ehNumeroValido(valor: any): boolean {
  return typeof valor === 'number' && !isNaN(valor) && isFinite(valor)
}
