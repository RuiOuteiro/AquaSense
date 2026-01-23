"""
Módulo de inferência para previsões em produção.

Fornece interface simples para obter sugestões de ajuste
de fotoperíodo baseado em dados de turbidez.
"""
from pathlib import Path
from typing import Dict, Tuple, Optional

import numpy as np
import torch

from .config import DEVICE, MODEL_PATH, SCALER_PATH
from .model import PhotoperiodNet
from .data_loader import StandardScaler
from .suggestions import get_full_suggestions


class PhotoperiodPredictor:
    """
    Classe para previsões de ajuste de fotoperíodo.
    
    Uso:
        predictor = PhotoperiodPredictor()
        result = predictor.predict(turbidity_24h=30, turbidity_now=45, trend=15)
        print(result['adjustment_hours'])
    """
    
    def __init__(self, model_path: Path = MODEL_PATH, scaler_path: Path = SCALER_PATH):
        self.device = DEVICE
        self.model = None
        self.scaler = None
        
        self._load_model(model_path)
        self._load_scaler(scaler_path)
    
    def _load_model(self, path: Path):
        """Carrega o modelo treinado."""
        if not path.exists():
            raise FileNotFoundError(f"Modelo não encontrado: {path}")
        
        self.model = PhotoperiodNet().to(self.device)
        self.model.load_state_dict(
            torch.load(path, map_location=self.device, weights_only=True)
        )
        self.model.eval()
        print(f"[✓] Modelo carregado: {path}")
    
    def _load_scaler(self, path: Path):
        """Carrega o scaler para normalização."""
        if path.exists():
            self.scaler = StandardScaler().load(path)
            print(f"[✓] Scaler carregado: {path}")
        else:
            print(f"[!] Scaler não encontrado, usando normalização manual")
            self.scaler = None
    
    def predict(
        self,
        turbidity_24h: float,
        turbidity_now: float,
        trend: Optional[float] = None,
        base_photoperiod: float = 8.0
    ) -> Dict[str, any]:
        """
        Prevê o ajuste de fotoperíodo recomendado.
        
        Args:
            turbidity_24h: Média de turbidez das últimas 24h (0-100%)
            turbidity_now: Turbidez actual (0-100%)
            trend: Tendência (diferença). Se None, calcula automaticamente.
            base_photoperiod: Fotoperíodo base em horas (default 8h)
        
        Returns:
            Dict com ajuste recomendado e informações adicionais
        """
        # Calcular tendência se não fornecida
        if trend is None:
            trend = turbidity_now - turbidity_24h
        
        # Preparar features
        features = np.array([[
            turbidity_24h / 100.0,
            turbidity_now / 100.0,
            (trend + 50) / 100.0,
            base_photoperiod / 16.0
        ]], dtype=np.float32)
        
        # Aplicar scaler se disponível
        if self.scaler is not None:
            features = self.scaler.transform(features)
        
        # Previsão
        x = torch.tensor(features, dtype=torch.float32).to(self.device)
        
        with torch.no_grad():
            normalized_output = self.model(x).item()
        
        # Desnormalizar: [-1, 1] -> [-12, 12] (mas limitamos a [-12, 0])
        adjustment = normalized_output * 12
        adjustment = max(-12, min(0, adjustment))
        
        # Calcular novo fotoperíodo sugerido
        suggested_photoperiod = max(2, base_photoperiod + adjustment)
        
        # Determinar nível de urgência
        urgency = self._determine_urgency(turbidity_now, trend)
        
        # Sugestões adicionais
        recommendations = self._get_recommendations(turbidity_now, trend, adjustment)
        
        return {
            'adjustment_hours': round(adjustment, 1),
            'suggested_photoperiod': round(suggested_photoperiod, 1),
            'urgency': urgency,
            'turbidity_level': self._classify_turbidity(turbidity_now),
            'recommendations': recommendations,
            'input': {
                'turbidity_24h': turbidity_24h,
                'turbidity_now': turbidity_now,
                'trend': round(trend, 1),
                'base_photoperiod': base_photoperiod
            }
        }
    
    def _determine_urgency(self, turbidity: float, trend: float) -> str:
        """Determina nível de urgência."""
        if turbidity > 80 or (turbidity > 60 and trend > 20):
            return 'critical'
        elif turbidity > 60 or (turbidity > 40 and trend > 15):
            return 'high'
        elif turbidity > 40 or trend > 10:
            return 'moderate'
        elif turbidity > 25:
            return 'low'
        return 'normal'
    
    def _classify_turbidity(self, turbidity: float) -> str:
        """Classifica nível de turbidez."""
        if turbidity > 80:
            return 'critical'
        elif turbidity > 60:
            return 'high'
        elif turbidity > 40:
            return 'moderate'
        elif turbidity > 20:
            return 'low'
        return 'clear'
    
    def _get_recommendations(
        self, turbidity: float, trend: float, adjustment: float
    ) -> list:
        """Gera lista de recomendações."""
        recs = []
        
        if turbidity > 80:
            recs.extend([
                "TPA urgente de 70-80%",
                "Suspender alimentação por 3 dias",
                "Desligar luz azul/noturna",
                "Verificar filtração"
            ])
        elif turbidity > 60:
            recs.extend([
                "TPA de 50-60%",
                "Reduzir alimentação em 50%",
                "Considerar desligar luz noturna"
            ])
        elif turbidity > 40:
            recs.extend([
                "TPA de 30-40%",
                "Reduzir alimentação ligeiramente"
            ])
        elif trend > 15:
            recs.append("Monitorizar evolução - tendência de aumento")
        
        if adjustment < -6:
            recs.append(f"Reduzir fotoperíodo em {abs(adjustment):.0f}h")
        elif adjustment < -2:
            recs.append(f"Ajustar fotoperíodo em {adjustment:.0f}h")
        
        if not recs:
            recs.append("Manter configurações actuais")
        
        return recs
    
    def predict_full(
        self,
        turbidity_24h: float,
        turbidity_now: float,
        current_intensity: int = 100,
        base_photoperiod: float = 8.0
    ) -> Dict[str, any]:
        """
        Previsão completa com todas as sugestões (TPA, luz noturna, alimentação).
        
        Returns:
            Dict com ajuste + sugestões completas de TPA, luz noturna, alimentação
        """
        # Obter ajuste do modelo neural
        basic_result = self.predict(turbidity_24h, turbidity_now, None, base_photoperiod)
        adjustment = basic_result['adjustment_hours']
        
        # Obter sugestões completas
        full = get_full_suggestions(
            turbidity_now=turbidity_now,
            turbidity_24h=turbidity_24h,
            current_intensity=current_intensity,
            base_photoperiod=int(base_photoperiod),
            adjustment_hours=adjustment
        )
        
        return full


