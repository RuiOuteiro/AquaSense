import pool from '../../utils/db'
import { requireAuth } from '../../utils/auth'

export default defineEventHandler(async (event) => {
  const user = requireAuth(event)
  const id = getRouterParam(event, 'id')

  if (!id) {
    throw createError({
      statusCode: 400,
      message: 'ID do aquário é obrigatório'
    })
  }

  try {
    const [existing] = await pool.execute(
      'SELECT id FROM aquarios WHERE id = ? AND utilizador_id = ?',
      [id, user.id]
    )

    if ((existing as any[]).length === 0) {
      throw createError({
        statusCode: 404,
        message: 'Aquário não encontrado'
      })
    }

    await pool.execute(
      'UPDATE aquarios SET ativo = 0 WHERE id = ?',
      [id]
    )

    return {
      success: true,
      message: 'Aquário removido com sucesso'
    }
  } catch (error: any) {
    if (error.statusCode) throw error
    console.error('[AQUARIO DELETE] Erro:', error.message)
    throw createError({
      statusCode: 500,
      message: 'Erro ao remover aquário'
    })
  }
})
