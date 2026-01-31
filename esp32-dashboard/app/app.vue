<!--
  AquaSense Dashboard - Interface de Monitorização de Aquário
  
  Descrição: Dashboard responsivo para monitorização e controlo de aquário
  através de ESP32. Inclui sensores de temperatura, pH, turbidez, humidade
  e controlo de iluminação e ventoinha.
  
  Autor: AquaSense Team
  Versão: 2.0.0
  Última Atualização: Janeiro 2026
-->
<template>
  <div class="app">
    <!-- ========== CABEÇALHO PRINCIPAL ========== -->
    <header class="header">
      <div class="header-content">
        <!-- Logótipo e título -->
        <div class="logo">
          <div class="logo-icon">
            <span class="material-icons-outlined">water_drop</span>
          </div>
          <div class="logo-text">
            <h1>AquaSense</h1>
            <span>Sistema de Manutenção de Aquário</span>
          </div>
        </div>

        <!-- Botões de acção do cabeçalho -->
        <div class="header-actions">
          <!-- Indicador de estado de ligação -->
          <div class="status-badge" :class="isConnected ? 'online' : 'offline'">
            <span class="status-dot"></span>
            {{ isConnected ? "Conectado" : "Desconectado" }}
          </div>

          <!-- Botão de consola -->
          <button class="console-btn" @click="toggleConsole" :class="{ active: showConsole }">
            <span class="material-icons-outlined">terminal</span>
          </button>

          <!-- Botão de definições -->
          <button class="settings-btn" @click="openSettings">
            <span class="material-icons-outlined">settings</span>
          </button>
        </div>
      </div>
    </header>

    <!-- ========== PAINEL DE CONSOLA ========== -->
    <div class="console-panel" v-if="showConsole">
      <div class="console-header">
        <h3><span class="material-icons-outlined">terminal</span> Consola ESP32</h3>
        <div class="console-actions">
          <button @click="clearConsole" title="Limpar">
            <span class="material-icons-outlined">delete</span>
          </button>
          <button @click="toggleConsole" title="Fechar">
            <span class="material-icons-outlined">close</span>
          </button>
        </div>
      </div>
      <div class="console-body" ref="consoleBody">
        <div v-for="(log, index) in consoleLogs" :key="index" class="console-line" :class="log.type">
          <span class="log-time">{{ log.time }}</span>
          <span class="log-msg">{{ log.message }}</span>
        </div>
        <div v-if="consoleLogs.length === 0" class="console-empty">
          A aguardar mensagens do ESP32...
        </div>
      </div>
    </div>

    <main class="main">
      <!-- ========== SECÇÃO DE ILUMINAÇÃO ========== -->
      <section class="lighting-section">
        <h2 class="section-title">
          <span class="material-icons-outlined">lightbulb</span>
          Iluminação
        </h2>

        <div class="lighting-cards">
          <!-- Card Luz Branca -->
          <div class="light-card white-light" :class="{ active: lightOn }">
            <div class="light-card-header">
              <div class="light-icon white">
                <span class="material-icons-outlined">wb_sunny</span>
              </div>
              <div class="light-info">
                <h3>Luz Branca</h3>
                <span class="light-mode" :class="'mode-' + config.luzModo">
                  {{
                    {
                      manual: "Manual",
                      horario: "Horário",
                      ciclo: "Ciclo",
                      ai: "IA",
                    }[config.luzModo] || "Horário"
                  }}
                  <span
                    v-if="config.luzModo === 'ciclo' && config.luzCicloInicio"
                    class="cycle-badge"
                    >{{ config.luzCicloHoras }}h</span
                  >
                </span>
              </div>
              <div class="light-toggle">
                <button
                  class="power-btn"
                  :class="{ on: lightOn }"
                  @click="toggleWhiteLight"
                >
                  <span class="material-icons-outlined"
                    >power_settings_new</span
                  >
                </button>
              </div>
            </div>

            <div class="light-card-body">
              <!-- Luz desligada -->
              <div class="off-display" v-if="!lightOn">
                <span class="status-pill off">Desligada</span>
              </div>

              <!-- Luz ligada - Modo Horário -->
              <div
                class="schedule-display"
                v-else-if="config.luzModo === 'horario'"
              >
                <div class="schedule-item">
                  <span class="material-icons-outlined">wb_twilight</span>
                  <span>{{
                    formatTime(config.luzHoraLigar, config.luzMinutoLigar)
                  }}</span>
                </div>
                <span class="schedule-separator">→</span>
                <div class="schedule-item">
                  <span class="material-icons-outlined">nights_stay</span>
                  <span>{{
                    formatTime(config.luzHoraDesligar, config.luzMinutoDesligar)
                  }}</span>
                </div>
              </div>

              <!-- Luz ligada - Modo Ciclo -->
              <div
                class="cycle-display"
                v-else-if="config.luzModo === 'ciclo' && config.luzCicloInicio"
              >
                <div class="schedule-display">
                  <div class="schedule-item">
                    <span class="material-icons-outlined">wb_twilight</span>
                    <span>{{ getCycleStartTime(config.luzCicloInicio) }}</span>
                  </div>
                  <span class="schedule-separator cycle"
                    >{{ config.luzCicloHoras }}h</span
                  >
                  <div class="schedule-item">
                    <span class="material-icons-outlined">nights_stay</span>
                    <span>{{
                      getCycleEndTime(
                        config.luzCicloInicio,
                        config.luzCicloHoras,
                      )
                    }}</span>
                  </div>
                </div>
              </div>

              <!-- Luz ligada - Modo IA -->
              <div
                class="ai-display"
                v-else-if="config.luzModo === 'ai' && config.luzCicloInicio"
              >
                <div class="schedule-display">
                  <div class="schedule-item">
                    <span class="material-icons-outlined">wb_twilight</span>
                    <span>{{ getCycleStartTime(config.luzCicloInicio) }}</span>
                  </div>
                  <span class="schedule-separator ai"
                    >{{ config.luzCicloHoras }}h</span
                  >
                  <div class="schedule-item">
                    <span class="material-icons-outlined">nights_stay</span>
                    <span>{{
                      getCycleEndTime(
                        config.luzCicloInicio,
                        config.luzCicloHoras,
                      )
                    }}</span>
                  </div>
                </div>
                <div class="intensity-display">
                  <span class="material-icons-outlined">light_mode</span>
                  <span>{{ config.luzIntensidade }}%</span>
                </div>
              </div>

              <!-- Luz ligada - Modo Manual -->
              <div
                class="intensity-control premium"
                v-else-if="config.luzModo === 'manual' && lightOn"
              >
                <div class="intensity-header">
                  <span class="intensity-label">Intensidade</span>
                  <span class="intensity-value"
                    >{{ config.luzIntensidade }}%</span
                  >
                </div>
                <div class="intensity-slider-wrap">
                  <input
                    type="range"
                    v-model.number="config.luzIntensidade"
                    @input="guardarIntensidade"
                    min="0"
                    max="100"
                    class="intensity-slider premium"
                    :style="{ '--progress': config.luzIntensidade + '%' }"
                  />
                </div>
              </div>

              <!-- Estado ligada (badge) -->
              <div
                class="manual-indicator"
                v-if="lightOn && config.luzModo !== 'manual'"
              >
                <span class="status-pill active">Ligada</span>
              </div>
            </div>
          </div>

          <!-- Card Luz Azul/Noturna -->
          <div class="light-card blue-light" :class="{ active: nightLightOn }">
            <div class="light-card-header">
              <div class="light-icon blue">
                <span class="material-icons-outlined">nightlight</span>
              </div>
              <div class="light-info">
                <h3>Luz Noturna</h3>
                <span
                  class="light-mode"
                  :class="'mode-' + config.luzNoturnaModo"
                >
                  {{
                    { manual: "Manual", horario: "Horário", ciclo: "Ciclo" }[
                      config.luzNoturnaModo
                    ] || "Horário"
                  }}
                  <span
                    v-if="
                      config.luzNoturnaModo === 'ciclo' &&
                      config.luzNoturnaCicloInicio
                    "
                    class="cycle-badge night"
                    >{{ config.luzNoturnaCicloHoras }}h</span
                  >
                </span>
              </div>
              <div class="light-toggle">
                <button
                  class="power-btn blue"
                  :class="{ on: nightLightOn }"
                  @click="toggleNightLight"
                >
                  <span class="material-icons-outlined"
                    >power_settings_new</span
                  >
                </button>
              </div>
            </div>

            <div class="light-card-body">
              <!-- Luz desligada -->
              <div class="off-display" v-if="!nightLightOn">
                <span class="status-pill off night">Desligada</span>
              </div>

              <!-- Luz ligada - Modo Horário -->
              <div
                class="schedule-display"
                v-else-if="config.luzNoturnaModo === 'horario'"
              >
                <div class="schedule-item">
                  <span class="material-icons-outlined">nights_stay</span>
                  <span>{{
                    formatTime(
                      config.luzNoturnaHoraLigar,
                      config.luzNoturnaMinutoLigar,
                    )
                  }}</span>
                </div>
                <span class="schedule-separator">→</span>
                <div class="schedule-item">
                  <span class="material-icons-outlined">wb_twilight</span>
                  <span>{{
                    formatTime(
                      config.luzNoturnaHoraDesligar,
                      config.luzNoturnaMinutoDesligar,
                    )
                  }}</span>
                </div>
              </div>

              <!-- Luz ligada - Modo Ciclo -->
              <div
                class="cycle-display night"
                v-else-if="
                  config.luzNoturnaModo === 'ciclo' &&
                  config.luzNoturnaCicloInicio
                "
              >
                <div class="schedule-display">
                  <div class="schedule-item">
                    <span class="material-icons-outlined">nights_stay</span>
                    <span>{{
                      getCycleStartTime(config.luzNoturnaCicloInicio)
                    }}</span>
                  </div>
                  <span class="schedule-separator cycle night"
                    >{{ config.luzNoturnaCicloHoras }}h</span
                  >
                  <div class="schedule-item">
                    <span class="material-icons-outlined">wb_twilight</span>
                    <span>{{
                      getCycleEndTime(
                        config.luzNoturnaCicloInicio,
                        config.luzNoturnaCicloHoras,
                      )
                    }}</span>
                  </div>
                </div>
              </div>

              <!-- Luz ligada - Modo Manual -->
              <div
                class="manual-status"
                v-else-if="config.luzNoturnaModo === 'manual' && nightLightOn"
              >
                <span class="status-text">Ligada</span>
              </div>

              <!-- Estado ligada (badge) -->
              <div
                class="manual-indicator"
                v-if="nightLightOn && config.luzNoturnaModo !== 'manual'"
              >
                <span class="status-pill active night">Ligada</span>
              </div>
            </div>

            <!-- Indicador de estado -->
            <!--   <div
              class="light-status-bar blue"
              :class="{ active: nightLightOn }"
            ></div> -->
          </div>
        </div>

        <!-- Hora atual -->
        <div class="current-time-display">
          <span class="material-icons-outlined">schedule</span>
          <span class="time">{{ currentTime }}</span>
        </div>
      </section>

      <!-- ========== SECÇÃO DE PARÂMETROS ========== -->
      <section class="parameters-section">
        <h2 class="section-title">
          <span class="material-icons-outlined">analytics</span>
          Parâmetros
        </h2>

        <div class="sensors-grid">
          <!-- Temperatura da Água -->
          <div class="sensor-card">
            <div class="sensor-header">
              <div class="sensor-icon temp">
                <span class="material-icons-outlined">device_thermostat</span>
              </div>
              <div class="sensor-info">
                <h3>Temperatura</h3>
                <span>Água do Aquário</span>
              </div>
            </div>
            <div class="sensor-value">
              <span class="value" :class="getTempClass">{{
                currentTemp !== null ? currentTemp.toFixed(1) : "--"
              }}</span>
              <span class="unit">°C</span>
            </div>
            <div class="sensor-footer">
              <div class="threshold">
                <span class="material-icons-outlined">arrow_upward</span>
                Liga: {{ config.tempLigar }}°C
              </div>
              <div class="threshold">
                <span class="material-icons-outlined">arrow_downward</span>
                Desliga: {{ config.tempDesligar }}°C
              </div>
            </div>
          </div>

          <!-- pH -->
          <div class="sensor-card">
            <div class="sensor-header">
              <div class="sensor-icon ph">
                <span class="material-icons-outlined">science</span>
              </div>
              <div class="sensor-info">
                <h3>pH</h3>
                <span>Acidez da Água</span>
              </div>
            </div>
            <div class="sensor-value">
              <span class="value ph-value" :class="getPhClass">{{
                currentPh !== null ? currentPh.toFixed(2) : "--"
              }}</span>
            </div>
            <div class="ph-scale">
              <div class="scale-bar"></div>
              <div class="scale-labels">
                <span>Ácido</span>
                <span>Neutro</span>
                <span>Alcalino</span>
              </div>
            </div>
            <!-- Tensão do sensor pH -->
            <div class="sensor-voltage" v-if="phVoltage !== null">
              <span class="material-icons-outlined">electric_bolt</span>
              {{ phVoltage.toFixed(3) }}V
            </div>
          </div>

          <!-- Turbidez -->
          <div class="sensor-card">
            <div class="sensor-header">
              <div class="sensor-icon turbidity">
                <span class="material-icons-outlined">blur_on</span>
              </div>
              <div class="sensor-info">
                <h3>Turbidez</h3>
                <span>Claridade da Água</span>
              </div>
            </div>
            <div class="sensor-value">
              <span class="value turbidity-value" :class="getTurbidityClass">{{
                turbidity !== null ? turbidity.toFixed(0) : "--"
              }}</span>
              <span class="unit">%</span>
            </div>
            <div class="turbidity-scale">
              <div class="scale-bar turbidity-bar"></div>
              <div class="scale-labels">
                <span>Limpa</span>
                <span>Turva</span>
              </div>
            </div>
            <!-- Tensão do sensor de turbidez -->
            <div class="sensor-voltage" v-if="turbidityVoltage !== null">
              <span class="material-icons-outlined">electric_bolt</span>
              {{ turbidityVoltage.toFixed(2) }}V
            </div>
          </div>

          <!-- Temperatura Ambiente -->
          <div class="sensor-card">
            <div class="sensor-header">
              <div class="sensor-icon ambient">
                <span class="material-icons-outlined">thermostat_auto</span>
              </div>
              <div class="sensor-info">
                <h3>Temp. Ambiente</h3>
                <span>Sensor DHT11</span>
              </div>
            </div>
            <div class="sensor-value">
              <span class="value ambient-value">{{
                ambientTemp !== null ? ambientTemp.toFixed(1) : "--"
              }}</span>
              <span class="unit">°C</span>
            </div>
          </div>

          <!-- Humidade -->
          <div class="sensor-card">
            <div class="sensor-header">
              <div class="sensor-icon humidity">
                <span class="material-icons-outlined">water_drop</span>
              </div>
              <div class="sensor-info">
                <h3>Humidade</h3>
                <span>Sensor DHT11</span>
              </div>
            </div>
            <div class="sensor-value">
              <span class="value humidity-value">{{
                humidity !== null ? humidity.toFixed(0) : "--"
              }}</span>
              <span class="unit">%</span>
            </div>
          </div>
        </div>
      </section>

      <!-- ========== SECÇÃO DA VENTOINHA ========== -->
      <section class="fan-section">
        <div class="fan-card" :class="{ active: fanOn }">
          <div class="fan-header">
            <div class="fan-icon" :class="{ active: fanOn }">
              <span class="material-icons-outlined">air</span>
            </div>
            <div class="fan-info">
              <h3>Ventoinha de Arrefecimento</h3>
              <span class="fan-mode">{{
                config.modoManual ? "Modo Manual" : "Modo Automático"
              }}</span>
            </div>
            <div class="fan-status-indicator">
              <span class="fan-status-text" :class="{ on: fanOn }">
                {{ fanOn ? "LIGADA" : "DESLIGADA" }}
              </span>
            </div>
          </div>

          <div class="fan-controls">
            <!-- Controlo rápido de modo manual - mostra apenas botão relevante -->
            <div class="quick-controls" v-if="config.modoManual">
              <button
                v-if="!fanOn"
                class="quick-btn on"
                @click="setVentoinhaManual(true)"
              >
                <span class="material-icons-outlined">power</span>
                Ligar
              </button>
              <button
                v-else
                class="quick-btn off active"
                @click="setVentoinhaManual(false)"
              >
                <span class="material-icons-outlined">power_off</span>
                Desligar
              </button>
            </div>

            <!-- Informação de temperatura (modo automático) -->
            <div class="auto-info" v-else>
              <div class="temp-threshold">
                <span class="material-icons-outlined">arrow_upward</span>
                <span
                  >Liga: <strong>{{ config.tempLigar }}°C</strong></span
                >
              </div>
              <div class="temp-threshold">
                <span class="material-icons-outlined">arrow_downward</span>
                <span
                  >Desliga: <strong>{{ config.tempDesligar }}°C</strong></span
                >
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- ========== HISTÓRICO DE LEITURAS ========== -->
      <section class="history">
        <div class="history-header">
          <h2>
            <span class="material-icons-outlined">history</span>
            Histórico de Leituras
          </h2>
          <span class="badge">{{ readings.length }} registos</span>
        </div>
        <div class="history-table" v-if="readings.length > 0">
          <table>
            <thead>
              <tr>
                <th>Data/Hora</th>
                <th>Sensor</th>
                <th>Valor</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="reading in readings.slice(0, 15)" :key="reading.id">
                <td>{{ formatDate(reading.created_at) }}</td>
                <td>
                  <span class="sensor-badge" :class="reading.sensor_type">
                    {{ translateSensorType(reading.sensor_type) }}
                  </span>
                </td>
                <td class="value-cell">{{ formatValue(reading) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="empty-state" v-else>
          <span class="material-icons-outlined">hourglass_empty</span>
          <p>A aguardar dados...</p>
        </div>
      </section>
    </main>

    <!-- ========== RODAPÉ ========== -->
    <footer class="footer">
      <span>Última atualização: {{ lastUpdate }}</span>
    </footer>

    <!-- ========== MODAL DE DEFINIÇÕES ========== -->
    <Teleport to="body">
      <Transition name="modal-fade">
        <div
          class="modal-overlay"
          v-if="showSettings"
          @click.self="closeSettings"
        >
          <div class="modal-container">
            <!-- Cabeçalho do modal -->
            <div class="modal-header">
              <h2>
                <span class="material-icons-outlined">settings</span>
                Definições
              </h2>
              <button class="close-btn" @click="closeSettings">
                <span class="material-icons-outlined">close</span>
              </button>
            </div>

            <!-- Conteúdo do modal com scroll personalizado -->
            <div class="modal-content custom-scroll">
              <!-- Secção: Ventoinha -->
              <div class="settings-section">
                <h3>
                  <span class="material-icons-outlined">air</span>
                  Ventoinha
                </h3>

                <div class="setting-group">
                  <label>Modo de Operação</label>
                  <div class="toggle-buttons">
                    <button
                      @click="setModoManual(false)"
                      :class="{ active: !config.modoManual }"
                    >
                      Automático
                    </button>
                    <button
                      @click="setModoManual(true)"
                      :class="{ active: config.modoManual }"
                    >
                      Manual
                    </button>
                  </div>
                </div>

                <div class="setting-group" v-if="!config.modoManual">
                  <label>Limites de Temperatura</label>
                  <div class="input-row">
                    <div class="input-field">
                      <span>Liga (°C)</span>
                      <input
                        type="number"
                        v-model.number="config.tempLigar"
                        @change="guardarConfig"
                        step="0.5"
                      />
                    </div>
                    <div class="input-field">
                      <span>Desliga (°C)</span>
                      <input
                        type="number"
                        v-model.number="config.tempDesligar"
                        @change="guardarConfig"
                        step="0.5"
                      />
                    </div>
                  </div>
                </div>
              </div>

              <!-- Secção: Luz Branca -->
              <div class="settings-section">
                <h3>
                  <span class="material-icons-outlined">wb_sunny</span>
                  Luz Branca
                </h3>

                <div class="setting-group">
                  <label>Modo</label>
                  <div class="toggle-buttons mode-buttons">
                    <button
                      @click="setLuzModo('manual')"
                      :class="{ active: config.luzModo === 'manual' }"
                    >
                      Manual
                    </button>
                    <button
                      @click="setLuzModo('horario')"
                      :class="{ active: config.luzModo === 'horario' }"
                    >
                      Horário
                    </button>
                    <button
                      @click="setLuzModo('ciclo')"
                      :class="{ active: config.luzModo === 'ciclo' }"
                    >
                      Ciclo
                    </button>
                    <button
                      @click="setLuzModo('ai')"
                      :class="{ active: config.luzModo === 'ai' }"
                      class="ai-btn"
                    >
                      <span class="material-icons-outlined">auto_awesome</span>
                      IA
                    </button>
                  </div>
                </div>

                <!-- Modo Horário -->
                <div class="setting-group" v-if="config.luzModo === 'horario'">
                  <label>Horário Fixo</label>
                  <div class="input-row">
                    <div class="input-field">
                      <span>Ligar</span>
                      <input
                        type="time"
                        :value="
                          formatTime(config.luzHoraLigar, config.luzMinutoLigar)
                        "
                        @change="updateLigarTime($event)"
                      />
                    </div>
                    <div class="input-field">
                      <span>Desligar</span>
                      <input
                        type="time"
                        :value="
                          formatTime(
                            config.luzHoraDesligar,
                            config.luzMinutoDesligar,
                          )
                        "
                        @change="updateDesligarTime($event)"
                      />
                    </div>
                  </div>
                  <label class="intensity-label-small">Intensidade</label>
                  <div class="intensity-slider-row">
                    <input
                      type="range"
                      min="0"
                      max="100"
                      v-model.number="config.luzIntensidade"
                      @change="guardarConfig"
                      class="intensity-slider"
                    />
                    <span class="intensity-value"
                      >{{ config.luzIntensidade }}%</span
                    >
                  </div>
                </div>

                <!-- Modo Ciclo -->
                <div class="setting-group" v-if="config.luzModo === 'ciclo'">
                  <label>Fotoperíodo (horas por dia)</label>
                  <div class="cycle-buttons">
                    <button
                      v-for="h in [4, 6, 8, 12, 16]"
                      :key="h"
                      @click="iniciarCicloLuz(h)"
                      :class="{
                        active:
                          config.luzCicloHoras === h && config.luzCicloInicio,
                      }"
                      class="cycle-btn"
                    >
                      {{ h }}h
                    </button>
                  </div>
                  <span class="setting-hint" v-if="config.luzCicloInicio">
                    Ciclo iniciado: liga {{ config.luzCicloHoras }}h por dia,
                    sempre à mesma hora
                  </span>
                  <label class="intensity-label-small">Intensidade</label>
                  <div class="intensity-slider-row">
                    <input
                      type="range"
                      min="0"
                      max="100"
                      v-model.number="config.luzIntensidade"
                      @change="guardarConfig"
                      class="intensity-slider"
                    />
                    <span class="intensity-value"
                      >{{ config.luzIntensidade }}%</span
                    >
                  </div>
                </div>

                <!-- Modo IA -->
                <div
                  class="setting-group ai-section"
                  v-if="config.luzModo === 'ai'"
                >
                  <div class="ai-card">
                    <div class="ai-header">
                      <span class="material-icons-outlined">psychology</span>
                      <span>Ajuste Inteligente</span>
                    </div>
                    <p class="ai-desc">
                      A IA analisa a turbidez e sugere ajustes de fotoperíodo,
                      intensidade, TPA e alimentação.
                    </p>
                    <button @click="fetchAISuggestion" class="ai-fetch-btn">
                      <span class="material-icons-outlined">refresh</span>
                      Obter Sugestão
                    </button>
                    <div v-if="aiSuggestion" class="ai-result">
                      <!-- Alerta -->
                      <div
                        class="ai-alert"
                        :class="getAlertClass(aiSuggestion.input?.turbidez_actual)"
                      >
                        <span class="material-icons-outlined">{{
                          aiSuggestion.input.turbidez_actual > 60 ? "warning" : "info"
                        }}</span>
                        <span>{{ aiSuggestion.razao }}</span>
                      </div>

                      <!-- Estatísticas principais -->
                      <div class="ai-stats-grid">
                        <div class="ai-stat-card">
                          <span class="label">Turbidez</span>
                          <span
                            class="value"
                            :class="
                              getTurbidityAlertClass(
                                aiSuggestion.input.turbidez_actual,
                              )
                            "
                            >{{
                              aiSuggestion.input.turbidez_actual?.toFixed(0)
                            }}%</span
                          >
                        </div>
                        <div class="ai-stat-card">
                          <span class="label">Fotoperíodo</span>
                          <span class="value highlight"
                            >{{ aiSuggestion.fotoperiodo_sugerido }}h</span
                          >
                          <span
                            class="change"
                            v-if="aiSuggestion.ajuste_horas !== 0"
                            >{{ aiSuggestion.ajuste_horas }}h</span
                          >
                        </div>
                        <div class="ai-stat-card">
                          <span class="label">Intensidade</span>
                          <span class="value"
                            >{{ aiSuggestion.intensidade_sugerida }}%</span
                          >
                        </div>
                        <div
                          class="ai-stat-card"
                          v-if="
                            aiSuggestion.tpa && aiSuggestion.tpa.percentagem > 0
                          "
                        >
                          <span class="label">TPA</span>
                          <span
                            class="value tpa"
                            :class="aiSuggestion.tpa.urgencia"
                            >{{ aiSuggestion.tpa.percentagem }}%</span
                          >
                          <span class="urgencia">{{
                            aiSuggestion.tpa.urgencia
                          }}</span>
                        </div>
                      </div>

                      <!-- TPA detalhado -->
                      <div
                        class="ai-tpa-detail"
                        v-if="
                          aiSuggestion.tpa && aiSuggestion.tpa.percentagem > 0
                        "
                      >
                        <span class="material-icons-outlined">water_drop</span>
                        <div class="tpa-info">
                          <span class="tpa-desc">{{
                            aiSuggestion.tpa.descricao
                          }}</span>
                          <span
                            class="tpa-freq"
                            v-if="aiSuggestion.tpa.frequencia"
                          >
                            Frequência: {{ aiSuggestion.tpa.frequencia }}
                            <span v-if="aiSuggestion.tpa.dias > 1">
                              ({{ aiSuggestion.tpa.dias }} dias)</span
                            >
                          </span>
                        </div>
                      </div>

                      <!-- Luz Noturna -->
                      <div
                        class="ai-night-light"
                        v-if="
                          aiSuggestion.luz_noturna &&
                          aiSuggestion.luz_noturna.accao !== 'manter'
                        "
                        :class="aiSuggestion.luz_noturna.accao"
                      >
                        <span class="material-icons-outlined">nightlight</span>
                        <span>{{ aiSuggestion.luz_noturna.razao }}</span>
                        <span
                          class="badge"
                          v-if="aiSuggestion.luz_noturna.forcar"
                          >FORÇAR</span
                        >
                      </div>

                      <!-- Alimentação -->
                      <div
                        class="ai-feeding"
                        v-if="
                          aiSuggestion.alimentacao &&
                          aiSuggestion.alimentacao.accao !== 'manter'
                        "
                      >
                        <span class="material-icons-outlined">restaurant</span>
                        <span>{{ aiSuggestion.alimentacao.descricao }}</span>
                      </div>

                      <!-- Lista de acções -->
                      <div
                        class="ai-actions"
                        v-if="aiSuggestion.accoes?.length"
                      >
                        <h4>Acções Recomendadas:</h4>
                        <ul>
                          <li
                            v-for="(accao, i) in aiSuggestion.accoes"
                            :key="i"
                          >
                            {{ accao }}
                          </li>
                        </ul>
                      </div>

                      <button @click="aplicarSugestaoIA" class="ai-apply-btn">
                        <span class="material-icons-outlined">check</span>
                        Aplicar Sugestão de Luz
                      </button>
                    </div>
                  </div>
                </div>

                <!-- Intensidade (sempre visível em modo manual) -->
                <div class="setting-group" v-if="config.luzModo === 'manual'">
                  <label>Intensidade</label>
                  <div class="slider-control">
                    <input
                      type="range"
                      v-model.number="config.luzIntensidade"
                      @input="guardarIntensidade"
                      min="0"
                      max="100"
                      class="slider premium-slider"
                      :style="{ '--progress': config.luzIntensidade + '%' }"
                    />
                    <span class="slider-value"
                      >{{ config.luzIntensidade }}%</span
                    >
                  </div>
                </div>

                <div class="setting-group">
                  <label>Velocidade de Transição</label>
                  <div class="slider-control">
                    <input
                      type="range"
                      v-model.number="config.luzFadeSpeed"
                      @input="guardarIntensidade"
                      min="1"
                      max="50"
                      class="slider premium-slider speed-slider"
                      :style="{
                        '--progress':
                          ((config.luzFadeSpeed - 1) / 49) * 100 + '%',
                      }"
                    />
                    <span class="slider-value"
                      >{{ config.luzFadeSpeed }}ms</span
                    >
                  </div>
                  <span class="setting-hint"
                    >Menor = mais rápido (1-50ms por passo)</span
                  >
                </div>
              </div>

              <!-- Secção: Luz Noturna -->
              <div class="settings-section">
                <h3>
                  <span class="material-icons-outlined">nightlight</span>
                  Luz Noturna
                </h3>

                <div class="setting-group">
                  <label>Modo</label>
                  <div class="toggle-buttons mode-buttons">
                    <button
                      @click="
                        config.luzNoturnaModo = 'manual';
                        setLuzNoturnaManual(true);
                      "
                      :class="{ active: config.luzNoturnaModo === 'manual' }"
                    >
                      Manual
                    </button>
                    <button
                      @click="
                        config.luzNoturnaModo = 'horario';
                        setLuzNoturnaManual(false);
                      "
                      :class="{ active: config.luzNoturnaModo === 'horario' }"
                    >
                      Horário
                    </button>
                    <button
                      @click="config.luzNoturnaModo = 'ciclo'"
                      :class="{ active: config.luzNoturnaModo === 'ciclo' }"
                    >
                      Ciclo
                    </button>
                  </div>
                </div>

                <!-- Modo Horário -->
                <div
                  class="setting-group"
                  v-if="config.luzNoturnaModo === 'horario'"
                >
                  <label>Horário Fixo</label>
                  <div class="input-row">
                    <div class="input-field">
                      <span>Ligar</span>
                      <input
                        type="time"
                        :value="
                          formatTime(
                            config.luzNoturnaHoraLigar,
                            config.luzNoturnaMinutoLigar,
                          )
                        "
                        @change="updateLuzNoturnaLigarTime($event)"
                      />
                    </div>
                    <div class="input-field">
                      <span>Desligar</span>
                      <input
                        type="time"
                        :value="
                          formatTime(
                            config.luzNoturnaHoraDesligar,
                            config.luzNoturnaMinutoDesligar,
                          )
                        "
                        @change="updateLuzNoturnaDesligarTime($event)"
                      />
                    </div>
                  </div>
                </div>

                <!-- Modo Ciclo -->
                <div
                  class="setting-group"
                  v-if="config.luzNoturnaModo === 'ciclo'"
                >
                  <label>Fotoperíodo (horas por dia)</label>
                  <div class="cycle-buttons night">
                    <button
                      v-for="h in [4, 6, 8, 12, 16]"
                      :key="h"
                      @click="iniciarCicloLuzNoturna(h)"
                      :class="{
                        active:
                          config.luzNoturnaCicloHoras === h &&
                          config.luzNoturnaCicloInicio,
                      }"
                      class="cycle-btn"
                    >
                      {{ h }}h
                    </button>
                  </div>
                  <span
                    class="setting-hint"
                    v-if="config.luzNoturnaCicloInicio"
                  >
                    Ciclo iniciado: liga {{ config.luzNoturnaCicloHoras }}h por
                    dia
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<!--
  Script de lógica do dashboard AquaSense
  
  Contém toda a lógica de estado, comunicação com API e manipulação de dados
  dos sensores e controlos do aquário.
