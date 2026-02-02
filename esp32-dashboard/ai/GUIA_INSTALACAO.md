# 🚀 Guia de Instalação AquaSense IA

## Passo 1: Estrutura de Diretórios

Organize os ficheiros desta forma:

```
aquasense/
├── ai/
│   ├── api_server.py
│   ├── requirements.txt
│   ├── README.md
│   │
│   ├── models/              # (será criado automaticamente)
│   │   ├── photoperiod_model.pt
│   │   ├── scaler.pkl
│   │   └── metrics.json
│   │
│   └── src/
│       ├── __init__.py
│       ├── config.py
│       ├── model.py
│       ├── data_loader.py
│       ├── train.py
│       ├── inference.py
│       ├── evaluate.py
│       └── suggestions.py
```

## Passo 2: Copiar os Ficheiros

Todos os ficheiros necessários estão na pasta `/mnt/user-data/outputs/`:

1. **Ficheiros da raiz (ai/):**
   - `api_server.py`
   - `requirements.txt`
   - `README.md`

2. **Ficheiros do src/ (ai/src/):**
   - `__init__.py`
   - `config.py`
   - `data_loader.py`
   - `model.py`
   - `train.py`
   - `inference.py`
   - `evaluate.py`
   - `suggestions.py`

## Passo 3: Instalação

```bash
# Navegar para a pasta
cd aquasense/ai

# Instalar dependências
pip install -r requirements.txt

# OU instalar manualmente:
pip install torch>=2.0.0 numpy>=1.24.0 flask>=3.0.0 flask-cors>=4.0.0 mysql-connector-python>=8.0.0 scikit-learn>=1.3.0
```

## Passo 4: Treinar o Modelo

```bash
# Isto irá:
# - Gerar 10,000 amostras de dados sintéticos
# - Treinar o modelo neural
# - Guardar modelo e scaler em models/
# - Mostrar métricas de performance

python -m src.train
```

**Output esperado:**
```
============================================================
TREINO DO MODELO (3 sensores)
============================================================
[✓] Dataset preparado:
    Treino: 8000 amostras
    Teste:  2000 amostras
[✓] Scaler guardado: models/scaler.pkl
Device: cpu

A treinar (máx 500 épocas, early stopping após 50 sem melhoria)...

Época   1/500 | Train: 0.0234 | Val: 0.0198 | LR: 0.001000 | Best ✓
Época  10/500 | Train: 0.0045 | Val: 0.0041 | LR: 0.001000 | Best ✓
...
Época  85/500 | Train: 0.0012 | Val: 0.0011 | LR: 0.000500 | Best ✓
Early stopping: 50 épocas sem melhoria

============================================================
RESULTADOS FINAIS
============================================================
Épocas treinadas: 135
Tempo de treino: 18.3s
Melhor Val Loss: 0.0011

Métricas no Test Set:
  MSE global (norm):  0.0012
  R² global (norm):   0.931

  Ajuste fotoperíodo:
    MAE: 0.52h
    Accuracy (<1h): 92.1%
    Accuracy (<2h): 98.5%

  TPA:
    MAE: 7.3%
    Accuracy (<5%): 78.2%
    Accuracy (<10%): 91.8%

  Alimentação:
    MAE: 8.1%
    Accuracy (<10%): 88.3%

Modelo guardado: models/photoperiod_model.pt
Métricas guardadas: models/metrics.json
```

## Passo 5: Testar o Modelo

```bash
python -m src.inference
```

**Output esperado:**
```
============================================================
TESTE DE INFERÊNCIA
============================================================
[✓] Modelo carregado: models/photoperiod_model.pt
[✓] Scaler carregado: models/scaler.pkl

Cenário      Turb     pH   Temp      Adj   TPA  Alim  Urgência
---------------------------------------------------------------------------
Normal        15%   7.20   25.5    -1.2h   18%  100%     normal
Moderada      45%   7.00   26.0    -3.5h   32%   75%   moderate
Alta          70%   7.10   27.5    -6.8h   58%   50%       high
Crítica       90%   7.00   28.0   -10.2h   78%    0%   critical
pH baixo      20%   6.30   26.0    -2.5h   28%   65%       high
Temp alta     20%   7.20   30.5    -2.1h   25%   70%       high
```

## Passo 6: Iniciar o Servidor API

```bash
python api_server.py
```

**Output esperado:**
```
============================================================
AquaSense AI API Server
============================================================

Endpoints disponíveis:
  GET  /api/ai/health      - Status do sistema
  GET  /api/ai/photoperiod - Obter sugestão de fotoperíodo
  POST /api/ai/apply       - Aplicar sugestão
  GET  /api/ai/stats       - Estatísticas de sensores

Modelo: ✓ Carregado
============================================================

[✓] Modelo carregado: models/photoperiod_model.pt
[✓] Scaler carregado: models/scaler.pkl
 * Serving Flask app 'api_server'
 * Debug mode: on
 * Running on http://0.0.0.0:5000
```

## Passo 7: Testar a API

```bash
# Verificar status
curl http://localhost:5000/api/ai/health

# Obter sugestão
curl http://localhost:5000/api/ai/photoperiod

# Estatísticas
curl http://localhost:5000/api/ai/stats
```

## ✅ Verificação Final

Verifique que tem:

- [ ] ✓ Pasta `models/` criada com:
  - [ ] `photoperiod_model.pt` (~50KB)
  - [ ] `scaler.pkl` (~1KB)
  - [ ] `metrics.json` (~2KB)

- [ ] ✓ Todos os testes passaram
- [ ] ✓ API responde em `http://localhost:5000`

## 🐛 Problemas Comuns

### "No module named 'src'"

```bash
# Certificar que está na pasta ai/
cd aquasense/ai

# E executar com -m
python -m src.train
```

### "Modelo não encontrado"

```bash
# Treinar primeiro
python -m src.train

# Depois testar
python -m src.inference
```

### "Database connection failed"

Editar `api_server.py` linha 35-41 com as credenciais corretas da base de dados:

```python
DB_CONFIG = {
    "host": "127.0.0.1",     # Seu host
    "port": 3309,            # Sua porta
    "user": "root",          # Seu utilizador
    "password": "",          # Sua password
    "database": "esp32_data" # Sua database
}
```

### Porta 5000 já em uso

```bash
# Mudar porta em api_server.py (última linha)
app.run(host='0.0.0.0', port=5001, debug=True)
```

## 📊 Avaliação Completa (Opcional)

```bash
# Gerar relatório completo de avaliação
python -m src.evaluate
```

Isto cria `models/evaluation_report.json` com:
- Métricas no test set
- Análise por faixa de turbidez
- Comparação com baseline

## 🎉 Pronto!

O sistema está instalado e funcional. Pode agora:

1. Integrar com o ESP32 através da API
2. Visualizar sugestões no frontend
3. Aplicar recomendações automaticamente
4. Monitorizar métricas de performance

---

**Suporte:** Se tiver problemas, verifique `models/metrics.json` para validar que o treino foi bem-sucedido.
