<!--
  Componente: Distintivo
  Descrição: Badge/pill para mostrar estados ou contadores
  
  @ficheiro components/primitivos/Distintivo.vue
  @autor AquaSense Team
-->
<template>
  <span 
    class="distintivo" 
    :class="[
      variante && `distintivo-${variante}`,
      tamanho && `distintivo-${tamanho}`
    ]"
  >
    <slot />
  </span>
</template>

<script setup lang="ts">
/**
 * Props do componente
 */
defineProps<{
  /** Variante de cor */
  variante?: 'sucesso' | 'aviso' | 'erro' | 'info' | 'neutro'
  /** Tamanho */
  tamanho?: 'pequeno' | 'grande'
}>()
</script>

<style scoped>
.distintivo {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  font-size: 0.75rem;
  font-weight: 500;
  border-radius: 20px;
  background: var(--fundo-hover, rgba(51, 65, 85, 0.5));
  color: var(--texto-secundario, #94a3b8);
}

.distintivo-pequeno {
  padding: 2px 6px;
  font-size: 0.625rem;
}

.distintivo-grande {
  padding: 6px 14px;
  font-size: 0.875rem;
}

.distintivo-sucesso {
  background: var(--cor-sucesso-fundo, rgba(16, 185, 129, 0.15));
  color: var(--cor-sucesso, #10b981);
}

.distintivo-aviso {
  background: var(--cor-aviso-fundo, rgba(245, 158, 11, 0.15));
  color: var(--cor-aviso, #f59e0b);
}

.distintivo-erro {
  background: var(--cor-erro-fundo, rgba(239, 68, 68, 0.15));
  color: var(--cor-erro, #ef4444);
}

.distintivo-info {
  background: var(--cor-info-fundo, rgba(59, 130, 246, 0.15));
  color: var(--cor-info, #3b82f6);
}

.distintivo-neutro {
  background: var(--fundo-hover, rgba(51, 65, 85, 0.5));
  color: var(--texto-terciario, #64748b);
}
</style>
