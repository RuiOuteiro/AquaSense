/**
 * Composable para gestão de autenticação
 * 
 * Gere o estado do utilizador actual e operações
 * de login/logout.
 * 
 * @ficheiro composables/useAutenticacao.ts
 * @autor AquaSense Team
 */

import type { Utilizador } from '~/types'

// Estado global partilhado
const utilizadorActual = ref<Utilizador | null>(null)

export function useAutenticacao() {
  /**
   * Obtém utilizador actual
   */
  async function obterUtilizadorActual(): Promise<Utilizador | null> {
    try {
      const res = await $fetch<{ success: boolean; user: Utilizador }>('/api/auth/me')
      if (res.success && res.user) {
        utilizadorActual.value = res.user
        return res.user
      }
    } catch {
      utilizadorActual.value = null
    }
    return null
  }

  /**
   * Termina sessão
   */
  async function terminarSessao(): Promise<void> {
    try {
      await $fetch('/api/auth/logout', { method: 'POST' })
    } catch {
      // Ignorar erro
    }
    utilizadorActual.value = null
    navigateTo('/login')
  }

  /**
   * Verifica se utilizador está autenticado
   */
  const estaAutenticado = computed(() => utilizadorActual.value !== null)

  return {
    utilizadorActual: readonly(utilizadorActual),
    estaAutenticado,
    obterUtilizadorActual,
    terminarSessao
  }
}
