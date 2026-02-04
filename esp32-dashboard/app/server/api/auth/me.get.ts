import pool from '../../utils/db'
import { getAuthUser } from '../../utils/auth'

export default defineEventHandler(async (event) => {
  const user = getAuthUser(event)
  
  if (!user) {
    throw createError({
      statusCode: 401,
      message: 'Não autenticado'
    })
  }

  try {
    // Buscar aquários do utilizador
    const [aquarios] = await pool.execute(
      'SELECT id, nome, descricao, device_id, criado_em FROM aquarios WHERE utilizador_id = ? AND ativo = 1',
      [user.id]
    )

    return {
      success: true,
      user,
      aquarios
    }
  } catch (error: any) {
    console.error('[AUTH ME] Erro:', error.message)
    throw createError({
      statusCode: 500,
      message: 'Erro ao obter dados do utilizador'
    })
  }
})
