/**
 * Composable para gestão de aquários
 * 
 * Gere operações CRUD de aquários do utilizador.
 * 
 * @ficheiro composables/useAquarios.ts
 * @autor AquaSense Team
 */

import type { Aquario, NovoAquario } from '~/types'

// Estado global partilhado
const aquarios = ref<Aquario[]>([])
const novoAquario = ref<NovoAquario>({
  nome: '',
  device_id: '',
  descricao: ''
})
const mostrarFormulario = ref(false)
const erro = ref('')
const sucesso = ref('')

export function useAquarios() {
  /**
   * Obtém aquários do utilizador
   */
  async function obterAquarios(): Promise<void> {
    try {
      const res = await $fetch<{ success: boolean; data?: Aquario[]; aquarios?: Aquario[] }>('/api/aquarios')
      if (res.success) {
        aquarios.value = res.data || res.aquarios || []
      }
    } catch (e) {
      console.error('[Aquários] Erro ao obter:', e)
    }
  }

  /**
   * Adiciona novo aquário
   */
  async function adicionarAquario(): Promise<boolean> {
    if (!novoAquario.value.nome.trim()) {
      erro.value = 'O nome é obrigatório'
      return false
    }
    
    try {
      const res = await $fetch<{ success: boolean }>('/api/aquarios', {
        method: 'POST',
        body: novoAquario.value
      })
      
      if (res.success) {
        sucesso.value = 'Aquário adicionado com sucesso'
        novoAquario.value = { nome: '', device_id: '', descricao: '' }
        mostrarFormulario.value = false
        await obterAquarios()
        setTimeout(() => { sucesso.value = '' }, 3000)
        return true
      }
    } catch (e: any) {
      erro.value = e.data?.message || 'Erro ao adicionar aquário'
    }
    return false
  }

  /**
   * Guarda alterações num aquário
   */
  async function guardarAquario(aquario: Aquario): Promise<boolean> {
    try {
      await $fetch(`/api/aquarios/${aquario.id}`, {
        method: 'PUT',
        body: {
          nome: aquario.nome,
          descricao: aquario.descricao,
          device_id: aquario.device_id
        }
      })
      sucesso.value = 'Aquário actualizado'
      setTimeout(() => { sucesso.value = '' }, 3000)
      return true
    } catch (e: any) {
      erro.value = e.data?.message || 'Erro ao guardar aquário'
      return false
    }
  }

  /**
   * Elimina um aquário
   */
  async function eliminarAquario(id: number): Promise<boolean> {
    if (!confirm('Tem a certeza que deseja eliminar este aquário?')) {
      return false
    }
    
    try {
      await $fetch(`/api/aquarios/${id}`, { method: 'DELETE' })
      sucesso.value = 'Aquário eliminado'
      await obterAquarios()
      return true
    } catch (e: any) {
      erro.value = e.data?.message || 'Erro ao eliminar aquário'
      return false
    }
  }

  /**
   * Limpa mensagens
   */
  function limparMensagens(): void {
    erro.value = ''
    sucesso.value = ''
  }

  /**
   * Abre formulário de novo aquário
   */
  function abrirFormulario(): void {
    novoAquario.value = { nome: '', device_id: '', descricao: '' }
    mostrarFormulario.value = true
    limparMensagens()
  }

  /**
   * Fecha formulário
   */
  function fecharFormulario(): void {
    mostrarFormulario.value = false
  }

  return {
    aquarios: readonly(aquarios),
    novoAquario,
    mostrarFormulario,
    erro,
    sucesso,
    obterAquarios,
    adicionarAquario,
    guardarAquario,
    eliminarAquario,
    limparMensagens,
    abrirFormulario,
    fecharFormulario
  }
}