-->
<script setup lang="ts">
import { nextTick } from 'vue';

// ========== INTERFACES ==========
// Estrutura de dados para leituras dos sensores
interface SensorReading {
  id: number;
  device_id: string;
  sensor_type: string;
  value: number;
  unit: string | null;
  created_at: string;
}

// ========== ESTADO DOS SENSORES ==========
const readings = ref<SensorReading[]>([]); // Histórico de leituras
const lastUpdate = ref(""); // Última atualização
const currentTemp = ref<number | null>(null); // Temperatura da água
const currentTempTime = ref<string | null>(null); // Timestamp da temperatura
const currentPh = ref<number | null>(null); // Valor do pH
const currentPhTime = ref<string | null>(null); // Timestamp do pH
const phVoltage = ref<number | null>(null); // Tensão do sensor de pH
const ambientTemp = ref<number | null>(null); // Temperatura ambiente
const humidity = ref<number | null>(null); // Humidade
const turbidity = ref<number | null>(null); // Turbidez (%)
const turbidityVoltage = ref<number | null>(null); // Tensão do sensor de turbidez

// ========== ESTADO DOS DISPOSITIVOS ==========
const fanOn = ref(false); // Estado da ventoinha
const fanStatusTime = ref<string | null>(null); // Timestamp do estado
const lightOn = ref(false); // Estado da luz branca
const lightOnTime = ref<number | null>(null); // Timestamp da luz
const nightLightOn = ref(false); // Estado da luz noturna
const isConnected = ref(false); // Estado de ligação ao ESP32
const lastSeenMs = ref<number | null>(null); // Último contacto com ESP32

