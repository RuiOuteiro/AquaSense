"""
Módulo de inferência para previsões em produção.

Versão: 3 sensores (turbidez + pH + temperatura)
Outputs: ajuste fotoperíodo, TPA%, alimentação%
"""
from pathlib import Path
from typing import Dict, Optional, Any
import numpy as np
import torch

from .config import DEVICE, MODEL_PATH, SCALER_PATH
from .model import AquaSenseNet
from .data_loader import StandardScaler
from .suggestions import get_full_suggestions


class AquaSensePredictor:
    """
    Classe para previsões (3 sensores).

    Uso:
        predictor = AquaSensePredictor()
        result = predictor.predict(turbidity=45, ph=7.1, temperature=26.5)
        print(result['adjustment_hours'], result['tpa_percentagem'], result['alimentacao_percentagem'])
    """

    def __init__(self, model_path: Path = MODEL_PATH, scaler_path: Path = SCALER_PATH):
        self.device = DEVICE
        self.model: Optional[AquaSenseNet] = None
        self.scaler: Optional[StandardScaler] = None

        self._load_model(model_path)
        self._load_scaler(scaler_path)

    def _load_model(self, path: Path):
        """Carrega o modelo treinado."""
        if not path.exists():
            raise FileNotFoundError(
                f"Modelo não encontrado: {path}\n"
                "Execute primeiro: python -m src.train"
            )

        self.model = AquaSenseNet().to(self.device)

        # Tentar carregar com weights_only (versões recentes)
        try:
            state_dict = torch.load(path, map_location=self.device, weights_only=True)
        except TypeError:
            # Fallback para versões antigas
            state_dict = torch.load(path, map_location=self.device)

        # Extrair state_dict se estiver em formato dict
        if isinstance(state_dict, dict) and "state_dict" in state_dict:
            state_dict = state_dict["state_dict"]
        elif isinstance(state_dict, dict) and "model_state_dict" in state_dict:
            state_dict = state_dict["model_state_dict"]

        try:
            self.model.load_state_dict(state_dict, strict=True)
        except RuntimeError as e:
            raise RuntimeError(
                "Modelo incompatível com a arquitectura actual.\n"
                "Solução: re-treinar com: python -m src.train\n"
                f"Erro: {e}"
            )

        self.model.eval()
        print(f"[✓] Modelo carregado: {path}")

    def _load_scaler(self, path: Path):
        """Carrega o scaler para normalização."""
        if path.exists():
            try:
                self.scaler = StandardScaler()
                self.scaler.load(path)
                print(f"[✓] Scaler carregado: {path}")
            except Exception as e:
                print(f"[!] Erro ao carregar scaler: {e}")
                self.scaler = None
        else:
            print(f"[!] Scaler não encontrado: {path}")
            self.scaler = None

    def predict(
        self,
        turbidity: float,
        ph: float,
        temperature: float,
        base_photoperiod: float = 8.0
    ) -> Dict[str, Any]:
        """
        Prevê ajuste de fotoperíodo, TPA e alimentação.

        Args:
            turbidity: Turbidez (0-100)
            ph: pH (0-14)
            temperature: Temperatura (°C)
            base_photoperiod: Fotoperíodo base (horas)

        Returns:
            Dict com previsões
        """
        if self.model is None:
            raise RuntimeError("Modelo não carregado.")

        # Sanitizar e validar inputs
        turbidity = float(np.clip(turbidity, 0.0, 100.0))
        ph = float(np.clip(ph, 0.0, 14.0))
        temperature = float(np.clip(temperature, -5.0, 45.0))
        base_photoperiod = float(np.clip(base_photoperiod, 0.0, 24.0))

        # Features RAW
        features = np.array([[turbidity, ph, temperature]], dtype=np.float32)

        # Aplicar scaler se disponível
        if self.scaler is not None:
            features = self.scaler.transform(features)

        # Previsão
        x = torch.tensor(features, dtype=torch.float32).to(self.device)

        with torch.no_grad():
            output = self.model(x)

        # Validar output
        if output.shape != (1, 3):
            raise RuntimeError(
                f"Output inesperado: {output.shape}. Esperado: (1, 3)\n"
                "Re-treinar o modelo."
            )

        # Desnormalizar outputs
        adjustment = float(output[0, 0].item()) * 12.0
        adjustment = max(-12.0, min(0.0, adjustment))

        tpa_pct = float(output[0, 1].item()) * 100.0
        tpa_pct = max(0.0, min(100.0, tpa_pct))

        feeding_pct = float(output[0, 2].item()) * 100.0
        feeding_pct = max(0.0, min(100.0, feeding_pct))

        # Fotoperíodo sugerido
        suggested_photoperiod = max(2.0, base_photoperiod + adjustment)

        # Urgência
        urgency = self._determine_urgency(turbidity, ph, temperature)

        # Recomendações
        recommendations = self._get_recommendations(
            turbidity, ph, temperature, adjustment, tpa_pct, feeding_pct
        )

        return {
            "adjustment_hours": round(adjustment, 1),
            "suggested_photoperiod": round(suggested_photoperiod, 1),
            "tpa_percentagem": round(tpa_pct, 0),
            "alimentacao_percentagem": round(feeding_pct, 0),
            "urgency": urgency,
            "turbidity_level": self._classify_turbidity(turbidity),
            "recommendations": recommendations,
            "input": {
                "turbidity": round(turbidity, 1),
                "ph": round(ph, 2),
                "temperature": round(temperature, 1),
                "base_photoperiod": base_photoperiod
            }
        }

    def predict_full(
        self,
        turbidity_24h: float,
        turbidity_now: float,
        current_intensity: int = 100,
        base_photoperiod: float = 8.0,
        ph: float = 7.0,
        temperature: float = 25.0
    ) -> Dict[str, Any]:
        """
        Previsão completa com sugestões detalhadas.
        Compatível com a API antiga (turbidity_24h).
        """
        # Usar turbidity_now como principal
        ai_result = self.predict(
            turbidity=turbidity_now,
            ph=ph,
            temperature=temperature,
            base_photoperiod=base_photoperiod
        )

        adjustment = ai_result["adjustment_hours"]
        tpa_pct = ai_result["tpa_percentagem"]
        feeding_pct = ai_result["alimentacao_percentagem"]

        full = get_full_suggestions(
            turbidity_now=turbidity_now,
            turbidity_24h=turbidity_24h,
            current_intensity=current_intensity,
            base_photoperiod=int(base_photoperiod),
            adjustment_hours=adjustment,
            ai_tpa_pct=tpa_pct,
            ai_feeding_pct=feeding_pct,
            ph=ph,
            temperature=temperature
        )

        return full

    def _determine_urgency(self, turbidity: float, ph: float, temperature: float) -> str:
        """Determina nível de urgência."""
        if ph < 6.2 or ph > 8.0 or temperature < 20.0 or temperature > 30.0:
            return "critical"
        if turbidity > 80:
            return "critical"
        elif turbidity > 60:
            return "high"
        elif turbidity > 40:
            return "moderate"
        elif turbidity > 25:
            return "low"
        return "normal"

    def _classify_turbidity(self, turbidity: float) -> str:
        """Classifica nível de turbidez."""
        if turbidity > 80:
            return "critical"
        elif turbidity > 60:
            return "high"
        elif turbidity > 40:
            return "moderate"
        elif turbidity > 20:
            return "low"
        return "clear"

    def _get_recommendations(
        self,
        turbidity: float,
        ph: float,
        temperature: float,
        adjustment: float,
        tpa_pct: float,
        feeding_pct: float
    ) -> list:
        """Gera recomendações."""
        recs = []

        # TPA
        if tpa_pct >= 70:
            recs.append(f"TPA urgente de {tpa_pct:.0f}%")
        elif tpa_pct >= 40:
            recs.append(f"TPA de {tpa_pct:.0f}% recomendada")
        elif tpa_pct >= 20:
            recs.append(f"TPA preventiva de {tpa_pct:.0f}%")

        # Alimentação
        if feeding_pct == 0:
            recs.append("Suspender alimentação")
        elif feeding_pct < 50:
            recs.append(f"Reduzir alimentação para {feeding_pct:.0f}%")
        elif feeding_pct < 100:
            recs.append(f"Alimentação a {feeding_pct:.0f}% do normal")

        # Fotoperíodo
        if adjustment < -6:
            recs.append(f"Reduzir fotoperíodo em {abs(adjustment):.0f}h")
        elif adjustment < -2:
            recs.append(f"Ajustar fotoperíodo em {adjustment:.0f}h")

        # pH/Temp
        if ph < 6.5 or ph > 7.8:
            recs.append(f"Verificar pH ({ph:.2f})")
        if temperature < 22.0 or temperature > 28.5:
            recs.append(f"Verificar temperatura ({temperature:.1f}°C)")

        # Turbidez
        if turbidity > 80:
            recs.append("Verificar filtração urgente")
        elif turbidity > 60:
            recs.append("Limpar filtro e reduzir luz")

        if not recs:
            recs.append("Manter configurações actuais")

        return recs


