# AquaSense - Sistema de Monitorização e Manutenção de Aquário

Dashboard para monitorização e controlo do aquário

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
For windows Node.js is [required](https://nodejs.org/en/download).

```bash

cd esp32-dashboard/app
npm install        # Só na primeira vez
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

## Portas

| Serviço | Porta |
|---------|-------|
| Dashboard | 3001 |
| API IA | 5000 |
| MySQL | 3309 |
