// ============================================================
// AquaSense - Sistema de Monitorização de Aquário
// ============================================================
// Controlador ESP32 para sensores e actuadores
// ============================================================

#include <OneWire.h>
#include <DallasTemperature.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <DHT.h>
#include <time.h>

// Ficheiro de configuração (credenciais, pinos, calibração)
#include "config.h"

// ========== SENSOR DHT11 (TEMPERATURA AMBIENTE) ==========
#define DHTTYPE DHT11
DHT dht(PINO_DHT, DHTTYPE);

// ========== CONFIGURAÇÃO WiFi (do config.h) ==========
const char* ssid = WIFI_SSID;
const char* senha = WIFI_PASSWORD;
const char* urlServidor = "http://" SERVER_IP ":3001/api/sensors";  // Endpoint batch
const char* urlConfig = "http://" SERVER_IP ":3001/api/config/esp32";

// Intervalo de envio de dados (ms)
#define INTERVALO_ENVIO INTERVALO_ENVIO_DADOS
unsigned long ultimoEnvio = 0;
unsigned long ultimaConfig = 0;

unsigned long ultimaTentativaWiFi = 0;

// ========== SENSOR DE TEMPERATURA ==========
OneWire oneWire(PINO_SENSOR_TEMP);
DallasTemperature sensores(&oneWire);

// ========== SENSOR DE pH (calibração no config.h) ==========
#define DECLIVE DECLIVE_PH
float turbidezSuavizada = 0.0;  // Média móvel
bool turbidezIniciada = false;

// ========== VENTOINHA ==========
#define PINO_VENTOINHA 27
float tempLigar = 14.0;      // Valor padrão, atualizado pelo servidor
float tempDesligar = 13.0;   // Valor padrão, atualizado pelo servidor
bool modoManual = false;     // Controlado pelo servidor
bool ventoinhaManual = false; // Controlado pelo servidor
bool ventoinhaLigada = false;

// ========== LED INDICADOR E BUZZER ==========
#define PINO_LED    25
#define PINO_BUZZER 33

// Configuração PWM do buzzer (passivo)
#define FREQ_BUZZER 2000
#define RES_BUZZER  8
#define DUTY_BUZZER 128   // ~50%
#define CANAL_BUZZER 1    // Canal PWM para buzzer

// Controlo do buzzer (toca 5 segundos)
bool buzzerActivo = false;
unsigned long inicioBuzzer = 0;

// ========== ILUMINAÇÃO DO AQUÁRIO (LED 12V via IRLZ44N com PWM) ==========
#define PINO_LUZ_AQUARIO 21  // GPIO21 (módulo MOSFET com 5V)
#define FREQ_LUZ 500         // 500Hz (módulos com opto podem falhar a 5kHz)
#define RES_LUZ 8            // 8 bits = 0-255
#define CANAL_LUZ 0          // Canal PWM para luz
#define LUZ_PWM_ATIVA_LOW 1  // 1: IN+=5V(VIN) e IN-=GPIO (LOW=ON). 0: duty normal (HIGH=ON)

// Configurações de iluminação (atualizadas pelo servidor)
int horaLigar = 8;         // Hora de ligar (0-23)
int minutoLigar = 0;       // Minuto de ligar
int horaDesligar = 20;     // Hora de desligar (0-23)
int minutoDesligar = 0;    // Minuto de desligar
bool luzManual = false;    // Modo: false=automático, true=manual
bool luzManualLigada = false;  // Estado manual (on/off)
int intensidadeLuz = 100;  // Intensidade 0-100%

// Modos de luz: "manual", "horario", "ciclo", "ai"
String luzModo = "horario";
int luzCicloHoras = 8;           // Duração do ciclo em horas
unsigned long luzCicloInicio = 0; // Timestamp Unix do início do ciclo

// Estado atual da luz
bool luzEstaLigada = false;
int brilhoAtual = 0;         // 0-255 para PWM
int brilhoAlvo = 0;          // Brilho alvo para fade
#define FADE_STEP 5           // ~3 segundos para fade completo
unsigned long ultimoFade = 0;
#define FADE_INTERVALO 15    // ms entre passos do fade

