import pool from '../../utils/db'
import { requireAuth } from '../../utils/auth'

export default defineEventHandler(async (event) => {
  const user = requireAuth(event)
  const body = await readBody(event)
  const { nome, descricao, device_id } = body

  if (!nome) {
    throw createError({
      statusCode: 400,
      message: 'Nome do aquário é obrigatório'
    })
  }

  try {
    const [result] = await pool.execute(
      'INSERT INTO aquarios (utilizador_id, nome, descricao, device_id) VALUES (?, ?, ?, ?)',
      [user.id, nome, descricao || null, device_id || null]
    )

    const aquarioId = (result as any).insertId

    await pool.execute(
      'INSERT INTO configuracoes (id, aquario_id) VALUES (?, ?)',
      [aquarioId, aquarioId]
    )

    return {
      success: true,
      message: 'Aquário criado com sucesso',
      aquario: {
        id: aquarioId,
        nome,
        descricao,
        device_id
      }
    }
  } catch (error: any) {
    console.error('[AQUARIOS POST] Erro:', error.message)
    throw createError({
      statusCode: 500,
      message: 'Erro ao criar aquário'
    })
  }
})
