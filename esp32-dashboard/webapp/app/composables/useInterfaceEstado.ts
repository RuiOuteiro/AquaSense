/**
 * Composable para estado da interface
 * 
 * Gere estados de visibilidade de modais, menus e painéis.
 * 
 * @ficheiro composables/useInterfaceEstado.ts
 * @autor AquaSense Team
 */

// Estado global partilhado
const mostrarDefinicoes = ref(false)
const mostrarGraficos = ref(false)
const mostrarPerfil = ref(false)
const mostrarConsola = ref(false)
const mostrarMenuHamburguer = ref(false)
const horaActual = ref('')

export function useInterfaceEstado() {
  // ========== MODAL DEFINIÇÕES ==========
  function abrirDefinicoes(): void {
    mostrarDefinicoes.value = true
    document.body.style.overflow = 'hidden'
  }

  function fecharDefinicoes(): void {
    mostrarDefinicoes.value = false
    document.body.style.overflow = ''
  }

  // ========== MODAL GRÁFICOS ==========
  function abrirGraficos(): void {
    mostrarGraficos.value = true
    document.body.style.overflow = 'hidden'
  }

  function fecharGraficos(): void {
    mostrarGraficos.value = false
    document.body.style.overflow = ''
  }

  // ========== MODAL PERFIL ==========
  function abrirPerfil(): void {
    mostrarPerfil.value = true
    document.body.style.overflow = 'hidden'
  }

  function fecharPerfil(): void {
    mostrarPerfil.value = false
    document.body.style.overflow = ''
  }

  // ========== CONSOLA ==========
  function alternarConsola(): void {
    mostrarConsola.value = !mostrarConsola.value
  }

  function fecharConsola(): void {
    mostrarConsola.value = false
  }

  // ========== MENU HAMBÚRGUER ==========
  function alternarMenuHamburguer(): void {
    mostrarMenuHamburguer.value = !mostrarMenuHamburguer.value
  }

  function fecharMenuHamburguer(): void {
    mostrarMenuHamburguer.value = false
  }

  // ========== RELÓGIO ==========
  function actualizarHora(): void {
    horaActual.value = new Date().toLocaleTimeString('pt-PT', {
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  return {
    // Estado
    mostrarDefinicoes: readonly(mostrarDefinicoes),
    mostrarGraficos: readonly(mostrarGraficos),
    mostrarPerfil: readonly(mostrarPerfil),
    mostrarConsola: readonly(mostrarConsola),
    mostrarMenuHamburguer: readonly(mostrarMenuHamburguer),
    horaActual: readonly(horaActual),
    
    // Definições
    abrirDefinicoes,
    fecharDefinicoes,
    
    // Gráficos
    abrirGraficos,
    fecharGraficos,
    
    // Perfil
    abrirPerfil,
    fecharPerfil,
    
    // Consola
    alternarConsola,
    fecharConsola,
    
    // Menu
    alternarMenuHamburguer,
    fecharMenuHamburguer,
    
    // Relógio
    actualizarHora
  }
}
