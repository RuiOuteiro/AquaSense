import pool from '../../utils/db'
import { getAuthUser } from '../../utils/auth'

export default defineEventHandler(async (event) => {
  const tokenUser = getAuthUser(event)
  
  if (!tokenUser) {
    throw createError({
      statusCode: 401,
      message: 'Não autenticado'
    })
  }

  try {
    // Procurar dados actualizados do utilizador da BD
    const [users] = await pool.execute(
      'SELECT id, nome, email FROM utilizadores WHERE id = ? AND ativo = 1',
      [tokenUser.id]
    )
    
    const dbUsers = users as any[]
    if (dbUsers.length === 0) {
      throw createError({
        statusCode: 404,
        message: 'Utilizador não encontrado'
      })
    }
    
    const user = {
      id: dbUsers[0].id,
      nome: dbUsers[0].nome,
      email: dbUsers[0].email
    }

    // Procurar aquários do utilizador
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
    if (error.statusCode) throw error
    console.error('[AUTH ME] Erro:', error.message)
    throw createError({
      statusCode: 500,
      message: 'Erro ao obter dados do utilizador'
    })
  }
})
