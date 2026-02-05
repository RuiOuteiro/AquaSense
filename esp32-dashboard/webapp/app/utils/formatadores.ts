/**
 * Funções de formatação de dados
 * 
 * @ficheiro utils/formatadores.ts
 * @autor AquaSense Team
 */

import type { LeituraSensor } from '~/types'

/**
 * Formata hora no formato HH:MM
 */
export function formatarHora(hora: number, minuto: number): string {
  return `${String(hora).padStart(2, '0')}:${String(minuto).padStart(2, '0')}`
}

/**
 * Formata data completa em PT-PT
 */
export function formatarData(data: string): string {
  return new Date(data).toLocaleString('pt-PT')
}

/**
 * Formata data curta (só dia e mês)
 */
export function formatarDataCurta(data: string): string {
  return new Date(data).toLocaleDateString('pt-PT', {
    day: '2-digit',
    month: 'short'
  })
}

/**
 * Formata hora actual
 */
export function formatarHoraActual(): string {
  return new Date().toLocaleTimeString('pt-PT', {
    hour: '2-digit',
    minute: '2-digit'
  })
}

/**
 * Formata hora actual com segundos
 */
export function formatarHoraActualCompleta(): string {
  return new Date().toLocaleTimeString('pt-PT')
}

/**
 * Formata valor de sensor para apresentação
 */
export function formatarValorSensor(leitura: LeituraSensor): string {
  const { sensor_type, value } = leitura
  
  switch (sensor_type) {
    case 'fan_status':
    case 'light_status':
    case 'night_light_status':
      return value >= 1 ? 'LIGADA' : 'DESLIGADA'
    case 'temperature':
    case 'ambient_temp':
      return `${value.toFixed(1)}°C`
    case 'humidity':
    case 'turbidity':
      return `${value.toFixed(0)}%`
    case 'pH':
      return value.toFixed(2)
    case 'pH_voltage':
      return `${value.toFixed(3)}V`
    case 'turbidity_voltage':
      return `${value.toFixed(2)}V`
    default:
      return `${value}`
  }
}

/**
 * Calcula duração do fotoperíodo
 */
export function calcularFotoperiodo(
  horaLigar: number,
  minutoLigar: number,
  horaDesligar: number,
  minutoDesligar: number
): string {
  const ligar = horaLigar * 60 + minutoLigar
  const desligar = horaDesligar * 60 + minutoDesligar
  let minutos = desligar - ligar
  if (minutos < 0) minutos += 24 * 60
  
  const h = Math.floor(minutos / 60)
  const m = minutos % 60
  return m > 0 ? `${h}h ${m}m` : `${h}h`
}

/**
 * Obtém hora de início do ciclo
 */
export function obterHoraInicioCiclo(inicio: string | null): string {
  if (!inicio) return '--:--'
  const d = new Date(inicio)
  return formatarHora(d.getHours(), d.getMinutes())
}

/**
 * Obtém hora de fim do ciclo
 */
export function obterHoraFimCiclo(inicio: string | null, horas: number): string {
  if (!inicio) return '--:--'
  const d = new Date(inicio)
  d.setHours(d.getHours() + horas)
  return formatarHora(d.getHours(), d.getMinutes())
}

/**
 * Formata duração de luz ligada
 */
export function formatarDuracaoLuz(tempoLigadaMs: number | null): string {
  if (!tempoLigadaMs) return ''
  const segundos = Math.floor((Date.now() - tempoLigadaMs) / 1000)
  const horas = Math.floor(segundos / 3600)
  const minutos = Math.floor((segundos % 3600) / 60)
  if (horas > 0) return `${horas}h ${minutos}m`
  return `${minutos}m`
}

/**
 * Arredonda valor para exibição em gráficos
 */
export function arredondarParaGrafico(valor: number): number {
  return Math.round(valor * 10) / 10
}
