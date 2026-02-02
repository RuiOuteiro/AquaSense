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
    
    # Intensidade sugerida (baseada apenas em turbidez)
    suggested_intensity = _calculate_intensity(current_intensity, turbidity_now)
    
    # Luz noturna/azul
    night_light = _calculate_nightlight(turbidity_now, trend)
    
    # Descrições detalhadas
    tpa_desc = _describe_tpa(ai_tpa_pct, severity)
    feeding_desc = _describe_feeding(ai_feeding_pct, severity)
    
    # Razão principal
    reason = _generate_reason(turbidity_now, ph, temperature, severity, trend)
    
    # Ações recomendadas
    actions = _generate_actions(
        turbidity_now, trend,
        adjustment_hours, ai_tpa_pct, ai_feeding_pct,
        tpa_desc, night_light, ph, temperature
    )
    
    return {
        "fotoperiodo_sugerido": round(suggested_photoperiod, 1),
        "ajuste_horas": round(adjustment_hours, 1),
        "intensidade_sugerida": suggested_intensity,
        
        "tpa": {
            "percentagem": round(ai_tpa_pct, 0),
            "descricao": tpa_desc
        },
        
        "alimentacao": {
            "percentagem": round(ai_feeding_pct, 0),
            "descricao": feeding_desc
        },
        
        "luz_noturna": night_light,
        
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
    turbidity: float
) -> int:
    """
    Calcula intensidade sugerida baseada APENAS na turbidez.
    (Lógica do ficheiro antigo)
    """
    if turbidity > 90:
        return min(current_intensity, 20)
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


def _calculate_nightlight(turbidity: float, trend: str) -> dict:
    """
    Gera sugestões para a luz noturna (azul).
    Baseado na turbidez actual e tendência.
    """
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
    turbidity: float, trend: str,
    adjustment: float, tpa_pct: float, feeding_pct: float,
    tpa_desc: str, night_light: dict,
    ph: Optional[float] = None, temperature: Optional[float] = None
) -> list:
    """
    Gera lista de ações recomendadas.
    
    Tipos de sugestões:
    - TPA (Troca Parcial de Água)
    - Alimentação
    - Fotoperíodo
    - Luz azul/noturna
    - Alertas pH/temperatura
    """
    actions = []
    nl_action = night_light.get("accao", "manter")
    
    # Ações por nível de turbidez (como no ficheiro antigo)
    if turbidity > 90:
        actions = [
            tpa_desc,
            "Suspender alimentação por 3+ dias",
            "Reduzir fotoperíodo para mínimo (2-4h)",
            "DESLIGAR luz azul completamente",
            "Verificar filtração e aumentar oxigenação"
        ]
    elif turbidity > 80:
        actions = [
            tpa_desc,
            "Suspender alimentação por 2 dias",
            "Reduzir fotoperíodo para 4h",
            "Desligar luz azul" if nl_action == "desligar" else "Reduzir luz azul"
        ]
    elif turbidity > 70:
        actions = [
            tpa_desc,
            "Suspender alimentação por 2 dias",
            "Reduzir fotoperíodo para 4-6h",
            night_light.get("razao", "")
        ]
    elif turbidity > 60:
        actions = [
            tpa_desc,
            "Reduzir alimentação para 50%",
            "Reduzir fotoperíodo",
            night_light.get("razao", "")
        ]
    elif turbidity > 40:
        actions = [
            tpa_desc,
            "Reduzir ligeiramente alimentação",
            "Ajustar fotoperíodo preventivamente"
        ]
    elif trend == "subida_rapida":
        actions = [
            "Monitorizar evolução",
            "Considerar TPA preventiva",
            "Reduzir alimentação"
        ]
    elif trend == "subida":
        actions = ["Monitorizar nos próximos dias"]
    else:
        actions = ["Manter rotina actual"]
    
    # Adicionar alertas de pH
    if ph is not None:
        if ph > 8.5:
            actions.append(f"pH ALTO ({ph:.1f}) - testar KH, verificar CO2")
        elif ph > 8.0:
            actions.append(f"pH elevado ({ph:.1f}) - testar KH/GH, monitorizar")
        elif ph < 6.0:
            actions.append(f"pH BAIXO ({ph:.1f}) - verificar injecção CO2, testar KH")
        elif ph < 6.5:
            actions.append(f"pH baixo ({ph:.1f}) - verificar CO2, monitorizar")
    
    # Adicionar alertas de temperatura
    if temperature is not None:
        if temperature > 30:
            actions.append(f"TEMP ALTA ({temperature:.0f}°C) - aumentar circulação, reduzir luz")
        elif temperature > 28:
            actions.append(f"Temperatura elevada ({temperature:.0f}°C) - monitorizar")
        elif temperature < 20:
            actions.append(f"TEMP BAIXA ({temperature:.0f}°C) - verificar aquecedor")
        elif temperature < 22:
            actions.append(f"Temperatura baixa ({temperature:.0f}°C) - monitorizar")
    
    # Remover ações vazias
    actions = [a for a in actions if a]
    
    return actions
