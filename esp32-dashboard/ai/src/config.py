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
OUTPUT_DIM = 3      # [ajuste fotoperíodo, TPA%, alimentação]

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

TPA_RULES = {
    90: 80,     # Crítico: 80%
    80: 70,     # Muito alto: 70%
    70: 60,     # Alto: 60%
    60: 50,     # Elevado: 50%
    50: 40,     # Moderado-alto: 40%
    40: 30,     # Moderado: 30%
    25: 20,     # Ligeiro: 20%
    0: 15       # Normal: 15% rotina
}

FEEDING_RULES = {
    90: 0,      # Crítico: suspender (0%)
    80: 0,      # Muito alto: suspender
    70: 0,      # Alto: suspender
    60: 50,     # Elevado: 50%
    40: 75,     # Moderado: 75%
    0: 100      # Normal: 100%
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


def get_expected_tpa(turbidity: float, trend: float = 0) -> float:
    """Calcula a percentagem de TPA esperada."""
    tpa = 15
    for threshold, pct in sorted(TPA_RULES.items(), reverse=True):
        if turbidity > threshold:
            tpa = pct
            break
    
    # Ajuste por tendência
    if trend > 15:
        tpa = min(100, tpa + 10)
    elif trend > 5:
        tpa = min(100, tpa + 5)
    
    return tpa


def get_expected_feeding(turbidity: float, trend: float = 0) -> float:
    """Calcula a percentagem de alimentação esperada (100=normal, 0=suspender)."""
    feeding = 100
    for threshold, pct in sorted(FEEDING_RULES.items(), reverse=True):
        if turbidity > threshold:
            feeding = pct
            break
    
    # Ajuste por tendência
    if trend > 15 and feeding > 0:
        feeding = max(0, feeding - 25)
    elif trend > 5 and feeding > 0:
        feeding = max(0, feeding - 10)
    
    return feeding
