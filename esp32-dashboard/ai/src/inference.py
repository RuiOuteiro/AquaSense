"""
Módulo de inferência para previsões em produção.

Fornece interface simples para obter sugestões de ajuste
de fotoperíodo, TPA e alimentação baseado em dados de turbidez.
"""
from pathlib import Path
from typing import Dict, Tuple, Optional

import numpy as np
import torch

from .config import DEVICE, MODEL_PATH, SCALER_PATH
from .model import AquaSenseNet, PhotoperiodNet
from .data_loader import StandardScaler
from .suggestions import get_full_suggestions


class AquaSensePredictor:
    """
    Classe para previsões de ajuste de fotoperíodo, TPA e alimentação.
    
    Uso:
        predictor = AquaSensePredictor()
        result = predictor.predict(turbidity_24h=30, turbidity_now=45)
        print(result['adjustment_hours'], result['tpa_percentagem'], result['alimentacao_percentagem'])
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
        
        self.model = AquaSenseNet().to(self.device)
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
            output = self.model(x)
        
        # Desnormalizar as 3 saídas
        adjustment = output[0, 0].item() * 12  # [-1, 1] -> [-12, 12]
        adjustment = max(-12, min(0, adjustment))
        
        tpa_pct = output[0, 1].item() * 100  # [0, 1] -> [0, 100]
        tpa_pct = max(0, min(100, tpa_pct))
        
        feeding_pct = output[0, 2].item() * 100  # [0, 1] -> [0, 100]
        feeding_pct = max(0, min(100, feeding_pct))
        
        # Calcular novo fotoperíodo sugerido
        suggested_photoperiod = max(2, base_photoperiod + adjustment)
        
        # Determinar nível de urgência
        urgency = self._determine_urgency(turbidity_now, trend)
        
        # Sugestões adicionais
        recommendations = self._get_recommendations(turbidity_now, trend, adjustment, tpa_pct, feeding_pct)
        
        return {
            'adjustment_hours': round(adjustment, 1),
            'suggested_photoperiod': round(suggested_photoperiod, 1),
            'tpa_percentagem': round(tpa_pct, 0),
            'alimentacao_percentagem': round(feeding_pct, 0),
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
        self, turbidity: float, trend: float, adjustment: float,
        tpa_pct: float = None, feeding_pct: float = None
    ) -> list:
        """Gera lista de recomendações baseada nas previsões do modelo."""
        recs = []
        
        # Usar valores do modelo se disponíveis
        if tpa_pct is not None:
            if tpa_pct >= 70:
                recs.append(f"TPA urgente de {tpa_pct:.0f}%")
            elif tpa_pct >= 40:
                recs.append(f"TPA de {tpa_pct:.0f}% recomendada")
            elif tpa_pct >= 20:
                recs.append(f"TPA preventiva de {tpa_pct:.0f}%")
        
        if feeding_pct is not None:
            if feeding_pct == 0:
                recs.append("Suspender alimentação")
            elif feeding_pct < 50:
                recs.append(f"Reduzir alimentação para {feeding_pct:.0f}%")
            elif feeding_pct < 100:
                recs.append(f"Alimentação a {feeding_pct:.0f}% do normal")
        
        if turbidity > 80:
            recs.append("Desligar luz azul/noturna")
            recs.append("Verificar filtração")
        elif turbidity > 60:
            recs.append("Considerar desligar luz noturna")
        
        if adjustment < -6:
            recs.append(f"Reduzir fotoperíodo em {abs(adjustment):.0f}h")
        elif adjustment < -2:
            recs.append(f"Ajustar fotoperíodo em {adjustment:.0f}h")
        
        if trend > 15 and not recs:
            recs.append("Monitorizar evolução - tendência de aumento")
        
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
        Usa o modelo neural para fotoperíodo, TPA e alimentação.
        
        Returns:
            Dict com ajuste + sugestões completas de TPA, luz noturna, alimentação
        """
        # Obter previsões do modelo neural (fotoperíodo, TPA, alimentação)
        ai_result = self.predict(turbidity_24h, turbidity_now, None, base_photoperiod)
        adjustment = ai_result['adjustment_hours']
        tpa_pct = ai_result['tpa_percentagem']
        feeding_pct = ai_result['alimentacao_percentagem']
        
        # Obter sugestões completas (luz noturna, intensidade, etc.)
        full = get_full_suggestions(
            turbidity_now=turbidity_now,
            turbidity_24h=turbidity_24h,
            current_intensity=current_intensity,
            base_photoperiod=int(base_photoperiod),
            adjustment_hours=adjustment,
            ai_tpa_pct=tpa_pct,
            ai_feeding_pct=feeding_pct
        )
        
        return full


# Alias para retrocompatibilidade
PhotoperiodPredictor = AquaSensePredictor


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
    predictor = AquaSensePredictor()
    return predictor.predict(turbidity_24h, turbidity_now, trend, base_photoperiod)


if __name__ == "__main__":
    print("=" * 60)
    print("TESTE DE INFERÊNCIA - AquaSenseNet")
    print("=" * 60)
    
    try:
        predictor = AquaSensePredictor()
        
        test_cases = [
            ("Água limpa", 10, 12, 2),
            ("Turbidez moderada", 35, 40, 5),
            ("Turbidez alta", 55, 65, 10),
            ("Situação crítica", 75, 90, 15),
            ("Piorando rápido", 30, 55, 25),
        ]
        
        print(f"\n{'Cenário':<18} {'Turb':>6} {'Ajuste':>8} {'TPA':>6} {'Alim':>6} {'Urgência':>10}")
        print("-" * 60)
        
        for name, t24h, t_now, trend in test_cases:
            result = predictor.predict(t24h, t_now, trend)
            print(
                f"{name:<18} "
                f"{t_now:>5.0f}% "
                f"{result['adjustment_hours']:>+7.1f}h "
                f"{result['tpa_percentagem']:>5.0f}% "
                f"{result['alimentacao_percentagem']:>5.0f}% "
                f"{result['urgency']:>10}"
            )
        
        print("\n--- Exemplo detalhado ---")
        result = predictor.predict(50, 65, 15, 10)
        print(f"\nInput: turbidez_24h=50%, turbidez_now=65%, trend=+15, base=10h")
        print(f"Ajuste fotoperíodo: {result['adjustment_hours']}h")
        print(f"Fotoperíodo sugerido: {result['suggested_photoperiod']}h")
        print(f"TPA sugerida: {result['tpa_percentagem']}%")
        print(f"Alimentação: {result['alimentacao_percentagem']}%")
        print(f"Urgência: {result['urgency']}")
        print(f"Recomendações:")
        for rec in result['recommendations']:
            print(f"  • {rec}")
            
    except FileNotFoundError as e:
        print(f"\n[ERRO] {e}")
        print("Execute primeiro: python -m src.train")
