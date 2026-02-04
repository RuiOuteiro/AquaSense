import pool from '../../utils/db'
import { requireAuth } from '../../utils/auth'

export default defineEventHandler(async (event) => {
  const user = requireAuth(event)
  const id = getRouterParam(event, 'id')
  const body = await readBody(event)
  const { nome, descricao, device_id } = body

  if (!id) {
    throw createError({
      statusCode: 400,
      message: 'ID do aquário é obrigatório'
    })
  }

  try {
    // Verificar se pertence ao utilizador
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

    // Actualizar
    await pool.execute(
      'UPDATE aquarios SET nome = COALESCE(?, nome), descricao = COALESCE(?, descricao), device_id = COALESCE(?, device_id) WHERE id = ?',
      [nome || null, descricao, device_id, id]
    )

    return {
      success: true,
      message: 'Aquário actualizado com sucesso'
    }
  } catch (error: any) {
    if (error.statusCode) throw error
    console.error('[AQUARIO PUT] Erro:', error.message)
    throw createError({
      statusCode: 500,
      message: 'Erro ao actualizar aquário'
    })
  }
})
