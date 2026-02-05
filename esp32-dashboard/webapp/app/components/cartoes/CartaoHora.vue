<!--
  Componente: CartaoHora
  Descrição: Cartão que exibe a hora actual, fotoperíodo e tempo desligado
  
  @ficheiro components/cartoes/CartaoHora.vue
  @autor AquaSense Team
-->
<template>
  <div class="cartao cartao-hora">
    <div class="cartao-hora-cabecalho">
      <div class="cartao-hora-titulo">
        <div class="cartao-hora-icone">
          <span class="material-icons-outlined">schedule</span>
        </div>
        <div>
          <div class="cartao-hora-valor">{{ horaActual }}</div>
          <div class="cartao-hora-etiqueta">HORA ACTUAL</div>
        </div>
      </div>
    </div>
    
    <div class="cartao-hora-info">
      <div class="info-item">
        <span class="info-etiqueta">Fotoperíodo</span>
        <span class="info-valor amarelo">{{ fotoperiodo }}</span>
      </div>
      <div class="info-item">
        <span class="info-etiqueta">Desligado</span>
        <span class="info-valor azul">{{ tempoDesligado }}</span>
      </div>
    </div>
    
    <div class="cartao-hora-intensidade">
      <span class="material-icons-outlined">wb_sunny</span>
      <div class="intensidade-barra">
        <div class="intensidade-preenchido" :style="{ width: intensidade + '%' }"></div>
      </div>
      <span class="intensidade-texto">{{ intensidade }}%</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

/**
 * Props do componente
 */
const props = defineProps<{
  /** Hora actual formatada */
  horaActual: string
  /** Duração do fotoperíodo */
  fotoperiodo: string
  /** Intensidade da luz */
  intensidade: number
  /** Horário da luz branca */
  horarioLuzBranca: string
  /** Horário da luz noturna */
  horarioLuzNoturna: string
}>()

/**
 * Calcula o tempo desligado (24h - fotoperíodo)
 */
const tempoDesligado = computed(() => {
  const match = props.fotoperiodo.match(/(\d+)/)
  if (match) {
    const horasLigado = parseInt(match[1])
    const horasDesligado = 24 - horasLigado
    return `${horasDesligado}h`
  }
  return '—'
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
}

.cartao:hover {
  border-color: rgba(59, 130, 246, 0.4);
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
}

.cartao-hora-cabecalho {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.cartao-hora-titulo {
  display: flex;
  align-items: center;
  gap: 12px;
}

.cartao-hora-icone {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: rgba(96, 165, 250, 0.15);
  display: flex;
  align-items: center;
  justify-content: center;
}

.cartao-hora-icone .material-icons-outlined {
  font-size: 22px;
  color: #60a5fa;
}

.cartao-hora-valor {
  font-size: 1.5rem;
  font-weight: 700;
  color: #60a5fa;
}

.cartao-hora-etiqueta {
  font-size: 0.65rem;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.cartao-hora-info {
  display: flex;
  gap: 16px;
  margin-bottom: 16px;
}

.info-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.info-etiqueta {
  font-size: 0.7rem;
  color: #64748b;
  text-transform: uppercase;
}

.info-valor {
  font-size: 1.1rem;
  font-weight: 600;
}

.info-valor.amarelo {
  color: #fbbf24;
}

.info-valor.azul {
  color: #60a5fa;
}

.cartao-hora-intensidade {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  background: rgba(30, 41, 59, 0.5);
  border-radius: 8px;
}

.cartao-hora-intensidade .material-icons-outlined {
  font-size: 18px;
  color: #fbbf24;
}

.intensidade-barra {
  flex: 1;
  height: 6px;
  background: rgba(51, 65, 85, 0.5);
  border-radius: 3px;
  overflow: hidden;
}

.intensidade-preenchido {
  height: 100%;
  background: linear-gradient(90deg, #fbbf24, #f59e0b);
  border-radius: 3px;
  transition: width 0.3s ease;
}

.intensidade-texto {
  font-size: 0.85rem;
  font-weight: 600;
  color: #fbbf24;
  min-width: 40px;
  text-align: right;
}
</style>
