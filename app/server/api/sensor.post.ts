import pool from '../utils/db'

export default defineEventHandler(async (event) => {
  const body = await readBody(event)
  
  const { device_id, sensor_type, value, unit } = body

  if (!device_id || !sensor_type || value === undefined) {
    throw createError({
      statusCode: 400,
      message: 'Campos obrigatórios em falta: device_id, sensor_type, value'
    })
  }

  try {
    const [result] = await pool.execute(
      'INSERT INTO leituras_sensores (id_dispositivo, tipo_sensor, valor, unidade) VALUES (?, ?, ?, ?)',
      [device_id, sensor_type, value, unit || null]
    )
    
    return {
      success: true,
      message: 'Dados inseridos com sucesso',
      id: (result as any).insertId
    }
  } catch (error: any) {
    throw createError({
      statusCode: 500,
      message: `Erro na base de dados: ${error.message}`
    })
  }
})