def predict_adjustment(
    turbidity_24h: float,
    turbidity_now: float,
    trend: float = None,
    base_photoperiod: float = 8.0
) -> Dict[str, any]:
    """
    Função de conveniência para previsão rápida.
    
    Args:
        turbidity_24h: Média de turbidez das últimas 24h
        turbidity_now: Turbidez actual
        trend: Tendência (opcional)
        base_photoperiod: Fotoperíodo base
    
    Returns:
        Dict com resultado da previsão
    """
    predictor = PhotoperiodPredictor()
    return predictor.predict(turbidity_24h, turbidity_now, trend, base_photoperiod)


if __name__ == "__main__":
    print("=" * 60)
    print("TESTE DE INFERÊNCIA")
    print("=" * 60)
    
    try:
        predictor = PhotoperiodPredictor()
        
        test_cases = [
            ("Água limpa", 10, 12, 2),
            ("Turbidez moderada", 35, 40, 5),
            ("Turbidez alta", 55, 65, 10),
            ("Situação crítica", 75, 90, 15),
            ("Piorando rápido", 30, 55, 25),
        ]
        
        print(f"\n{'Cenário':<20} {'Turbidez':>10} {'Ajuste':>10} {'Urgência':>12}")
        print("-" * 55)
        
        for name, t24h, t_now, trend in test_cases:
            result = predictor.predict(t24h, t_now, trend)
            print(
                f"{name:<20} "
                f"{t_now:>9.0f}% "
                f"{result['adjustment_hours']:>+9.1f}h "
                f"{result['urgency']:>12}"
            )
        
        print("\n--- Exemplo detalhado ---")
        result = predictor.predict(50, 65, 15, 10)
        print(f"\nInput: turbidez_24h=50%, turbidez_now=65%, trend=+15, base=10h")
        print(f"Ajuste: {result['adjustment_hours']}h")
        print(f"Fotoperíodo sugerido: {result['suggested_photoperiod']}h")
        print(f"Urgência: {result['urgency']}")
        print(f"Recomendações:")
        for rec in result['recommendations']:
            print(f"  • {rec}")
            
    except FileNotFoundError as e:
        print(f"\n[ERRO] {e}")
        print("Execute primeiro: python -m src.train")
