"""
Módulo de sugestões completas para o sistema AquaSense.

Converte previsões do modelo em recomendações acionáveis.
Versão: 3 sensores (turbidez + pH + temperatura)
"""
from typing import Dict, Optional


def get_full_suggestions(
    turbidity_now: float,
    turbidity_24h: Optional[float],
    current_intensity: int,
    base_photoperiod: int,
    adjustment_hours: float,
    ai_tpa_pct: float,
    ai_feeding_pct: float,
    ph: Optional[float] = None,
    temperature: Optional[float] = None
) -> Dict:
    """
    Gera sugestões completas baseadas nos outputs do modelo + contexto.
    
    Args:
        turbidity_now: Turbidez actual
        turbidity_24h: Turbidez média 24h (opcional, pode ser None)
        current_intensity: Intensidade actual da luz (%)
        base_photoperiod: Fotoperíodo base (horas)
        adjustment_hours: Ajuste sugerido pelo modelo (negativo)
        ai_tpa_pct: TPA sugerido pelo modelo (%)
        ai_feeding_pct: Alimentação sugerida pelo modelo (%)
        ph: pH actual (opcional)
        temperature: Temperatura actual (opcional)
    
    Returns:
        Dict com sugestões completas
    """
    # Fotoperíodo sugerido
    suggested_photoperiod = max(2.0, min(14.0, base_photoperiod + adjustment_hours))
    
    # Determinar severidade
    severity = _classify_severity(turbidity_now, ph, temperature)
    
    # Tendência (se temos média 24h)
    if turbidity_24h is not None:
        trend = _calculate_trend(turbidity_24h, turbidity_now)
    else:
        trend = "desconhecida"
    
    # Intensidade sugerida
    suggested_intensity = _calculate_intensity(
        current_intensity, adjustment_hours, turbidity_now, severity
    )
    
    # Luz noturna
    nightlight_hours = _calculate_nightlight(severity, trend, suggested_photoperiod)
    
    # Descrições detalhadas
    tpa_desc = _describe_tpa(ai_tpa_pct, severity)
    feeding_desc = _describe_feeding(ai_feeding_pct, severity)
    
    # Razão principal
    reason = _generate_reason(turbidity_now, ph, temperature, severity, trend)
    
    # Ações recomendadas
    actions = _generate_actions(
        turbidity_now, ph, temperature,
        adjustment_hours, ai_tpa_pct, ai_feeding_pct,
        suggested_intensity, current_intensity,
        nightlight_hours, severity
    )
    
    return {
        "fotoperiodo_sugerido": round(suggested_photoperiod, 1),
        "intensidade_sugerida": suggested_intensity,
        "luz_noturna_horas": round(nightlight_hours, 1),
        
        "tpa": {
            "percentagem": round(ai_tpa_pct, 0),
            "descricao": tpa_desc
        },
        
        "alimentacao": {
            "percentagem": round(ai_feeding_pct, 0),
            "descricao": feeding_desc
        },
        
        "severidade": severity,
        "tendencia": trend,
        "razao": reason,
        "accoes": actions,
        
        "input": {
            "turbidez_actual": round(turbidity_now, 1),
            "turbidez_24h": round(turbidity_24h, 1) if turbidity_24h is not None else None,
            "intensidade_actual": current_intensity,
            "fotoperiodo_base": base_photoperiod,
            "ph": round(ph, 2) if ph is not None else None,
            "temperatura": round(temperature, 1) if temperature is not None else None
        }
    }


def _classify_severity(turbidity: float, ph: Optional[float], temp: Optional[float]) -> str:
    """Classifica severidade global."""
    # Factores críticos
    if turbidity >= 80:
        return "critica"
    
    if ph is not None:
        if ph < 6.2 or ph > 8.0:
            return "critica"
    
    if temp is not None:
        if temp < 20.0 or temp > 30.0:
            return "critica"
    
    # Alta
    if turbidity >= 60:
        return "alta"
    
    if ph is not None:
        if ph < 6.5 or ph > 7.8:
            return "alta"
    
    if temp is not None:
        if temp < 22.0 or temp > 28.5:
            return "alta"
    
    # Moderada
    if turbidity >= 40:
        return "moderada"
    
    # Baixa
    if turbidity >= 25:
        return "baixa"
    
    return "normal"


