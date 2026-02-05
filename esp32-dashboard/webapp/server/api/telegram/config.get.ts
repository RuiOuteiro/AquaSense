import pool from '../../utils/db'
import { requireAuth } from '../../utils/auth'

export default defineEventHandler(async (event) => {
  const user = requireAuth(event)

  try {
    const [rows] = await pool.execute(
      'SELECT telegram_chat_id, telegram_alertas FROM utilizadores WHERE id = ?',
      [user.id]
    )

    const users = rows as any[]
    if (users.length === 0) {
      throw createError({
        statusCode: 404,
        message: 'Utilizador não encontrado'
      })
    }

    return {
      success: true,
      data: {
        chat_id: String(users[0].telegram_chat_id || ''),
        activo: Boolean(users[0].telegram_alertas)
      }
    }
  } catch (error: any) {
    if (error.statusCode) throw error
    
    console.error('[TELEGRAM CONFIG] Erro:', error.message)
    throw createError({
      statusCode: 500,
      message: 'Erro ao obter configuração Telegram'
    })
  }
})
