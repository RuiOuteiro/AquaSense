/**
 * Tipos e interfaces do AquaSense
 * 
 * @ficheiro types/index.ts
 * @autor AquaSense Team
 * @versao 1.0.0
 */

// ========== LEITURAS DE SENSORES ==========
export interface LeituraSensor {
  id: number
  device_id: string
  sensor_type: TipoSensor
  value: number
  unit: string | null
  created_at: string
}

export type TipoSensor = 
  | 'temperature' 
  | 'pH' 
  | 'pH_voltage'
  | 'turbidity' 
  | 'turbidity_voltage'
  | 'ambient_temp' 
  | 'humidity'
  | 'fan_status' 
  | 'light_status' 
  | 'night_light_status'
  | 'light_brightness'

// ========== CONFIGURAÇÃO DO SISTEMA ==========
export interface ConfiguracaoSistema {
  // Ventoinha
  modoManual: boolean
  ventoinhaManual: boolean
  tempLigar: number
  tempDesligar: number
  
  // Luz branca
  luzManual: boolean
  luzEstado: boolean
  luzModo: ModoLuz
  luzCicloHoras: number
  luzCicloInicio: string | null
  luzHoraLigar: number
  luzMinutoLigar: number
  luzHoraDesligar: number
  luzMinutoDesligar: number
  luzIntensidade: number
  luzFadeSpeed: number
  
  // Luz noturna
  luzNoturnaManual: boolean
  luzNoturnaEstado: boolean
  luzNoturnaModo: ModoLuzNoturna
  luzNoturnaCicloHoras: number
  luzNoturnaCicloInicio: string | null
  luzNoturnaHoraLigar: number
  luzNoturnaMinutoLigar: number
  luzNoturnaHoraDesligar: number
  luzNoturnaMinutoDesligar: number
  
  // IA
  aiAjusteFotoperiodo: boolean
  aiFotoperiodoSugerido: number | null
}

export type ModoLuz = 'manual' | 'horario' | 'ciclo' | 'ai'
export type ModoLuzNoturna = 'manual' | 'horario' | 'ciclo'

// ========== SUGESTÃO IA ==========
export interface SugestaoIA {
  fotoperiodo_sugerido: number
  ajuste_horas: number
  razao: string
  intensidade_sugerida?: number
  severidade: 'normal' | 'moderada' | 'alta' | 'critica'
  tendencia: string
  input: EntradaIA
  tpa?: SugestaoTPA
  luz_noturna?: SugestaoLuzNoturna
  alimentacao?: SugestaoAlimentacao
  accoes?: string[]
}

export interface EntradaIA {
  fotoperiodo_base: number
  intensidade_actual: number
  ph: number
  temperatura: number
  turbidez_24h: number
  turbidez_actual: number
}

export interface SugestaoTPA {
  percentagem: number
  urgencia: string
  frequencia: string
  dias: number
  descricao: string
}

export interface SugestaoLuzNoturna {
  accao: 'ligar' | 'desligar' | 'manter'
  razao: string
  forcar: boolean
  periodo_max?: number
}

export interface SugestaoAlimentacao {
  accao: 'manter' | 'reduzir' | 'suspender'
  descricao: string
  dias?: number
  percentagem?: number
}

// ========== UTILIZADOR ==========
export interface Utilizador {
  id: number
  nome: string
  email: string
}

export interface Aquario {
  id: number
  nome: string
  device_id: string
  descricao: string
  total_leituras?: number
}

// ========== CONSOLA ==========
export interface RegistoConsola {
  hora: string
  mensagem: string
  tipo: 'info' | 'warn' | 'error' | 'success'
}

// ========== ALERTAS ==========
export interface ConfiguracaoAlertas {
  activo: boolean
  tempMin: number
  tempMax: number
  phMin: number
  phMax: number
  turbidezMax: number
  humidadeMin: number
  humidadeMax: number
}

// ========== GRÁFICOS ==========
export interface DadosGrafico {
  value: number
  created_at: string
}

export interface EstatisticasLuz {
  whiteLight: { date: string; hours: number }[]
  blueLight: { date: string; hours: number }[]
}

// ========== FORMULÁRIO PERFIL ==========
export interface FormularioPerfil {
  nome: string
  email: string
  currentPassword: string
  newPassword: string
}

// ========== TELEGRAM ==========
export interface ConfiguracaoTelegram {
  chat_id: string
  activo: boolean
}

// ========== NOVO AQUÁRIO ==========
export interface NovoAquario {
  nome: string
  device_id: string
  descricao: string
}
