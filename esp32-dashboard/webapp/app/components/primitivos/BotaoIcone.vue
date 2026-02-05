<!--
  Componente: BotaoIcone
  Descrição: Botão com apenas um ícone, usado em acções rápidas
  
  @ficheiro components/primitivos/BotaoIcone.vue
  @autor AquaSense Team
-->
<template>
  <button
    class="botao-icone"
    :class="[
      tamanho && `botao-icone-${tamanho}`,
      variante && `botao-icone-${variante}`
    ]"
    :disabled="desactivado"
    :title="titulo"
    @click="$emit('click')"
  >
    <span>{{ icone }}</span>
  </button>
</template>

<script setup lang="ts">
/**
 * Props do componente
 */
defineProps<{
  /** Emoji ou ícone a mostrar */
  icone: string
  /** Título para tooltip */
  titulo?: string
  /** Tamanho: pequeno, normal */
  tamanho?: 'pequeno'
  /** Variante de cor */
  variante?: 'primario' | 'perigo' | 'sucesso'
  /** Estado desactivado */
  desactivado?: boolean
}>()

/**
 * Eventos emitidos
 */
defineEmits<{
  click: []
}>()
</script>

<style scoped>
.botao-icone {
  width: 40px;
  height: 40px;
  padding: 0;
  border-radius: var(--raio-medio, 12px);
  background: var(--fundo-hover, rgba(51, 65, 85, 0.5));
  color: var(--texto-secundario, #94a3b8);
  font-size: 1.25rem;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.botao-icone:hover:not(:disabled) {
  background: rgba(71, 85, 105, 0.6);
  color: var(--texto-principal, #e2e8f0);
}

.botao-icone:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.botao-icone-pequeno {
  width: 32px;
  height: 32px;
  font-size: 1rem;
}

.botao-icone-primario {
  background: var(--cor-primaria, #3b82f6);
  color: white;
}

.botao-icone-primario:hover:not(:disabled) {
  background: var(--cor-primaria-clara, #60a5fa);
}

.botao-icone-perigo:hover:not(:disabled) {
  background: rgba(239, 68, 68, 0.2);
  color: var(--cor-erro, #ef4444);
}

.botao-icone-sucesso {
  background: var(--cor-sucesso, #10b981);
  color: white;
}
</style>
