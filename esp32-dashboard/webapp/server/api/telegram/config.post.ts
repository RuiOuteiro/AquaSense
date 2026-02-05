import pool from '../../utils/db'
import { requireAuth } from '../../utils/auth'

export default defineEventHandler(async (event) => {
  const user = requireAuth(event)
  const body = await readBody(event)
  const { chat_id, activo } = body

  if (!chat_id || !chat_id.trim()) {
    throw createError({
      statusCode: 400,
      message: 'Chat ID é obrigatório'
    })
  }

  try {
    await pool.execute(
      'UPDATE utilizadores SET telegram_chat_id = ?, telegram_alertas = ? WHERE id = ?',
      [chat_id.trim(), activo !== false ? 1 : 0, user.id]
    )

    return {
      success: true,
      message: 'Telegram configurado com sucesso!'
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
