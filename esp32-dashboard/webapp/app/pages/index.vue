<!--
  Página Principal do Dashboard AquaSense
  
  @ficheiro pages/index.vue
  @autor AquaSense Team
  @versao 2.0.0 (Refactorado)
-->
<template>
  <div class="app">
    <!-- Popup de Alertas -->
    <AlertPopup
      v-for="alert in alerts"
      :key="alert.id"
      :visible="true"
      :type="alert.type"
      :title="alert.title"
      :message="alert.message"
      @close="dismissAlert(alert.id)"
    />
    
    <!-- Cabeçalho -->
    <Cabecalho
      :ligado="ligado"
      :menu-aberto="mostrarMenuHamburguer"
      @alternar-menu="alternarMenuHamburguer"
      @abrir-graficos="abrirGraficos"
      @alternar-consola="alternarConsola"
      @abrir-definicoes="abrirDefinicoes"
      @abrir-perfil="abrirPerfil"
      @terminar-sessao="terminarSessao"
    />
    
    <!-- Painel da Consola -->
    <PainelConsola
      :visivel="mostrarConsola"
      :registos="[...registos]"
      @fechar="fecharConsola"
      @limpar="limparConsola"
    />
    
    <!-- Conteúdo Principal -->
    <main class="main">
      <!-- Secção de Iluminação -->
      <SeccaoIluminacao
        :config="config"
        :luz-branca-ligada="luzBrancaLigada"
        :luz-noturna-ligada="luzNoturnaLigada"
        :hora-actual="horaActual"
        :fotoperiodo="fotoperiodoTotal"
        @alternar-luz-branca="alternarLuzBranca"
        @alternar-luz-noturna="alternarLuzNoturna"
      />
      
      <!-- Secção de Parâmetros -->
      <SeccaoParametros
        :temperatura-agua="temperaturaAgua"
        :temperatura-ambiente="temperaturaAmbiente"
        :ph="ph"
        :tensao-p-h="tensaoPH"
        :turbidez="turbidez"
        :tensao-turbidez="tensaoTurbidez"
        :humidade="humidade"
        :limite-temp-alto="config.tempLigar"
        :limite-temp-baixo="config.tempDesligar"
      />
      
      <!-- Secção da Ventoinha -->
      <section class="fan-section">
        <CartaoVentoinha
          :ligada="ventoinhaLigada"
          :modo-manual="config.modoManual"
          :temp-ligar="config.tempLigar"
          :temp-desligar="config.tempDesligar"
        />
      </section>
      
      <!-- Secção de Histórico -->
      <SeccaoHistorico
        :leituras="[...leituras]"
        :limite="10"
      />
    </main>
    
    <!-- Rodapé -->
    <Rodape :ultima-actualizacao="ultimaActualizacao" />
    
    <!-- Modal de Definições -->
    <ModalDefinicoes
      :visivel="mostrarDefinicoes"
      :config="config"
      :alert-config="alertConfig"
      :sugestao-i-a="sugestaoIA ? { ...sugestaoIA, accoes: sugestaoIA.accoes ? [...sugestaoIA.accoes] : undefined } : null"
      @fechar="fecharDefinicoes"
      @definir-modo-manual-ventoinha="definirModoManualVentoinha"
      @definir-estado-ventoinha="definirEstadoVentoinha"
      @actualizar-temp-ligar="actualizarTempLigar"
      @actualizar-temp-desligar="actualizarTempDesligar"
      @definir-modo-luz="definirModoLuz"
      @definir-estado-luz-manual="definirEstadoLuzManual"
      @actualizar-horario-luz-branca="actualizarHorarioLuzBranca"
      @iniciar-ciclo-luz="iniciarCicloLuz"
      @actualizar-intensidade="actualizarIntensidade"
      @guardar-intensidade="guardarIntensidade"
      @obter-sugestao-i-a="obterSugestaoIA"
      @aplicar-sugestao-i-a="aplicarSugestaoIA"
      @definir-modo-luz-noturna="definirModoLuzNoturna"
      @definir-estado-luz-noturna-manual="definirEstadoLuzNoturnaManual"
      @actualizar-horario-luz-noturna="actualizarHorarioLuzNoturna"
      @iniciar-ciclo-luz-noturna="iniciarCicloLuzNoturna"
      @actualizar-alerta-activo="actualizarAlertaActivo"
      @actualizar-alerta-temp-min="actualizarAlertaTempMin"
      @actualizar-alerta-temp-max="actualizarAlertaTempMax"
      @actualizar-alerta-ph-min="actualizarAlertaPhMin"
      @actualizar-alerta-ph-max="actualizarAlertaPhMax"
      @actualizar-alerta-turbidez-max="actualizarAlertaTurbidezMax"
    />
    
    <!-- Modal de Gráficos -->
    <ModalGraficos
      :visivel="mostrarGraficos"
      :periodo="periodo"
      :a-carregar="aCarregarGraficos"
      :opcoes-temperatura="opcoesTemperatura"
      :series-temperatura="seriesTemperatura"
      :opcoes-p-h="opcoesPH"
      :series-p-h="seriesPH"
      :opcoes-turbidez="opcoesTurbidez"
      :series-turbidez="seriesTurbidez"
      :opcoes-luz-branca="opcoesLuzBranca"
      :series-luz-branca="seriesLuzBranca"
      :opcoes-luz-noturna="opcoesLuzNoturna"
      :series-luz-noturna="seriesLuzNoturna"
      @fechar="fecharGraficos"
      @alterar-periodo="alterarPeriodo"
    />
    
    <!-- Modal de Perfil -->
    <ModalPerfil
      :visivel="mostrarPerfil"
      :formulario="formularioPerfil"
      :telegram="configuracaoTelegram"
      :aquarios="[...aquarios].map(a => ({...a}))"
      :novo-aquario="novoAquario"
      :mostrar-formulario-aquario="mostrarFormularioAquario"
      :a-carregar="aCarregarPerfil"
      :a-carregar-telegram="aCarregarTelegram"
      :erro="erroPerfil"
      :sucesso="sucessoPerfil"
      @fechar="fecharPerfil"
      @actualizar-nome="actualizarNome"
      @actualizar-email="actualizarEmail"
      @alterar-palavra-passe="alterarPalavraPasse"
      @testar-telegram="testarTelegram"
      @guardar-telegram="guardarTelegram"
      @abrir-formulario-aquario="abrirFormularioAquario"
      @fechar-formulario-aquario="fecharFormularioAquario"
      @adicionar-aquario="adicionarAquario"
      @guardar-aquario="guardarAquario"
      @eliminar-aquario="eliminarAquario"
    />
  </div>