// ========== LUZ NOTURNA (LED azul via Relé K2) ==========
#define PINO_LUZ_NOTURNA 23  // GPIO23 para relé K2
bool luzNoturnaManual = false;     // Modo: false=automático, true=manual
bool luzNoturnaLigada = false;     // Estado atual
bool luzNoturnaManualLigada = false; // Estado manual (on/off)
int horaLigarNoturna = 20;         // Hora de ligar (0-23)
int minutoLigarNoturna = 0;
int horaDesligarNoturna = 8;       // Hora de desligar (0-23)
int minutoDesligarNoturna = 0;

// ========== SISTEMA DE LOGS REMOTO ==========
const char* urlLogs = "http://" SERVER_IP ":3001/api/logs";
#define MAX_LOG_BUFFER 50
String logBuffer[MAX_LOG_BUFFER];
String logTypes[MAX_LOG_BUFFER];
int logCount = 0;
unsigned long ultimoEnvioLogs = 0;
#define INTERVALO_LOGS 2000  // Enviar logs a cada 2 segundos

// Adiciona log ao buffer (sem imprimir - para uso com Serial separado)
void addLog(String msg, String tipo = "info") {
  if (logCount < MAX_LOG_BUFFER) {
    logBuffer[logCount] = msg;
    logTypes[logCount] = tipo;
    logCount++;
  }
}

// Wrapper que imprime E adiciona ao buffer
void logRemote(String msg, String tipo = "info") {
  Serial.println(msg);
  addLog(msg, tipo);
}

void enviarLogs() {
  if (WiFi.status() != WL_CONNECTED || logCount == 0) return;
  
  HTTPClient http;
  http.begin(urlLogs);
  http.addHeader("Content-Type", "application/json");
  http.setTimeout(3000);
  
  StaticJsonDocument<4096> doc;
  doc["device_id"] = "ESP32-AquaSense";
  JsonArray logs = doc.createNestedArray("logs");
  
  for (int i = 0; i < logCount; i++) {
    JsonObject log = logs.createNestedObject();
    log["message"] = logBuffer[i];
    log["type"] = logTypes[i];
  }
  
  String json;
  serializeJson(doc, json);
  
  int code = http.POST(json);
  if (code == 200) {
    logCount = 0;  // Limpar buffer após envio
  }
  http.end();
}

// ========== FUNÇÕES DO BUZZER ==========
void iniciarBuzzer() {
  ledcWriteChannel(CANAL_BUZZER, DUTY_BUZZER);
  buzzerActivo = true;
  inicioBuzzer = millis();
}

void pararBuzzer() {
  ledcWriteChannel(CANAL_BUZZER, 0);
  buzzerActivo = false;
}

