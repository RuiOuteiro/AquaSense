import pool from '../utils/db'

export default defineEventHandler(async () => {
  try {
    const [rows] = await pool.execute(
      'SELECT * FROM configuracoes WHERE id = 1'
    )
    
    return {
      success: true,
      data: (rows as any[])[0] || null
    }
  } catch (error: any) {
    throw createError({
      statusCode: 500,
      message: `Erro na base de dados: ${error.message}`
    })
  }
})
