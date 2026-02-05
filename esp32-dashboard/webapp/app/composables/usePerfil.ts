/**
 * Composable para gestão do perfil do utilizador
 * 
 * Gere actualização de dados pessoais e alteração
 * de palavra-passe.
 * 
 * @ficheiro composables/usePerfil.ts
 * @autor AquaSense Team
 */

import type { FormularioPerfil } from '~/types'
import { useAutenticacao } from './useAutenticacao'

// Estado global partilhado
const formulario = ref<FormularioPerfil>({
  nome: '',
  email: '',
  currentPassword: '',
  newPassword: ''
})
const aCarregar = ref(false)
const erro = ref('')
const sucesso = ref('')

export function usePerfil() {
  const { utilizadorActual, obterUtilizadorActual } = useAutenticacao()

  /**
   * Inicializa formulário com dados do utilizador
   */
  function inicializarFormulario(): void {
    if (utilizadorActual.value) {
      formulario.value.nome = utilizadorActual.value.nome
      formulario.value.email = utilizadorActual.value.email
    }
    erro.value = ''
    sucesso.value = ''
  }

  /**
   * Limpa mensagens
   */
  function limparMensagens(): void {
    erro.value = ''
    sucesso.value = ''
  }

  /**
   * Actualiza nome do utilizador
   */
  async function actualizarNome(): Promise<void> {
    limparMensagens()
    aCarregar.value = true
    try {
      const res = await $fetch<{ success: boolean }>('/api/auth/update-name', {
        method: 'POST',
        body: { nome: formulario.value.nome }
      })
      if (res.success) {
        sucesso.value = 'Nome actualizado com sucesso'
        await obterUtilizadorActual()
        setTimeout(() => { sucesso.value = '' }, 3000)
      }
    } catch (e: any) {
      erro.value = e.data?.message || 'Erro ao actualizar nome'
    } finally {
      aCarregar.value = false
    }
  }

  /**
   * Actualiza email do utilizador
   */
  async function actualizarEmail(): Promise<void> {
    limparMensagens()
    aCarregar.value = true
    try {
      const res = await $fetch<{ success: boolean }>('/api/auth/update-email', {
        method: 'POST',
        body: { email: formulario.value.email }
      })
      if (res.success) {
        sucesso.value = 'Email actualizado com sucesso'
        await obterUtilizadorActual()
        setTimeout(() => { sucesso.value = '' }, 3000)
      }
    } catch (e: any) {
      erro.value = e.data?.message || 'Erro ao actualizar email'
    } finally {
      aCarregar.value = false
    }
  }

  /**
   * Altera palavra-passe
   */
  async function alterarPalavraPasse(): Promise<void> {
    limparMensagens()
    
    if (!formulario.value.currentPassword || !formulario.value.newPassword) {
      erro.value = 'Preencha ambos os campos de palavra-passe'
      return
    }
    
    if (formulario.value.newPassword.length < 6) {
      erro.value = 'A nova palavra-passe deve ter pelo menos 6 caracteres'
      return
    }
    
    aCarregar.value = true
    try {
      const res = await $fetch<{ success: boolean }>('/api/auth/change-password', {
        method: 'POST',
        body: {
          currentPassword: formulario.value.currentPassword,
          newPassword: formulario.value.newPassword
        }
      })
      if (res.success) {
        sucesso.value = 'Palavra-passe alterada com sucesso'
        formulario.value.currentPassword = ''
        formulario.value.newPassword = ''
      }
    } catch (e: any) {
      erro.value = e.data?.message || 'Erro ao alterar palavra-passe'
    } finally {
      aCarregar.value = false
    }
  }

  return {
    formulario,
    aCarregar: readonly(aCarregar),
    erro,
    sucesso,
    inicializarFormulario,
    limparMensagens,
    actualizarNome,
    actualizarEmail,
    alterarPalavraPasse
  }
}
