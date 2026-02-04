"""
Configurações centralizadas do módulo de IA AquaSense.

Este ficheiro contém todas as constantes e configurações do sistema.
Modificar aqui para ajustar hiperparâmetros, caminhos ou regras de baseline.

Arquitectura do modelo:
    - Input (3): turbidez (0-100), pH (0-14), temperatura (°C)
    - Output (3): ajuste fotoperíodo (h), TPA (%), alimentação (%)

Ambiente:
    - Desenvolvimento: valores default
    - Produção: configurar via variáveis de ambiente (DB_HOST, DB_PORT, etc.)
"""
from pathlib import Path
import os
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
# Configurável via variáveis de ambiente para produção
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "127.0.0.1"),
    "port": int(os.getenv("DB_PORT", "3309")),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "esp32_data"),
}

# ==============================
# MODELO
# ==============================
INPUT_DIM = 3       # [turbidez, pH, temperatura]
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
# REGRAS (BASELINE) PARA LABELS
# ==============================
# Turbidez é o driver principal (algas/partículas).
# pH e temperatura entram como moderadores (stress/instabilidade).

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

# Ranges "ideais" (genéricos) para justificar moderação
PH_OK_MIN, PH_OK_MAX = 6.5, 7.5
PH_WARN_MIN, PH_WARN_MAX = 6.8, 7.2
TEMP_OK_MIN, TEMP_OK_MAX = 22.0, 28.0


def _turbidity_bucket_value(value: float, rules: dict) -> float:
    """Aplica regras por thresholds (maior threshold que value ultrapassa)."""
    for threshold, out in sorted(rules.items(), reverse=True):
        if value > threshold:
            return float(out)
    return float(list(rules.values())[-1])


def _risk_multiplier(ph: float | None, temperature: float | None) -> float:
    """
    Retorna um multiplicador de risco (>=1) com base em pH e temperatura.
    - normal: 1.0
    - moderado: 1.1
    - alto: 1.25
    - crítico: 1.4
    """
    risk = 1.0

    # pH
    if ph is not None:
        if ph < 6.2 or ph > 8.0:
            risk = max(risk, 1.4)
        elif ph < PH_WARN_MIN or ph > PH_WARN_MAX:
            risk = max(risk, 1.25)
        elif ph < PH_OK_MIN or ph > PH_OK_MAX:
            risk = max(risk, 1.1)

    # temperatura
    if temperature is not None:
        if temperature < 20.0 or temperature > 30.0:
            risk = max(risk, 1.4)
        elif temperature < 22.0 or temperature > 28.5:
            risk = max(risk, 1.25)
        elif temperature < TEMP_OK_MIN or temperature > TEMP_OK_MAX:
            risk = max(risk, 1.1)

    return float(risk)


def get_expected_adjustment(
    turbidity: float,
    trend: float = 0.0,
    ph: float | None = None,
    temperature: float | None = None
) -> float:
    """
    Ajuste esperado de fotoperíodo (horas <= 0).
    Baseado APENAS em turbidez (pH/temp não afectam).
    """
    turbidity = float(turbidity)
    trend = float(trend)

    adjustment = _turbidity_bucket_value(turbidity, TURBIDITY_RULES)

    # Ajuste adicional por tendência
    if trend > 15:
        adjustment -= 2
    elif trend > 5:
        adjustment -= 1

    # pH/temp NÃO afectam fotoperíodo - apenas turbidez

    # Clamp final
    adjustment = max(-12.0, min(0.0, adjustment))
    return float(adjustment)


def get_expected_tpa(
    turbidity: float,
    trend: float = 0.0,
    ph: float | None = None,
    temperature: float | None = None
) -> float:
    """
    Percentagem de TPA esperada (0..100).
    Baseada APENAS em turbidez (pH/temp não afectam).
    """
    turbidity = float(turbidity)
    trend = float(trend)

    tpa = _turbidity_bucket_value(turbidity, TPA_RULES)

    # Ajuste por tendência
    if trend > 15:
        tpa = min(100.0, tpa + 10.0)
    elif trend > 5:
        tpa = min(100.0, tpa + 5.0)

    # pH/temp NÃO afectam TPA - apenas turbidez

    return float(max(0.0, min(100.0, tpa)))


def get_expected_feeding(
    turbidity: float,
    trend: float = 0.0,
    ph: float | None = None,
    temperature: float | None = None
) -> float:
    """
    Percentagem de alimentação esperada (0..100).
    Baseada APENAS em turbidez (pH/temp não afectam).
    """
    turbidity = float(turbidity)
    trend = float(trend)

    feeding = _turbidity_bucket_value(turbidity, FEEDING_RULES)

    # Ajuste por tendência
    if trend > 15 and feeding > 0:
        feeding = max(0.0, feeding - 25.0)
    elif trend > 5 and feeding > 0:
        feeding = max(0.0, feeding - 10.0)

    # pH/temp NÃO afectam alimentação - apenas turbidez

    return float(max(0.0, min(100.0, feeding)))
