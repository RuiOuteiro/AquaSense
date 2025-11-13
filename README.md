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
- 
