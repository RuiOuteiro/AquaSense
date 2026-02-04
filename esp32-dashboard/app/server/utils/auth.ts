import bcrypt from 'bcryptjs'
import jwt from 'jsonwebtoken'
import type { H3Event } from 'h3'

// Chave secreta para JWT (em produção usar variável de ambiente)
const JWT_SECRET = process.env.JWT_SECRET || 'aquasense_super_secret_key_2026_change_in_production'
const JWT_EXPIRES_IN = '7d'

export interface UserPayload {
  id: number
  email: string
  nome: string
}

export interface AuthToken {
  user: UserPayload
  iat: number
  exp: number
}

/**
 * Hash de password com bcrypt
 */
export async function hashPassword(password: string): Promise<string> {
  return bcrypt.hash(password, 10)
}

/**
 * Verificar password
 */
export async function verifyPassword(password: string, hash: string): Promise<boolean> {
  return bcrypt.compare(password, hash)
}

/**
 * Gerar JWT token
 */
export function generateToken(user: UserPayload): string {
  return jwt.sign({ user }, JWT_SECRET, { expiresIn: JWT_EXPIRES_IN })
}

/**
 * Verificar e descodificar JWT token
 */
export function verifyToken(token: string): AuthToken | null {
  try {
    return jwt.verify(token, JWT_SECRET) as AuthToken
  } catch {
    return null
  }
}

/**
 * Obter token do header Authorization ou cookie
 */
export function getTokenFromEvent(event: H3Event): string | null {
  // Tentar header Authorization
  const authHeader = getHeader(event, 'authorization')
  if (authHeader?.startsWith('Bearer ')) {
    return authHeader.substring(7)
  }
  
  // Tentar cookie
  const cookies = parseCookies(event)
  return cookies.auth_token || null
}

/**
 * Obter utilizador autenticado do evento
 */
export function getAuthUser(event: H3Event): UserPayload | null {
  const token = getTokenFromEvent(event)
  if (!token) return null
  
  const decoded = verifyToken(token)
  return decoded?.user || null
}

/**
 * Middleware helper - requer autenticação
 */
export function requireAuth(event: H3Event): UserPayload {
  const user = getAuthUser(event)
  if (!user) {
    throw createError({
      statusCode: 401,
      message: 'Não autenticado'
    })
  }
  return user
}

/**
 * Definir cookie de autenticação
 */
export function setAuthCookie(event: H3Event, token: string) {
  setCookie(event, 'auth_token', token, {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'lax',
    maxAge: 60 * 60 * 24 * 7, // 7 dias
    path: '/'
  })
}

/**
 * Remover cookie de autenticação
 */
export function clearAuthCookie(event: H3Event) {
  deleteCookie(event, 'auth_token', {
    path: '/'
  })
}
