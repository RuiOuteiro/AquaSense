
# AquaSense

## Descrição

O **AquaSense** é um sistema inteligente para gestão e manutenção de aquários, cujo principal objetivo é automatizar e optimizar tarefas críticas como iluminação, controlo de parâmetros da água e arrefecimento, tirando partido de conectividade Wi-Fi, aplicação móvel e técnicas de inteligência artificial.

## Principais Funcionalidades

- **Sistema de iluminação inteligente**
  - Simulação de nascer e pôr do sol através de dimming (PWM), com fotoperíodo definido pelo utilizador na aplicação móvel.
  - Ajuste automático do fotoperíodo através de inteligência artificial, com base na claridade da água medida por um LDR que analisa a quantidade de luz que atravessa a coluna de água, permitindo detectar indiretamente a presença de algas e ajustar o fotoperíodo em conformidade.
  - Integração de uma API de meteorologia para adaptar o fotoperíodo às condições exteriores (ex: dias muito escuros, trovoadas, vagas de calor), aproximando o ciclo de luz no aquário das condições naturais. [pode ser desactivado pelo utilizador]

- **Conectividade e aplicação móvel**
  - Comunicação via wifi entre o ESP32 e o backend.
  - Aplicação móvel para:
    - Configuração do fotoperíodo.
    - Consultas em tempo real, e históricos de medições.
    - Receção de alertas e notificações com sugestões de acções a tomar perante as situações.

- **Monitorização contínua de parâmetros**
  - PH da água.
  - Temperatura da água.
  - Temperatura ambiente.

- **Alertas**
  - Notificações quando qualquer parâmetro sai dos intervalos definidos como seguros (PH, temperatura da água, temperatura ambiente, claridade anormal da água).

- **Arrefecimento automático**
  - Acionamento de uma ventoinha de arrefecimento quando a temperatura da água atinge ou ultrapassa os 30 °C, ajudando a manter o aquário dentro de uma faixa térmica segura.


## Hardware Necessário
- Kit básico de início para ESP32: microcontrolador central responsável pela leitura dos sensores e controlo das ações
- Fita LED 12V: iluminação controlada pelo ESP32
- Fonte 12V DC 2A :alimentação da fita LED
- Adaptador DC fêmea: Para obter uma ligação segura da fonte de alimentação
- MOSFET IRLZ44N (x2): Para controlar a voltagem da fita LED e ventoinha
- Resistências 220Ω: para protecção e condicionamento de sinal
- Ventoinha 12V:  sistema de arrefecimento controlado automaticamente
- LDR: sensor de luminosidade para detecção de fitoplancton na coluna de água.
- DS18B20: sensor de temperatura da água
- Sonda de PH + módulo PH-4502C: medição do PH da água através de saída analógica
- Cabos e breadboard:  prototipagem e ligações elétricas
- Caixa plástica: Para a proteção e organização do hardware

## Software Necessário

**Microcontrolador (ESP32)**
Software para programar e controlar o ESP32:

 - Arduino IDE (ou PlatformIO em VSCode)
 - Bibliotecas Arduino:
	 - WiFi.h - ligação à rede Wi-Fi
	 - HTTPClient.h - envio de dados via REST
	 - ArduinoJson.h - codificação/descodificação de JSON
	 - OneWire.h - comunicação com o DS18B20
	 - DallasTemperature.h - temperatura da água
	 - analogRead() + ESP32AnalogRead (opcional) - leitura do pH
	 - DHT.h - sensor de temperatura ambiente
	 - LEDC (PWM) - controlo da iluminação
	 - time.h - sincronização NTP

**Backend**
 - PHP 8.1.2
 - Servidor apache [Via XAMPP]
 - Extensões PHP necessárias:
	 - php-mysql - ligação ao MySQL 
	 - php-curl - chamadas à API de meteorologia
	 - php-json - manipulação de JSON
- Base de Dados MySQL 8, phpMyAdmin [Via XAMPP]

**Frontend**

 - HTML 
 - CSS 
 - JavaScript 

**Inteligência Artificial**
 - Python 3.10+
 - Bibliotecas:
	 - pandas - limpeza e organização dos dados
	 - numpy - operações matemáticas
	 - scikit-learn - modelos preditivos
	 - matplotlib - gráficos e análises
	 - seaborn - visualização de dados
	 - joblib - guardar/carregar modelos
	 - requests - fazer chamadas externas

**Ferramentas de Desenvolvimento**

 - Git - relatórios / repositório do projecto
 - Draw.io - diagramas da infraestrutura 
 - Wokwi - simulação de ESP32
 - Postman - testar endpoints REST
 - VSCode - desenvolvimento de backend, frontend e scripts para Python
 - EasyEDA - esquemas elétricos

**Planeamento** 
![Imagem planeamento](https://github.com/RuiOuteiro/AquaSense/blob/main/Documentacao/1aEntrega/Ficheiros/Planeamento.png "Planeamento")
Link para o planeamento (gráfico de gantt): [link](https://github.com/RuiOuteiro/AquaSense/blob/main/Documentacao/1aEntrega/Ficheiros/Planeamento_PBL.xlsx)

**Esboço do artefacto físico a construir** 
![Imagem do artefacto](https://github.com/RuiOuteiro/AquaSense/blob/main/Documentacao/1aEntrega/Ficheiros/Diagrama%20PBL.png "Esboço")
Link para o esboço (feito no DrawIO): [link](https://github.com/RuiOuteiro/AquaSense/blob/main/Documentacao/1aEntrega/Ficheiros/Diagrama%20PBL.drawio)
