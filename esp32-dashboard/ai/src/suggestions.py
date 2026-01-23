"""
Módulo de sugestões completas para o aquário.

Inclui:
- Ajuste de fotoperíodo
- Ajuste de intensidade
- TPA (Troca Parcial de Água)
- Luz noturna (azul)
- Alimentação
"""
from typing import Dict, Tuple, List


def calculate_intensity(turbidity: float, current_intensity: int) -> int:
    """Calcula intensidade sugerida baseada na turbidez."""
    if turbidity > 90:
        return min(current_intensity, 20)  # Máximo 20% - caso crítico
    elif turbidity > 80:
        return min(current_intensity, 30)
    elif turbidity > 70:
        return min(current_intensity, 40)
    elif turbidity > 60:
        return min(current_intensity, 50)
    elif turbidity > 50:
        return min(current_intensity, 70)
    elif turbidity > 40:
        return min(current_intensity, 80)
    return current_intensity


def calculate_tpa(turbidity: float, trend: float) -> Dict:
    """Calcula percentagem, urgência e frequência de TPA sugerida."""
    if turbidity > 90:
        return {
            "percentagem": 80,
            "urgencia": "critico",
            "frequencia": "diário",
            "dias": 3,
            "descricao": "TPA de 80% imediata + 50% diário por 3 dias"
        }
    elif turbidity > 80:
        return {
            "percentagem": 70,
            "urgencia": "urgente",
            "frequencia": "diário",
            "dias": 2,
            "descricao": "TPA de 70% imediata + 40% amanhã"
        }
    elif turbidity > 70:
        return {
            "percentagem": 60,
            "urgencia": "urgente",
            "frequencia": "48h",
            "dias": 2,
            "descricao": "TPA de 60% agora + 30% em 48h"
        }
    elif turbidity > 60:
        return {
            "percentagem": 50,
            "urgencia": "recomendado",
            "frequencia": "48h",
            "dias": 2,
            "descricao": "TPA de 50% recomendada"
        }
    elif turbidity > 50:
        return {
            "percentagem": 40,
            "urgencia": "recomendado",
            "frequencia": "semanal",
            "dias": 1,
            "descricao": "TPA de 40% recomendada"
        }
    elif turbidity > 40:
        return {
            "percentagem": 30,
            "urgencia": "sugerido",
            "frequencia": "semanal",
            "dias": 1,
            "descricao": "TPA de 30% sugerida"
        }
    elif turbidity > 25 or trend > 10:
        return {
            "percentagem": 20,
            "urgencia": "preventivo",
            "frequencia": "semanal",
            "dias": 1,
            "descricao": "TPA preventiva de 20%"
        }
    return {
        "percentagem": 15,
        "urgencia": "rotina",
        "frequencia": "semanal",
        "dias": 1,
        "descricao": "TPA de rotina semanal"
    }


def calculate_night_light(turbidity: float, trend: float) -> Dict:
    """Gera sugestões para a luz noturna (azul)."""
    if turbidity > 90:
        return {
            "accao": "desligar",
            "razao": "Desligar luz azul completamente - situação crítica de algas",
            "forcar": True
        }
    elif turbidity > 80:
        return {
            "accao": "desligar",
            "razao": "Desligar luz azul para reduzir crescimento de algas",
            "forcar": False
        }
    elif turbidity > 70:
        return {
            "accao": "reduzir",
            "periodo_max": 4,
            "razao": "Reduzir período da luz azul para máximo 4h",
            "forcar": False
        }
    elif turbidity > 60:
        return {
            "accao": "reduzir",
            "periodo_max": 6,
            "razao": "Limitar luz azul a 6h por noite",
            "forcar": False
        }
    elif turbidity > 40:
        return {
            "accao": "monitorizar",
            "razao": "Monitorizar - considerar reduzir se piorar",
            "forcar": False
        }
    return {
        "accao": "manter",
        "razao": "Luz azul pode manter configuração normal",
        "forcar": False
    }


def calculate_feeding(turbidity: float, trend: float) -> Dict:
    """Sugestões de alimentação baseada na turbidez."""
    if turbidity > 90:
        return {
            "accao": "suspender",
            "dias": 4,
            "descricao": "Suspender alimentação por 4+ dias"
        }
    elif turbidity > 80:
        return {
            "accao": "suspender",
            "dias": 3,
            "descricao": "Suspender alimentação por 3 dias"
        }
    elif turbidity > 70:
        return {
            "accao": "suspender",
            "dias": 2,
            "descricao": "Suspender alimentação por 2 dias"
        }
    elif turbidity > 60:
        return {
            "accao": "reduzir",
            "percentagem": 50,
            "descricao": "Reduzir alimentação em 50%"
        }
    elif turbidity > 40:
        return {
            "accao": "reduzir",
            "percentagem": 25,
            "descricao": "Reduzir alimentação em 25%"
        }
    return {
        "accao": "manter",
        "descricao": "Manter alimentação normal"
    }


