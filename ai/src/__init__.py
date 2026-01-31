"""
AquaSense AI - Módulo de Inteligência Artificial

Sistema de ajuste automático de fotoperíodo para aquários,
baseado em análise de turbidez, pH e temperatura da água.

Módulos:
    config      - Configurações do sistema
    model       - Arquitectura da rede neural
    data_loader - Carregamento e preparação de dados
    train       - Treino com validação cruzada
    inference   - Previsões em produção
    evaluate    - Avaliação e métricas
    suggestions - Sugestões completas (TPA, luz, alimentação)

Uso rápido:
    from src.inference import AquaSensePredictor
    
    predictor = AquaSensePredictor()
    result = predictor.predict(turbidity=45, ph=7.1, temperature=26.0)
    print(result)
"""
__version__ = "1.0.0"
__author__ = "AquaSense Team"

from .inference import AquaSensePredictor, PhotoperiodPredictor
from .model import AquaSenseNet, PhotoperiodNet, BaselineModel
from .config import (
    MODEL_PATH,
    SCALER_PATH,
    METRICS_PATH,
    INPUT_DIM,
    OUTPUT_DIM,
    get_expected_adjustment,
    get_expected_tpa,
    get_expected_feeding
)

__all__ = [
    "AquaSensePredictor",
    "PhotoperiodPredictor",
    "AquaSenseNet",
    "PhotoperiodNet",
    "BaselineModel",
    "MODEL_PATH",
    "SCALER_PATH",
    "METRICS_PATH",
    "INPUT_DIM",
    "OUTPUT_DIM",
    "get_expected_adjustment",
    "get_expected_tpa",
    "get_expected_feeding",
]