# Alias para retrocompatibilidade
PhotoperiodPredictor = AquaSensePredictor


if __name__ == "__main__":
    print("=" * 60)
    print("TESTE DE INFERÊNCIA")
    print("=" * 60)

    try:
        predictor = AquaSensePredictor()

        test_cases = [
            ("Normal", 15, 7.2, 25.5),
            ("Moderada", 45, 7.0, 26.0),
            ("Alta", 70, 7.1, 27.5),
            ("Crítica", 90, 7.0, 28.0),
            ("pH baixo", 20, 6.3, 26.0),
            ("Temp alta", 20, 7.2, 30.5),
        ]

        print(f"\n{'Cenário':<12} {'Turb':>6} {'pH':>6} {'Temp':>7} {'Adj':>8} {'TPA':>6} {'Alim':>6} {'Urgência':>10}")
        print("-" * 75)

        for name, turb, ph, temp in test_cases:
            result = predictor.predict(turbidity=turb, ph=ph, temperature=temp)
            print(
                f"{name:<12} "
                f"{turb:>5.0f}% "
                f"{ph:>5.2f} "
                f"{temp:>6.1f} "
                f"{result['adjustment_hours']:>+7.1f}h "
                f"{result['tpa_percentagem']:>5.0f}% "
                f"{result['alimentacao_percentagem']:>5.0f}% "
                f"{result['urgency']:>10}"
            )

    except FileNotFoundError as e:
        print(f"\n[ERRO] {e}")
        print("Execute: python -m src.train")
