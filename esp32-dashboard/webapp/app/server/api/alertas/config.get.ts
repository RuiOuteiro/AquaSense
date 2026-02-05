import pool from '../../utils/db'
import { requireAuth } from '../../utils/auth'

export default defineEventHandler(async (event) => {
  const user = requireAuth(event)

  try {
    const [rows] = await pool.execute(
      `SELECT enabled, temp_min, temp_max, ph_min, ph_max, 
              turbidez_max, humidade_min, humidade_max 
       FROM alertas_config WHERE utilizador_id = ?`,
      [user.id]
    )

    const configs = rows as any[]
    
    // Se não existe config, criar com valores default
    if (configs.length === 0) {
      await pool.execute(
        'INSERT INTO alertas_config (utilizador_id) VALUES (?)',
        [user.id]
      )
      
      return {
        success: true,
        config: {
          enabled: true,
          tempMin: 22,
          tempMax: 28,
          phMin: 6.5,
          phMax: 7.5,
          turbidezMax: 30,
          humidadeMin: 40,
          humidadeMax: 80
        }
      }
    }

    const cfg = configs[0]
    return {
      success: true,
      config: {
        enabled: cfg.enabled === 1,
        tempMin: parseFloat(cfg.temp_min),
        tempMax: parseFloat(cfg.temp_max),
        phMin: parseFloat(cfg.ph_min),
        phMax: parseFloat(cfg.ph_max),
        turbidezMax: parseFloat(cfg.turbidez_max),
        humidadeMin: parseFloat(cfg.humidade_min),
        humidadeMax: parseFloat(cfg.humidade_max)
      }
    }
  } catch (error: any) {
    console.error('[ALERTAS CONFIG] Erro:', error.message)
    throw createError({
      statusCode: 500,
      message: 'Erro ao obter configuração de alertas'
    })
  }
})