def _calculate_trend(turbidity_24h: float, turbidity_now: float) -> str:
    """Calcula tendência."""
    diff = turbidity_now - turbidity_24h
    
    if diff > 15:
        return "subida_rapida"
    elif diff > 5:
        return "subida"
    elif diff < -15:
        return "descida_rapida"
    elif diff < -5:
        return "descida"
    else:
        return "estavel"


def _calculate_intensity(
    current_intensity: int,
    adjustment_hours: float,
    turbidity: float,
    severity: str
) -> int:
    """Calcula intensidade sugerida."""
    if severity == "critica":
        return 30
    elif severity == "alta":
        return 50
    elif turbidity >= 60:
        return max(30, current_intensity - 30)
    elif adjustment_hours <= -6:
        return max(40, current_intensity - 25)
    elif adjustment_hours <= -4:
        return max(60, current_intensity - 15)
    elif adjustment_hours <= -2:
        return max(70, current_intensity - 10)
    else:
        return current_intensity


def _calculate_nightlight(severity: str, trend: str, photoperiod: float) -> float:
    """Calcula horas de luz noturna."""
    # Se fotoperíodo muito baixo, luz noturna ajuda
    if photoperiod <= 4:
        if severity == "critica" and trend in ["descida", "descida_rapida"]:
            return 3.0
        elif severity == "alta":
            return 2.0
        else:
            return 1.0
    
    # Transições
    if severity == "critica" and trend in ["descida", "descida_rapida"]:
        return 2.0
    elif severity == "alta" and trend == "descida_rapida":
        return 1.0
    
    return 0.0


def _describe_tpa(tpa_pct: float, severity: str) -> str:
    """Gera descrição de TPA."""
    if tpa_pct >= 70:
        return f"TPA URGENTE de {tpa_pct:.0f}% nas próximas 12-24h"
    elif tpa_pct >= 50:
        return f"TPA de {tpa_pct:.0f}% recomendada nas próximas 24-48h"
    elif tpa_pct >= 30:
        return f"TPA de {tpa_pct:.0f}% esta semana"
    elif tpa_pct >= 20:
        return f"TPA preventiva de {tpa_pct:.0f}% quando conveniente"
    else:
        return f"TPA de manutenção de {tpa_pct:.0f}% (rotina semanal)"


def _describe_feeding(feeding_pct: float, severity: str) -> str:
    """Gera descrição de alimentação."""
    if feeding_pct == 0:
        if severity == "critica":
            return "SUSPENDER alimentação por 4-5 dias"
        else:
            return "SUSPENDER alimentação por 2-3 dias"
    elif feeding_pct < 25:
        return f"Alimentar apenas {feeding_pct:.0f}% do normal por 3-4 dias"
    elif feeding_pct < 50:
        return f"Reduzir alimentação para {feeding_pct:.0f}% por alguns dias"
    elif feeding_pct < 75:
        return f"Alimentar a {feeding_pct:.0f}% do normal"
    elif feeding_pct < 100:
        return f"Manter alimentação a {feeding_pct:.0f}%"
    else:
        return "Alimentação normal"