// ========== OBTER CONFIGURAÇÕES DO SERVIDOR ==========
void obterConfig() {
  if (WiFi.status() != WL_CONNECTED) return;
  
  HTTPClient http;
  http.begin(urlConfig);
  http.setTimeout(8000);
  http.setReuse(false);
  int codigoHTTP = http.GET();
  
  if (codigoHTTP == 200) {
    String resposta = http.getString();
    StaticJsonDocument<1024> doc;
    DeserializationError erro = deserializeJson(doc, resposta);
    
    if (!erro) {
      modoManual = doc["modo_manual"] | false;
      ventoinhaManual = doc["ventoinha_manual"] | false;
      tempLigar = doc["temp_ligar"] | 14.0;
      tempDesligar = doc["temp_desligar"] | 13.0;
      
      // Configurações de iluminação principal (branca)
      luzManual = doc["luz_manual"] | false;
      luzManualLigada = doc["luz_estado"] | false;
      horaLigar = doc["luz_hora_ligar"] | 8;
      minutoLigar = doc["luz_minuto_ligar"] | 0;
      horaDesligar = doc["luz_hora_desligar"] | 20;
      minutoDesligar = doc["luz_minuto_desligar"] | 0;
      intensidadeLuz = doc["luz_intensidade"] | 100;
      
      // Modo de luz e ciclo
      const char* modo = doc["luz_modo"] | "horario";
      luzModo = String(modo);
      luzCicloHoras = doc["luz_ciclo_horas"] | 8;
      
      // Converter ISO timestamp para Unix
      const char* cicloInicioStr = doc["luz_ciclo_inicio"] | "";
      if (strlen(cicloInicioStr) > 0) {
        struct tm tm = {0};
        // Formato: 2026-01-22T02:08:00.000Z
        sscanf(cicloInicioStr, "%d-%d-%dT%d:%d:%d", &tm.tm_year, &tm.tm_mon, &tm.tm_mday, &tm.tm_hour, &tm.tm_min, &tm.tm_sec);
        tm.tm_year -= 1900;
        tm.tm_mon -= 1;
        luzCicloInicio = mktime(&tm);
      }
      
      // Configurações de luz noturna (azul)
      luzNoturnaManual = doc["luz_noturna_manual"] | false;
      luzNoturnaManualLigada = doc["luz_noturna_estado"] | false;
      horaLigarNoturna = doc["luz_noturna_hora_ligar"] | 20;
      minutoLigarNoturna = doc["luz_noturna_minuto_ligar"] | 0;
      horaDesligarNoturna = doc["luz_noturna_hora_desligar"] | 8;
      minutoDesligarNoturna = doc["luz_noturna_minuto_desligar"] | 0;
      
      Serial.println("[CONFIG] Atualizada do servidor");
      addLog("[CONFIG] Atualizada do servidor", "success");
    }
  } else if (codigoHTTP < 0) {
    String erroConfig = "[CONFIG] Erro: " + http.errorToString(codigoHTTP);
    Serial.println(erroConfig);
    addLog(erroConfig, "error");
  }
  http.end();
}

// ========== CONTROLO DE ILUMINAÇÃO ==========
void controlarLuz() {
  bool deveLigar = false;
  int intensidade255 = map(constrain(intensidadeLuz, 0, 100), 0, 100, 0, 255);
  
  if (luzModo == "manual") {
    // MODO MANUAL: on/off e intensidade
    deveLigar = luzManualLigada;
    brilhoAlvo = deveLigar ? intensidade255 : 0;
    
  } else if (luzModo == "horario") {
    // MODO HORÁRIO: baseado no horário fixo
    struct tm timeinfo;
    if (getLocalTime(&timeinfo)) {
      int horaAtual = timeinfo.tm_hour;
      int minutoAtual = timeinfo.tm_min;
      int agora = horaAtual * 60 + minutoAtual;
      int inicio = horaLigar * 60 + minutoLigar;
      int fim = horaDesligar * 60 + minutoDesligar;
      
      if (fim > inicio) {
        deveLigar = (agora >= inicio && agora < fim);
      } else {
        deveLigar = (agora >= inicio || agora < fim);
      }
      brilhoAlvo = deveLigar ? intensidade255 : 0;
    }
    
  } else if (luzModo == "ciclo" || luzModo == "ai") {
    // MODO CICLO/AI: baseado no timestamp de início e duração
    if (luzCicloInicio > 0) {
      time_t agora;
      time(&agora);
      
      // Calcular segundos desde o início do ciclo
      long segundosPassados = agora - luzCicloInicio;
      long duracaoCicloSeg = luzCicloHoras * 3600L;
      long periodoCiclo = 24L * 3600L;  // 24 horas
      
      // Posição dentro do ciclo de 24h
      long posicaoNoCiclo = segundosPassados % periodoCiclo;
      if (posicaoNoCiclo < 0) posicaoNoCiclo += periodoCiclo;
      
      // Luz ligada nas primeiras 'luzCicloHoras' horas do ciclo
      deveLigar = (posicaoNoCiclo < duracaoCicloSeg);
      brilhoAlvo = deveLigar ? intensidade255 : 0;
    }
  }
  
  luzEstaLigada = deveLigar;
  
  // Fade gradual: aproximar brilhoAtual do brilhoAlvo
  if (millis() - ultimoFade >= FADE_INTERVALO) {
    ultimoFade = millis();
    if (brilhoAtual < brilhoAlvo) {
      brilhoAtual = min(brilhoAtual + FADE_STEP, brilhoAlvo);
    } else if (brilhoAtual > brilhoAlvo) {
      brilhoAtual = max(brilhoAtual - FADE_STEP, brilhoAlvo);
    }
  }
  
  // Controlo PWM
  int duty = brilhoAtual;
  #if LUZ_PWM_ATIVA_LOW
    duty = 255 - duty;
  #endif
  ledcWriteChannel(CANAL_LUZ, duty);
}

