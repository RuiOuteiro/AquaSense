# AquaSense IA - Sistema de Sugestões

Modelo de IA para otimização do fotoperíodo e qualidade da água do aquário.

## 🎯 O que faz

A IA analisa **3 parâmetros principais**:
- 🌊 **Turbidez** - Nível de algas e partículas na água (0-100%)
- 🧪 **pH** - Acidez/alcalinidade da água (6.0-8.5)
- 🌡️ **Temperatura** - Temperatura da água (°C)

E sugere automaticamente:
- ⏰ **Fotoperíodo** - Horas de luz por dia (menos luz = menos algas)
- 💡 **Intensidade** - Percentagem de brilho da luz
- 💧 **TPA** - Troca Parcial de Água recomendada
- 🍽️ **Alimentação** - Ajustes na quantidade de comida
- 🌙 **Luz Noturna** - Quando usar luz azul

## 🚀 Início Rápido

### 1. Instalação

```bash
cd ai
pip install -r requirements.txt
```

### 2. Treinar o Modelo

```bash
python -m src.train
```

Isto irá:
- Gerar 10,000 amostras sintéticas de dados
- Treinar o modelo com validação cruzada
- Guardar modelo e scaler em `models/`
- Mostrar métricas de performance

### 3. Testar o Modelo

```bash
python -m src.inference
```

### 4. Iniciar o Servidor API

```bash
python api_server.py
```

O servidor inicia em `http://localhost:5000`

## 📡 Endpoints da API

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/ai/health` | Status do sistema |
| GET | `/api/ai/photoperiod` | Obter sugestão completa |
| POST | `/api/ai/apply` | Aplicar sugestão |
| GET | `/api/ai/stats` | Estatísticas de sensores |

### Exemplo de Resposta

```json
{
  "fotoperiodo_sugerido": 6.5,
  "intensidade_sugerida": 60,
  "luz_noturna_horas": 2.0,
  "tpa": {
    "percentagem": 40,
    "descricao": "TPA de 40% recomendada nas próximas 24-48h"
  },
  "alimentacao": {
    "percentagem": 50,
    "descricao": "Reduzir alimentação para 50% por alguns dias"
  },
  "severidade": "alta",
  "tendencia": "subida",
  "razao": "Turbidez elevada (65%); tendência de subida",
  "accoes": [
    "⚡ Fazer TPA de 40% nas próximas 24-48h",
    "🍽️ Reduzir alimentação para 50%",
    "💡 Reduzir fotoperíodo em 4h",
    "🔅 Reduzir intensidade para 60%",
    "🌙 Ativar luz noturna por 2.0h"
  ]
}
```

## 🧠 Como Funciona

### Arquitetura do Modelo

```
INPUT (3 features)
   ↓
[Turbidez, pH, Temperatura]
   ↓
Neural Network (32 hidden units)
   ↓
OUTPUT (3 targets)
   ↓
[Ajuste Fotoperíodo, TPA%, Alimentação%]
```

### Regras Base

O modelo é treinado com regras que consideram:

**Turbidez** (driver principal):
- 80-100% → Crítico (reduzir luz 8-10h, TPA 70-80%, suspender alimentação)
- 60-80% → Alto (reduzir luz 5-8h, TPA 50-70%, alimentação 50%)
- 40-60% → Moderado (reduzir luz 3-5h, TPA 30-50%, alimentação 75%)
- 20-40% → Baixo (reduzir luz 1-3h, TPA 20-30%, alimentação normal)
- 0-20% → Normal (manter, TPA 15%, alimentação normal)

**pH e Temperatura** (moderadores):
- Fora do ideal (pH < 6.5 ou > 7.8, Temp < 22°C ou > 28°C) → Aumenta urgência de TPA e reduz alimentação

### Métricas Esperadas

Com 10,000 amostras de treino:

| Métrica | Fotoperíodo | TPA | Alimentação |
|---------|-------------|-----|-------------|
| MAE | < 1h | < 10% | < 10% |
| Accuracy (<2h ou <10%) | > 90% | > 85% | > 85% |
| R² | > 0.90 | > 0.85 | > 0.85 |

## 📂 Estrutura do Projeto

```
ai/
├── api_server.py          # Servidor Flask (porta 5000)
├── requirements.txt       # Dependências Python
├── README.md             # Esta documentação
│
├── models/               # Modelos treinados
│   ├── photoperiod_model.pt   # Pesos do modelo neural
│   ├── scaler.pkl            # Scaler para normalização
│   └── metrics.json          # Métricas de avaliação
│
└── src/                  # Código fonte
    ├── __init__.py       # Módulo Python
    ├── config.py         # Configurações e regras
    ├── model.py          # Arquitetura da rede neural
    ├── data_loader.py    # Geração de dados sintéticos
    ├── train.py          # Script de treino
    ├── inference.py      # Previsões em produção
    ├── evaluate.py       # Avaliação e métricas
    └── suggestions.py    # Lógica de sugestões
