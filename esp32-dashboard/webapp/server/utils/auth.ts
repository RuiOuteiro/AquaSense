import bcrypt from 'bcryptjs'
import jwt from 'jsonwebtoken'
import type { H3Event } from 'h3'

const JWT_SECRET = process.env.JWT_SECRET || 'aquasense_super_secret_key_2026_change_in_production'
const JWT_EXPIRES_IN = '10y'

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

export async function hashPassword(password: string): Promise<string> {
  return bcrypt.hash(password, 10)
}

export async function verifyPassword(password: string, hash: string): Promise<boolean> {
  return bcrypt.compare(password, hash)
}

export function generateToken(user: UserPayload): string {
  return jwt.sign({ user }, JWT_SECRET, { expiresIn: JWT_EXPIRES_IN })
}

export function verifyToken(token: string): AuthToken | null {
  try {
    return jwt.verify(token, JWT_SECRET) as AuthToken
  } catch {
    return null
  }
}

export function getTokenFromEvent(event: H3Event): string | null {
  const authHeader = getHeader(event, 'authorization')
  if (authHeader?.startsWith('Bearer ')) {
    return authHeader.substring(7)
  }
  
  const cookies = parseCookies(event)
  return cookies.auth_token || null
}

export function getAuthUser(event: H3Event): UserPayload | null {
  const token = getTokenFromEvent(event)
  if (!token) return null
  
  const decoded = verifyToken(token)
  return decoded?.user || null
}

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

export function setAuthCookie(event: H3Event, token: string) {
  setCookie(event, 'auth_token', token, {
    httpOnly: true,
    secure: false,
    sameSite: 'lax',
    maxAge: 60 * 60 * 24 * 365 * 10,
    path: '/'
  })
}

export function clearAuthCookie(event: H3Event) {
  deleteCookie(event, 'auth_token', {
    path: '/'
  })
}