def determine_actions(
    turbidity: float,
    trend: float,
    tpa: Dict,
    night_light: Dict
) -> Tuple[str, List[str]]:
    """Determina razão principal e lista de acções recomendadas."""
    actions = []
    tpa_desc = tpa.get("descricao", "")
    nl_action = night_light.get("accao", "manter")
    
    if turbidity > 90:
        reason = "CRÍTICO: Turbidez extrema - acção imediata necessária"
        actions = [
            tpa_desc,
            "Suspender alimentação por 3+ dias",
            "Reduzir fotoperíodo para 2h",
            "Reduzir intensidade para 20%",
            "DESLIGAR luz azul completamente",
            "Verificar filtração e aumentar oxigenação",
            "Considerar tratamento anti-algas"
        ]
    elif turbidity > 80:
        reason = "ALERTA: Turbidez muito alta - risco de proliferação de algas"
        actions = [
            tpa_desc,
            "Suspender alimentação por 2 dias",
            "Reduzir fotoperíodo para mínimo (4h)",
            "Reduzir intensidade da luz para 30%",
            "Desligar luz azul" if nl_action == "desligar" else "Reduzir luz azul",
            "Verificar filtração e aumentar oxigenação"
        ]
    elif turbidity > 70:
        reason = "Turbidez alta - proliferação de algas provável"
        actions = [
            tpa_desc,
            "Suspender alimentação por 2 dias",
            "Reduzir fotoperíodo para 4-6h",
            "Reduzir intensidade da luz para 40%",
            night_light.get("razao", "")
        ]
    elif turbidity > 60:
        reason = "Turbidez elevada - possível proliferação de algas"
        actions = [
            tpa_desc,
            "Reduzir alimentação para 50%",
            "Reduzir fotoperíodo",
            "Considerar reduzir intensidade da luz",
            night_light.get("razao", "")
        ]
    elif turbidity > 40:
        reason = "Turbidez moderada - monitorizar situação"
        actions = [
            tpa_desc,
            "Reduzir ligeiramente alimentação",
            "Ajustar fotoperíodo preventivamente"
        ]
    elif trend > 15:
        reason = "Turbidez a aumentar rapidamente - acção preventiva"
        actions = [
            "Monitorizar evolução",
            "Considerar TPA preventiva",
            "Reduzir alimentação"
        ]
    elif trend > 5:
        reason = "Turbidez com tendência de aumento"
        actions = ["Monitorizar nos próximos dias"]
    else:
        reason = "Condições normais"
        actions = ["Manter rotina actual"]
    
    # Remover acções vazias
    actions = [a for a in actions if a]
    
    return reason, actions


def get_full_suggestions(
    turbidity_now: float,
    turbidity_24h: float,
    current_intensity: int = 100,
    base_photoperiod: int = 8,
    adjustment_hours: float = 0
) -> Dict:
    """
    Gera sugestões completas para o aquário.
    
    Args:
        turbidity_now: Turbidez actual (0-100%)
        turbidity_24h: Média de turbidez das últimas 24h
        current_intensity: Intensidade actual da luz (0-100%)
        base_photoperiod: Fotoperíodo base configurado
        adjustment_hours: Ajuste de horas (do modelo neural)
    
    Returns:
        Dict com todas as sugestões
    """
    trend = turbidity_now - turbidity_24h
    
    # Calcular fotoperíodo sugerido
    min_photoperiod = 2 if turbidity_now > 90 else 4
    suggested_photoperiod = max(min_photoperiod, base_photoperiod + int(adjustment_hours))
    
    # Calcular sugestões
    intensity = calculate_intensity(turbidity_now, current_intensity)
    tpa = calculate_tpa(turbidity_now, trend)
    night_light = calculate_night_light(turbidity_now, trend)
    feeding = calculate_feeding(turbidity_now, trend)
    reason, actions = determine_actions(turbidity_now, trend, tpa, night_light)
    
    return {
        "fotoperiodo_base": base_photoperiod,
        "fotoperiodo_sugerido": suggested_photoperiod,
        "ajuste_horas": int(adjustment_hours),
        "intensidade_atual": current_intensity,
        "intensidade_sugerida": intensity,
        "tpa": tpa,
        "luz_noturna": night_light,
        "alimentacao": feeding,
        "turbidez_atual": turbidity_now,
        "turbidez_media_24h": turbidity_24h,
        "tendencia": round(trend, 1),
        "razao": reason,
        "accoes": actions
    }


if __name__ == "__main__":
    # Teste
    print("=== Teste de Sugestões ===\n")
    
    test_cases = [
        (15, 12, "Água limpa"),
        (45, 40, "Moderada"),
        (65, 55, "Elevada"),
        (85, 75, "Crítica"),
    ]
    
    for t_now, t_24h, name in test_cases:
        result = get_full_suggestions(t_now, t_24h, adjustment_hours=-2)
        print(f"--- {name} (turbidez {t_now}%) ---")
        print(f"  Razão: {result['razao']}")
        print(f"  TPA: {result['tpa']['descricao']}")
        print(f"  Luz noturna: {result['luz_noturna']['accao']}")
        print(f"  Alimentação: {result['alimentacao']['descricao']}")
        print(f"  Intensidade: {result['intensidade_sugerida']}%")
        print()
