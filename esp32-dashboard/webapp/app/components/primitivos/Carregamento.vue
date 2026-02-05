<!--
  Componente: Carregamento
  Descrição: Indicador de carregamento (spinner)
  
  @ficheiro components/primitivos/Carregamento.vue
  @autor AquaSense Team
-->
<template>
  <div class="carregamento" :class="[tamanho && `carregamento-${tamanho}`]">
    <span class="carregamento-spinner">⟳</span>
    <span v-if="texto" class="carregamento-texto">{{ texto }}</span>
  </div>
</template>

<script setup lang="ts">
/**
 * Props do componente
 */
defineProps<{
  /** Texto a mostrar */
  texto?: string
  /** Tamanho */
  tamanho?: 'pequeno' | 'grande'
}>()
</script>

<style scoped>
.carregamento {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 16px;
}

.carregamento-spinner {
  font-size: 1.5rem;
  animation: rodar 1s linear infinite;
  color: var(--cor-primaria, #3b82f6);
}

.carregamento-texto {
  font-size: 0.875rem;
  color: var(--texto-secundario, #94a3b8);
}

.carregamento-pequeno {
  padding: 8px;
}

.carregamento-pequeno .carregamento-spinner {
  font-size: 1rem;
}

.carregamento-grande .carregamento-spinner {
  font-size: 2rem;
}

@keyframes rodar {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>