// ========== ESTADO DA INTERFACE ==========
const showSettings = ref(false); // Visibilidade do modal de definições
const showConsole = ref(false); // Visibilidade da consola
const currentTime = ref(""); // Hora actual formatada

// ========== CONSOLA ESP32 ==========
interface ConsoleLog {
  time: string;
  message: string;
  type: 'info' | 'warn' | 'error' | 'success';
}
const consoleLogs = ref<ConsoleLog[]>([]);
const consoleBody = ref<HTMLElement | null>(null);

const addConsoleLog = (message: string, type: ConsoleLog['type'] = 'info') => {
  const now = new Date();
  const time = now.toLocaleTimeString('pt-PT');
  consoleLogs.value.push({ time, message, type });
  if (consoleLogs.value.length > 200) {
    consoleLogs.value.shift();
  }
  nextTick(() => {
    if (consoleBody.value) {
      consoleBody.value.scrollTop = consoleBody.value.scrollHeight;
    }
  });
};

const toggleConsole = () => {
  showConsole.value = !showConsole.value;
};

const clearConsole = () => {
  consoleLogs.value = [];
};

// ========== CONFIGURAÇÃO DO SISTEMA ==========
// Configurações sincronizadas com o servidor
const config = reactive({
  // Ventoinha
  modoManual: false, // Modo manual da ventoinha
  ventoinhaManual: false, // Estado manual da ventoinha
  tempLigar: 14.0, // Temperatura para ligar (automático)
  tempDesligar: 13.0, // Temperatura para desligar (automático)

  // Luz branca
  luzManual: false, // Modo manual da luz branca
  luzEstado: false, // Estado manual da luz branca
  luzModo: "horario" as "manual" | "horario" | "ciclo" | "ai", // Modo de operação
  luzCicloHoras: 8, // Duração do ciclo (4, 6, 8, 12, 16)
  luzCicloInicio: null as string | null, // Timestamp do início do ciclo
  luzHoraLigar: 8, // Hora de ligar (automático)
  luzMinutoLigar: 0, // Minuto de ligar
  luzHoraDesligar: 20, // Hora de desligar (automático)
  luzMinutoDesligar: 0, // Minuto de desligar
  luzIntensidade: 100, // Intensidade PWM (0-100%)
  luzFadeSpeed: 10, // Velocidade de transição (ms por passo)

  // Luz noturna
  luzNoturnaManual: false, // Modo manual da luz noturna
  luzNoturnaEstado: false, // Estado manual da luz noturna
  luzNoturnaModo: "horario" as "manual" | "horario" | "ciclo", // Modo de operação
  luzNoturnaCicloHoras: 8, // Duração do ciclo
  luzNoturnaCicloInicio: null as string | null, // Timestamp do início do ciclo
  luzNoturnaHoraLigar: 20, // Hora de ligar (automático)
  luzNoturnaMinutoLigar: 0, // Minuto de ligar
  luzNoturnaHoraDesligar: 8, // Hora de desligar (automático)
  luzNoturnaMinutoDesligar: 0, // Minuto de desligar

  // IA
  aiAjusteFotoperiodo: false, // Ajuste automático por IA
  aiFotoperiodoSugerido: null as number | null, // Sugestão da IA
});