</template>

<script setup lang="ts">
/**
 * Script principal do Dashboard AquaSense
 * 
 * Coordena todos os composables e componentes da aplicação.
 */

// ========== COMPONENTES ==========
import AlertPopup from '~/components/AlertPopup.vue'
import Cabecalho from '~/components/layout/Cabecalho.vue'
import PainelConsola from '~/components/layout/PainelConsola.vue'
import Rodape from '~/components/layout/Rodape.vue'
import SeccaoIluminacao from '~/components/seccoes/SeccaoIluminacao.vue'
import SeccaoParametros from '~/components/seccoes/SeccaoParametros.vue'
import SeccaoHistorico from '~/components/seccoes/SeccaoHistorico.vue'
import CartaoVentoinha from '~/components/cartoes/CartaoVentoinha.vue'
import ModalDefinicoes from '~/components/modais/ModalDefinicoes.vue'
import ModalGraficos from '~/components/modais/ModalGraficos.vue'
import ModalPerfil from '~/components/modais/ModalPerfil.vue'

// ========== COMPOSABLES ==========
import { useAlerts } from '~/composables/useAlerts'
import { useConsola } from '~/composables/useConsola'
import { useDadosSensores } from '~/composables/useDadosSensores'
import { useConfiguracaoSistema } from '~/composables/useConfiguracaoSistema'
import { useGraficos } from '~/composables/useGraficos'
import { useAutenticacao } from '~/composables/useAutenticacao'
import { usePerfil } from '~/composables/usePerfil'
import { useAquarios } from '~/composables/useAquarios'
import { useTelegram } from '~/composables/useTelegram'
import { useInterfaceEstado } from '~/composables/useInterfaceEstado'

