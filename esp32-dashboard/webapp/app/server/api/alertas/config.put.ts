import pool from '../../utils/db'
import { requireAuth } from '../../utils/auth'

export default defineEventHandler(async (event) => {
  const user = requireAuth(event)
  const body = await readBody(event)

  const { enabled, tempMin, tempMax, phMin, phMax, turbidezMax, humidadeMin, humidadeMax, tempAmbienteMin, tempAmbienteMax } = body

  try {
    // Verificar se existe config
    const [existing] = await pool.execute(
      'SELECT id FROM alertas_config WHERE utilizador_id = ?',
      [user.id]
    )

    if ((existing as any[]).length === 0) {
      // Criar novo
      await pool.execute(
        `INSERT INTO alertas_config 
         (utilizador_id, enabled, temp_min, temp_max, ph_min, ph_max, turbidez_max, humidade_min, humidade_max, temp_ambiente_min, temp_ambiente_max) 
         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
        [user.id, enabled ? 1 : 0, tempMin, tempMax, phMin, phMax, turbidezMax, humidadeMin, humidadeMax, tempAmbienteMin || 18, tempAmbienteMax || 30]
      )
    } else {
      // Atualizar existente
      await pool.execute(
        `UPDATE alertas_config SET 
         enabled = ?, temp_min = ?, temp_max = ?, ph_min = ?, ph_max = ?, 
         turbidez_max = ?, humidade_min = ?, humidade_max = ?,
         temp_ambiente_min = ?, temp_ambiente_max = ?
         WHERE utilizador_id = ?`,
        [enabled ? 1 : 0, tempMin, tempMax, phMin, phMax, turbidezMax, humidadeMin, humidadeMax, tempAmbienteMin || 18, tempAmbienteMax || 30, user.id]
      )
    }

    return {
      success: true,
      message: 'Configuração de alertas guardada'
    }
  } catch (error: any) {
    console.error('[ALERTAS CONFIG] Erro:', error.message)
    throw createError({
      statusCode: 500,
      message: 'Erro ao guardar configuração de alertas'
    })
  }
})
