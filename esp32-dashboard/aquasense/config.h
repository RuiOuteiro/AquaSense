// ============================================================
// AquaSense - Ficheiro de Configuração
// ============================================================
// Todas as credenciais, pinos e constantes de calibração
// ============================================================

#ifndef CONFIG_H
#define CONFIG_H

// ========== CONFIGURAÇÃO WiFi ==========
#define WIFI_SSID "<WIFI_SSID>"
#define WIFI_PASSWORD "<WIFI_Password>"

// ========== CONFIGURAÇÃO DO SERVIDOR ==========
#define SERVER_IP "<Server_IP>"
#define SERVER_PORT 3001
#define DEVICEID "ESP32_001"

// Macro auxiliar para converter número em string
#define stringify(x) stringify2(x)
#define stringify2(x) #x

// ========== INTERVALOS DE TEMPO (ms) ==========
#define INTERVALO_ENVIO_DADOS 15000    // Envio de dados ao servidor (15s)
#define INTERVALO_CONFIG 10000         // Obter config do servidor (10s)
#define INTERVALO_WIFI_RECONNECT 10000 // Tentar reconectar WiFi (10s)

// ========== SENSOR DE TEMPERATURA DS18B20 ==========
#define PINO_SENSOR_TEMP 4

// ========== SENSOR DHT11 (TEMPERATURA AMBIENTE) ==========
#define PINO_DHT 26

// ========== SENSOR DE pH ==========
#define PINO_PH 34
#define TENSAO_PH7 1.634   // Tensão quando pH=7 (recalibrado: 1.544V = pH 7.5)
#define DECLIVE_PH 0.18    // Variação de tensão por unidade de pH (~180mV por pH)

// ========== SENSOR DE TURBIDEZ ==========
#define PINO_TURBIDEZ 35
#define TENSAO_AGUA_LIMPA 3.14  // Tensão com água limpa (calibrar)
#define TENSAO_AGUA_TURVA 2.0   // Tensão com água muito turva

// ========== VENTOINHA ==========
#define PINO_VENTOINHA 27

// ========== LED INDICADOR E BUZZER ==========
#define PINO_LED 25
#define PINO_BUZZER 33

// ========== ILUMINAÇÃO (PWM) ==========
#define PINO_LUZ_AQUARIO 21
#define FREQ_LUZ 500
#define RES_LUZ 8
#define CANAL_LUZ 0
#define LUZ_PWM_ATIVA_LOW 1

// ========== LUZ NOTURNA ==========
#define PINO_LUZ_NOTURNA 23

#endif
