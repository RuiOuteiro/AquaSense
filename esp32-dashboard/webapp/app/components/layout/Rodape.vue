<!--
  Componente: Rodape
  Descrição: Rodapé com última actualização
  
  @ficheiro components/layout/Rodape.vue
  @autor AquaSense Team
-->
<template>
  <footer class="rodape">
    <div class="rodape-actualizacao">
      <span>🕐</span>
      <span>Última actualização: {{ ultimaActualizacao || '--:--:--' }}</span>
    </div>
  </footer>
</template>

<script setup lang="ts">
/**
 * Props do componente
 */
defineProps<{
  /** Hora da última actualização */
  ultimaActualizacao: string
}>()
</script>

<style scoped>
.rodape {
  text-align: center;
  padding: 24px;
  color: #64748b;
  font-size: 0.75rem;
}

.rodape-actualizacao {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}
</style>
