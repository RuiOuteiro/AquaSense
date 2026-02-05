<!--
  Componente: SeccaoIluminacao
  Descrição: Secção que agrupa os cartões de iluminação
  
  @ficheiro components/seccoes/SeccaoIluminacao.vue
  @autor AquaSense Team
-->
<template>
  <section class="lighting-section">
    <h2 class="section-title">
      <span class="material-icons-outlined">lightbulb</span>
      Iluminação
    </h2>
    
    <div class="lighting-cards">
      <CartaoLuzBranca
        :ligada="luzBrancaLigada"
        :modo="config.luzModo"
        :intensidade="config.luzIntensidade"
        :hora-ligar-h="config.luzHoraLigar"
        :hora-ligar-m="config.luzMinutoLigar"
        :hora-desligar-h="config.luzHoraDesligar"
        :hora-desligar-m="config.luzMinutoDesligar"
        :ciclo-inicio="config.luzCicloInicio"
        :ciclo-horas="config.luzCicloHoras"
        @alternar="$emit('alternarLuzBranca')"
      />
      
      <CartaoLuzNoturna
        :ligada="luzNoturnaLigada"
        :modo="config.luzNoturnaModo"
        :hora-ligar-h="config.luzNoturnaHoraLigar"
        :hora-ligar-m="config.luzNoturnaMinutoLigar"
        :hora-desligar-h="config.luzNoturnaHoraDesligar"
        :hora-desligar-m="config.luzNoturnaMinutoDesligar"
        :ciclo-inicio="config.luzNoturnaCicloInicio"
        :ciclo-horas="config.luzNoturnaCicloHoras"
        @alternar="$emit('alternarLuzNoturna')"
      />
      
      <CartaoHora
        :hora-actual="horaActual"
        :fotoperiodo="fotoperiodo"
        :intensidade="config.luzIntensidade"
        :horario-luz-branca="horarioLuzBranca"
        :horario-luz-noturna="horarioLuzNoturna"
      />
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import CartaoLuzBranca from '~/components/cartoes/CartaoLuzBranca.vue'
import CartaoLuzNoturna from '~/components/cartoes/CartaoLuzNoturna.vue'
import CartaoHora from '~/components/cartoes/CartaoHora.vue'
import type { ConfiguracaoSistema } from '~/types'
import { formatarHora } from '~/utils/formatadores'

/**
 * Props do componente
 */
const props = defineProps<{
  config: ConfiguracaoSistema
  luzBrancaLigada: boolean
  luzNoturnaLigada: boolean
  horaActual: string
  fotoperiodo: string
}>()

/**
 * Horário formatado da luz branca
 */
const horarioLuzBranca = computed(() => {
  const ligar = formatarHora(props.config.luzHoraLigar, props.config.luzMinutoLigar)
  const desligar = formatarHora(props.config.luzHoraDesligar, props.config.luzMinutoDesligar)
  return `${ligar} - ${desligar}`
})

/**
 * Horário formatado da luz noturna
 */
const horarioLuzNoturna = computed(() => {
  const ligar = formatarHora(props.config.luzNoturnaHoraLigar, props.config.luzNoturnaMinutoLigar)
  const desligar = formatarHora(props.config.luzNoturnaHoraDesligar, props.config.luzNoturnaMinutoDesligar)
  return `${ligar} - ${desligar}`
})

/**
 * Eventos emitidos
 */
defineEmits<{
  'alternarLuzBranca': []
  'alternarLuzNoturna': []
}>()
</script>

<style scoped>
/* Estilos herdados do dashboard.css */
</style>