// ========== CONTROLO DE LUZ NOTURNA ==========
void controlarLuzNoturna() {
  bool deveLigar = false;
  
  if (luzNoturnaManual) {
    // MODO MANUAL: on/off
    deveLigar = luzNoturnaManualLigada;
  } else {
    // MODO AUTOMÁTICO: baseado no horário
    struct tm timeinfo;
    if (getLocalTime(&timeinfo)) {
      int horaAtual = timeinfo.tm_hour;
      int minutoAtual = timeinfo.tm_min;
      int agora = horaAtual * 60 + minutoAtual;
      int inicio = horaLigarNoturna * 60 + minutoLigarNoturna;
      int fim = horaDesligarNoturna * 60 + minutoDesligarNoturna;
      
      if (fim > inicio) {
        deveLigar = (agora >= inicio && agora < fim);
      } else {
        deveLigar = (agora >= inicio || agora < fim);
      }
    }
  }
  
  if (deveLigar != luzNoturnaLigada) {
    luzNoturnaLigada = deveLigar;
    digitalWrite(PINO_LUZ_NOTURNA, deveLigar ? HIGH : LOW);  // Relé ativo em HIGH
    String luzNLog = "[LUZ NOTURNA] " + String(deveLigar ? "LIGADA" : "DESLIGADA");
    Serial.println(luzNLog);
    addLog(luzNLog, "info");
  }
}

// ========== ENVIO DE DADOS (BATCH - 1 POST com tudo) ==========
void enviarTodosDados(float temp, float tempAmb, float hum, float ph, float tensaoPH,
                      float turbidez, float tensaoTurb, bool ventoinha, 
                      bool luz, int brilho, bool luzNoturna) {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("[HTTP] Sem WiFi, a saltar envio");
    addLog("[HTTP] Sem WiFi, a saltar envio", "warn");
    return;
  }
  
  HTTPClient http;
  http.begin(urlServidor);
  http.setTimeout(8000);  // Timeout mais generoso
  http.setReuse(false);   // Não reutilizar conexão (evita stale connections)
  http.addHeader("Content-Type", "application/json");
  
  // Construir JSON com todos os sensores
  StaticJsonDocument<512> doc;
  doc["device_id"] = "ESP32_001";
  JsonArray sensors = doc.createNestedArray("sensors");
  
  // Adicionar sensores válidos
  if (temp > -50 && temp < 100) {
    JsonObject s = sensors.createNestedObject();
    s["type"] = "temperature"; s["value"] = temp; s["unit"] = "C";
  }
  if (!isnan(tempAmb)) {
    JsonObject s1 = sensors.createNestedObject();
    s1["type"] = "ambient_temp"; s1["value"] = tempAmb; s1["unit"] = "C";
    JsonObject s2 = sensors.createNestedObject();
    s2["type"] = "humidity"; s2["value"] = hum; s2["unit"] = "%";
  }
  JsonObject sp = sensors.createNestedObject();
  sp["type"] = "pH"; sp["value"] = ph; sp["unit"] = "pH";
  JsonObject spv = sensors.createNestedObject();
  spv["type"] = "pH_voltage"; spv["value"] = tensaoPH; spv["unit"] = "V";
  JsonObject st = sensors.createNestedObject();
  st["type"] = "turbidity"; st["value"] = turbidez; st["unit"] = "%";
  JsonObject stv = sensors.createNestedObject();
  stv["type"] = "turbidity_voltage"; stv["value"] = tensaoTurb; stv["unit"] = "V";
  JsonObject sf = sensors.createNestedObject();
  sf["type"] = "fan_status"; sf["value"] = ventoinha ? 1 : 0; sf["unit"] = "bool";
  JsonObject sl = sensors.createNestedObject();
  sl["type"] = "light_status"; sl["value"] = luz ? 1 : 0; sl["unit"] = "bool";
  JsonObject sb = sensors.createNestedObject();
  sb["type"] = "light_brightness"; sb["value"] = brilho; sb["unit"] = "level";
  JsonObject sn = sensors.createNestedObject();
  sn["type"] = "night_light_status"; sn["value"] = luzNoturna ? 1 : 0; sn["unit"] = "bool";
  
  String json;
  serializeJson(doc, json);
  
  int codigoHTTP = http.POST(json);
  if (codigoHTTP == 200) {
    Serial.println("[HTTP] Dados enviados OK");
    addLog("[HTTP] Dados enviados OK", "success");
  } else if (codigoHTTP > 0) {
    String httpResp = "[HTTP] Resposta: " + String(codigoHTTP);
    Serial.println(httpResp);
    addLog(httpResp, "warn");
  } else {
    String httpErr = "[HTTP] Erro: " + http.errorToString(codigoHTTP);
    Serial.println(httpErr);
    addLog(httpErr, "error");
  }
  http.end();
}

