<!--
  Componente: ModalDefinicoes
  Descrição: Modal de definições do sistema (ventoinha, luzes, alertas)
  
  @ficheiro components/modais/ModalDefinicoes.vue
  @autor AquaSense Team
-->
<template>
  <ModalBase
    :visivel="visivel"
    titulo="Definições"
    icone="settings"
    classe-extra="settings-modal"
    @fechar="$emit('fechar')"
  >
    <!-- SECCÃO VENTOINHA -->
    <div class="settings-section">
      <h3 class="settings-section-title">
        <span class="material-icons-outlined">air</span>
        Ventoinha
      </h3>
      
      <div class="setting-group">
        <label>Modo de Operação</label>
        <div class="toggle-buttons">
          <button
            :class="{ active: !config.modoManual }"
            @click="$emit('definirModoManualVentoinha', false)"
          >
            Automático
          </button>
          <button
            :class="{ active: config.modoManual }"
            @click="$emit('definirModoManualVentoinha', true)"
          >
            Manual
          </button>
        </div>
      </div>
      
      <div v-if="config.modoManual" class="setting-group">
        <label>Estado da Ventoinha</label>
        <div class="toggle-buttons">
          <button
            :class="{ active: !config.ventoinhaManual }"
            @click="$emit('definirEstadoVentoinha', false)"
          >
            Desligada
          </button>
          <button
            :class="{ active: config.ventoinhaManual, success: config.ventoinhaManual }"
            @click="$emit('definirEstadoVentoinha', true)"
          >
            Ligada
          </button>
        </div>
      </div>
      
      <div v-else class="setting-group">
        <label>Limites de Temperatura</label>
        <div class="input-row">
          <div class="input-field">
            <span>Liga (°C)</span>
            <input 
              type="number" 
              :value="config.tempLigar"
              step="0.5"
              @change="$emit('actualizarTempLigar', Number(($event.target as HTMLInputElement).value))"
            />
          </div>
          <div class="input-field">
            <span>Desliga (°C)</span>
            <input 
              type="number" 
              :value="config.tempDesligar"
              step="0.5"
              @change="$emit('actualizarTempDesligar', Number(($event.target as HTMLInputElement).value))"
            />
          </div>
        </div>
      </div>
    </div>
    
    <!-- SECCÃO LUZ BRANCA -->
    <div class="settings-section">
      <h3 class="settings-section-title">
        <span class="material-icons-outlined">wb_sunny</span>
        Luz Branca
      </h3>
      
      <!-- Selector de Modo -->
      <div class="modos-selector">
        <button 
          v-for="modo in modosLuz" 
          :key="modo.valor"
          class="mode-btn"
          :class="{ active: config.luzModo === modo.valor }"
          @click="$emit('definirModoLuz', modo.valor)"
        >
          <span class="material-icons-outlined">{{ modo.icone }}</span>
          {{ modo.etiqueta }}
        </button>
      </div>
      
      <!-- Modo Manual -->
      <div v-if="config.luzModo === 'manual'" class="modo-conteudo">
        <div class="opcao-linha">
          <div class="opcao-info">
            <span class="opcao-titulo">Estado</span>
          </div>
          <Comutador 
            :model-value="config.luzEstado"
            @update:model-value="$emit('definirEstadoLuzManual', $event)"
          />
        </div>
      </div>
      
      <!-- Modo Horário -->
      <div v-else-if="config.luzModo === 'horario'" class="modo-conteudo">
        <div class="horarios-linha">
          <CampoHora
            etiqueta="Ligar"
            :hora="config.luzHoraLigar"
            :minuto="config.luzMinutoLigar"
            @update="(h, m) => $emit('actualizarHorarioLuzBranca', 'ligar', h, m)"
          />
          <CampoHora
            etiqueta="Desligar"
            :hora="config.luzHoraDesligar"
            :minuto="config.luzMinutoDesligar"
            @update="(h, m) => $emit('actualizarHorarioLuzBranca', 'desligar', h, m)"
          />
        </div>
      </div>
      
      <!-- Modo Ciclo -->
      <div v-else-if="config.luzModo === 'ciclo'" class="modo-conteudo">
        <p class="modo-descricao">Seleccione a duração do fotoperíodo:</p>
        <div class="ciclos-selector">
          <button 
            v-for="h in opcoesFotoperiodo" 
            :key="h"
            class="ciclo-botao"
            :class="{ activo: config.luzCicloHoras === h }"
            @click="$emit('iniciarCicloLuz', h)"
          >
            {{ h }}h
          </button>
        </div>
        <p v-if="config.luzCicloInicio" class="ciclo-info">
          Iniciado: {{ formatarCicloInicio(config.luzCicloInicio) }}
        </p>
      </div>
      
      <!-- Modo IA -->
      <div v-else-if="config.luzModo === 'ai'" class="setting-group ai-section">
        <div class="ai-card">
          <div class="ai-header">
            <span class="material-icons-outlined">psychology</span>
            <span>Ajuste Inteligente</span>
          </div>
          <p class="ai-desc">
            A IA analisa a turbidez e sugere ajustes de fotoperíodo,
            intensidade, TPA e alimentação.
          </p>
          <button class="ai-fetch-btn" @click="$emit('obterSugestaoIA')">
            <span class="material-icons-outlined">refresh</span>
            Obter Sugestão
          </button>
          
          <div v-if="sugestaoIA" class="ai-result">
            <!-- Alerta -->
            <div class="ai-alert" :class="'alert-' + sugestaoIA.severidade">
              <span class="material-icons-outlined">
                {{ sugestaoIA.severidade === 'critica' || sugestaoIA.severidade === 'alta' ? 'warning' : 'info' }}
              </span>
              <span>{{ sugestaoIA.razao?.replace(/\s*\(\d+%?\)/, '') }}</span>
            </div>
            
            <!-- Estatísticas principais -->
            <div class="ai-stats-grid">
              <div class="ai-stat-card">
                <span class="label">Turbidez</span>
                <span class="value" :class="sugestaoIA.severidade">
                  {{ sugestaoIA.input?.turbidez_actual?.toFixed(0) || '—' }}%
                </span>
              </div>
              <div class="ai-stat-card">
                <span class="label">Fotoperíodo</span>
                <span class="value highlight">{{ sugestaoIA.fotoperiodo_sugerido }}h</span>
                <span v-if="sugestaoIA.ajuste_horas !== 0" class="change">
                  {{ sugestaoIA.ajuste_horas > 0 ? '+' : '' }}{{ sugestaoIA.ajuste_horas }}h
                </span>
              </div>
              <div class="ai-stat-card">
                <span class="label">Intensidade</span>
                <span class="value">{{ sugestaoIA.intensidade_sugerida }}%</span>
              </div>
              <div v-if="sugestaoIA.tpa && sugestaoIA.tpa.percentagem > 0" class="ai-stat-card">
                <span class="label">TPA</span>
                <span class="value tpa" :class="sugestaoIA.tpa.urgencia">
                  {{ sugestaoIA.tpa.percentagem }}%
                </span>
                <span class="urgencia">{{ sugestaoIA.tpa.urgencia }}</span>
              </div>
            </div>
            
            <!-- TPA detalhado -->
            <div v-if="sugestaoIA.tpa && sugestaoIA.tpa.percentagem > 0" class="ai-tpa-detail">
              <span class="material-icons-outlined">water_drop</span>
              <div class="tpa-info">
                <span class="tpa-desc">{{ sugestaoIA.tpa.descricao }}</span>
                <span v-if="sugestaoIA.tpa.frequencia" class="tpa-freq">
                  Frequência: {{ sugestaoIA.tpa.frequencia }}
                  <span v-if="sugestaoIA.tpa.dias > 1">({{ sugestaoIA.tpa.dias }} dias)</span>
                </span>
              </div>
            </div>
            
            <!-- Botão aplicar -->
            <button class="ai-apply-btn" @click="$emit('aplicarSugestaoIA')">
              <span class="material-icons-outlined">check</span>
              Aplicar Sugestão
            </button>
          </div>
        </div>
      </div>
      
      <!-- Intensidade -->
      <div class="intensidade-secao">
        <label class="intensidade-etiqueta">Intensidade: {{ config.luzIntensidade }}%</label>
        <Deslizador
          :model-value="config.luzIntensidade"
          :min="0"
          :max="100"
          :mostrar-valor="false"
          @update:model-value="$emit('actualizarIntensidade', $event)"
          @change="$emit('guardarIntensidade')"
        />
      </div>
    </div>
    
    <!-- SECCÃO LUZ NOTURNA -->
    <div class="settings-section">
      <h3 class="settings-section-title">
        <span class="material-icons-outlined">nightlight</span>
        Luz Noturna
      </h3>
      
      <div class="modos-selector">
        <button 
          v-for="modo in modosLuzNoturna" 
          :key="modo.valor"
          class="mode-btn"
          :class="{ active: config.luzNoturnaModo === modo.valor }"
          @click="$emit('definirModoLuzNoturna', modo.valor)"
        >
          <span class="material-icons-outlined">{{ modo.icone }}</span>
          {{ modo.etiqueta }}
        </button>
      </div>
      
      <!-- Modo Manual -->
      <div v-if="config.luzNoturnaModo === 'manual'" class="modo-conteudo">
        <div class="opcao-linha">
          <div class="opcao-info">
            <span class="opcao-titulo">Estado</span>
          </div>
          <Comutador 
            :model-value="config.luzNoturnaEstado"
            @update:model-value="$emit('definirEstadoLuzNoturnaManual', $event)"
          />
        </div>
      </div>
      
      <!-- Modo Horário -->
      <div v-else-if="config.luzNoturnaModo === 'horario'" class="modo-conteudo">
        <div class="horarios-linha">
          <CampoHora
            etiqueta="Ligar"
            :hora="config.luzNoturnaHoraLigar"
            :minuto="config.luzNoturnaMinutoLigar"
            @update="(h, m) => $emit('actualizarHorarioLuzNoturna', 'ligar', h, m)"
          />
          <CampoHora
            etiqueta="Desligar"
            :hora="config.luzNoturnaHoraDesligar"
            :minuto="config.luzNoturnaMinutoDesligar"
            @update="(h, m) => $emit('actualizarHorarioLuzNoturna', 'desligar', h, m)"
          />
        </div>
      </div>
      
      <!-- Modo Ciclo -->
      <div v-else-if="config.luzNoturnaModo === 'ciclo'" class="modo-conteudo">
        <p class="modo-descricao">Seleccione a duração:</p>
        <div class="ciclos-selector">
          <button 
            v-for="h in opcoesFotoperiodo" 
            :key="h"
            class="ciclo-botao"
            :class="{ activo: config.luzNoturnaCicloHoras === h }"
            @click="$emit('iniciarCicloLuzNoturna', h)"
          >
            {{ h }}h
          </button>
        </div>
      </div>
    </div>
    
    <!-- SECCÃO ALERTAS -->
    <div class="settings-section">
      <h3 class="settings-section-title">
        <span class="material-icons-outlined">notifications</span>
        Alertas
      </h3>
      
      <div class="opcao-linha">
        <div class="opcao-info">
          <span class="opcao-titulo">Alertas Activos</span>
          <span class="opcao-descricao">Receber notificações de parâmetros fora do normal</span>
        </div>
        <Comutador 
          :model-value="alertConfig.enabled"
          @update:model-value="$emit('actualizarAlertaActivo', $event)"
        />
      </div>
      
      <div v-if="alertConfig.enabled" class="alertas-limites">
        <div class="limite-grupo">
          <label>Temperatura</label>
          <div class="limite-campos">
            <input 
              type="number" 
              :value="alertConfig.tempMin"
              class="campo-numero"
              @change="$emit('actualizarAlertaTempMin', Number(($event.target as HTMLInputElement).value))"
            />
            <span>-</span>
            <input 
              type="number" 
              :value="alertConfig.tempMax"
              class="campo-numero"
              @change="$emit('actualizarAlertaTempMax', Number(($event.target as HTMLInputElement).value))"
            />
            <span>°C</span>
          </div>
        </div>
        
        <div class="limite-grupo">
          <label>pH</label>
          <div class="limite-campos">
            <input 
              type="number" 
              step="0.1"
              :value="alertConfig.phMin"
              class="campo-numero"
              @change="$emit('actualizarAlertaPhMin', Number(($event.target as HTMLInputElement).value))"
            />
            <span>-</span>
            <input 
              type="number" 
              step="0.1"
              :value="alertConfig.phMax"
              class="campo-numero"
              @change="$emit('actualizarAlertaPhMax', Number(($event.target as HTMLInputElement).value))"
            />
          </div>
        </div>
        
        <div class="limite-grupo">
          <label>Turbidez máx.</label>
          <div class="limite-campos">
            <input 
              type="number" 
              :value="alertConfig.turbidezMax"
              class="campo-numero"
              @change="$emit('actualizarAlertaTurbidezMax', Number(($event.target as HTMLInputElement).value))"
            />
            <span>%</span>
          </div>
        </div>
      </div>
    </div>
  </ModalBase>
