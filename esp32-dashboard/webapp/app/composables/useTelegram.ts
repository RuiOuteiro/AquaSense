/**
 * Composable para gestão do Telegram
 * 
 * Gere configuração e teste de notificações Telegram.
 * 
 * @ficheiro composables/useTelegram.ts
 * @autor AquaSense Team
 */

import type { ConfiguracaoTelegram } from '~/types'

// Estado global partilhado
const configuracao = ref<ConfiguracaoTelegram>({
  chat_id: '',
  activo: false
})
const aCarregar = ref(false)
const erro = ref('')
const sucesso = ref('')

export function useTelegram() {
  /**
   * Obtém configuração do Telegram
   */
  async function obterConfiguracao(): Promise<void> {
    try {
      const res = await $fetch<{ 
        success: boolean
        data?: { chat_id: string; activo: boolean }
        config?: { chat_id: string; alertas_enabled: boolean }
      }>('/api/telegram/config')
      
      if (res.success) {
        if (res.data) {
          configuracao.value.chat_id = res.data.chat_id || ''
          configuracao.value.activo = res.data.activo || false
        } else if (res.config) {
          configuracao.value.chat_id = res.config.chat_id || ''
          configuracao.value.activo = res.config.alertas_enabled || false
        }
      }
    } catch (e) {
      console.error('[Telegram] Erro ao obter configuração:', e)
    }
  }

  /**
   * Guarda configuração do Telegram
   */
  async function guardarConfiguracao(): Promise<boolean> {
    limparMensagens()
    aCarregar.value = true
    
    try {
      const res = await $fetch<{ success: boolean }>('/api/telegram/config', {
        method: 'POST',
        body: {
          chat_id: configuracao.value.chat_id,
          activo: configuracao.value.activo
        }
      })
      
      if (res.success) {
        sucesso.value = 'Configuração Telegram guardada'
        setTimeout(() => { sucesso.value = '' }, 3000)
        return true
      }
    } catch (e: any) {
      erro.value = e.data?.message || 'Erro ao guardar configuração Telegram'
    } finally {
      aCarregar.value = false
    }
    return false
  }

  /**
   * Testa envio de mensagem
   */
  async function testarEnvio(): Promise<boolean> {
    limparMensagens()
    
    if (!configuracao.value.chat_id) {
      erro.value = 'Introduza o Chat ID primeiro'
      return false
    }
    
    aCarregar.value = true
    try {
      const res = await $fetch<{ success: boolean }>('/api/telegram/test', {
        method: 'POST',
        body: { chat_id: configuracao.value.chat_id }
      })
      
      if (res.success) {
        sucesso.value = 'Mensagem de teste enviada! Verifique o Telegram.'
        setTimeout(() => { sucesso.value = '' }, 5000)
        return true
      }
    } catch (e: any) {
      erro.value = e.data?.message || 'Erro ao enviar mensagem de teste'
    } finally {
      aCarregar.value = false
    }
    return false
  }

  /**
   * Limpa mensagens
   */
  function limparMensagens(): void {
    erro.value = ''
    sucesso.value = ''
  }

  return {
    configuracao,
    aCarregar: readonly(aCarregar),
    erro,
    sucesso,
    obterConfiguracao,
    guardarConfiguracao,
    testarEnvio,
    limparMensagens
  }
}