// ========== UTILITÁRIOS ==========
import { INTERVALO_DADOS, INTERVALO_LOGS, INTERVALO_RELOGIO } from '~/utils/constantes'
import { calcularFotoperiodo, formatarDuracaoLuz } from '~/utils/formatadores'

// ========== ALERTAS (existente) ==========
const { 
  alerts, 
  removeAlert: dismissAlert, 
  checkParameters, 
  alertConfig, 
  loadConfig: loadAlertConfig,
  updateConfig: actualizarConfigAlertas
} = useAlerts()

// ========== CONSOLA ==========
const { 
  registos, 
  adicionarRegisto, 
  limparConsola, 
  obterLogsESP32 
} = useConsola()

// ========== DADOS DOS SENSORES ==========
const {
  leituras,
  ultimaActualizacao,
  temperaturaAgua,
  temperaturaAmbiente,
  ph,
  tensaoPH,
  turbidez,
  tensaoTurbidez,
  humidade,
  ventoinhaLigada,
  luzBrancaLigada,
  luzNoturnaLigada,
  luzBrancaTempoLigada,
  ligado,
  obterDados
} = useDadosSensores()

// ========== CONFIGURAÇÃO DO SISTEMA ==========
const {
  config,
  sugestaoIA,
  carregarConfiguracao,
  guardarConfiguracao,
  guardarIntensidade,
  definirModoManualVentoinha,
  definirEstadoVentoinha,
  definirModoLuz,
  definirEstadoLuzManual,
  iniciarCicloLuz,
  alternarLuzBranca,
  actualizarHorarioLuzBranca,
  definirModoLuzNoturna,
  definirEstadoLuzNoturnaManual,
  iniciarCicloLuzNoturna,
  alternarLuzNoturna,
  actualizarHorarioLuzNoturna,
  obterSugestaoIA,
  aplicarSugestaoIA
} = useConfiguracaoSistema()

// ========== GRÁFICOS ==========
const {
  periodo,
  aCarregar: aCarregarGraficos,
  obterDadosGraficos,
  alterarPeriodo,
  opcoesTemperatura,
  seriesTemperatura,
  opcoesPH,
  seriesPH,
  opcoesTurbidez,
  seriesTurbidez,
  opcoesLuzBranca,
  seriesLuzBranca,
  opcoesLuzNoturna,
  seriesLuzNoturna
} = useGraficos()

// ========== AUTENTICAÇÃO ==========
const { terminarSessao, obterUtilizadorActual } = useAutenticacao()

// ========== PERFIL ==========
const {
  formulario: formularioPerfil,
  aCarregar: aCarregarPerfil,
  erro: erroPerfil,
  sucesso: sucessoPerfil,
  inicializarFormulario,
  actualizarNome,
  actualizarEmail,
  alterarPalavraPasse
} = usePerfil()

// ========== AQUÁRIOS ==========
const {
  aquarios,
  novoAquario,
  mostrarFormulario: mostrarFormularioAquario,
  obterAquarios,
  adicionarAquario,
  guardarAquario,
  eliminarAquario,
  abrirFormulario: abrirFormularioAquario,
  fecharFormulario: fecharFormularioAquario
} = useAquarios()

// ========== TELEGRAM ==========
const {
  configuracao: configuracaoTelegram,
  aCarregar: aCarregarTelegram,
  obterConfiguracao: obterConfiguracaoTelegram,
  guardarConfiguracao: guardarTelegram,
  testarEnvio: testarTelegram
} = useTelegram()

// ========== INTERFACE ==========
const {
  mostrarDefinicoes,
  mostrarGraficos,
  mostrarPerfil,
  mostrarConsola,
  mostrarMenuHamburguer,
  horaActual,
  abrirDefinicoes,
  fecharDefinicoes,
  abrirGraficos: abrirGraficosUI,
  fecharGraficos,
  abrirPerfil: abrirPerfilUI,
  fecharPerfil,
  alternarConsola,
  fecharConsola,
  alternarMenuHamburguer,
  fecharMenuHamburguer,
  actualizarHora
} = useInterfaceEstado()

// ========== COMPUTED ==========

/**
 * Calcula o fotoperíodo total baseado no modo
 */
