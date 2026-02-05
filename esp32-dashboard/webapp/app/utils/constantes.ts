/**
 * Constantes globais da aplicação
 * 
 * @ficheiro utils/constantes.ts
 * @autor AquaSense Team
 */

// ========== INTERVALOS DE ACTUALIZAÇÃO (ms) ==========
export const INTERVALO_DADOS = 5000        // Obter dados dos sensores
export const INTERVALO_LOGS = 2000         // Obter logs do ESP32
export const INTERVALO_RELOGIO = 1000      // Actualizar relógio

// ========== LIMITES POR DEFEITO ==========
export const LIMITES_DEFEITO = {
  tempMin: 22,
  tempMax: 28,
  phMin: 6.5,
  phMax: 7.5,
  turbidezMax: 50,
  humidadeMin: 40,
  humidadeMax: 80
}

// ========== TIMEOUT DE LIGAÇÃO ==========
export const TIMEOUT_CONEXAO = 30000       // 30 segundos para considerar desligado

// ========== OPÇÕES DE FOTOPERÍODO ==========
export const OPCOES_FOTOPERIODO = [4, 6, 8, 12, 16]

// ========== MÁXIMO DE REGISTOS NA CONSOLA ==========
export const MAX_REGISTOS_CONSOLA = 200

// ========== MAPEAMENTO DE TIPOS DE SENSOR PARA PT-PT ==========
export const TRADUCAO_SENSORES: Record<string, string> = {
  temperature: 'Temperatura',
  pH: 'pH',
  pH_voltage: 'Tensão pH',
  fan_status: 'Ventoinha',
  ambient_temp: 'Temp. Ambiente',
  humidity: 'Humidade',
  turbidity: 'Turbidez',
  turbidity_voltage: 'Tensão Turbidez',
  light_status: 'Luz Branca',
  night_light_status: 'Luz Noturna',
  light_brightness: 'Brilho Luz'
}

// ========== CORES DOS SENSORES ==========
export const CORES_SENSORES = {
  temperature: '#ff6b6b',
  pH: '#4ecdc4',
  turbidity: '#ffe66d',
  humidity: '#a78bfa',
  ambient_temp: '#f472b6'
}

// ========== PERÍODOS DE GRÁFICOS ==========
export const PERIODOS_GRAFICO = [
  { valor: 6, etiqueta: '6h' },
  { valor: 12, etiqueta: '12h' },
  { valor: 24, etiqueta: '24h' },
  { valor: 48, etiqueta: '48h' },
  { valor: 168, etiqueta: '7d' }
]