</template>

<script setup lang="ts">
import ModalBase from './ModalBase.vue'
import Comutador from '~/components/primitivos/Comutador.vue'
import Deslizador from '~/components/primitivos/Deslizador.vue'
import CampoHora from '~/components/primitivos/CampoHora.vue'
import type { ConfiguracaoSistema, SugestaoIA, ModoLuz, ModoLuzNoturna } from '~/types'
import type { AlertConfig } from '~/composables/useAlerts'
import { OPCOES_FOTOPERIODO } from '~/utils/constantes'

/**
 * Props do componente
 */
defineProps<{
  visivel: boolean
  config: ConfiguracaoSistema
  alertConfig: AlertConfig
  sugestaoIA: SugestaoIA | null
}>()

/**
 * Eventos emitidos
 */
defineEmits<{
  'fechar': []
  // Ventoinha
  'definirModoManualVentoinha': [activo: boolean]
  'definirEstadoVentoinha': [ligada: boolean]
  'actualizarTempLigar': [temp: number]
  'actualizarTempDesligar': [temp: number]
  // Luz branca
  'definirModoLuz': [modo: ModoLuz]
  'definirEstadoLuzManual': [ligada: boolean]
  'actualizarHorarioLuzBranca': [tipo: 'ligar' | 'desligar', hora: number, minuto: number]
  'iniciarCicloLuz': [horas: number]
  'actualizarIntensidade': [valor: number]
  'guardarIntensidade': []
  // IA
  'obterSugestaoIA': []
  'aplicarSugestaoIA': []
  // Luz noturna
  'definirModoLuzNoturna': [modo: ModoLuzNoturna]
  'definirEstadoLuzNoturnaManual': [ligada: boolean]
  'actualizarHorarioLuzNoturna': [tipo: 'ligar' | 'desligar', hora: number, minuto: number]
  'iniciarCicloLuzNoturna': [horas: number]
  // Alertas
  'actualizarAlertaActivo': [activo: boolean]
  'actualizarAlertaTempMin': [valor: number]
  'actualizarAlertaTempMax': [valor: number]
  'actualizarAlertaPhMin': [valor: number]
  'actualizarAlertaPhMax': [valor: number]
  'actualizarAlertaTurbidezMax': [valor: number]
}>()