const fotoperiodoTotal = computed(() => {
  if (config.luzModo === 'ciclo' || config.luzModo === 'ai') {
    return config.luzCicloHoras > 0 ? `${config.luzCicloHoras}h` : '--'
  }
  return calcularFotoperiodo(
    config.luzHoraLigar,
    config.luzMinutoLigar,
    config.luzHoraDesligar,
    config.luzMinutoDesligar
  )
})

/**
 * Duração da luz branca ligada
 */
const duracaoLuzBranca = computed(() => {
  return formatarDuracaoLuz(luzBrancaTempoLigada.value)
})

// ========== FUNÇÕES AUXILIARES ==========

/**
 * Abre modal de gráficos e carrega dados
 */
async function abrirGraficos() {
  abrirGraficosUI()
  fecharMenuHamburguer()
  await obterDadosGraficos()
}

/**
 * Abre modal de perfil e carrega dados
 */
async function abrirPerfil() {
  abrirPerfilUI()
  fecharMenuHamburguer()
  await obterUtilizadorActual()
  inicializarFormulario()
  await Promise.all([
    obterAquarios(),
    obterConfiguracaoTelegram()
  ])
}

/**
 * Actualiza temperatura de ligar ventoinha
 */
async function actualizarTempLigar(temp: number) {
  config.tempLigar = temp
  await guardarConfiguracao()
}

/**
 * Actualiza temperatura de desligar ventoinha
 */
async function actualizarTempDesligar(temp: number) {
  config.tempDesligar = temp
  await guardarConfiguracao()
}

/**
 * Actualiza intensidade da luz
 */
function actualizarIntensidade(valor: number) {
  config.luzIntensidade = valor
}

/**
 * Actualiza configuração de alertas
 */
function actualizarAlertaActivo(activo: boolean) {
  actualizarConfigAlertas({ enabled: activo })
}

function actualizarAlertaTempMin(valor: number) {
  actualizarConfigAlertas({ tempMin: valor })
}

function actualizarAlertaTempMax(valor: number) {
  actualizarConfigAlertas({ tempMax: valor })
}

function actualizarAlertaPhMin(valor: number) {
  actualizarConfigAlertas({ phMin: valor })
}

function actualizarAlertaPhMax(valor: number) {
  actualizarConfigAlertas({ phMax: valor })
}

function actualizarAlertaTurbidezMax(valor: number) {
  actualizarConfigAlertas({ turbidezMax: valor })
}

// ========== CICLO DE VIDA ==========
onMounted(async () => {
  adicionarRegisto('AquaSense Dashboard iniciado', 'success')
  adicionarRegisto('A carregar configuração...', 'info')
  
  // Carregar dados iniciais
  await loadAlertConfig()
  await carregarConfiguracao()
  await obterDados()
  
  // Verificar parâmetros
  checkParameters({
    temperatura: temperaturaAgua.value,
    ph: ph.value,
    turbidez: turbidez.value,
    humidade: humidade.value
  })
  
  // Intervalos de actualização
  setInterval(obterDados, INTERVALO_DADOS)
  setInterval(obterLogsESP32, INTERVALO_LOGS)
  
  // Actualizar relógio
  actualizarHora()
  setInterval(actualizarHora, INTERVALO_RELOGIO)
})

// Verificar parâmetros quando mudam
watch([temperaturaAgua, ph, turbidez, humidade], () => {
  checkParameters({
    temperatura: temperaturaAgua.value,
    ph: ph.value,
    turbidez: turbidez.value,
    humidade: humidade.value
  })
})
</script>

<style>
@import '~/assets/css/main.css';

.aplicacao {
  min-height: 100vh;
  background: linear-gradient(135deg, #0c1222 0%, #1a1f35 100%);
  color: #e2e8f0;
  font-family: 'Inter', -apple-system, sans-serif;
}

.conteudo-principal {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
}

.seccao {
  margin-bottom: 32px;
}

.seccao-titulo {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 1.125rem;
  font-weight: 600;
  color: #e2e8f0;
  margin-bottom: 16px;
}

.seccao-titulo-icone {
  font-size: 1.5rem;
}
/* Estilos adicionais removidos - usar dashboard.css */
</style>