// ========== CONFIGURAÇÃO INICIAL ==========
void setup() {
  Serial.begin(115200);
  delay(1000);

  // Ligar ao WiFi
  Serial.print("A ligar ao WiFi");
  WiFi.mode(WIFI_STA);
  WiFi.persistent(false);
  WiFi.setAutoReconnect(true);
  WiFi.setSleep(false);
  WiFi.begin(ssid, senha);
  unsigned long inicioWiFi = millis();
  while (WiFi.status() != WL_CONNECTED && (millis() - inicioWiFi) < 20000) {
    delay(500);
    Serial.print(".");
  }
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println();
    Serial.print("WiFi ligado! IP: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\n[WiFi] Falhou a ligação inicial (vai tentar reconectar no loop)");
  }

  // Iniciar sensores
  sensores.begin();
  dht.begin();  // Inicializar DHT11
  analogReadResolution(12);
  analogSetAttenuation(ADC_11db);

  // Configurar pinos
  pinMode(PINO_VENTOINHA, OUTPUT);
  digitalWrite(PINO_VENTOINHA, HIGH); // Desligada (relé activo em LOW)

  pinMode(PINO_LUZ_NOTURNA, OUTPUT);
  digitalWrite(PINO_LUZ_NOTURNA, LOW); // Desligada (relé activo em HIGH)
  

  pinMode(PINO_LED, OUTPUT);
  digitalWrite(PINO_LED, LOW);

  // Configurar buzzer PWM (canal 1)
  ledcAttachChannel(PINO_BUZZER, FREQ_BUZZER, RES_BUZZER, CANAL_BUZZER);
  pararBuzzer();

  // Configurar luz PWM (Módulo F5305S) - começa desligada
  ledcAttachChannel(PINO_LUZ_AQUARIO, FREQ_LUZ, RES_LUZ, CANAL_LUZ);
  ledcWriteChannel(CANAL_LUZ, LUZ_PWM_ATIVA_LOW ? 255 : 0);    // OFF

  // Configurar NTP para hora
  configTime(0, 0, "pool.ntp.org", "time.nist.gov");
  setenv("TZ", "WET0WEST,M3.5.0/1,M10.5.0", 1);
  tzset();

  // Obter config imediatamente
  delay(1000);
  obterConfig();

  Serial.println("=== SISTEMA INICIADO ===");
}

