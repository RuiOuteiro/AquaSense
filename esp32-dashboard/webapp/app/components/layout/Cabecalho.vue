<!--
  Componente: Cabecalho
  Descrição: Cabeçalho principal da aplicação com logo e menu
  
  @ficheiro components/layout/Cabecalho.vue
  @autor AquaSense Team
-->
<template>
  <header class="header">
    <div class="header-content">
      <!-- Logótipo -->
      <div class="logo">
        <div class="logo-icon">
          <img src="/Logo.png" alt="AquaSense Logo" />
        </div>
        <div class="logo-text">
          <h1>AquaSense</h1>
          <span>Sistema de Manutenção de Aquário</span>
        </div>
      </div>
      
      <!-- Acções -->
      <div class="header-actions">
        <!-- Estado de ligação -->
        <div class="status-badge" :class="ligado ? 'online' : 'offline'">
          <span class="status-dot" />
          {{ ligado ? 'Conectado' : 'Desconectado' }}
        </div>
        
        <!-- Menu hambúrguer -->
        <div ref="menuRef" class="burger-menu">
          <button 
            class="burger-btn"
            :class="{ active: menuAberto }"
            @click.stop="emit('alternarMenu')"
          >
            <span class="material-icons-outlined">{{ menuAberto ? 'close' : 'menu' }}</span>
          </button>
          
          <!-- Dropdown -->
          <Transition name="dropdown">
            <div v-if="menuAberto" class="burger-dropdown" @click.stop>
              <button class="dropdown-item" @click="$emit('abrirGraficos')">
                <span class="material-icons-outlined">show_chart</span>
                Gráficos
              </button>
              <button class="dropdown-item" @click="$emit('alternarConsola')">
                <span class="material-icons-outlined">terminal</span>
                Consola
              </button>
              <button class="dropdown-item" @click="$emit('abrirDefinicoes')">
                <span class="material-icons-outlined">settings</span>
                Definições
              </button>
              
              <div class="dropdown-divider" />
              
              <button class="dropdown-item" @click="$emit('abrirPerfil')">
                <span class="material-icons-outlined">person</span>
                Perfil
              </button>
              <button class="dropdown-item logout" @click="$emit('terminarSessao')">
                <span class="material-icons-outlined">logout</span>
                Sair
              </button>
            </div>
          </Transition>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'

/**
 * Props do componente
 */
const props = defineProps<{
  /** ESP32 está ligado */
  ligado: boolean
  /** Menu está aberto */
  menuAberto: boolean
}>()

/**
 * Eventos emitidos
 */
const emit = defineEmits<{
  'alternarMenu': []
  'abrirGraficos': []
  'alternarConsola': []
  'abrirDefinicoes': []
  'abrirPerfil': []
  'terminarSessao': []
}>()

const menuRef = ref<HTMLElement | null>(null)

/**
 * Fechar menu ao clicar fora
 */
function handleClickOutside(event: MouseEvent) {
  if (props.menuAberto && menuRef.value && !menuRef.value.contains(event.target as Node)) {
    emit('alternarMenu')
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.header {
  background: rgba(15, 23, 42, 0.95);
  backdrop-filter: blur(10px);
  padding: 1rem 0;
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-icon {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #06b6d44a, #3b82f626);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.logo-icon img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.logo-text h1 {
  font-size: 1.25rem;
  font-weight: 700;
  margin: 0;
  color: white;
}

.logo-text span {
  font-size: 0.75rem;
  color: #94a3b8;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.status-badge {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 500;
}

.status-badge.online {
  background: rgba(16, 185, 129, 0.15);
  color: #10b981;
}

.status-badge.offline {
  background: rgba(239, 68, 68, 0.15);
  color: #ef4444;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: currentColor;
  animation: pulse 2s infinite;
}

.burger-menu {
  position: relative;
}

.burger-btn {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  background: rgba(51, 65, 85, 0.5);
  border: none;
  color: #94a3b8;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.burger-btn:hover,
.burger-btn.active {
  background: rgba(51, 65, 85, 0.8);
  color: #f1f5f9;
}

.burger-dropdown {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  background: rgba(30, 41, 59, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 12px;
  border: 1px solid rgba(148, 163, 184, 0.1);
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.4);
  min-width: 180px;
  overflow: hidden;
  z-index: 1000;
}

.dropdown-item {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  background: transparent;
  border: none;
  color: #e2e8f0;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s ease;
  text-align: left;
}

.dropdown-item:hover {
  background: rgba(51, 65, 85, 0.5);
}

.dropdown-item .material-icons-outlined {
  font-size: 20px;
  color: #94a3b8;
}

.dropdown-item:hover .material-icons-outlined {
  color: #f1f5f9;
}

.dropdown-item.logout {
  color: #f87171;
}

.dropdown-item.logout:hover {
  background: rgba(239, 68, 68, 0.2);
}

.dropdown-item.logout .material-icons-outlined {
  color: #f87171;
}

.dropdown-divider {
  height: 1px;
  background: rgba(148, 163, 184, 0.1);
  margin: 4px 0;
}

.dropdown-enter-active,
.dropdown-leave-active {
  transition: all 0.2s ease;
}

.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

@media (max-width: 768px) {
  .header-content {
    padding: 0 1rem;
  }
  
  .logo-icon {
    width: 40px;
    height: 40px;
  }
  
  .logo-text h1 {
    font-size: 1.125rem;
  }
  
  .status-badge {
    display: none;
  }
}
</style>