def _generate_reason(
    turbidity: float,
    ph: Optional[float],
    temp: Optional[float],
    severity: str,
    trend: str
) -> str:
    """Gera razão principal."""
    reasons = []
    
    if severity == "critica":
        if turbidity >= 80:
            reasons.append(f"Turbidez crítica ({turbidity:.0f}%)")
        if ph is not None and (ph < 6.2 or ph > 8.0):
            reasons.append(f"pH crítico ({ph:.2f})")
        if temp is not None and (temp < 20.0 or temp > 30.0):
            reasons.append(f"Temperatura crítica ({temp:.1f}°C)")
    
    elif severity == "alta":
        if turbidity >= 60:
            reasons.append(f"Turbidez elevada ({turbidity:.0f}%)")
        if ph is not None and (ph < 6.5 or ph > 7.8):
            reasons.append(f"pH fora do ideal ({ph:.2f})")
        if temp is not None and (temp < 22.0 or temp > 28.5):
            reasons.append(f"Temperatura elevada ({temp:.1f}°C)")
    
    elif severity == "moderada":
        reasons.append(f"Turbidez moderada ({turbidity:.0f}%)")
    
    else:
        reasons.append(f"Água em boas condições ({turbidity:.0f}%)")
    
    if trend == "subida_rapida":
        reasons.append("tendência de subida rápida")
    elif trend == "subida":
        reasons.append("tendência de subida")
    
    return "; ".join(reasons) if reasons else "Parâmetros normais"


def _generate_actions(
    turbidity: float, ph: Optional[float], temp: Optional[float],
    adjustment: float, tpa_pct: float, feeding_pct: float,
    suggested_intensity: int, current_intensity: int,
    nightlight: float, severity: str
) -> list:
    """Gera lista de ações recomendadas."""
    actions = []
    
    # TPA
    if tpa_pct >= 70:
        actions.append(f"Fazer TPA URGENTE de {tpa_pct:.0f}% nas próximas 12-24h")
    elif tpa_pct >= 50:
        actions.append(f"Fazer TPA de {tpa_pct:.0f}% nas próximas 24-48h")
    elif tpa_pct >= 30:
        actions.append(f"Fazer TPA de {tpa_pct:.0f}% esta semana")
    elif tpa_pct >= 20:
        actions.append(f"TPA preventiva de {tpa_pct:.0f}%")
    
    # Alimentação
    if feeding_pct == 0:
        actions.append("SUSPENDER alimentação completamente")
    elif feeding_pct < 50:
        actions.append(f"Reduzir alimentação para {feeding_pct:.0f}%")
    elif feeding_pct < 100:
        actions.append(f"Alimentar a {feeding_pct:.0f}% do normal")
    
    # Fotoperíodo
    if abs(adjustment) >= 6:
        actions.append(f"Reduzir fotoperíodo em {abs(adjustment):.0f}h")
    elif abs(adjustment) >= 2:
        actions.append(f"Ajustar fotoperíodo em {adjustment:.0f}h")
    
    # Intensidade
    if suggested_intensity != current_intensity:
        diff = suggested_intensity - current_intensity
        if diff < -20:
            actions.append(f"Reduzir intensidade para {suggested_intensity}%")
        elif diff > 20:
            actions.append(f"Aumentar intensidade para {suggested_intensity}%")
    
    # Luz noturna
    if nightlight > 0:
        actions.append(f"Ativar luz noturna por {nightlight:.1f}h")
    
    # Alertas pH/temp
    if ph is not None:
        if ph < 6.2 or ph > 8.0:
            actions.append(f"pH CRÍTICO ({ph:.2f}) - verificar imediatamente")
        elif ph < 6.5 or ph > 7.8:
            actions.append(f"pH fora do ideal ({ph:.2f}) - monitorizar")
    
    if temp is not None:
        if temp < 20.0 or temp > 30.0:
            actions.append(f"Temperatura CRÍTICA ({temp:.1f}°C) - ajustar urgente")
        elif temp < 22.0 or temp > 28.5:
            actions.append(f"Temperatura elevada ({temp:.1f}°C) - verificar")
    
    # Manutenção geral
    if severity == "critica":
        actions.append("Verificar filtração e limpeza geral do sistema")
        actions.append("Testar parâmetros completos (NO3, PO4, GH, KH)")
    elif severity == "alta":
        actions.append("Verificar e limpar filtro")
    
    if not actions:
        actions.append("Manter configurações actuais")
    
    return actions
