import pool from '../../utils/db'

export default defineEventHandler(async () => {
  try {
    const [rows] = await pool.execute(
      'SELECT * FROM configuracoes WHERE id = 1'
    )
    
    const config = (rows as any[])[0]
    
    if (!config) {
      return {
        modo_manual: false,
        ventoinha_manual: false,
        temp_ligar: 14.0,
        temp_desligar: 13.0,
        luz_manual: false,
        luz_estado: false,
        luz_hora_ligar: 8,
        luz_minuto_ligar: 0,
        luz_hora_desligar: 20,
        luz_minuto_desligar: 0,
        luz_intensidade: 100,
        luz_fade_speed: 10,
        luz_noturna_manual: false,
        luz_noturna_estado: false,
        luz_noturna_hora_ligar: 20,
        luz_noturna_minuto_ligar: 0,
        luz_noturna_hora_desligar: 8,
        luz_noturna_minuto_desligar: 0
      }
    }
    
    return {
      modo_manual: config.modo_manual === 1,
      ventoinha_manual: config.ventoinha_manual === 1,
      temp_ligar: parseFloat(config.temp_ligar),
      temp_desligar: parseFloat(config.temp_desligar),
      luz_manual: config.luz_manual === 1,
      luz_estado: config.luz_estado === 1,
      luz_modo: config.luz_modo ?? 'horario',
      luz_ciclo_horas: config.luz_ciclo_horas ?? 8,
      luz_ciclo_inicio: config.luz_ciclo_inicio ?? null,
      luz_hora_ligar: config.luz_hora_ligar ?? 8,
      luz_minuto_ligar: config.luz_minuto_ligar ?? 0,
      luz_hora_desligar: config.luz_hora_desligar ?? 20,
      luz_minuto_desligar: config.luz_minuto_desligar ?? 0,
      luz_intensidade: config.luz_intensidade ?? 100,
      luz_fade_speed: config.luz_fade_speed ?? 10,
      luz_noturna_manual: config.luz_noturna_manual === 1,
      luz_noturna_estado: config.luz_noturna_estado === 1,
      luz_noturna_modo: config.luz_noturna_modo ?? 'horario',
      luz_noturna_ciclo_horas: config.luz_noturna_ciclo_horas ?? 8,
      luz_noturna_ciclo_inicio: config.luz_noturna_ciclo_inicio ?? null,
      luz_noturna_hora_ligar: config.luz_noturna_hora_ligar ?? 20,
      luz_noturna_minuto_ligar: config.luz_noturna_minuto_ligar ?? 0,
      luz_noturna_hora_desligar: config.luz_noturna_hora_desligar ?? 8,
      luz_noturna_minuto_desligar: config.luz_noturna_minuto_desligar ?? 0
    }
  } catch (error: any) {
    return {
      modo_manual: false,
      ventoinha_manual: false,
      temp_ligar: 14.0,
      temp_desligar: 13.0,
      luz_manual: false,
      luz_estado: false,
      luz_hora_ligar: 8,
      luz_minuto_ligar: 0,
      luz_hora_desligar: 20,
      luz_minuto_desligar: 0,
      luz_intensidade: 100,
      luz_fade_speed: 10,
      luz_noturna_manual: false,
      luz_noturna_estado: false,
      luz_noturna_hora_ligar: 20,
      luz_noturna_minuto_ligar: 0,
      luz_noturna_hora_desligar: 8,
      luz_noturna_minuto_desligar: 0
    }
  }
})