```

## 🔧 Uso Programático

### Python

```python
from src.inference import AquaSensePredictor

# Inicializar predictor
predictor = AquaSensePredictor()

# Fazer previsão
result = predictor.predict(
    turbidity=65.0,      # Turbidez em %
    ph=7.1,              # pH
    temperature=26.5,    # Temperatura em °C
    base_photoperiod=10  # Fotoperíodo atual em horas
)

print(f"Ajuste: {result['adjustment_hours']}h")
print(f"TPA: {result['tpa_percentagem']}%")
print(f"Alimentação: {result['alimentacao_percentagem']}%")

# Sugestões completas
full = predictor.predict_full(
    turbidity_24h=60.0,  # Média 24h
    turbidity_now=65.0,  # Atual
    current_intensity=100,
    base_photoperiod=10,
    ph=7.1,
    temperature=26.5
)

print(full['razao'])
print(full['accoes'])
```

### API (cURL)

```bash
# Obter sugestão
curl http://localhost:5000/api/ai/photoperiod

# Aplicar sugestão
curl -X POST http://localhost:5000/api/ai/apply \
  -H "Content-Type: application/json" \
  -d '{"fotoperiodo_sugerido": 6.5, "intensidade_sugerida": 60}'

# Estatísticas
curl http://localhost:5000/api/ai/stats
```

## 🔬 Desenvolvimento

### Retreinar o Modelo

```bash
# Com validação cruzada (5-fold)
python -m src.train

# Avaliar performance
python -m src.evaluate
```

### Testar Diferentes Cenários

```python
from src.inference import AquaSensePredictor

predictor = AquaSensePredictor()

# Cenários de teste
scenarios = [
    ("Normal", 15, 7.2, 25.5),
    ("Moderado", 45, 7.0, 26.0),
    ("Alto", 70, 7.1, 27.5),
    ("Crítico", 90, 7.0, 28.0),
    ("pH baixo", 20, 6.3, 26.0),
    ("Temp alta", 20, 7.2, 30.5),
]

for name, turb, ph, temp in scenarios:
    result = predictor.predict(turbidity=turb, ph=ph, temperature=temp)
    print(f"{name}: Ajuste={result['adjustment_hours']}h, " 
          f"TPA={result['tpa_percentagem']}%, "
          f"Urgência={result['urgency']}")
```

## 🐛 Resolução de Problemas

### Erro: "Modelo não encontrado"

```bash
# Treinar o modelo primeiro
python -m src.train
```

### Erro: "ModuleNotFoundError"

```bash
# Instalar dependências
pip install -r requirements.txt
```

### Erro: "Database connection failed"

Verificar se a base de dados MySQL está a correr e as credenciais em `api_server.py` estão corretas.

### Performance baixa

- Aumentar `EPOCHS` em `src/config.py` (default: 500)
- Aumentar `HIDDEN_DIM` para mais neurónios (default: 32)
- Gerar mais dados de treino (default: 10,000)

## 📊 Monitorização

O sistema guarda métricas em `models/metrics.json`:

```json
{
  "epochs_trained": 245,
  "training_time_seconds": 12.5,
  "best_val_loss": 0.0023,
  "test_metrics": {
    "mae_photoperiod": 0.45,
    "accuracy_1h": 94.2,
    "mae_tpa": 6.8,
    "accuracy_tpa_10pct": 89.5,
    "mae_feeding": 7.2,
    "r2": 0.92
  }
}
```

## 🔮 Próximas Melhorias

- [ ] Adicionar mais sensores (NO3, PO4, O2)
- [ ] Sistema de feedback do utilizador
- [ ] Auto-tuning baseado em resultados reais
- [ ] Previsão de tendências futuras
- [ ] Alertas proativos via email/push
- [ ] Dashboard web interativo

## 📝 Licença

MIT License - AquaSense Team 2025

---

**Versão:** 1.0.0  
**Última atualização:** Janeiro 2025
