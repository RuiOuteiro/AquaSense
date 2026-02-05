# AquaSense - Sistema de Monitorização de Aquário

Dashboard para monitorização e controlo de aquário com ESP32, IA e interface web.

## Início Rápido

### 1. Base de Dados (MySQL)

```bash
# Iniciar XAMPP (MySQL na porta 3309)
sudo /opt/lampp/lampp startmysql

# Ou usar o XAMPP Control Panel
```

Importar schema (primeira vez):
```bash
mysql -u root -P 3309 < schema_dump.sql
```

### 2. Dashboard Web

```bash
cd esp32-dashboard/webapp/app
npm install        # Só na primeira vez
npm install --save vue3-apexcharts # Só na primeira vez
npm run dev        # Inicia em http://localhost:3001
```

### 3. Servidor IA

```bash
cd esp32-dashboard/ai
pip install -r requirements.txt   # Só na primeira vez
python3 api_server.py             # Inicia em http://localhost:5000
```

### 4. ESP32

1. Abrir `aquasense/aquasense.ino` no Arduino IDE
2. Configurar WiFi em `aquasense/config.h`
3. Compilar e carregar para o ESP32

## Estrutura

```
esp32-dashboard/
├── app/              # Frontend Vue/Nuxt
├── server/           # API endpoints
├── ai/               # Modelo de IA
│   ├── api_server.py # Servidor Flask
│   └── src/          # Módulos do modelo
└── aquasense/        # Código ESP32
```

## Configuração

### WiFi do ESP32 (`aquasense/config.h`)
```cpp
#define WIFI_SSID "nome_da_rede"
#define WIFI_PASSWORD "password"
#define SERVER_IP "192.168.1.X"  // IP do servidor
```

### Base de Dados (`.env`)
```
DB_HOST=127.0.0.1
DB_PORT=3309
DB_USER=root
DB_PASSWORD=
DB_NAME=esp32_data
```
### Credenciais
```
Utilizador: aquasense@email.pt
Password: admin123
```

## Comandos Úteis

| Comando | Descrição |
|---------|-----------|
| `npm run dev` | Iniciar dashboard |
| `python3 ai/api_server.py` | Iniciar servidor IA |
| `sudo /opt/lampp/lampp startmysql` | Iniciar MySQL |

## Notificações Telegram

O AquaSense envia alertas para o Telegram quando os sensores saem dos limites definidos.

### Configurar Bot

1. Abrir o Telegram e procurar **@BotFather**
2. Enviar `/newbot` e segue as instruções
3. Guardar o **token** do bot (já configurado no sistema)

### Obter Chat ID

1. Procurar **@userinfobot** no Telegram
2. Enviar qualquer mensagem
3. Copiar o **ID**

### Ativar no Dashboard

1. Abrir o **Perfil** no dashboard do Aquasense
2. Na secção **Alertas Telegram**, colar o Chat ID
3. Guardar
4. Receber mensagem de confirmação no Telegram

## Portas

| Serviço | Porta |
|---------|-------|
| Dashboard | 3001 |
| IA API | 5000 |
| MySQL | 3309 |
