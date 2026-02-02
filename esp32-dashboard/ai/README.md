# AquaSense IA

Sistema de Snteligência Artificial para análise de parâmetros da água e apresentação de sugestões automáticas para controlo de iluminação, manutenção e alimentação de aquários.

## Objetivo

O sistema recolhe dados de sensores e produz recomendações operacionais com base em regras e num modelo treinado com dados sintéticos.

## Parâmetros de Entrada

- Turbidez da água (percentagem de 0 a 100)
- pH da água (valor numérico)
- Temperatura da água (valor numérico em graus Celsius)

## Parâmetros de Saída

- Fotoperíodo recomendado (horas por dia)
- Intensidade da luz (percentagem)
- Duração da luz noturna (horas)
- Percentagem de TPA recomendada
- Ajuste percentual da alimentação
- Grau de severidade
- Tendência dos valores
- Lista de acções sugeridas

## Regras Base

### Turbidez

- 80 a 100
Redução acentuada do fotoperíodo
TPA elevada
Alimentação suspensa ou mínima

- 60 a 80
Redução significativa do fotoperíodo
TPA média a elevada
Alimentação reduzida

- 40 a 60
Redução moderada do fotoperíodo
TPA média
Alimentação ligeiramente reduzida

- 20 a 40
Pequenos ajustes
TPA baixa
Alimentação normal

- 0 a 20
Sem ajustes relevantes

### pH e Temperatura

Valores fora dos intervalos recomendados aumentam a urgência de TPA e reduzem a alimentação.

Intervalo de pH de referência
6.5 a 7.8

Intervalo de temperatura de referência
22 a 28 graus Celsius

## Arquitetura do Modelo

Entrada:
- Turbidez
- pH
- Temperatura

Processamento:
- Rede neural simples com uma camada oculta

Saída:
- Ajuste do fotoperíodo
- Percentagem de TPA
- Percentagem de alimentação

## Estrutura do Projeto

```text
ai/
├── api_server.py
├── requirements.txt
├── models/
│ ├── photoperiod_model.pt
│ ├── scaler.pkl
│ └── metrics.json
└── src/
├── config.py
├── model.py
├── data_loader.py
├── train.py
├── inference.py
├── evaluate.py
└── suggestions.py
```

## Instalação

```bash
pip install -r requirements.txt
```

## Treino do Modelo

```bash
python -m src.train
```

## Inferência

```bash
python -m src.inference
```

## Servidor API

```bash
python api_server.py
```

Servidor em:
http://localhost:5000

## Endpoints Principais

- GET /api/ai/health
- GET /api/ai/photoperiod
- POST /api/ai/apply
- GET /api/ai/stats

## Exemplo de Utilização em Python

```python
from src.inference import AquaSensePredictor

predictor = AquaSensePredictor()

resultado = predictor.predict(
turbidity=65.0,
ph=7.1,
temperature=26.5,
base_photoperiod=10
)
```

## Notas

- O sistema utiliza dados sintéticos para treino
- O modelo deve ser re-treinado sempre que existirem uma quantidade significativa de novos dados
