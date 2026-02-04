# Relatório Final - Projeto AquaSense

**Universidade:** IADE - Universidade Europeia

**Unidade Curricular:** PBL para 4 UC's (IoT, Sistemas Distribuidos, Engenharia de Software e IA)

**Grupo e ano Letivo:** Grupo 3 (2025/2026)

**Autores:** Rui Outeiro, Emanuel Carvalho, Paulo Jadaugy


- [Relatório Final - Projeto AquaSense](#relatório-final---projeto-aquasense)
  - [Introdução](#introdução)
  - [Problema](#problema)
  - [Solução Proposta](#solução-proposta)
  - [Estruturação da arquitetura](#estruturação-da-arquitetura)



## Identificação do Problema

Em muitos aquários, não existe um sistema acessível e autónomo que permita acompanhar a qualidade da água em tempo real, seja do trabalho ou de outro pais, nomeadamente parâmetros como pH, turbidez e temperatura.
Devido a ausência esta monotorização compromete o equilíbrio do ecossistema aquático e afeta a saúda dos organismos vivos e a deteção precoce de situações críticas.

As soluções atualmente disponíveis no mercado são limitadas, pouco integradas e sem capacidade de analise inteligente AI dos dados recolhidos e extremamente caras.
Devido a estas situações torna-se relevante desenvolver uma solução inteligente, acessível e inovadora que seja capaz de recolher dados, processar e analisar os dados da agua em tempo real e que recorre a inteligência artificial para tomar decisões emitir alertas ajudar na manutenção dos aquários 

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
    SB <== "DADOS / COMANDOS" ==> DW

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
[Link do projeto](https://app.cirkitdesigner.com/project/a4304a47-1a98-431c-bca2-73c1af9060d3)

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
