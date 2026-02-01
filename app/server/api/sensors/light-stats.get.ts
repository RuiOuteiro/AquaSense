import pool from '../../utils/db'

export default defineEventHandler(async (event) => {
  const query = getQuery(event)
  const days = parseInt(query.days as string) || 7

  try {
    // Buscar todas as leituras de luz branca com timestamps
    const [whiteLightRows] = await pool.execute(`
      SELECT 
        DATE(data_hora) as dia,
        data_hora,
        valor
      FROM leituras_sensores 
      WHERE tipo_sensor = 'light_status'
        AND data_hora >= DATE_SUB(NOW(), INTERVAL ? DAY)
      ORDER BY data_hora ASC
    `, [days])

    // Buscar todas as leituras de luz azul com timestamps
    const [blueLightRows] = await pool.execute(`
      SELECT 
        DATE(data_hora) as dia,
        data_hora,
        valor
      FROM leituras_sensores 
      WHERE tipo_sensor = 'night_light_status'
        AND data_hora >= DATE_SUB(NOW(), INTERVAL ? DAY)
      ORDER BY data_hora ASC
    `, [days])

    // Calcular horas reais ligada por dia (baseado em intervalos entre leituras)
    const calculateHoursPerDay = (rows: any[]) => {
      const dayMap: Record<string, number> = {}
      
      for (let i = 0; i < rows.length - 1; i++) {
        const current = rows[i]
        const next = rows[i + 1]
        const dia = current.dia.toISOString().split('T')[0]
        
        // Se a luz estava ligada (valor > 0), contar o intervalo até próxima leitura
        if (current.valor > 0) {
          const intervalMs = new Date(next.data_hora).getTime() - new Date(current.data_hora).getTime()
          const intervalHours = intervalMs / (1000 * 60 * 60)
          
          // Limitar a 1 hora max por intervalo (evitar gaps grandes)
          const hoursToAdd = Math.min(intervalHours, 1)
          
          if (!dayMap[dia]) dayMap[dia] = 0
          dayMap[dia] += hoursToAdd
        }
      }
      
      return Object.entries(dayMap).map(([date, hours]) => ({
        date,
        hours: Math.round(hours * 10) / 10
      })).sort((a, b) => a.date.localeCompare(b.date))
    }

    const whiteLightData = calculateHoursPerDay(whiteLightRows as any[])
    const blueLightData = calculateHoursPerDay(blueLightRows as any[])

    return {
      success: true,
      data: {
        whiteLight: whiteLightData,
        blueLight: blueLightData
      }
    }
  } catch (error: any) {
    throw createError({
      statusCode: 500,
      message: `Erro na base de dados: ${error.message}`
    })
  }
})