// Estado da IA
const aiSuggestion = ref<{
  fotoperiodo_sugerido: number;
  ajuste_horas: number;
  razao: string;
  intensidade_sugerida?: number;

  input: {
    fotoperiodo_base: number; 
    intensidade_actual: number;
    ph: number;
    temperatura: number;
    turbidez_24h: number;
    turbidez_actual: number;
  }
  tpa?: {
    percentagem: number;
    urgencia: string;
    frequencia: string;
    dias: number;
    descricao: string;
  };
  luz_noturna?: {
    accao: string;
    razao: string;
    forcar: boolean;
    periodo_max?: number;
  };
  alimentacao?: {
    accao: string;
    descricao: string;
    dias?: number;
    percentagem?: number;
  };
  accoes?: string[];
} | null>(null);

// Funções auxiliares para classes de alerta
const getAlertClass = (turbidez: number) => {
  if (turbidez > 80) return "alert-critical";
  if (turbidez > 60) return "alert-warning";
  if (turbidez > 40) return "alert-moderate";
  return "alert-ok";
};

const getTurbidityAlertClass = (turbidez: number) => {
  if (turbidez > 80) return "critical";
  if (turbidez > 60) return "warning";
  if (turbidez > 40) return "moderate";
  return "ok";
};

const formatTime = (hour: number, minute: number) => {
  return `${String(hour).padStart(2, "0")}:${String(minute).padStart(2, "0")}`;
};

const updateLigarTime = async (event: Event) => {
  const input = event.target as HTMLInputElement;
  const [h, m] = input.value.split(":").map(Number);
  config.luzHoraLigar = h ?? 8;
  config.luzMinutoLigar = m ?? 0;
  await guardarConfig();
};

const updateDesligarTime = async (event: Event) => {
  const input = event.target as HTMLInputElement;
  const [h, m] = input.value.split(":").map(Number);
  config.luzHoraDesligar = h ?? 20;
  config.luzMinutoDesligar = m ?? 0;
  await guardarConfig();
};

const updateLuzNoturnaLigarTime = async (event: Event) => {
  const input = event.target as HTMLInputElement;
  const [h, m] = input.value.split(":").map(Number);
  config.luzNoturnaHoraLigar = h ?? 20;
  config.luzNoturnaMinutoLigar = m ?? 0;
  await guardarConfig();
};

const updateLuzNoturnaDesligarTime = async (event: Event) => {
  const input = event.target as HTMLInputElement;
  const [h, m] = input.value.split(":").map(Number);
  config.luzNoturnaHoraDesligar = h ?? 8;
  config.luzNoturnaMinutoDesligar = m ?? 0;
  await guardarConfig();
};

const lightOnDuration = computed(() => {
  if (!lightOn.value || !lightOnTime.value) return "";
  const seconds = Math.floor((Date.now() - lightOnTime.value) / 1000);
  const hours = Math.floor(seconds / 3600);
  const mins = Math.floor((seconds % 3600) / 60);
  if (hours > 0) return `${hours}h ${mins}m`;
  return `${mins}m`;
});

const getTempClass = computed(() => {
  if (currentTemp.value === null) return "";
  if (currentTemp.value >= config.tempLigar) return "high";
  if (currentTemp.value <= config.tempDesligar) return "low";
  return "normal";
});

const getPhClass = computed(() => {
  if (currentPh.value === null) return "";
  if (currentPh.value < 6.5) return "acidic";
  if (currentPh.value > 7.5) return "alkaline";
  return "neutral";
});

const getTurbidityClass = computed(() => {
  if (turbidity.value === null) return "";
  if (turbidity.value <= 20) return "clear";
  if (turbidity.value >= 60) return "murky";
  return "moderate";
});

const formatDate = (date: string) => new Date(date).toLocaleString("pt-PT");

// Obter hora de início do ciclo (HH:MM)
const getCycleStartTime = (inicio: string | null) => {
  if (!inicio) return "--:--";
  const d = new Date(inicio);
  return `${String(d.getHours()).padStart(2, "0")}:${String(d.getMinutes()).padStart(2, "0")}`;
};

// Obter hora de fim do ciclo (início + horas)
const getCycleEndTime = (inicio: string | null, horas: number) => {
  if (!inicio) return "--:--";
  const d = new Date(inicio);
  d.setHours(d.getHours() + horas);
  return `${String(d.getHours()).padStart(2, "0")}:${String(d.getMinutes()).padStart(2, "0")}`;
};

// Traduzir tipos de sensor para português
const translateSensorType = (type: string) => {
  const t: Record<string, string> = {
    temperature: "Temperatura",
    pH: "pH",
    pH_voltage: "Tensão pH",
    fan_status: "Ventoinha",
    ambient_temp: "Temp. Ambiente",
    humidity: "Humidade",
    turbidity: "Turbidez",
    turbidity_voltage: "Tensão Turbidez",
    light_status: "Luz Branca",
    night_light_status: "Luz Noturna",
  };
  return t[type] || type;
};

// Formatar valores dos sensores para apresentação
const formatValue = (r: SensorReading) => {
  if (r.sensor_type === "fan_status")
    return r.value >= 1 ? "LIGADA" : "DESLIGADA";
  if (
    r.sensor_type === "light_status" ||
    r.sensor_type === "night_light_status"
  )
    return r.value >= 1 ? "LIGADA" : "DESLIGADA";
  if (r.sensor_type === "temperature") return `${r.value.toFixed(1)}°C`;
  if (r.sensor_type === "ambient_temp") return `${r.value.toFixed(1)}°C`;
  if (r.sensor_type === "humidity") return `${r.value.toFixed(0)}%`;
  if (r.sensor_type === "pH") return r.value.toFixed(2);
  if (r.sensor_type === "pH_voltage") return `${r.value.toFixed(3)}V`;
  if (r.sensor_type === "turbidity") return `${r.value.toFixed(0)}%`;
  if (r.sensor_type === "turbidity_voltage") return `${r.value.toFixed(2)}V`;
  return `${r.value}`;
};

