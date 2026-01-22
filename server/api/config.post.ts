import pool from '../utils/db'

export default defineEventHandler(async (event) => {
  const body = await readBody(event)
  
  const { 
    modo_manual, ventoinha_manual, temp_ligar, temp_desligar,
    luz_manual, luz_estado, luz_hora_ligar, luz_minuto_ligar, 
    luz_hora_desligar, luz_minuto_desligar, luz_intensidade, luz_fade_speed,
    luz_modo, luz_ciclo_horas, luz_ciclo_inicio,
    luz_noturna_manual, luz_noturna_estado, luz_noturna_hora_ligar,
    luz_noturna_minuto_ligar, luz_noturna_hora_desligar, luz_noturna_minuto_desligar,
    luz_noturna_modo, luz_noturna_ciclo_horas, luz_noturna_ciclo_inicio,
    ai_ajuste_fotoperiodo
  } = body

  try {
    await pool.execute(
      `UPDATE configuracoes SET 
        modo_manual = ?, ventoinha_manual = ?, temp_ligar = ?, temp_desligar = ?,
        luz_manual = ?, luz_estado = ?, luz_hora_ligar = ?, luz_minuto_ligar = ?, 
        luz_hora_desligar = ?, luz_minuto_desligar = ?, luz_intensidade = ?, luz_fade_speed = ?,
        luz_modo = ?, luz_ciclo_horas = ?, luz_ciclo_inicio = ?,
        luz_noturna_manual = ?, luz_noturna_estado = ?, luz_noturna_hora_ligar = ?,
        luz_noturna_minuto_ligar = ?, luz_noturna_hora_desligar = ?, luz_noturna_minuto_desligar = ?,
        luz_noturna_modo = ?, luz_noturna_ciclo_horas = ?, luz_noturna_ciclo_inicio = ?,
        ai_ajuste_fotoperiodo = ?
      WHERE id = 1`,
      [
        modo_manual ? 1 : 0, ventoinha_manual ? 1 : 0, temp_ligar, temp_desligar,
        luz_manual ? 1 : 0, luz_estado ? 1 : 0, 
        luz_hora_ligar ?? 8, luz_minuto_ligar ?? 0,
        luz_hora_desligar ?? 20, luz_minuto_desligar ?? 0, 
        luz_intensidade ?? 100, luz_fade_speed ?? 10,
        luz_modo ?? 'horario', luz_ciclo_horas ?? 8, luz_ciclo_inicio ? new Date(luz_ciclo_inicio) : null,
        luz_noturna_manual ? 1 : 0, luz_noturna_estado ? 1 : 0,
        luz_noturna_hora_ligar ?? 20, luz_noturna_minuto_ligar ?? 0,
        luz_noturna_hora_desligar ?? 8, luz_noturna_minuto_desligar ?? 0,
        luz_noturna_modo ?? 'horario', luz_noturna_ciclo_horas ?? 8, luz_noturna_ciclo_inicio ? new Date(luz_noturna_ciclo_inicio) : null,
        ai_ajuste_fotoperiodo ? 1 : 0
      ]
    )
    
    return {
      success: true,
      message: 'Configurações guardadas com sucesso'
    }
  } catch (error: any) {
    throw createError({
      statusCode: 500,
      message: `Erro na base de dados: ${error.message}`
    })
  }
})
