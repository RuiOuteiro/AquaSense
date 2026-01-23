"""
Servidor API Flask para o modelo de IA AquaSense.
Fornece endpoints para sugestões de ajuste de fotoperíodo.

Endpoints:
    GET  /api/ai/photoperiod - Obter sugestão completa
    POST /api/ai/apply       - Aplicar sugestão
    GET  /api/ai/stats       - Estatísticas de turbidez
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
import mysql.connector
from datetime import datetime, timedelta
from src.inference import PhotoperiodPredictor

# Inicializar preditor (carrega modelo uma vez)
try:
    predictor = PhotoperiodPredictor()
except FileNotFoundError:
    predictor = None
    print("[AVISO] Modelo não encontrado. Execute: python3 -m src.train")

app = Flask(__name__)
CORS(app)

DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 3309,
    "user": "root",
    "password": "",
    "database": "esp32_data"
}

def get_turbidity_stats():
    """Obtém estatísticas de turbidez das últimas 24 horas."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        # Média das últimas 24h
        cursor.execute("""
            SELECT AVG(valor) as media_24h
            FROM leituras_sensores 
            WHERE tipo_sensor = 'turbidity'
            AND data_hora >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
        """)
        result = cursor.fetchone()
        media_24h = float(result['media_24h']) if result['media_24h'] else 15.0
        
        # Última leitura
        cursor.execute("""
            SELECT valor
            FROM leituras_sensores 
            WHERE tipo_sensor = 'turbidity'
            ORDER BY data_hora DESC
            LIMIT 1
        """)
        result = cursor.fetchone()
        atual = float(result['valor']) if result else media_24h
        
        cursor.close()
        conn.close()
        
        return media_24h, atual
    except Exception as e:
        print(f"Erro DB: {e}")
        return 15.0, 15.0

def get_current_config():
    """Obtém configuração actual do sistema."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM configuracoes WHERE id = 1")
        config = cursor.fetchone()
        cursor.close()
        conn.close()
        return config
    except Exception:
        return None

def update_ai_suggestion(fotoperiodo_sugerido):
    """Guarda sugestão de IA na base de dados."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE configuracoes SET ai_fotoperiodo_sugerido = %s WHERE id = 1",
            (fotoperiodo_sugerido,)
        )
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Erro ao actualizar sugestão: {e}")

@app.route('/api/ai/photoperiod', methods=['GET'])
def get_photoperiod_suggestion():
    """
    Devolve sugestão completa de ajuste de fotoperíodo.
    Inclui TPA, luz noturna, intensidade e alimentação.
    """
    if predictor is None:
        return jsonify({"error": "Modelo não carregado"}), 500
    config = get_current_config()
    if not config:
        return jsonify({"error": "Configuração não encontrada"}), 500
    
    # Determinar fotoperíodo base
    fotoperiodo_base = config.get('luz_ciclo_horas', 8)
    if not fotoperiodo_base:
        # Calcular a partir do horário
        hora_ligar = config.get('luz_hora_ligar', 8)
        hora_desligar = config.get('luz_hora_desligar', 20)
        if hora_desligar > hora_ligar:
            fotoperiodo_base = hora_desligar - hora_ligar
        else:
            fotoperiodo_base = (24 - hora_ligar) + hora_desligar
    
    # Obter turbidez
    media_24h, atual = get_turbidity_stats()
    
    # Obter intensidade actual
    intensidade = config.get('luz_intensidade', 100)
    
    # Calcular sugestões completas
    result = predictor.predict_full(
        turbidity_24h=media_24h,
        turbidity_now=atual,
        current_intensity=intensidade,
        base_photoperiod=fotoperiodo_base
    )
    
    # Guardar sugestão na DB
    update_ai_suggestion(result['fotoperiodo_sugerido'])
    
    return jsonify(result)

@app.route('/api/ai/apply', methods=['POST'])
def apply_ai_suggestion():
    """
    Aplica a sugestão de IA à configuração do sistema.
    Actualiza fotoperíodo e intensidade conforme sugerido.
    """
    if predictor is None:
        return jsonify({"error": "Modelo não carregado"}), 500
    data = request.json or {}
    fotoperiodo = data.get('fotoperiodo_sugerido')
    
    if not fotoperiodo:
        # Calcular se não fornecido
        config = get_current_config()
        media_24h, atual = get_turbidity_stats()
        result = predictor.predict_full(media_24h, atual, 100, 8)
        fotoperiodo = result['fotoperiodo_sugerido']
    
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Actualizar ciclo de horas
        cursor.execute(
            "UPDATE configuracoes SET luz_ciclo_horas = %s WHERE id = 1",
            (fotoperiodo,)
        )
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "message": f"Fotoperíodo actualizado para {fotoperiodo}h",
            "fotoperiodo": fotoperiodo
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/ai/stats', methods=['GET'])
def get_stats():
    """Devolve estatísticas de turbidez para gráficos."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        # Últimas 24h em intervalos de 1h
        cursor.execute("""
            SELECT 
                DATE_FORMAT(data_hora, '%Y-%m-%d %H:00') as hora,
                AVG(valor) as turbidez
            FROM leituras_sensores 
            WHERE tipo_sensor = 'turbidity'
            AND data_hora >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
            GROUP BY DATE_FORMAT(data_hora, '%Y-%m-%d %H:00')
            ORDER BY hora
        """)
        hourly = cursor.fetchall()
        
        # Últimos 7 dias
        cursor.execute("""
            SELECT 
                DATE(data_hora) as dia,
                AVG(valor) as turbidez
            FROM leituras_sensores 
            WHERE tipo_sensor = 'turbidity'
            AND data_hora >= DATE_SUB(NOW(), INTERVAL 7 DAY)
            GROUP BY DATE(data_hora)
            ORDER BY dia
        """)
        daily = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "hourly": hourly,
            "daily": daily
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("AquaSense AI API Server")
    print("Endpoints:")
    print("  GET  /api/ai/photoperiod - Obter sugestão de fotoperíodo")
    print("  POST /api/ai/apply       - Aplicar sugestão")
    print("  GET  /api/ai/stats       - Estatísticas de turbidez")
    app.run(host='0.0.0.0', port=5000, debug=True)
