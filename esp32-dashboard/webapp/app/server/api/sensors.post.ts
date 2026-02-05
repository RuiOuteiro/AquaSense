import pool from '../utils/db'
import { sendAlerta } from '../utils/telegram'

// Cache para evitar spam de alertas (1 alerta por tipo a cada 5 minutos)
const alertCache: Record<string, number> = {}
const ALERT_COOLDOWN = 5 * 60 * 1000 // 5 minutos

// Função para verificar e enviar alertas
async function checkAndSendAlerts(aquarioId: number, sensors: any[], deviceId: string) {
  try {
    // Obter utilizador, config telegram e config alertas
    const [rows] = await pool.execute(
      `SELECT u.id as user_id, u.telegram_chat_id, u.telegram_alertas,
              ac.enabled, ac.temp_min, ac.temp_max, ac.ph_min, ac.ph_max,
              ac.turbidez_max, ac.humidade_min, ac.humidade_max,
              ac.temp_ambiente_min, ac.temp_ambiente_max
       FROM utilizadores u 
       JOIN aquarios a ON a.utilizador_id = u.id 
       LEFT JOIN alertas_config ac ON ac.utilizador_id = u.id
       WHERE a.id = ? AND u.telegram_chat_id IS NOT NULL AND u.telegram_alertas = 1`,
      [aquarioId]
    )
    
    const users = rows as any[]
    if (users.length === 0) return
    
    const user = users[0]
    const chatId = user.telegram_chat_id
    
    // Se alertas desativados, não enviar
    if (user.enabled === 0) return
    
    // Construir limites da BD (ou usar defaults)
    const LIMITES: Record<string, { min: number; max: number }> = {
      temperature: { min: user.temp_min || 22, max: user.temp_max || 28 },
      ambient_temp: { min: user.temp_ambiente_min || 18, max: user.temp_ambiente_max || 30 },
      humidity: { min: user.humidade_min || 40, max: user.humidade_max || 80 },
      ph: { min: user.ph_min || 6.5, max: user.ph_max || 7.5 },
      turbidity: { min: 0, max: user.turbidez_max || 30 }
    }
    
    for (const sensor of sensors) {
      const tipo = sensor.type?.toLowerCase()
      let valor = sensor.value
      
      // Aplicar mesma correção do pH
      if (tipo === 'ph' && typeof valor === 'number') {
        valor = valor - 2.5
      }
      
      const limites = LIMITES[tipo]
      if (!limites) continue
      
      const foraDoLimite = valor < limites.min || valor > limites.max
      if (!foraDoLimite) continue
      
      // Verificar cooldown
      const cacheKey = `${deviceId}_${tipo}`
      const lastAlert = alertCache[cacheKey] || 0
      if (Date.now() - lastAlert < ALERT_COOLDOWN) continue
      
      // Enviar alerta
      const enviado = await sendAlerta(chatId, sensor.type, valor)
      
      if (enviado) {
        alertCache[cacheKey] = Date.now()
        console.log(`[TELEGRAM] Alerta enviado: ${tipo} = ${valor}`)
      }
    }
  } catch (error) {
    console.error('[TELEGRAM] Erro ao verificar alertas:', error)
  }
}

// Endpoint para receber TODOS os dados do ESP32 num único POST
export default defineEventHandler(async (event) => {
  const body = await readBody(event)
  
  const { device_id, sensors, aquario_id } = body

  console.log('[SENSORS POST] Recebido:', { device_id, aquario_id, sensorsCount: sensors?.length, sensors: sensors?.map((s: any) => s.type) })

  if (!device_id || !sensors || !Array.isArray(sensors)) {
    console.log('[SENSORS POST] Erro: campos em falta')
    throw createError({
      statusCode: 400,
      message: 'Campos obrigatórios: device_id, sensors (array)'
    })
  }

  try {
    // Determinar aquario_id pelo device_id se não fornecido
    let targetAquarioId = aquario_id
    if (!aquario_id) {
      const [aquarios] = await pool.execute(
        'SELECT id FROM aquarios WHERE device_id = ? AND ativo = 1 LIMIT 1',
        [device_id]
      )
      if ((aquarios as any[]).length > 0) {
        targetAquarioId = (aquarios as any[])[0].id
      } else {
        // Criar aquário automaticamente se não existir
        const [result] = await pool.execute(
          'INSERT INTO aquarios (nome, device_id, utilizador_id) VALUES (?, ?, ?)',
          [`Aquário ${device_id}`, device_id, 1]
        ) as any
        targetAquarioId = result.insertId
        console.log(`[SENSORS] Aquário criado automaticamente: ${targetAquarioId}`)
      }
    }

    // Inserir todos os sensores numa única transação
    const connection = await pool.getConnection()
    await connection.beginTransaction()
    
    try {
      let inserted = 0
      for (const sensor of sensors) {
        const { type, unit } = sensor
        let { value } = sensor
        
        // Correcção de calibração do pH (-2.5 para compensar erro do sensor)
        if (type === 'pH' && typeof value === 'number') {
          value = value - 2.5
        }
        
        if (type && value !== undefined) {
          await connection.execute(
            'INSERT INTO leituras_sensores (aquario_id, id_dispositivo, tipo_sensor, valor, unidade) VALUES (?, ?, ?, ?, ?)',
            [targetAquarioId, device_id, type, value, unit || null]
          )
          inserted++
        }
      }
      await connection.commit()
      connection.release()
      
      console.log(`[SENSORS POST] OK: ${inserted} sensores inseridos`)
      
      // Verificar alertas e enviar Telegram
      checkAndSendAlerts(targetAquarioId, sensors, device_id)
      
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