const carregarConfig = async () => {
  try {
    const res = await $fetch<{ success: boolean; data: any }>("/api/config");
    if (res.success && res.data) {
      config.modoManual = res.data.modo_manual;
      config.ventoinhaManual = res.data.ventoinha_manual;
      config.tempLigar = parseFloat(res.data.temp_ligar);
      config.tempDesligar = parseFloat(res.data.temp_desligar);
      config.luzManual = res.data.luz_manual ?? false;
      config.luzEstado = res.data.luz_estado ?? false;
      config.luzHoraLigar = res.data.luz_hora_ligar ?? 8;
      config.luzMinutoLigar = res.data.luz_minuto_ligar ?? 0;
      config.luzHoraDesligar = res.data.luz_hora_desligar ?? 20;
      config.luzMinutoDesligar = res.data.luz_minuto_desligar ?? 0;
      config.luzIntensidade = res.data.luz_intensidade ?? 100;
      config.luzFadeSpeed = res.data.luz_fade_speed ?? 10;
      config.luzModo = res.data.luz_modo ?? "horario";
      config.luzCicloHoras = res.data.luz_ciclo_horas ?? 8;
      config.luzCicloInicio = res.data.luz_ciclo_inicio ?? null;
      config.luzNoturnaManual = res.data.luz_noturna_manual ?? false;
      config.luzNoturnaEstado = res.data.luz_noturna_estado ?? false;
      config.luzNoturnaModo = res.data.luz_noturna_modo ?? "horario";
      config.luzNoturnaCicloHoras = res.data.luz_noturna_ciclo_horas ?? 8;
      config.luzNoturnaCicloInicio = res.data.luz_noturna_ciclo_inicio ?? null;
      config.luzNoturnaHoraLigar = res.data.luz_noturna_hora_ligar ?? 20;
      config.luzNoturnaMinutoLigar = res.data.luz_noturna_minuto_ligar ?? 0;
      config.luzNoturnaHoraDesligar = res.data.luz_noturna_hora_desligar ?? 8;
      config.luzNoturnaMinutoDesligar =
        res.data.luz_noturna_minuto_desligar ?? 0;
      config.aiAjusteFotoperiodo = res.data.ai_ajuste_fotoperiodo ?? false;
      config.aiFotoperiodoSugerido = res.data.ai_fotoperiodo_sugerido ?? null;
    }
  } catch (e) {
    console.error(e);
  }
};

const guardarConfig = async () => {
  try {
    await $fetch("/api/config", {
      method: "POST",
      body: {
        modo_manual: config.modoManual,
        ventoinha_manual: config.ventoinhaManual,
        temp_ligar: config.tempLigar,
        temp_desligar: config.tempDesligar,
        luz_manual: config.luzManual,
        luz_estado: config.luzEstado,
        luz_hora_ligar: config.luzHoraLigar,
        luz_minuto_ligar: config.luzMinutoLigar,
        luz_hora_desligar: config.luzHoraDesligar,
        luz_minuto_desligar: config.luzMinutoDesligar,
        luz_intensidade: config.luzIntensidade,
        luz_fade_speed: config.luzFadeSpeed,
        luz_modo: config.luzModo,
        luz_ciclo_horas: config.luzCicloHoras,
        luz_ciclo_inicio: config.luzCicloInicio,
        luz_noturna_manual: config.luzNoturnaManual,
        luz_noturna_estado: config.luzNoturnaEstado,
        luz_noturna_hora_ligar: config.luzNoturnaHoraLigar,
        luz_noturna_minuto_ligar: config.luzNoturnaMinutoLigar,
        luz_noturna_hora_desligar: config.luzNoturnaHoraDesligar,
        luz_noturna_minuto_desligar: config.luzNoturnaMinutoDesligar,
        luz_noturna_modo: config.luzNoturnaModo,
        luz_noturna_ciclo_horas: config.luzNoturnaCicloHoras,
        luz_noturna_ciclo_inicio: config.luzNoturnaCicloInicio,
        ai_ajuste_fotoperiodo: config.aiAjusteFotoperiodo,
      },
    });
    await fetchData();
  } catch (e) {
    console.error(e);
  }
};

// Guardar apenas intensidade (sem fetchData para não interromper o slider)
const guardarIntensidade = async () => {
  try {
    await $fetch("/api/config", {
      method: "POST",
      body: {
        modo_manual: config.modoManual,
        ventoinha_manual: config.ventoinhaManual,
        temp_ligar: config.tempLigar,
        temp_desligar: config.tempDesligar,
        luz_manual: config.luzManual,
        luz_estado: config.luzEstado,
        luz_hora_ligar: config.luzHoraLigar,
        luz_minuto_ligar: config.luzMinutoLigar,
        luz_hora_desligar: config.luzHoraDesligar,
        luz_minuto_desligar: config.luzMinutoDesligar,
        luz_intensidade: config.luzIntensidade,
        luz_fade_speed: config.luzFadeSpeed,
        luz_noturna_manual: config.luzNoturnaManual,
        luz_noturna_estado: config.luzNoturnaEstado,
        luz_noturna_hora_ligar: config.luzNoturnaHoraLigar,
        luz_noturna_minuto_ligar: config.luzNoturnaMinutoLigar,
        luz_noturna_hora_desligar: config.luzNoturnaHoraDesligar,
        luz_noturna_minuto_desligar: config.luzNoturnaMinutoDesligar,
      },
    });
    // NÃO chamar fetchData aqui para não interromper o slider
  } catch (e) {
    console.error(e);
  }
};

const setModoManual = async (v: boolean) => {
  config.modoManual = v;
  await guardarConfig();
};
const setVentoinhaManual = async (v: boolean) => {
  config.ventoinhaManual = v;
  await guardarConfig();
};
const setLuzManual = async (v: boolean) => {
  config.luzManual = v;
  config.luzModo = v ? "manual" : "horario";
  await guardarConfig();
};
const setLuzEstado = async (v: boolean) => {
  config.luzManual = true;
  config.luzModo = "manual";
  config.luzEstado = v;
  await guardarConfig();
};

// Definir modo de luz (manual, horario, ciclo, ai)
const setLuzModo = async (modo: "manual" | "horario" | "ciclo" | "ai") => {
  config.luzModo = modo;
  config.luzManual = modo === "manual";
  if (modo === "ciclo") {
    // Não iniciar ciclo ainda - esperar que o utilizador escolha as horas
    config.luzCicloHoras = 0; // Reset para nenhum seleccionado
    config.luzCicloInicio = null;
  }
  await guardarConfig();
};

// Iniciar ciclo de luz com duração específica
const iniciarCicloLuz = async (horas: number) => {
  config.luzModo = "ciclo";
  config.luzCicloHoras = horas;
  config.luzCicloInicio = new Date().toISOString();
  config.luzEstado = true; // LIGAR a luz imediatamente
  config.luzManual = false;
  await guardarConfig();
};

// Funções para luz noturna
const setLuzNoturnaManual = async (v: boolean) => {
  config.luzNoturnaManual = v;
  config.luzNoturnaModo = v ? "manual" : "horario";
  await guardarConfig();
};

const setLuzNoturnaEstado = async (v: boolean) => {
  config.luzNoturnaManual = true;
  config.luzNoturnaModo = "manual";
  config.luzNoturnaEstado = v;
  await guardarConfig();
};

const iniciarCicloLuzNoturna = async (horas: number) => {
  config.luzNoturnaModo = "ciclo";
  config.luzNoturnaCicloHoras = horas;
  config.luzNoturnaCicloInicio = new Date().toISOString();
  config.luzNoturnaEstado = true; // LIGAR a luz imediatamente
  config.luzNoturnaManual = false;
  await guardarConfig();
};

// Buscar sugestão da IA
const fetchAISuggestion = async () => {
  addConsoleLog('A obter sugestão da IA...', 'info');
  try {
    const res = await $fetch<any>("http://localhost:5000/api/ai/photoperiod");
    aiSuggestion.value = res;
    addConsoleLog(`IA: Fotoperíodo ${res.fotoperiodo_sugerido}h, Intensidade ${res.intensidade_sugerida}%`, 'success');
  } catch (e) {
    console.error("Erro ao buscar sugestão IA:", e);
    addConsoleLog(`Erro IA: ${e}`, 'error');
  }
};

// Aplicar sugestão da IA
const aplicarSugestaoIA = async () => {
  if (aiSuggestion.value) {
    addConsoleLog('A aplicar sugestão da IA...', 'info');
    // Actualizar configuração local
    config.luzModo = "ai";
    config.luzManual = false; // Deixar modo AI controlar
    config.luzCicloHoras = aiSuggestion.value.fotoperiodo_sugerido;
    config.luzCicloInicio = new Date().toISOString();
    config.luzEstado = true; // Ligar a luz
    config.aiAjusteFotoperiodo = true;

    // Aplicar intensidade sugerida se disponível
    if (aiSuggestion.value.intensidade_sugerida !== undefined) {
      config.luzIntensidade = aiSuggestion.value.intensidade_sugerida;
    }

    // Aplicar sugestão de luz noturna
    if (aiSuggestion.value.luz_noturna) {
      const luzNoturna = aiSuggestion.value.luz_noturna;
      if (luzNoturna.accao === 'desligar' || luzNoturna.forcar === false) {
        // Desligar luz noturna
        config.luzNoturnaManual = true;
        config.luzNoturnaEstado = false;
        nightLightOn.value = false;
        addConsoleLog('Luz noturna: DESLIGADA (sugestão IA)', 'info');
      } else if (luzNoturna.accao === 'ligar' || luzNoturna.forcar === true) {
        // Ligar luz noturna
        config.luzNoturnaManual = true;
        config.luzNoturnaEstado = true;
        nightLightOn.value = true;
        addConsoleLog('Luz noturna: LIGADA (sugestão IA)', 'info');
      }
    }

    // Guardar e actualizar estado visual
    await guardarConfig();
    lightOn.value = true; // Actualizar card imediatamente
    addConsoleLog(`Configuração aplicada: ${config.luzCicloHoras}h @ ${config.luzIntensidade}%`, 'success');
  }
};

// ========== FUNÇÕES DO MODAL DE DEFINIÇÕES ==========
// Abrir modal de definições
const openSettings = () => {
  showSettings.value = true;
  document.body.style.overflow = "hidden"; // Prevenir scroll do body
};

// Fechar modal de definições
const closeSettings = () => {
  showSettings.value = false;
  document.body.style.overflow = ""; // Restaurar scroll do body
};

// ========== FUNÇÕES DE CONTROLO RÁPIDO DE LUZES ==========
// Alternar luz branca (liga/desliga)
const toggleWhiteLight = async () => {
  config.luzManual = true;
  config.luzEstado = !lightOn.value;
  await guardarConfig();
};

// Alternar luz noturna (liga/desliga)
const toggleNightLight = async () => {
  config.luzNoturnaManual = true;
  config.luzNoturnaEstado = !nightLightOn.value;
  await guardarConfig();
};

