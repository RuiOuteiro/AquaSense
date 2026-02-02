"""
Modelo de rede neural e baseline para o AquaSense.

INPUT (3):
  0) turbidez (0-100)
  1) pH (0-14)
  2) temperatura (°C)

OUTPUT (3):
  0) ajuste fotoperíodo normalizado  -> [-1, 0]   (multiplicar por 12 => horas em [-12, 0])
  1) TPA normalizado                -> [0, 1]    (multiplicar por 100 => %)
  2) alimentação normalizado         -> [0, 1]    (multiplicar por 100 => %)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

import torch
import torch.nn as nn

from .config import (
    INPUT_DIM, HIDDEN_DIM, OUTPUT_DIM,
    get_expected_adjustment, get_expected_tpa, get_expected_feeding
)


class PhotoperiodNet(nn.Module):
    """
    Rede neural multi-output.

    Inputs (3):
      [turbidez, pH, temperatura]
    Outputs (3) normalizados:
      [ajuste/12, tpa/100, feeding/100]
    """

    def __init__(self, input_dim: int = INPUT_DIM, hidden_dim: int = HIDDEN_DIM, output_dim: int = OUTPUT_DIM):
        super().__init__()
        if output_dim != 3:
            raise ValueError(f"Este modelo foi desenhado para output_dim=3, recebido: {output_dim}")

        self.feature_extractor = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.10),

            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.10),
        )

        self.shared = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
        )

        # Head 0: ajuste fotoperíodo (normalizado)
        # Queremos intervalo [-1, 0] porque o ajuste é sempre <= 0 nas regras.
        # Sigmoid => [0,1]  -> negando => [-1,0]
        self.head_adjustment = nn.Sequential(
            nn.Linear(hidden_dim // 2, 1),
            nn.Sigmoid()
        )

        # Head 1: TPA (normalizado em [0,1])
        self.head_tpa = nn.Sequential(
            nn.Linear(hidden_dim // 2, 1),
            nn.Sigmoid()
        )

        # Head 2: alimentação (normalizado em [0,1])
        self.head_feeding = nn.Sequential(
            nn.Linear(hidden_dim // 2, 1),
            nn.Sigmoid()
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        x: (batch, 3)
        return: (batch, 3)  -> [adj_norm, tpa_norm, feeding_norm]
        """
        feats = self.feature_extractor(x)
        feats = self.shared(feats)

        adj = -self.head_adjustment(feats)  # [-1, 0]
        tpa = self.head_tpa(feats)          # [0, 1]
        feed = self.head_feeding(feats)     # [0, 1]

        out = torch.cat([adj, tpa, feed], dim=1)  # (batch, 3)
        return out


# Mantém compatibilidade com o teu inference.py (que estava a instanciar AquaSenseNet)
# Assim evitas rebentar imports em vários sítios.
AquaSenseNet = PhotoperiodNet


@dataclass
class BaselinePrediction:
    adjustment_hours: float
    tpa_percent: float
    feeding_percent: float

    def as_dict(self) -> Dict[str, float]:
        return {
            "adjustment_hours": float(self.adjustment_hours),
            "tpa_percent": float(self.tpa_percent),
            "feeding_percent": float(self.feeding_percent),
        }

    def as_normalized(self) -> Dict[str, float]:
        return {
            "adjustment_norm": float(self.adjustment_hours / 12.0),
            "tpa_norm": float(self.tpa_percent / 100.0),
            "feeding_norm": float(self.feeding_percent / 100.0),
        }


class BaselineModel:
    """
    Baseline baseado nas regras (config.py).
    Devolve SEMPRE 3 outputs (ajuste, TPA e alimentação).
    """

    @staticmethod
    def predict(turbidity: float, ph: float = None, temperature: float = None) -> BaselinePrediction:
        adj = get_expected_adjustment(turbidity, ph=ph, temperature=temperature)   # horas (<=0)
        tpa = get_expected_tpa(turbidity, ph=ph, temperature=temperature)          # %
        feed = get_expected_feeding(turbidity, ph=ph, temperature=temperature)     # %
        return BaselinePrediction(adj, tpa, feed)

    @staticmethod
    def predict_dict(turbidity: float, ph: float = None, temperature: float = None) -> Dict[str, float]:
        return BaselineModel.predict(turbidity, ph, temperature).as_dict()

    @staticmethod
    def predict_normalized(turbidity: float, ph: float = None, temperature: float = None) -> Dict[str, float]:
        """
        Útil se quiseres comparar com o output direto do modelo (que está normalizado).
        """
        return BaselineModel.predict(turbidity, ph, temperature).as_normalized()
