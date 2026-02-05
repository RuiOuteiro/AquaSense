import pool from '../../utils/db'
import { requireAuth } from '../../utils/auth'

export default defineEventHandler(async (event) => {
  const user = requireAuth(event)
  const body = await readBody(event)

  const { enabled, tempMin, tempMax, phMin, phMax, turbidezMax, humidadeMin, humidadeMax } = body

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
         (utilizador_id, enabled, temp_min, temp_max, ph_min, ph_max, turbidez_max, humidade_min, humidade_max) 
         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)`,
        [user.id, enabled ? 1 : 0, tempMin, tempMax, phMin, phMax, turbidezMax, humidadeMin, humidadeMax]
      )
    } else {
      // Atualizar existente
      await pool.execute(
        `UPDATE alertas_config SET 
         enabled = ?, temp_min = ?, temp_max = ?, ph_min = ?, ph_max = ?, 
         turbidez_max = ?, humidade_min = ?, humidade_max = ?
         WHERE utilizador_id = ?`,
        [enabled ? 1 : 0, tempMin, tempMax, phMin, phMax, turbidezMax, humidadeMin, humidadeMax, user.id]
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