const fetchData = async () => {
  try {
    const res = await $fetch<{ success: boolean; data: SensorReading[] }>(
      "/api/sensor?limit=100",
    );
    if (res.success && res.data.length > 0) {
      addConsoleLog(`Recebidos ${res.data.length} registos de sensores`, 'success');
      readings.value = res.data.map((r) => ({
        ...r,
        value: parseFloat(String(r.value)),
      }));
      // Verificar se ESP32 está a enviar dados recentes (últimos 30s)
      const latestReading = res.data[0];
      if (latestReading) {
        const lastTime = new Date(latestReading.created_at).getTime();
        lastSeenMs.value = Number.isFinite(lastTime) ? lastTime : Date.now();
        const now = Date.now();
        isConnected.value = now - (lastSeenMs.value ?? now) < 30000; // 30 segundos
      } else {
        const now = Date.now();
        isConnected.value = now - (lastSeenMs.value ?? 0) < 30000;
      }
      const temp = res.data.find((r) => r.sensor_type === "temperature");
      if (temp) {
        currentTemp.value = parseFloat(String(temp.value));
        currentTempTime.value = temp.created_at;
      }
      const ph = res.data.find((r) => r.sensor_type === "pH");
      if (ph) {
        currentPh.value = parseFloat(String(ph.value));
        currentPhTime.value = ph.created_at;
      }
      // Tensão do sensor de pH
      const phV = res.data.find((r) => r.sensor_type === "pH_voltage");
      if (phV) {
        phVoltage.value = parseFloat(String(phV.value));
      }
      const fan = res.data.find((r) => r.sensor_type === "fan_status");
      if (fan) {
        fanOn.value = parseFloat(String(fan.value)) >= 1;
        fanStatusTime.value = fan.created_at;
      }
      const ambient = res.data.find((r) => r.sensor_type === "ambient_temp");
      if (ambient) {
        ambientTemp.value = parseFloat(String(ambient.value));
      }
      const hum = res.data.find((r) => r.sensor_type === "humidity");
      if (hum) {
        humidity.value = parseFloat(String(hum.value));
      }
      const turb = res.data.find((r) => r.sensor_type === "turbidity");
      if (turb) {
        turbidity.value = parseFloat(String(turb.value));
      }
      const turbV = res.data.find((r) => r.sensor_type === "turbidity_voltage");
      if (turbV) {
        turbidityVoltage.value = parseFloat(String(turbV.value));
      }
      const light = res.data.find((r) => r.sensor_type === "light_status");
      if (light) {
        const wasOff = !lightOn.value;
        lightOn.value = parseFloat(String(light.value)) >= 1;
        if (lightOn.value && wasOff) {
          lightOnTime.value = Date.now();
        } else if (!lightOn.value) {
          lightOnTime.value = null;
        }
      }
      // Estado da luz noturna
      const nightLight = res.data.find(
        (r) => r.sensor_type === "night_light_status",
      );
      if (nightLight) {
        nightLightOn.value = parseFloat(String(nightLight.value)) >= 1;
      }
    }
    lastUpdate.value = new Date().toLocaleTimeString("pt-PT");
  } catch (e) {
    console.error(e);
    addConsoleLog(`Erro ao obter dados: ${e}`, 'error');
    const now = Date.now();
    isConnected.value = now - (lastSeenMs.value ?? 0) < 30000;
  }
};

// Buscar logs do ESP32
let lastLogTimestamp = 0;
const fetchESP32Logs = async () => {
  try {
    const res = await $fetch<{ success: boolean; logs: any[]; timestamp: number }>(
      `/api/logs?since=${lastLogTimestamp}`
    );
    if (res.success && res.logs.length > 0) {
      for (const log of res.logs) {
        // Adicionar apenas logs novos do ESP32
        consoleLogs.value.push({
          time: log.time,
          message: `[ESP32] ${log.message}`,
          type: log.type || 'info'
        });
      }
      // Limitar a 200 logs
      while (consoleLogs.value.length > 200) {
        consoleLogs.value.shift();
      }
      lastLogTimestamp = res.timestamp;
      // Auto-scroll
      nextTick(() => {
        if (consoleBody.value) {
          consoleBody.value.scrollTop = consoleBody.value.scrollHeight;
        }
      });
    }
  } catch (e) {
    // Silencioso - logs são opcionais
  }
};

onMounted(() => {
  addConsoleLog('AquaSense Dashboard iniciado', 'success');
  addConsoleLog('A carregar configuração...', 'info');
  carregarConfig();
  fetchData();
  setInterval(fetchData, 5000);
  
  // Buscar logs do ESP32 a cada 2 segundos
  setInterval(fetchESP32Logs, 2000);

  // Atualizar hora atual
  const updateTime = () => {
    currentTime.value = new Date().toLocaleTimeString("pt-PT", {
      hour: "2-digit",
      minute: "2-digit",
    });
  };
  updateTime();
  setInterval(updateTime, 1000);
});
</script>

<!--
  Estilos do Dashboard AquaSense
  
  Tema escuro com gradientes modernos e animações suaves.
  Responsivo para desktop e dispositivos móveis.
-->
<style scoped>
/* ========== RESET E BASE ========== */
*,
*::before,
*::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
  border: none;
}

/* ========== CUSTOM SCROLLBAR ========== */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: rgba(15, 23, 42, 0.5);
  border-radius: 4px;
}

