<!--
  Componente: CartaoLuzNoturna
  Descrição: Cartão de controlo da luz noturna (azul)
  
  @ficheiro components/cartoes/CartaoLuzNoturna.vue
  @autor AquaSense Team
-->
<template>
  <div class="cartao cartao-luz noturna" :class="{ ligado: ligada }">
    <div class="cartao-luz-cabecalho">
      <div class="cartao-luz-titulo">
        <div class="cartao-luz-icone">
          <span class="material-icons-outlined">nightlight</span>
        </div>
        <div>
          <div class="cartao-luz-nome">Luz Noturna</div>
          <div class="cartao-luz-estado">
            {{ ligada ? 'LIGADA' : 'DESLIGADA' }}
          </div>
        </div>
      </div>
      
      <button 
        class="botao-alternar"
        :class="{ activo: ligada }"
        @click="$emit('alternar')"
      >
        <span class="material-icons-outlined">{{ ligada ? 'pause' : 'play_arrow' }}</span>
      </button>
    </div>
    
    <div class="cartao-luz-info">
      <div class="info-item">
        <span class="info-etiqueta">Modo</span>
        <span class="info-valor">{{ modoTexto }}</span>
      </div>
    </div>
    
    <div v-if="mostrarHorario" class="cartao-luz-horario">
      <span class="material-icons-outlined">schedule</span>
      <span>{{ horaLigar }}</span>
      <span class="material-icons-outlined">arrow_forward</span>
      <span>{{ horaDesligar }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { ModoLuzNoturna } from '~/types'
import { formatarHora, obterHoraInicioCiclo, obterHoraFimCiclo } from '~/utils/formatadores'

/**
 * Props do componente
 */
const props = defineProps<{
  /** Luz está ligada */
  ligada: boolean
  /** Modo actual */
  modo: ModoLuzNoturna
  /** Hora de ligar (modo horário) */
  horaLigarH?: number
  horaLigarM?: number
  /** Hora de desligar (modo horário) */
  horaDesligarH?: number
  horaDesligarM?: number
  /** Início do ciclo */
  cicloInicio?: string | null
  /** Horas do ciclo */
  cicloHoras?: number
}>()

/**
 * Eventos emitidos
 */
defineEmits<{
  'alternar': []
}>()

/**
 * Texto do modo
 */
const modoTexto = computed(() => {
  const modos: Record<ModoLuzNoturna, string> = {
    manual: 'Manual',
    horario: 'Horário',
    ciclo: 'Ciclo'
  }
  return modos[props.modo] || props.modo
})

/**
 * Mostrar horário
 */
const mostrarHorario = computed(() => {
  return props.modo === 'horario' || props.modo === 'ciclo'
})

/**
 * Hora de ligar formatada
 */
const horaLigar = computed(() => {
  if (props.modo === 'ciclo') {
    return obterHoraInicioCiclo(props.cicloInicio ?? null)
  }
  return formatarHora(props.horaLigarH ?? 20, props.horaLigarM ?? 0)
})

/**
 * Hora de desligar formatada
 */
const horaDesligar = computed(() => {
  if (props.modo === 'ciclo') {
    return obterHoraFimCiclo(props.cicloInicio ?? null, props.cicloHoras ?? 8)
  }
  return formatarHora(props.horaDesligarH ?? 8, props.horaDesligarM ?? 0)
})
</script>

<style scoped>
.cartao {
  background: linear-gradient(145deg, rgba(30, 41, 59, 0.9), rgba(15, 23, 42, 0.95));
  border: 1px solid rgba(148, 163, 184, 0.1);
  border-radius: 16px;
  padding: 20px;
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.cartao:hover {
  border-color: rgba(96, 165, 250, 0.4);
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
}

.cartao-luz.noturna::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, #60a5fa, #3b82f6);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.cartao-luz.noturna.ligado::before {
  opacity: 1;
}

.cartao-luz.noturna.ligado {
  border-color: rgba(96, 165, 250, 0.3);
  box-shadow: 0 0 20px rgba(96, 165, 250, 0.1);
}

.cartao-luz-cabecalho {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.cartao-luz-titulo {
  display: flex;
  align-items: center;
  gap: 12px;
}

.cartao-luz-icone {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(96, 165, 250, 0.15);
  color: #60a5fa;
  transition: all 0.3s ease;
}

.cartao-luz-icone .material-icons-outlined {
  font-size: 24px;
}

.cartao-luz.noturna.ligado .cartao-luz-icone {
  background: #60a5fa;
  color: #000;
  box-shadow: 0 0 20px rgba(96, 165, 250, 0.5);
}

.cartao-luz-nome {
  font-size: 1rem;
  font-weight: 600;
  color: #e2e8f0;
}

.cartao-luz-estado {
  font-size: 0.75rem;
  color: #64748b;
}

.cartao-luz.noturna.ligado .cartao-luz-estado {
  color: #60a5fa;
}

.botao-alternar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: none;
  background: rgba(51, 65, 85, 0.5);
  color: #94a3b8;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.botao-alternar .material-icons-outlined {
  font-size: 20px;
}

.botao-alternar:hover {
  background: rgba(71, 85, 105, 0.6);
}

.botao-alternar.activo {
  background: #60a5fa;
  color: #000;
}

.cartao-luz-info {
  display: flex;
  gap: 24px;
  margin-bottom: 12px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.info-etiqueta {
  font-size: 0.625rem;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.info-valor {
  font-size: 0.9rem;
  font-weight: 600;
  color: #e2e8f0;
}

.cartao-luz-horario {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.85rem;
  color: #94a3b8;
  padding-top: 12px;
  border-top: 1px solid rgba(148, 163, 184, 0.1);
}

.cartao-luz-horario .material-icons-outlined {
  font-size: 16px;
  color: #64748b;
}
</style>
