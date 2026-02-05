import pool from '../../utils/db'
import { requireAuth } from '../../utils/auth'
import { testTelegramConnection } from '../../utils/telegram'

export default defineEventHandler(async (event) => {
  const user = requireAuth(event)
  const body = await readBody(event)
  const { chat_id, alertas_enabled } = body

  if (!chat_id || !chat_id.trim()) {
    throw createError({
      statusCode: 400,
      message: 'Chat ID é obrigatório'
    })
  }

  try {
    // Testar conexão antes de guardar
    const testOk = await testTelegramConnection(chat_id.trim())
    
    if (!testOk) {
      throw createError({
        statusCode: 400,
        message: 'Não foi possível enviar mensagem para este Chat ID. Verifica se iniciaste conversa com o bot.'
      })
    }

    // Guardar na base de dados
    await pool.execute(
      'UPDATE utilizadores SET telegram_chat_id = ?, telegram_alertas = ? WHERE id = ?',
      [chat_id.trim(), alertas_enabled !== false ? 1 : 0, user.id]
    )

    return {
      success: true,
      message: 'Telegram configurado com sucesso! Verifica a mensagem de teste.'
    }
  } catch (error: any) {
    if (error.statusCode) throw error
    
    console.error('[TELEGRAM CONFIG] Erro:', error.message)
    throw createError({
      statusCode: 500,
      message: 'Erro ao configurar Telegram'
    })
  }
})