::-webkit-scrollbar-thumb {
  background: linear-gradient(135deg, #3b82f6, #6366f1);
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(135deg, #60a5fa, #818cf8);
}

/* Firefox scrollbar */
* {
  scrollbar-width: thin;
  scrollbar-color: #3b82f6 rgba(15, 23, 42, 0.5);
}

.app {
  min-height: 100vh;
  background: linear-gradient(135deg, #0c1222 0%, #1a1f35 100%);
  color: #e2e8f0;
  font-family:
    "Inter",
    -apple-system,
    sans-serif;
}

/* ========== CABEÇALHO ========== */
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
  background: linear-gradient(135deg, #06b6d4, #3b82f6);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.logo-icon span {
  font-size: 28px;
  color: white;
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

/* Acções do cabeçalho */
.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.settings-btn {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  background: rgba(51, 65, 85, 0.5);
  color: #94a3b8;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.settings-btn:hover {
  background: rgba(51, 65, 85, 0.8);
  color: #f1f5f9;
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

@keyframes pulse {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

/* ========== CONTEÚDO PRINCIPAL ========== */
.main {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem 1.5rem;
}

/* ========== TÍTULOS DE SECÇÃO ========== */
.section-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 1.25rem;
  font-weight: 600;
  color: #f1f5f9;
  margin-bottom: 1.5rem;
}

.section-title span {
  font-size: 24px;
  color: #3b82f6;
}

/* ========== SECÇÃO DE ILUMINAÇÃO ========== */
.lighting-section {
  margin-bottom: 2rem;
}

.lighting-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 1.5rem;
  margin-bottom: 1rem;
}

.light-card {
  background: rgba(30, 41, 59, 0.7);
  border-radius: 20px;
  padding: 1.5rem;
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.light-card:hover {
  transform: translateY(-2px);
  background: rgba(30, 41, 59, 0.9);
}
.light-card.white-light.active {
  border-color: rgba(245, 158, 11, 0.5);
}
.light-card.blue-light.active {
  border-color: rgba(99, 102, 241, 0.5);
}

.light-card-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 1rem;
}

.light-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.light-icon span {
  font-size: 24px;
  color: white;
}
.light-icon.white {
  background: linear-gradient(135deg, #f59e0b, #fbbf24);
}
.light-icon.blue {
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
}

.light-info {
  flex: 1;
}
.light-info h3 {
  font-size: 1.1rem;
  font-weight: 600;
  margin: 0;
  color: #f1f5f9;
}
.light-mode {
  font-size: 0.75rem;
  color: #94a3b8;
}

/* Botão de energia */
.power-btn {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: rgba(51, 65, 85, 0.5);
  color: #64748b;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.power-btn:hover {
  background: rgba(51, 65, 85, 0.8);
}
.power-btn.on {
  background: linear-gradient(135deg, #f59e0b, #fbbf24);
  color: white;
}
.power-btn.blue.on {
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: white;
}

.light-card-body {
  min-height: 60px;
}

/* Horário automático */
.schedule-display {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 0.75rem;
  background: rgba(51, 65, 85, 0.3);
  border-radius: 10px;
}

.schedule-item {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #94a3b8;
}

.schedule-item span:first-child {
  font-size: 18px;
}
.schedule-separator {
  color: #64748b;
  font-size: 1.25rem;
}

/* Controlo de intensidade */
.intensity-control {
  padding: 0.5rem 0;
}

.intensity-label {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
  font-size: 0.875rem;
  color: #94a3b8;
}

.intensity-value {
  color: #f59e0b;
  font-weight: 600;
}

.slider {
  width: 100%;
  height: 8px;
  border-radius: 4px;
  background: #1e293b;
  appearance: none;
  cursor: pointer;
}

.slider::-webkit-slider-thumb {
  appearance: none;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #f59e0b;
  cursor: pointer;
}

.slider::-moz-range-thumb {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #f59e0b;
  cursor: pointer;
  border: none;
}

/* ========== SLIDER PREMIUM (INTENSIDADE) ========== */
.intensity-control.premium {
  padding: 0.75rem;
  background: rgba(51, 65, 85, 0.3);
  border-radius: 12px;
  margin-top: 0.5rem;
}

.intensity-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.intensity-header .intensity-label {
  font-size: 0.875rem;
  color: #94a3b8;
  font-weight: 500;
}

.intensity-header .intensity-value {
  font-size: 1.25rem;
  font-weight: 700;
  color: #f59e0b;
}

.intensity-slider-wrap {
  position: relative;
}

.intensity-slider.premium {
  width: 100%;
  height: 8px;
  border-radius: 4px;
  background: linear-gradient(
    to right,
    #f59e0b var(--progress, 50%),
    #1e293b var(--progress, 50%)
  );
  appearance: none;
  cursor: pointer;
  transition: background 0.1s ease;
}

.intensity-slider.premium::-webkit-slider-thumb {
  appearance: none;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: linear-gradient(135deg, #f59e0b, #fbbf24);
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(245, 158, 11, 0.4);
  transition:
    transform 0.2s ease,
    box-shadow 0.2s ease;
}

.intensity-slider.premium::-webkit-slider-thumb:hover {
  transform: scale(1.1);
  box-shadow: 0 4px 12px rgba(245, 158, 11, 0.5);
}

.intensity-slider.premium::-moz-range-thumb {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: linear-gradient(135deg, #f59e0b, #fbbf24);
  cursor: pointer;
  border: none;
  box-shadow: 0 2px 8px rgba(245, 158, 11, 0.4);
}

/* Controlos de intensidade nos modos ciclo/horário */
.intensity-label-small {
  display: block;
  font-size: 0.8rem;
  color: #94a3b8;
  margin-top: 1rem;
  margin-bottom: 0.5rem;
}

.intensity-slider-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.intensity-slider-row .intensity-slider {
  flex: 1;
  height: 6px;
  border-radius: 3px;
  background: #1e293b;
  appearance: none;
  cursor: pointer;
}

.intensity-slider-row .intensity-slider::-webkit-slider-thumb {
  appearance: none;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: linear-gradient(135deg, #f59e0b, #fbbf24);
  cursor: pointer;
  box-shadow: 0 2px 6px rgba(245, 158, 11, 0.4);
}

.intensity-slider-row .intensity-slider::-moz-range-thumb {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: linear-gradient(135deg, #f59e0b, #fbbf24);
  cursor: pointer;
  border: none;
}

.intensity-slider-row .intensity-value {
  min-width: 45px;
  font-size: 0.9rem;
  font-weight: 600;
  color: #fbbf24;
  text-align: right;
}

/* Status pill para estado manual */
.manual-indicator {
  display: flex;
  justify-content: center;
  padding: 0.5rem;
}

.status-pill {
  padding: 0.5rem 1.5rem;
  border-radius: 20px;
  font-size: 0.875rem;
  font-weight: 600;
  background: rgba(51, 65, 85, 0.5);
  color: #94a3b8;
}

.status-pill.active {
  background: rgba(245, 158, 11, 0.2);
  color: #f59e0b;
}

/* ========== SLIDER CONTROL (MODAL) ========== */
.slider-control {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.slider-control .slider {
  flex: 1;
}

.slider-control .slider-value {
  min-width: 60px;
  text-align: right;
  font-size: 1rem;
  font-weight: 600;
  color: #f59e0b;
}

.premium-slider {
  height: 8px;
  border-radius: 4px;
  background: linear-gradient(
    to right,
    #f59e0b var(--progress, 50%),
    #1e293b var(--progress, 50%)
  );
  -webkit-appearance: none;
  appearance: none;
}

.premium-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: linear-gradient(135deg, #f59e0b, #fbbf24);
  box-shadow: 0 2px 8px rgba(245, 158, 11, 0.4);
  cursor: pointer;
  border: none;
}

.speed-slider {
  background: linear-gradient(
    to right,
    #3b82f6 var(--progress, 50%),
    #1e293b var(--progress, 50%)
  );
}

.speed-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: linear-gradient(135deg, #3b82f6, #60a5fa);
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.4);
  cursor: pointer;
  border: none;
}

.setting-hint {
  display: block;
  font-size: 0.75rem;
  color: #64748b;
  margin-top: 0.5rem;
}

/* Cycle and AI display in cards */
.cycle-display,
.ai-display {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.75rem;
  background: rgba(245, 158, 11, 0.1);
  border-radius: 10px;
}

.cycle-info,
.ai-info {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #f59e0b;
  font-size: 0.9rem;
}

.ai-display {
  background: rgba(139, 92, 246, 0.1);
}

.ai-info {
  color: #a78bfa;
}

.cycle-badge {
  background: #f59e0b;
  color: #0f172a;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.7rem;
  font-weight: 700;
  margin-left: 4px;
}

.light-mode.mode-ciclo {
  color: #f59e0b;
}

.light-mode.mode-ai {
  color: #a78bfa;
}

.schedule-separator.cycle {
  background: linear-gradient(135deg, #f59e0b, #fbbf24);
  color: #0f172a;
  padding: 4px 10px;
  border-radius: 12px;
  font-weight: 700;
  font-size: 0.85rem;
}

.schedule-separator.cycle.night {
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: white;
}

.schedule-separator.ai {
  background: linear-gradient(135deg, #8b5cf6, #a78bfa);
  color: white;
  padding: 4px 10px;
  border-radius: 12px;
  font-weight: 700;
  font-size: 0.85rem;
}

.intensity-display {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  margin-top: 8px;
  font-size: 0.85rem;
  color: #fbbf24;
}
.intensity-display .material-icons-outlined {
  font-size: 16px;
}

.cycle-badge.night {
  background: #6366f1;
}

.cycle-display.night {
  background: rgba(99, 102, 241, 0.1);
}

.status-pill.active.night {
  background: rgba(99, 102, 241, 0.2);
  color: #818cf8;
}

.off-display {
  display: flex;
  justify-content: center;
  padding: 0.75rem;
}

.status-pill.off {
  background: rgba(51, 65, 85, 0.5);
  color: #64748b;
}

.status-pill.off.night {
  background: rgba(51, 65, 85, 0.5);
  color: #64748b;
}

/* Estado manual */
.manual-status {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.75rem;
  background: rgba(51, 65, 85, 0.3);
  border-radius: 10px;
}

.status-text {
  color: #94a3b8;
  font-weight: 500;
}

/* Barra de estado da luz */
.light-status-bar {
  height: 4px;
  border-radius: 2px;
  margin-top: 1rem;
  background: rgba(51, 65, 85, 0.5);
  transition: all 0.3s ease;
}

.light-status-bar.active {
  background: linear-gradient(to right, #f59e0b, #fbbf24);
}
.light-status-bar.blue.active {
  background: linear-gradient(to right, #6366f1, #8b5cf6);
}

/* Hora atual */
.current-time-display {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 0.75rem;
  background: rgba(30, 41, 59, 0.5);
  border-radius: 12px;
  margin-top: 1rem;
}

.current-time-display span:first-child {
  color: #64748b;
}
.current-time-display .time {
  font-size: 1.5rem;
  font-weight: 700;
  color: #f59e0b;
  font-family: monospace;
}

/* ========== SECÇÃO DE PARÂMETROS ========== */
.parameters-section {
  margin-bottom: 2rem;
}

.sensors-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
}

.sensor-card {
  background: rgba(30, 41, 59, 0.7);
  border-radius: 20px;
  padding: 1.5rem;
  transition: all 0.3s ease;
}

.sensor-card:hover {
  transform: translateY(-2px);
  background: rgba(30, 41, 59, 0.9);
}

.sensor-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 1.25rem;
}

.sensor-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.sensor-icon span {
  font-size: 24px;
  color: white;
}
.sensor-icon.temp {
  background: linear-gradient(135deg, #f97316, #ef4444);
}
.sensor-icon.ph {
  background: linear-gradient(135deg, #8b5cf6, #a855f7);
}
.sensor-icon.ambient {
  background: linear-gradient(135deg, #06b6d4, #0891b2);
}
.sensor-icon.humidity {
  background: linear-gradient(135deg, #3b82f6, #6366f1);
}
.sensor-icon.turbidity {
  background: linear-gradient(135deg, #14b8a6, #06b6d4);
}

.sensor-info h3 {
  font-size: 1rem;
  font-weight: 600;
  margin: 0;
  color: #f1f5f9;
}
.sensor-info span {
  font-size: 0.75rem;
  color: #94a3b8;
}

.sensor-value {
  display: flex;
  align-items: baseline;
  gap: 4px;
  margin-bottom: 0.75rem;
}

.sensor-value .value {
  font-size: 2.75rem;
  font-weight: 700;
  color: #f1f5f9;
}
.sensor-value .value.high {
  color: #ef4444;
}
.sensor-value .value.low {
  color: #3b82f6;
}
.sensor-value .value.normal {
  color: #f97316;
}
.sensor-value .value.acidic {
  color: #ef4444;
}
.sensor-value .value.neutral {
  color: #10b981;
}
.sensor-value .value.alkaline {
  color: #3b82f6;
}
.sensor-value .value.clear {
  color: #10b981;
}
.sensor-value .value.moderate {
  color: #f59e0b;
}
.sensor-value .value.murky {
  color: #ef4444;
}
.sensor-value .unit {
  font-size: 1.25rem;
  color: #64748b;
}

.sensor-footer {
  display: flex;
  gap: 1rem;
}

.threshold {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 0.75rem;
  color: #94a3b8;
}

.threshold span {
  font-size: 14px;
}

/* Escalas de pH e turbidez */
.ph-scale,
.turbidity-scale {
  margin-top: 0.5rem;
}

.scale-bar {
  height: 6px;
  border-radius: 3px;
  background: linear-gradient(to right, #ef4444, #22c55e, #3b82f6);
}

.turbidity-bar {
  background: linear-gradient(to right, #10b981, #f59e0b, #ef4444);
}

.scale-labels {
  display: flex;
  justify-content: space-between;
  font-size: 0.7rem;
  color: #64748b;
  margin-top: 4px;
}

/* Tensão do sensor */
.sensor-voltage {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-top: 0.75rem;
  font-size: 0.8rem;
  color: #94a3b8;
}

.sensor-voltage span {
  font-size: 16px;
}

/* ========== SECÇÃO DA VENTOINHA ========== */
.fan-section {
  margin-bottom: 2rem;
}

.fan-card {
  background: rgba(30, 41, 59, 0.7);
  border-radius: 20px;
  padding: 1.5rem;
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.fan-card.active {
  border-color: rgba(16, 185, 129, 0.5);
  background: rgba(16, 185, 129, 0.05);
}

.fan-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 1rem;
}

.fan-icon {
  width: 56px;
  height: 56px;
  border-radius: 14px;
  background: #475569;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.fan-icon span {
  font-size: 28px;
  color: white;
}
.fan-icon.active {
  background: linear-gradient(135deg, #10b981, #14b8a6);
}

.fan-info {
  flex: 1;
}
.fan-info h3 {
  font-size: 1.1rem;
  font-weight: 600;
  margin: 0;
  color: #f1f5f9;
}
.fan-mode {
  font-size: 0.75rem;
  color: #94a3b8;
}

.fan-status-text {
  font-size: 1rem;
  font-weight: 700;
  color: #64748b;
  padding: 0.5rem 1rem;
  background: rgba(51, 65, 85, 0.5);
  border-radius: 8px;
}

.fan-status-text.on {
  color: #10b981;
  background: rgba(16, 185, 129, 0.15);
}

.fan-controls {
  margin-bottom: 1rem;
}

.quick-controls {
  display: flex;
  gap: 12px;
}

.quick-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px 20px;
  border-radius: 10px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  background: rgba(51, 65, 85, 0.5);
  color: #94a3b8;
}

.quick-btn:hover {
  background: rgba(51, 65, 85, 0.8);
}
.quick-btn.on.active {
  background: #10b981;
  color: white;
}
.quick-btn.off.active {
  background: #ef4444;
  color: white;
}

.auto-info {
  display: flex;
  gap: 1.5rem;
  padding: 0.75rem;
  background: rgba(51, 65, 85, 0.3);
  border-radius: 10px;
}

.temp-threshold {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #94a3b8;
  font-size: 0.9rem;
}

.temp-threshold strong {
  color: #f1f5f9;
}

/* ========== HISTÓRICO ========== */
.history {
  background: rgba(30, 41, 59, 0.7);
  border-radius: 20px;
  overflow: hidden;
  margin-bottom: 2rem;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  background: rgba(51, 65, 85, 0.3);
}

.history-header h2 {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 1.125rem;
  font-weight: 600;
  margin: 0;
}

.history-header h2 span {
  font-size: 20px;
  color: #64748b;
}

.badge {
  background: #334155;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.75rem;
  color: #94a3b8;
}

.history-table {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
}
th,
td {
  padding: 1rem 1.5rem;
  text-align: left;
}
th {
  font-size: 0.75rem;
  text-transform: uppercase;
  color: #64748b;
  font-weight: 500;
}
tr:not(:last-child) {
  border-bottom: 1px solid rgba(51, 65, 85, 0.5);
}
tbody tr:hover {
  background: rgba(51, 65, 85, 0.3);
}
td {
  font-size: 0.875rem;
  color: #e2e8f0;
}

.sensor-badge {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 500;
}

.sensor-badge.temperature {
  background: rgba(249, 115, 22, 0.2);
  color: #fb923c;
}
.sensor-badge.pH {
  background: rgba(139, 92, 246, 0.2);
  color: #a78bfa;
}
.sensor-badge.pH_voltage {
  background: rgba(139, 92, 246, 0.2);
  color: #a78bfa;
}
.sensor-badge.fan_status {
  background: rgba(16, 185, 129, 0.2);
  color: #34d399;
}
.sensor-badge.turbidity {
  background: rgba(20, 184, 166, 0.2);
  color: #2dd4bf;
}
.sensor-badge.turbidity_voltage {
  background: rgba(20, 184, 166, 0.2);
  color: #2dd4bf;
}
.sensor-badge.light_status {
  background: rgba(245, 158, 11, 0.2);
  color: #fbbf24;
}
.sensor-badge.night_light_status {
  background: rgba(99, 102, 241, 0.2);
  color: #a5b4fc;
}

.value-cell {
  font-weight: 600;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  color: #64748b;
}

.empty-state span {
  font-size: 48px;
  margin-bottom: 1rem;
}

/* ========== RODAPÉ ========== */
.footer {
  text-align: center;
  padding: 1.5rem;
  color: #64748b;
  font-size: 0.75rem;
}

/* ========== MODAL DE DEFINIÇÕES ========== */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.modal-container {
  background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
  border-radius: 20px;
  width: 100%;
  max-width: 600px;
  max-height: 85vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
  font-family:
    "Inter",
    -apple-system,
    BlinkMacSystemFont,
    "Segoe UI",
    Roboto,
    sans-serif;
}

.modal-container input {
  font-family:
    "Inter",
    -apple-system,
    BlinkMacSystemFont,
    "Segoe UI",
    Roboto,
    sans-serif;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid rgba(51, 65, 85, 0.5);
}

.modal-header h2 {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 1.25rem;
  font-weight: 600;
  margin: 0;
  color: #f1f5f9;
}

.modal-header h2 span {
  font-size: 24px;
  color: #3b82f6;
}

.close-btn {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: rgba(51, 65, 85, 0.5);
  color: #94a3b8;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.close-btn:hover {
  background: rgba(239, 68, 68, 0.3);
  color: #ef4444;
}

/* Scroll personalizado */
.modal-content {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
}

.custom-scroll::-webkit-scrollbar {
  width: 8px;
}
.custom-scroll::-webkit-scrollbar-track {
  background: rgba(51, 65, 85, 0.2);
  border-radius: 4px;
}
.custom-scroll::-webkit-scrollbar-thumb {
  background: rgba(99, 102, 241, 0.5);
  border-radius: 4px;
}
.custom-scroll::-webkit-scrollbar-thumb:hover {
  background: rgba(99, 102, 241, 0.7);
}

/* Secções do modal */
.settings-section {
  background: rgba(51, 65, 85, 0.3);
  border-radius: 16px;
  padding: 1.25rem;
  margin-bottom: 1rem;
}

.settings-section h3 {
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

.settings-section h3 span {
  font-size: 20px;
  color: #3b82f6;
}

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
.toggle-buttons button:active:not(:disabled) {
  filter: brightness(0.8);
}
.toggle-buttons button.active {
  background: #3b82f6;
  color: white;
}
.toggle-buttons button.active.success {
  background: #10b981;
}
.toggle-buttons button.active.danger {
  background: #ef4444;
}
.toggle-buttons button:disabled {
  cursor: not-allowed;
  opacity: 0.5;
}

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
  font-family:
    "Inter",
    -apple-system,
    BlinkMacSystemFont,
    "Segoe UI",
    Roboto,
    sans-serif;
}

.input-field input:focus {
  outline: 2px solid #3b82f6;
}

/* Fix time input icons - make them white */
.input-field input[type="time"] {
  color-scheme: dark;
}

.input-field input[type="time"]::-webkit-calendar-picker-indicator {
  filter: invert(1);
  opacity: 0.7;
  cursor: pointer;
}

.input-field input[type="time"]::-webkit-calendar-picker-indicator:hover {
  opacity: 1;
}

/* Animações do modal */
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: all 0.3s ease;
}

.modal-fade-enter-active .modal-container,
.modal-fade-leave-active .modal-container {
  transition: all 0.3s ease;
}

.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}

.modal-fade-enter-from .modal-container,
.modal-fade-leave-to .modal-container {
  transform: scale(0.95) translateY(20px);
  opacity: 0;
}

/* Material Icons */
.material-icons-outlined {
  font-family: "Material Icons Outlined";
  font-size: 24px;
  line-height: 1;
}

/* ========== BOTÕES DE MODO E CICLO ========== */
.mode-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.mode-buttons button {
  flex: 1;
  min-width: 70px;
  padding: 0.5rem 0.75rem;
  font-size: 0.8rem;
}

.mode-buttons .ai-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  color: white;
  background: linear-gradient(135deg, #8b5cf6, #6366f1);
}

.mode-buttons .ai-btn.active {
  background: linear-gradient(135deg, #a78bfa, #818cf8);
  box-shadow: 0 0 12px rgba(139, 92, 246, 0.5);
}

.mode-buttons .ai-btn .material-icons-outlined {
  font-size: 16px;
}

.cycle-buttons {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.cycle-btn {
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

.cycle-btn:hover {
  background: rgba(245, 158, 11, 0.1);
  border-color: rgba(245, 158, 11, 0.3);
  color: #f59e0b;
}

.cycle-btn.active {
  background: linear-gradient(135deg, #f59e0b, #fbbf24);
  border-color: #f59e0b;
  color: #0f172a;
  box-shadow: 0 0 12px rgba(245, 158, 11, 0.4);
}

.cycle-buttons.night .cycle-btn:hover {
  background: rgba(99, 102, 241, 0.1);
  border-color: rgba(99, 102, 241, 0.3);
  color: #6366f1;
}

.cycle-buttons.night .cycle-btn.active {
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  border-color: #6366f1;
  color: white;
  box-shadow: 0 0 12px rgba(99, 102, 241, 0.4);
}

/* ========== SECÇÃO IA ========== */
.ai-section {
  margin-top: 0.5rem;
}

.ai-card {
  background: linear-gradient(
    135deg,
    rgba(139, 92, 246, 0.1),
    rgba(99, 102, 241, 0.1)
  );
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
.ai-alert.alert-critical {
  background: rgba(239, 68, 68, 0.2);
  color: #fca5a5;
}
.ai-alert.alert-warning {
  background: rgba(245, 158, 11, 0.2);
  color: #fcd34d;
}
.ai-alert.alert-moderate {
  background: rgba(59, 130, 246, 0.2);
  color: #93c5fd;
}
.ai-alert.alert-ok {
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
.ai-stat-card .value.critical {
  color: #f87171;
}
.ai-stat-card .value.warning {
  color: #fbbf24;
}
.ai-stat-card .value.moderate {
  color: #60a5fa;
}
.ai-stat-card .value.ok {
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

/* TPA detalhado */
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

/* Luz noturna */
.ai-night-light {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  border-radius: 8px;
  font-size: 0.8rem;
  margin-bottom: 1rem;
}
.ai-night-light.desligar {
  background: rgba(239, 68, 68, 0.15);
  color: #fca5a5;
}
.ai-night-light.reduzir {
  background: rgba(245, 158, 11, 0.15);
  color: #fcd34d;
}
.ai-night-light.monitorizar {
  background: rgba(59, 130, 246, 0.15);
  color: #93c5fd;
}
.ai-night-light .material-icons-outlined {
  font-size: 18px;
}
.ai-night-light .badge {
  margin-left: auto;
  padding: 2px 8px;
  background: rgba(239, 68, 68, 0.3);
  border-radius: 4px;
  font-size: 0.65rem;
  font-weight: 700;
  color: #f87171;
}

.ai-feeding {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  background: rgba(245, 158, 11, 0.1);
  border-radius: 8px;
  font-size: 0.8rem;
  color: #fcd34d;
  margin-bottom: 1rem;
}
.ai-feeding .material-icons-outlined {
  font-size: 18px;
}

.ai-actions {
  background: rgba(30, 41, 59, 0.6);
  padding: 12px;
  border-radius: 8px;
  margin-bottom: 1rem;
}
.ai-actions h4 {
  font-size: 0.75rem;
  color: #94a3b8;
  margin: 0 0 8px 0;
  text-transform: uppercase;
}
.ai-actions ul {
  margin: 0;
  padding-left: 20px;
}
.ai-actions li {
  font-size: 0.8rem;
  color: #cbd5e1;
  margin-bottom: 4px;
}

.ai-apply-btn {
  width: 100%;
  padding: 0.75rem;
  background: linear-gradient(135deg, #10b981, #059669);
  border: none;
  border-radius: 8px;
  color: white;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.ai-apply-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4);
}

/* ========== CONSOLA ESP32 ========== */
.console-btn {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  background: rgba(30, 41, 59, 0.8);
  border: 1px solid rgba(148, 163, 184, 0.2);
  color: #94a3b8;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}
.console-btn:hover {
  background: rgba(51, 65, 85, 0.8);
  color: #e2e8f0;
}
.console-btn.active {
  background: rgba(59, 130, 246, 0.2);
  border-color: #3b82f6;
  color: #60a5fa;
}

.console-panel {
  position: fixed;
  top: 80px;
  right: 16px;
  width: 450px;
  max-width: calc(100vw - 32px);
  background: rgba(15, 23, 42, 0.98);
  border: 1px solid rgba(148, 163, 184, 0.2);
  border-radius: 12px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.5);
  z-index: 1000;
  display: flex;
  flex-direction: column;
  max-height: 60vh;
}
.console-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border-bottom: 1px solid rgba(148, 163, 184, 0.1);
  background: rgba(30, 41, 59, 0.5);
  border-radius: 12px 12px 0 0;
}
.console-header h3 {
  margin: 0;
  font-size: 0.9rem;
  color: #e2e8f0;
  display: flex;
  align-items: center;
  gap: 8px;
}
.console-header h3 .material-icons-outlined {
  font-size: 18px;
  color: #10b981;
}
.console-actions {
  display: flex;
  gap: 4px;
}
.console-actions button {
  width: 28px;
  height: 28px;
  border-radius: 6px;
  background: transparent;
  border: none;
  color: #64748b;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}
.console-actions button:hover {
  background: rgba(239, 68, 68, 0.2);
  color: #f87171;
}
.console-actions button .material-icons-outlined {
  font-size: 16px;
}
.console-body {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
  font-family: 'Fira Code', 'Consolas', monospace;
  font-size: 0.75rem;
  line-height: 1.5;
}
.console-line {
  display: flex;
  gap: 10px;
  padding: 3px 0;
  border-bottom: 1px solid rgba(148, 163, 184, 0.05);
}
.console-line.info { color: #94a3b8; }
.console-line.success { color: #10b981; }
.console-line.warn { color: #f59e0b; }
.console-line.error { color: #ef4444; }
.log-time {
  color: #475569;
  flex-shrink: 0;
}
.log-msg {
  word-break: break-word;
}
.console-empty {
  color: #475569;
  text-align: center;
  padding: 2rem;
  font-style: italic;
}

/* ========== RESPONSIVO ========== */
@media (max-width: 768px) {
  .header-content {
    padding: 0 1rem;
  }
  .main {
    padding: 1rem;
  }
  .lighting-cards {
    grid-template-columns: 1fr;
  }
  .sensors-grid {
    grid-template-columns: 1fr;
  }
  .auto-info {
    flex-direction: column;
    gap: 0.75rem;
  }
  .modal-container {
    max-height: 90vh;
  }
}
</style>

<!-- Estilos globais -->
<style>
html,
body {
  margin: 0 !important;
  padding: 0 !important;
  border: none !important;
  outline: none !important;
  background: #0c1222 !important;
}
</style>