const opcoesFotoperiodo = OPCOES_FOTOPERIODO

const modosLuz = [
  { valor: 'manual' as ModoLuz, etiqueta: 'Manual', icone: 'pan_tool' },
  { valor: 'horario' as ModoLuz, etiqueta: 'Horário', icone: 'schedule' },
  { valor: 'ciclo' as ModoLuz, etiqueta: 'Ciclo', icone: 'autorenew' },
  { valor: 'ai' as ModoLuz, etiqueta: 'IA', icone: 'smart_toy' }
]

const modosLuzNoturna = [
  { valor: 'manual' as ModoLuzNoturna, etiqueta: 'Manual', icone: 'pan_tool' },
  { valor: 'horario' as ModoLuzNoturna, etiqueta: 'Horário', icone: 'schedule' },
  { valor: 'ciclo' as ModoLuzNoturna, etiqueta: 'Ciclo', icone: 'autorenew' }
]

function formatarCicloInicio(inicio: string): string {
  return new Date(inicio).toLocaleString('pt-PT', {
    day: '2-digit',
    month: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>

<style scoped>
/* Secções */
.settings-section {
  background: rgba(51, 65, 85, 0.3);
  border-radius: 16px;
  padding: 1.25rem;
  margin-bottom: 1rem;
}

.settings-section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 1rem;
  font-weight: 600;
  color: #f1f5f9;
  margin-bottom: 1rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid rgba(51, 65, 85, 0.5);
}

.settings-section-title .material-icons-outlined {
  font-size: 20px;
  color: #3b82f6;
}

/* Linhas de opção */
.opcao-linha {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 0;
  border-bottom: 1px solid rgba(51, 65, 85, 0.3);
}

.opcao-linha:last-child {
  border-bottom: none;
}

.opcao-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.opcao-titulo {
  font-size: 0.875rem;
  font-weight: 500;
  color: #e2e8f0;
}

.opcao-descricao {
  font-size: 0.75rem;
  color: #64748b;
}

/* Setting groups */
.setting-group {
  margin-bottom: 1rem;
}

.setting-group:last-child {
  margin-bottom: 0;
}

.setting-group label {
  display: block;
  font-size: 0.875rem;
  color: #94a3b8;
  margin-bottom: 0.75rem;
}

/* Toggle buttons */
.toggle-buttons {
  display: flex;
  gap: 8px;
}

.toggle-buttons button {
  flex: 1;
  padding: 12px 16px;
  border: none;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  background: #1e293b;
  color: #94a3b8;
}

.toggle-buttons button:hover:not(:disabled) {
  filter: brightness(1.3);
}

.toggle-buttons button.active {
  background: #3b82f6;
  color: white;
}

.toggle-buttons button.active.success {
  background: #10b981;
}

/* Input row and fields */
.input-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.input-field span {
  display: block;
  font-size: 0.75rem;
  color: #64748b;
  margin-bottom: 6px;
}

.input-field input {
  width: 100%;
  padding: 10px 12px;
  background: #1e293b;
  border: none;
  border-radius: 8px;
  color: white;
  font-size: 1rem;
  box-sizing: border-box;
  -moz-appearance: textfield;
  appearance: textfield;
}

.input-field input::-webkit-outer-spin-button,
.input-field input::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

.input-field input:focus {
  outline: 2px solid #3b82f6;
}

/* Campos de número (alertas) */
.campo-numero {
  width: 100%;
  padding: 10px 12px;
  background: #1e293b;
  border: none;
  border-radius: 8px;
  color: white;
  font-size: 1rem;
  box-sizing: border-box;
  -moz-appearance: textfield;
  appearance: textfield;
}

.campo-numero::-webkit-outer-spin-button,
.campo-numero::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

.campo-numero:focus {
  outline: 2px solid #3b82f6;
}

/* Botões de modo */
.modos-selector {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.mode-btn {
  flex: 1;
  min-width: 70px;
  padding: 12px 16px;
  border: none;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  background: #1e293b;
  color: #94a3b8;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

.mode-btn .material-icons-outlined {
  font-size: 18px;
}

.mode-btn:hover:not(:disabled) {
  filter: brightness(1.3);
}

.mode-btn.active {
  background: #3b82f6;
  color: white;
}

/* Conteúdo do modo */
.modo-conteudo {
  padding: 12px;
  background: rgba(30, 41, 59, 0.5);
  border-radius: 10px;
  margin-bottom: 16px;
}

.modo-descricao {
  font-size: 0.875rem;
  color: #94a3b8;
  margin-bottom: 12px;
}

.horarios-linha {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

/* Botões de ciclo */
.ciclos-selector {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.ciclo-botao {
  flex: 1;
  min-width: 50px;
  padding: 0.75rem 1rem;
  background: rgba(51, 65, 85, 0.5);
  border: 1px solid rgba(148, 163, 184, 0.2);
  border-radius: 8px;
  color: #94a3b8;
  font-weight: 600;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.ciclo-botao:hover {
  background: rgba(245, 158, 11, 0.1);
  border-color: rgba(245, 158, 11, 0.3);
  color: #f59e0b;
}

.ciclo-botao.activo {
  background: linear-gradient(135deg, #f59e0b, #fbbf24);
  border-color: #f59e0b;
  color: #0f172a;
  box-shadow: 0 0 12px rgba(245, 158, 11, 0.4);
}

.ciclo-info {
  margin-top: 12px;
  font-size: 0.75rem;
  color: #64748b;
}

/* Botões */
.botao {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px 20px;
  border: none;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.botao .material-icons-outlined {
  font-size: 18px;
}

.botao-primario {
  background: linear-gradient(135deg, #3b82f6, #6366f1);
  color: white;
}

.botao-primario:hover {
  filter: brightness(1.1);
}

.botao-sucesso {
  background: linear-gradient(135deg, #10b981, #059669);
  color: white;
  width: 100%;
  margin-top: 12px;
}

/* ========== SECÇÃO IA ========== */
.ai-section {
  margin-top: 0.5rem;
}

.ai-card {
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.1), rgba(99, 102, 241, 0.1));
  border: 1px solid rgba(139, 92, 246, 0.3);
  border-radius: 12px;
  padding: 1rem;
}

.ai-header {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #a78bfa;
  font-weight: 600;
  margin-bottom: 0.75rem;
}

.ai-header .material-icons-outlined {
  font-size: 20px;
}

.ai-desc {
  font-size: 0.8rem;
  color: #94a3b8;
  margin-bottom: 1rem;
  line-height: 1.4;
}

.ai-fetch-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  width: 100%;
  padding: 0.75rem;
  background: linear-gradient(135deg, #8b5cf6, #6366f1);
  border: none;
  border-radius: 8px;
  color: white;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.ai-fetch-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(139, 92, 246, 0.4);
}

.ai-fetch-btn .material-icons-outlined {
  font-size: 18px;
}

.ai-result {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid rgba(139, 92, 246, 0.2);
}

.ai-alert {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  border-radius: 8px;
  font-size: 0.85rem;
  margin-bottom: 1rem;
}

.ai-alert.alert-critica {
  background: rgba(239, 68, 68, 0.2);
  color: #fca5a5;
}

.ai-alert.alert-alta {
  background: rgba(245, 158, 11, 0.2);
  color: #fcd34d;
}

.ai-alert.alert-moderada {
  background: rgba(59, 130, 246, 0.2);
  color: #93c5fd;
}

.ai-alert.alert-normal {
  background: rgba(16, 185, 129, 0.2);
  color: #6ee7b7;
}

.ai-stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
  margin-bottom: 1rem;
}

.ai-stat-card {
  background: rgba(30, 41, 59, 0.8);
  padding: 12px;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.ai-stat-card .label {
  font-size: 0.7rem;
  color: #64748b;
  text-transform: uppercase;
}

.ai-stat-card .value {
  font-size: 1.2rem;
  font-weight: 700;
  color: #e2e8f0;
}

.ai-stat-card .value.highlight {
  color: #a78bfa;
}

.ai-stat-card .value.critica {
  color: #f87171;
}

.ai-stat-card .value.alta {
  color: #fbbf24;
}

.ai-stat-card .value.moderada {
  color: #60a5fa;
}

.ai-stat-card .value.normal {
  color: #34d399;
}

.ai-stat-card .value.tpa.urgente {
  color: #f87171;
}

.ai-stat-card .value.tpa.recomendado {
  color: #fbbf24;
}

.ai-stat-card .value.tpa.sugerido {
  color: #60a5fa;
}

.ai-stat-card .change {
  font-size: 0.75rem;
  color: #f87171;
}

.ai-stat-card .urgencia {
  font-size: 0.65rem;
  color: #94a3b8;
  text-transform: uppercase;
}

.ai-tpa-detail {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 12px;
  background: rgba(59, 130, 246, 0.1);
  border-radius: 8px;
  margin-bottom: 1rem;
}

.ai-tpa-detail .material-icons-outlined {
  font-size: 20px;
  color: #60a5fa;
}

.ai-tpa-detail .tpa-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.ai-tpa-detail .tpa-desc {
  font-size: 0.85rem;
  color: #93c5fd;
  font-weight: 500;
}

.ai-tpa-detail .tpa-freq {
  font-size: 0.75rem;
  color: #64748b;
}

.ai-apply-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  width: 100%;
  padding: 0.75rem;
  background: linear-gradient(135deg, #10b981, #059669);
  border: none;
  border-radius: 8px;
  color: white;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.ai-apply-btn:hover {
  filter: brightness(1.1);
}

.ai-apply-btn .material-icons-outlined {
  font-size: 18px;
}

/* Intensidade */
.intensidade-secao {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid rgba(51, 65, 85, 0.5);
}

.intensidade-etiqueta {
  display: block;
  font-size: 0.875rem;
  color: #94a3b8;
  margin-bottom: 8px;
}

/* Alertas */
.alertas-limites {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 12px;
}

.limite-grupo label {
  display: block;
  font-size: 0.75rem;
  color: #64748b;
  margin-bottom: 6px;
}

.limite-campos {
  display: flex;
  align-items: center;
  gap: 8px;
}

.limite-campos .campo-numero {
  width: 80px;
}

.limite-campos span {
  color: #64748b;
  font-size: 0.875rem;
}
</style>
