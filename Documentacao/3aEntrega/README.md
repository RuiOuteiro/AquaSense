# Sistema para controlo de qualidade de um aquário - AquaSense

"PROPÓSITO"

**Autores:** Rui Outeiro, Emanuel Carvalho, Paulo Jadaugy

Estrutura exemplo

- Identificação do problema 
- Identificação de requisitos
- Estruturação da arquitetura 
  - Camada de perceção/dispositivos 
    - Hardware 
    - Software
    - Processamento de dados 
    - Conectividade 
    - Segurança
  - Camada de rede 
    - Hardware 
    - Software
    - Conectividade 
    - Segurança
  - Camada de processamento de dados
    - Hardware
    - Software
    - Processamento de dados
    - Conectividade
    - Segurança
  - Camada de aplicação
    - Hardware 
    - Software
    - Processamento de dados 
    - Conectividade 
    - Segurança
- Conclusão

## Introdução

## Problema

## Solução Proposta

## Estruturação da arquitetura

```mermaid
graph TD
    %% Node Definitions
    SA["<b>Sensores e Atuadores</b><br/><br/><u>Sensores:</u><br/>- DHT11 (Temperatura / Humidade)<br/>- DS18B20 (Temperatura da água)<br/>- Sensor de pH<br/>- Sensor de Turbidez<br/><br/><u>Atuadores:</u><br/>- Relé 2 canais (Ventoinha / Linha 12V)<br/>- MOSFET (Fita LED 12V)<br/>- Buzzer<br/>- LED vermelho"]
    
    ESP32[ESP32]
    
    WF["<b>Wi-Fi (HTTP / JSON)</b><br/><br/>• Nuxt Nitro Server (API REST)<br/>• Recebe dados do ESP32<br/>• Armazena leituras<br/>• Processa comandos<br/>• Fornece dados ao dashboard<br/><br/>Base de Dados: MySQL"]
    
    SB["<b>Servidor / Backend</b><br/><br/>• Recebe dados do ESP32<br/>• Armazena leituras<br/>• Fornece dados ao dashboard"]
    
    DW["<b>Dashboard Web</b><br/><br/>Interface do utilizador"]

    %% Connections with Arrows and Labels
    SA <== "DADOS / COMANDOS" ==> ESP32
    ESP32 ==>|DADOS| WF
    WF <== "DADOS / COMANDOS" ==> SB
    SB ==>|DADOS| DW

    %% Styling
    style SA fill:#7d94f5,stroke:#333,stroke-width:1px
    style ESP32 fill:#2c3e50,stroke:#333,stroke-width:1px,color:#fff
    style WF fill:#7d94f5,stroke:#333,stroke-width:1px
    style SB fill:#7d94f5,stroke:#333,stroke-width:1px
    style DW fill:#7d94f5,stroke:#333,stroke-width:1px
```
    
### Camada de perceção/dispositivos

#### Hardware 

![Imagem do circuito](./Ficheiros/circuit_image.svg)

#### Software
#### Processamento de dados 
#### Conectividade 
#### Segurança


### Camada de rede 
#### Hardware 
#### Software
#### Conectividade 
#### Segurança
### Camada de processamento de dados
#### Hardware
#### Software
#### Processamento de dados
#### Conectividade
#### Segurança

### Camada de aplicação
#### Hardware 
#### Software
#### Processamento de dados 
#### Conectividade 
#### Segurança
