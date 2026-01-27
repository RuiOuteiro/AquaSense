# AquaSense IA - Sistema de Sugestões

Modelo de IA para optimização do fotoperíodo e qualidade da água do aquário.

## O que faz

A IA analisa a **turbidez da água** e sugere:
- **Fotoperíodo** - Horas de luz por dia (menos luz = menos algas)
- **Intensidade** - Percentagem de brilho da luz
- **TPA** - Troca Parcial de Água recomendada
- **Alimentação** - Ajustes na quantidade de comida
- **Luz Noturna** - Quando usar luz azul

## Iniciar o Servidor

```bash
cd ai
python3 api_server.py
```

O servidor inicia em `http://localhost:5000`

## Endpoints

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/ai/photoperiod` | Obter sugestão actual |
| POST | `/api/ai/apply` | Aplicar sugestão |
| GET | `/api/ai/stats` | Estatísticas de turbidez |

## Como Funciona

1. O ESP32 envia leituras de turbidez para a base de dados
2. A IA lê a turbidez actual e média das últimas 24h
3. Calcula a tendência (a subir, estável, a descer)
4. Gera sugestões baseadas em regras:

| Turbidez | Fotoperíodo | TPA | Alimentação |
|----------|-------------|-----|-------------|
| > 90% | 2h | 50% urgente | Suspender 4 dias |
| 70-90% | 4h | 40% | Suspender 2-3 dias |
| 50-70% | 6h | 30% | Reduzir 50% |
| 30-50% | 8h | 20% | Reduzir 25% |
| < 30% | 10-12h | 10-15% | Normal |

## Estrutura

```
ai/
├── api_server.py     # Servidor Flask (porta 5000)
├── models/           # Modelo treinado
│   ├── photoperiod_model.pt
│   └── scaler.pkl
└── src/
    ├── config.py     # Configurações
    ├── model.py      # Arquitectura da rede neural
    ├── inference.py  # Previsões
    └── suggestions.py # Lógica de sugestões
```

## Dependências

```bash
pip install flask flask-cors torch numpy scikit-learn mysql-connector-python
```

Ou usar o requirements.txt:
```bash
pip install -r requirements.txt
```