// ========== CICLO PRINCIPAL ==========
void loop() {
  // Reconectar WiFi de forma robusta
  if (WiFi.status() != WL_CONNECTED) {
    if (millis() - ultimaTentativaWiFi >= INTERVALO_WIFI_RECONNECT) {
      ultimaTentativaWiFi = millis();
      Serial.println("[WiFi] Reconectando (disconnect+begin)...");
      WiFi.disconnect(true);  // Desconectar completamente
      delay(100);
      WiFi.begin(ssid, senha);
    }
  }

  // Obter configurações do servidor periodicamente
  if (millis() - ultimaConfig >= INTERVALO_CONFIG) {
    ultimaConfig = millis();
    obterConfig();
  }

  // Ler temperatura da água (DS18B20)
  sensores.requestTemperatures();
  float temperatura = sensores.getTempCByIndex(0);

  // Ler temperatura ambiente e humidade (DHT11) - apenas a cada 2 segundos
  static float tempAmbiente = NAN;
  static float humidade = NAN;
  static unsigned long ultimaLeituraDHT = 0;
  if (millis() - ultimaLeituraDHT >= 2000) {
    ultimaLeituraDHT = millis();
    float t = dht.readTemperature();
    float h = dht.readHumidity();
    if (!isnan(t)) tempAmbiente = t;
    if (!isnan(h)) humidade = h;
    String dhtLog = "[DHT] Pino: " + String(PINO_DHT) + " | Temp: " + String(tempAmbiente, 1) + "C | Hum: " + String(humidade, 1);
    Serial.println(dhtLog);
    addLog(dhtLog, "info");
  }

  // Ler pH (média de 10 leituras - sem delay )
  uint32_t soma = 0;
  for (int i = 0; i < 10; i++) {
    soma += analogRead(PINO_PH);
    delayMicroseconds(500);  // 0.5ms em vez de 5ms
  }
  int leituraPH = soma / 10;
  float tensaoPH = leituraPH * (3.3 / 4095.0);
  float ph = 7.0 + (TENSAO_PH7 - tensaoPH) / DECLIVE;
  String phLog = "[pH DEBUG] Tensão: " + String(tensaoPH, 3) + "V | ADC: " + String(leituraPH);
  Serial.println(phLog);
  addLog(phLog, "info");

  // Ler turbidez (média de 20 leituras - sem delay )
  uint32_t somaTurb = 0;
  for (int i = 0; i < 20; i++) {
    somaTurb += analogRead(PINO_TURBIDEZ);
    delayMicroseconds(500);  // 0.5ms em vez de 2ms
  }
  int leituraTurb = somaTurb / 20;
  // Tensão no GPIO (após divisor): ADC * 3.3V / 4095
  // Tensão original do sensor: tensaoGPIO * (10k+1.2k+1.2k+10k) / (1.2k+1.2k+10k) ≈ tensaoGPIO * 1.806
  float tensaoTurb = (leituraTurb * 3.3 / 4095.0) * 1.806;
  
  // Converter para percentagem (0% = limpa, 100% = turva)
  // Quanto MENOR a tensão, MAIS turva a água
  float turbidezPercent = 0.0;
  if (tensaoTurb >= TENSAO_AGUA_LIMPA) {
    turbidezPercent = 0;  // Água limpa
  } else if (tensaoTurb <= TENSAO_AGUA_TURVA) {
    turbidezPercent = 100;  // Muito turva
  } else {
    turbidezPercent = (TENSAO_AGUA_LIMPA - tensaoTurb) / (TENSAO_AGUA_LIMPA - TENSAO_AGUA_TURVA) * 100;
  }
  
  // Aplicar média móvel exponencial para suavizar
  if (!turbidezIniciada) {
    turbidezSuavizada = turbidezPercent;
    turbidezIniciada = true;
  } else {
    turbidezSuavizada = turbidezSuavizada * 0.7 + turbidezPercent * 0.3;  // Suavização moderada
  }
  
  String turbLog = "[TURBIDEZ DEBUG] Tensão: " + String(tensaoTurb, 3) + "V | ADC: " + String(leituraTurb) + 
                   " | Raw: " + String(turbidezPercent, 1) + "% | Suavizado: " + String(turbidezSuavizada, 1) + "%";
  Serial.println(turbLog);
  addLog(turbLog, "info");

  // Controlo da ventoinha
  if (modoManual) {
    // MODO MANUAL: controlado pelo website
    if (ventoinhaManual && !ventoinhaLigada) {
      ventoinhaLigada = true;
      digitalWrite(PINO_VENTOINHA, LOW);
      iniciarBuzzer();
    } else if (!ventoinhaManual && ventoinhaLigada) {
      ventoinhaLigada = false;
      digitalWrite(PINO_VENTOINHA, HIGH);
      pararBuzzer();
    }
  } else {
    // MODO AUTOMÁTICO: baseado na temperatura
    if (temperatura != DEVICE_DISCONNECTED_C) {
      if (!ventoinhaLigada && temperatura >= tempLigar) {
        ventoinhaLigada = true;
        digitalWrite(PINO_VENTOINHA, LOW);
        iniciarBuzzer();
      }
      if (ventoinhaLigada && temperatura <= tempDesligar) {
        ventoinhaLigada = false;
        digitalWrite(PINO_VENTOINHA, HIGH);
        pararBuzzer();
      }
    }
  }

  // LED indica estado da ventoinha
  digitalWrite(PINO_LED, ventoinhaLigada ? HIGH : LOW);

  // Buzzer desliga após 5 segundos
  if (buzzerActivo && (millis() - inicioBuzzer >= 5000)) {
    pararBuzzer();
  }

  // Controlar iluminação do aquário
  controlarLuz();
  controlarLuzNoturna();

  // Log de estado completo (como no Serial Monitor)
  addLog("------------------------", "info");
  
  String estadoLinha1 = "Modo: " + String(modoManual ? "MANUAL" : "AUTO") + 
                        " | Temp Água: " + String(temperatura, 1) + "°C" +
                        " | Ventoinha: " + String(ventoinhaLigada ? "ON" : "OFF") +
                        " | pH: " + String(ph, 2) +
                        " | Turbidez: " + String(turbidezPercent, 1) + "%";
  Serial.println(estadoLinha1);
  addLog(estadoLinha1, "info");
  
  if (!isnan(tempAmbiente)) {
    String estadoLinha2 = "Temp Ambiente: " + String(tempAmbiente, 1) + "°C | Humidade: " + String(humidade, 1) + "%";
    Serial.println(estadoLinha2);
    addLog(estadoLinha2, "info");
  }
  
  struct tm timeinfo;
  String estadoLinha3 = "";
  if (getLocalTime(&timeinfo)) {
    String minStr = timeinfo.tm_min < 10 ? "0" + String(timeinfo.tm_min) : String(timeinfo.tm_min);
    estadoLinha3 = "Hora: " + String(timeinfo.tm_hour) + ":" + minStr + " | ";
  }
  estadoLinha3 += "Luz Branca: " + String(luzEstaLigada ? "ON" : "OFF") + 
                  " (" + String(brilhoAtual) + "/255) | Luz Noturna: " + String(luzNoturnaLigada ? "ON" : "OFF");
  Serial.println(estadoLinha3);
  addLog(estadoLinha3, "info");

  // Enviar logs para o dashboard
  if (millis() - ultimoEnvioLogs >= INTERVALO_LOGS) {
    ultimoEnvioLogs = millis();
    enviarLogs();
  }

  // Enviar dados para o servidor (1 único POST com tudo)
  if (millis() - ultimoEnvio >= INTERVALO_ENVIO) {
    ultimoEnvio = millis();
    enviarTodosDados(temperatura, tempAmbiente, humidade, ph, tensaoPH,
                     turbidezSuavizada, tensaoTurb, ventoinhaLigada,
                     luzEstaLigada, brilhoAtual, luzNoturnaLigada);
  }

  delay(50);
}

