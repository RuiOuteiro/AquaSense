<!--
  Componente: ModalPerfil
  Descrição: Modal de gestão de perfil, Telegram e aquários
  Estrutura igual ao original AquaSense
  
  @ficheiro components/modais/ModalPerfil.vue
  @autor AquaSense Team
-->
<template>
  <Teleport to="body">
    <Transition name="modal-fade">
      <div v-if="visivel" class="modal-overlay" @click.self="fecharModal">
        <div class="modal-container profile-modal">
          <div class="modal-header">
            <h2>
              <span class="material-icons-outlined">person</span>
              Perfil
            </h2>
            <button class="close-btn" @click="fecharModal">
              <span class="material-icons-outlined">close</span>
            </button>
          </div>

          <div class="modal-content custom-scroll">
            <!-- Mensagens -->
            <Transition name="fade">
              <div v-if="sucesso" class="profile-message success">
                <span class="material-icons-outlined">check_circle</span>
                {{ sucesso }}
              </div>
            </Transition>
            <Transition name="fade">
              <div v-if="erro" class="profile-message error">
                <span class="material-icons-outlined">error</span>
                {{ erro }}
              </div>
            </Transition>

            <!-- Informações Pessoais -->
            <div class="settings-section">
              <h3>
                <span class="material-icons-outlined">account_circle</span>
                Informações Pessoais
              </h3>
              
              <div class="profile-form">
                <div class="form-group">
                  <label>Nome</label>
                  <div class="input-wrapper">
                    <span class="input-icon material-icons-outlined">person</span>
                    <input
                      type="text"
                      v-model="formulario.nome"
                      placeholder="O seu nome"
                      class="modern-input"
                    />
                    <button 
                      class="input-action" 
                      @click="$emit('actualizarNome')" 
                      :disabled="aCarregar || !formulario?.nome?.trim()"
                      title="Guardar"
                    >
                      <span class="material-icons-outlined">{{ aCarregar ? 'sync' : 'check' }}</span>
                    </button>
                  </div>
                </div>

                <div class="form-group">
                  <label>Email</label>
                  <div class="input-wrapper">
                    <span class="input-icon material-icons-outlined">email</span>
                    <input
                      type="email"
                      v-model="formulario.email"
                      placeholder="O seu email"
                      class="modern-input"
                    />
                    <button 
                      class="input-action" 
                      @click="$emit('actualizarEmail')" 
                      :disabled="aCarregar || !formulario?.email?.trim()"
                      title="Guardar"
                    >
                      <span class="material-icons-outlined">{{ aCarregar ? 'sync' : 'check' }}</span>
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <!-- Segurança -->
            <div class="settings-section">
              <h3>
                <span class="material-icons-outlined">shield</span>
                Segurança
              </h3>
              
              <div class="profile-form">
                <div class="form-group">
                  <label>Password Actual</label>
                  <div class="input-wrapper">
                    <span class="input-icon material-icons-outlined">lock</span>
                    <input
                      :type="mostrarPwActual ? 'text' : 'password'"
                      v-model="formulario.currentPassword"
                      placeholder="Introduza a password actual"
                      class="modern-input"
                    />
                    <button class="input-action toggle" @click="mostrarPwActual = !mostrarPwActual" type="button">
                      <span class="material-icons-outlined">{{ mostrarPwActual ? 'visibility_off' : 'visibility' }}</span>
                    </button>
                  </div>
                </div>

                <div class="form-group">
                  <label>Nova Password</label>
                  <div class="input-wrapper">
                    <span class="input-icon material-icons-outlined">lock_reset</span>
                    <input
                      :type="mostrarPwNova ? 'text' : 'password'"
                      v-model="formulario.newPassword"
                      placeholder="Mínimo 6 caracteres"
                      class="modern-input"
                    />
                    <button class="input-action toggle" @click="mostrarPwNova = !mostrarPwNova" type="button">
                      <span class="material-icons-outlined">{{ mostrarPwNova ? 'visibility_off' : 'visibility' }}</span>
                    </button>
                  </div>
                </div>

                <button 
                  class="action-btn primary" 
                  @click="$emit('alterarPalavraPasse')" 
                  :disabled="aCarregar || !formulario?.currentPassword || !formulario?.newPassword"
                >
                  <span class="material-icons-outlined">{{ aCarregar ? 'sync' : 'lock_reset' }}</span>
                  {{ aCarregar ? 'A alterar...' : 'Alterar Password' }}
                </button>
              </div>
            </div>

            <!-- Telegram -->
            <div class="settings-section">
              <h3>
                <span class="material-icons-outlined">send</span>
                Alertas Telegram
              </h3>
              
              <p class="telegram-info">
                Recebe alertas no Telegram quando os sensores saírem dos limites.
              </p>
              
              <div class="form-group">
                <label>Chat ID</label>
                <div class="input-wrapper">
                  <span class="input-icon material-icons-outlined">tag</span>
                  <input
                    type="text"
                    :value="telegram?.chat_id || ''"
                    @input="telegram.chat_id = ($event.target as HTMLInputElement).value"
                    placeholder="Ex: 7104165881"
                    class="modern-input"
                  />
                  <button 
                    class="input-action" 
                    @click="$emit('guardarTelegram')" 
                    :disabled="aCarregarTelegram || !telegram?.chat_id?.trim()"
                    title="Guardar e testar"
                  >
                    <span class="material-icons-outlined">{{ aCarregarTelegram ? 'sync' : 'check' }}</span>
                  </button>
                </div>
              </div>
              
              <div class="telegram-help">
                <span class="material-icons-outlined">info</span>
                <span>Envia mensagem ao <strong>@userinfobot</strong> no Telegram para obter o teu ID.</span>
              </div>
            </div>

            <!-- Aquários -->
            <div class="settings-section">
              <div class="section-header">
                <h3>
                  <span class="material-icons-outlined">water</span>
                  Meus Aquários
                </h3>
                <button class="add-btn" @click="$emit('abrirFormularioAquario')" title="Adicionar aquário">
                  <span class="material-icons-outlined">add</span>
                </button>
              </div>

              <!-- Formulário adicionar aquário -->
              <div v-if="mostrarFormularioAquario" class="add-aquario-form">
                <div class="form-group">
                  <div class="input-wrapper">
                    <span class="input-icon material-icons-outlined">water_drop</span>
                    <input
                      type="text"
                      v-model="novoAquario.nome"
                      placeholder="Nome do aquário"
                      class="modern-input"
                    />
                  </div>
                </div>
                <div class="form-group">
                  <div class="input-wrapper">
                    <span class="input-icon material-icons-outlined">memory</span>
                    <input
                      type="text"
                      v-model="novoAquario.device_id"
                      placeholder="Device ID (ex: ESP32_001)"
                      class="modern-input"
                    />
                  </div>
                </div>
                <div class="form-group">
                  <div class="input-wrapper">
                    <span class="input-icon material-icons-outlined">description</span>
                    <input
                      type="text"
                      v-model="novoAquario.descricao"
                      placeholder="Descrição (opcional)"
                      class="modern-input"
                    />
                  </div>
                </div>
                <div class="form-actions">
                  <button class="action-btn secondary" @click="$emit('fecharFormularioAquario')">Cancelar</button>
                  <button class="action-btn primary" @click="$emit('adicionarAquario')" :disabled="!novoAquario?.nome?.trim()">
                    <span class="material-icons-outlined">add</span>
                    Adicionar
                  </button>
                </div>
              </div>
              
              <!-- Lista de aquários -->
              <div v-if="aquarios && aquarios.length > 0" class="aquarios-list">
                <div class="aquario-card-full" v-for="aq in aquarios" :key="aq.id">
                  <div class="aquario-card-header">
                    <div class="aquario-icon">
                      <span class="material-icons-outlined">waves</span>
                    </div>
                    <div class="aquario-title-area">
                      <span class="aquario-nome">{{ aq.nome }}</span>
                      <span class="aquario-stats">
                        <span class="material-icons-outlined">analytics</span>
                        {{ (aq.total_leituras || 0).toLocaleString() }} leituras
                      </span>
                    </div>
                    <button class="icon-btn danger" @click="$emit('eliminarAquario', aq.id)" title="Eliminar">
                      <span class="material-icons-outlined">delete</span>
                    </button>
                  </div>
                  
                  <div class="aquario-fields">
                    <div class="aquario-field">
                      <label>Nome</label>
                      <div class="input-wrapper">
                        <span class="input-icon material-icons-outlined">label</span>
                        <input
                          type="text"
                          v-model="aq.nome"
                          class="modern-input"
                          @change="$emit('guardarAquario', aq)"
                        />
                      </div>
                    </div>
                    
                    <div class="aquario-field">
                      <label>ID do ESP32</label>
                      <div class="input-wrapper">
                        <span class="input-icon material-icons-outlined">memory</span>
                        <input
                          type="text"
                          v-model="aq.device_id"
                          placeholder="Ex: ESP32_001"
                          class="modern-input"
                          @change="$emit('guardarAquario', aq)"
                        />
                      </div>
                    </div>
                    
                    <div class="aquario-field">
                      <label>Descrição</label>
                      <div class="input-wrapper">
                        <span class="input-icon material-icons-outlined">description</span>
                        <input
                          type="text"
                          v-model="aq.descricao"
                          placeholder="Descrição do aquário"
                          class="modern-input"
                          @change="$emit('guardarAquario', aq)"
                        />
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              
              <div v-else-if="!mostrarFormularioAquario" class="aquarios-empty">
                <span class="material-icons-outlined">info</span>
                <div>
                  <p>Nenhum aquário configurado</p>
                  <button class="link-btn" @click="$emit('abrirFormularioAquario')">Adicionar o primeiro aquário</button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import type { FormularioPerfil, ConfiguracaoTelegram, Aquario, NovoAquario } from '~/types'

/**
 * Estado local
 */
const mostrarPwActual = ref(false)
const mostrarPwNova = ref(false)

/**
 * Props do componente
 */
defineProps<{
  visivel: boolean
  formulario: FormularioPerfil
  telegram: ConfiguracaoTelegram
  aquarios: Aquario[]
  novoAquario: NovoAquario
  mostrarFormularioAquario: boolean
  aCarregar: boolean
  aCarregarTelegram: boolean
  erro: string
  sucesso: string
}>()

/**
 * Eventos emitidos
 */
const emit = defineEmits<{
  (e: 'fechar'): void
  (e: 'actualizarNome'): void
  (e: 'actualizarEmail'): void
  (e: 'alterarPalavraPasse'): void
  (e: 'testarTelegram'): void
  (e: 'guardarTelegram'): void
  (e: 'abrirFormularioAquario'): void
  (e: 'fecharFormularioAquario'): void
  (e: 'adicionarAquario'): void
  (e: 'guardarAquario', aquario: Aquario): void
  (e: 'eliminarAquario', id: number): void
}>()

/**
 * Fecha o modal
 */
function fecharModal() {
  emit('fechar')
}
</script>

<!-- Estilos em dashboard.css -->
