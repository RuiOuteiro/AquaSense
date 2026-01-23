"""
Configurações centralizadas do módulo de IA AquaSense.
"""
from pathlib import Path
import torch

# ==============================
# CAMINHOS
# ==============================
BASE_DIR = Path(__file__).resolve().parents[1]  # .../ai
SRC_DIR = BASE_DIR / "src"
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"
NOTEBOOKS_DIR = BASE_DIR / "notebooks"

# Criar pastas se não existirem
DATA_DIR.mkdir(parents=True, exist_ok=True)
MODELS_DIR.mkdir(parents=True, exist_ok=True)

# Ficheiros do modelo
MODEL_PATH = MODELS_DIR / "photoperiod_model.pt"
SCALER_PATH = MODELS_DIR / "scaler.pkl"
METRICS_PATH = MODELS_DIR / "metrics.json"

# ==============================
# BASE DE DADOS
# ==============================
DB_CONFIG = {
    'host': '127.0.0.1',
    'port': 3309,
    'user': 'root',
    'password': '',
    'database': 'esp32_data'
}

# ==============================
# MODELO
# ==============================
INPUT_DIM = 4       # Média 24h, turbidez actual, tendência, fotoperíodo base
HIDDEN_DIM = 32     # Neurónios na camada oculta
OUTPUT_DIM = 1      # Ajuste de fotoperíodo (horas)

# ==============================
# TREINO
# ==============================
BATCH_SIZE = 32
EPOCHS = 500
LEARNING_RATE = 0.001
PATIENCE = 50       # Early stopping
K_FOLDS = 5         # Validação cruzada
TEST_SIZE = 0.2     # 20% para teste
RANDOM_SEED = 42

# ==============================
# DEVICE
# ==============================
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# ==============================
# REGRAS DE TURBIDEZ (para labels)
# ==============================
TURBIDITY_RULES = {
    90: -10,    # Crítico: -10h
    80: -8,     # Muito alto: -8h
    70: -6,     # Alto: -6h
    60: -5,     # Elevado: -5h
    50: -4,     # Moderado-alto: -4h
    40: -3,     # Moderado: -3h
    30: -2,     # Ligeiro: -2h
    20: -1,     # Baixo: -1h
    0: 0        # Normal: sem ajuste
}

def get_expected_adjustment(turbidity: float, trend: float = 0) -> float:
    """Calcula o ajuste esperado com base nas regras definidas."""
    adjustment = 0
    for threshold, adj in sorted(TURBIDITY_RULES.items(), reverse=True):
        if turbidity > threshold:
            adjustment = adj
            break
    
    # Ajuste adicional por tendência
    if trend > 15:
        adjustment -= 2
    elif trend > 5:
        adjustment -= 1
    
    return max(-12, adjustment)
