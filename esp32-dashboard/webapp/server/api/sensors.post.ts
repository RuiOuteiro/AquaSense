import pool from '../utils/db'

// Endpoint para receber TODOS os dados do ESP32 num único POST
export default defineEventHandler(async (event) => {
  const body = await readBody(event)
  
  const { device_id, sensors } = body

  console.log('[SENSORS POST] Recebido:', { device_id, sensorsCount: sensors?.length, sensors: sensors?.map((s: any) => s.type) })

  if (!device_id || !sensors || !Array.isArray(sensors)) {
    console.log('[SENSORS POST] Erro: campos em falta')
    throw createError({
      statusCode: 400,
      message: 'Campos obrigatórios: device_id, sensors (array)'
    })
  }

  try {
    // Inserir todos os sensores numa única transação
    const connection = await pool.getConnection()
    await connection.beginTransaction()
    
    try {
      let inserted = 0
      for (const sensor of sensors) {
        const { type, unit } = sensor
        let { value } = sensor
        
        if (type && value !== undefined) {
          await connection.execute(
            'INSERT INTO leituras_sensores (id_dispositivo, tipo_sensor, valor, unidade) VALUES (?, ?, ?, ?)',
            [device_id, type, value, unit || null]
          )
          inserted++
        }
      }
      await connection.commit()
      connection.release()
      
      console.log(`[SENSORS POST] OK: ${inserted} sensores inseridos`)
      
      return {
        success: true,
        message: `${inserted} leituras inseridas`,
        count: inserted
      }
    } catch (err: any) {
      await connection.rollback()
      connection.release()
      console.log('[SENSORS POST] Erro na transação:', err.message)
      throw err
    }
  } catch (error: any) {
    console.log('[SENSORS POST] Erro geral:', error.message)
    throw createError({
      statusCode: 500,
      message: `Erro na base de dados: ${error.message}`
    })
  }
})
