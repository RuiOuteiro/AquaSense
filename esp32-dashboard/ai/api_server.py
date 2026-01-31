"""
Servidor API Flask para o modelo de IA AquaSense.
Fornece endpoints para sugestões de ajuste de fotoperíodo.

Endpoints:
    GET  /api/ai/photoperiod - Obter sugestão completa
    POST /api/ai/apply       - Aplicar sugestão
    GET  /api/ai/stats       - Estatísticas de turbidez
    GET  /api/ai/health      - Status do sistema
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
import mysql.connector
from datetime import datetime, timedelta

try:
    from src.inference import PhotoperiodPredictor
    predictor = PhotoperiodPredictor()
    MODEL_LOADED = True
except FileNotFoundError:
    predictor = None
    MODEL_LOADED = False
    print("[AVISO] Modelo não encontrado. Execute: python -m src.train")
except Exception as e:
    predictor = None
    MODEL_LOADED = False
    print(f"[ERRO] Falha ao carregar modelo: {e}")

app = Flask(__name__)
CORS(app)

DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 3309,
    "user": "root",
    "password": "",
    "database": "esp32_data"
}


def get_db_connection():
    """Cria conexão com a base de dados."""
    return mysql.connector.connect(**DB_CONFIG)


def get_sensor_stats():
    """Obtém estatísticas de sensores das últimas 24 horas."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Turbidez
        cursor.execute("""
            SELECT AVG(valor) as media_24h, MAX(valor) as max_24h, MIN(valor) as min_24h
            FROM leituras_sensores 
            WHERE tipo_sensor = 'turbidity'
            AND data_hora >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
        """)
        turb_stats = cursor.fetchone()
        turbidity_24h = float(turb_stats['media_24h']) if turb_stats and turb_stats['media_24h'] else 15.0
        
        # Última leitura de turbidez
        cursor.execute("""
            SELECT valor
            FROM leituras_sensores 
            WHERE tipo_sensor = 'turbidity'
            ORDER BY data_hora DESC
            LIMIT 1
        """)
        turb_now = cursor.fetchone()
        turbidity_now = float(turb_now['valor']) if turb_now else turbidity_24h
        
        # pH
        cursor.execute("""
            SELECT valor
            FROM leituras_sensores 
            WHERE tipo_sensor = 'ph'
            ORDER BY data_hora DESC
            LIMIT 1
        """)
        ph_reading = cursor.fetchone()
        ph = float(ph_reading['valor']) if ph_reading else 7.0
        
        # Temperatura
        cursor.execute("""
            SELECT valor
            FROM leituras_sensores 
            WHERE tipo_sensor = 'temperature'
            ORDER BY data_hora DESC
            LIMIT 1
        """)
        temp_reading = cursor.fetchone()
        temperature = float(temp_reading['valor']) if temp_reading else 25.0
        
        cursor.close()
        conn.close()
        
        return {
            "turbidity_24h": turbidity_24h,
            "turbidity_now": turbidity_now,
            "ph": ph,
            "temperature": temperature
        }
    except Exception as e:
        print(f"Erro DB: {e}")
        return {
            "turbidity_24h": 15.0,
            "turbidity_now": 15.0,
            "ph": 7.0,
            "temperature": 25.0
        }


def get_current_config():
    """Obtém configuração actual do sistema."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM configuracoes WHERE id = 1")
        config = cursor.fetchone()
        cursor.close()
        conn.close()
        return config
    except Exception as e:
        print(f"Erro ao obter config: {e}")
        return None


def update_ai_suggestion(fotoperiodo_sugerido):
    """Guarda sugestão de IA na base de dados."""
    try:
        conn = get_db_connection()
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


@app.route('/api/ai/health', methods=['GET'])
def health_check():
    """Verifica status do sistema."""
    return jsonify({
        "status": "ok" if MODEL_LOADED else "no_model",
        "model_loaded": MODEL_LOADED,
        "message": "Modelo carregado" if MODEL_LOADED else "Modelo não encontrado. Execute: python -m src.train"
    })


@app.route('/api/ai/photoperiod', methods=['GET'])
def get_photoperiod_suggestion():
    """
    Devolve sugestão completa de ajuste de fotoperíodo.
    Inclui TPA, luz noturna, intensidade e alimentação.
    """
    if not MODEL_LOADED or predictor is None:
        return jsonify({
            "error": "Modelo não carregado",
            "message": "Execute: python -m src.train"
        }), 500
    
    try:
        config = get_current_config()
        if not config:
            return jsonify({"error": "Configuração não encontrada"}), 500
        
        # Determinar fotoperíodo base
        fotoperiodo_base = config.get('luz_ciclo_horas', 8)
        if not fotoperiodo_base:
            hora_ligar = config.get('luz_hora_ligar', 8)
            hora_desligar = config.get('luz_hora_desligar', 20)
            if hora_desligar > hora_ligar:
                fotoperiodo_base = hora_desligar - hora_ligar
            else:
                fotoperiodo_base = (24 - hora_ligar) + hora_desligar
        
        # Obter dados dos sensores
        sensor_data = get_sensor_stats()
        
        # Obter intensidade actual
        intensidade = config.get('luz_intensidade', 100)
        
        # Calcular sugestões completas
        result = predictor.predict_full(
            turbidity_24h=sensor_data['turbidity_24h'],
            turbidity_now=sensor_data['turbidity_now'],
            current_intensity=intensidade,
            base_photoperiod=fotoperiodo_base,
            ph=sensor_data['ph'],
            temperature=sensor_data['temperature']
        )
        
        # Guardar sugestão na DB
        update_ai_suggestion(result['fotoperiodo_sugerido'])
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({
            "error": str(e),
            "message": "Erro ao gerar sugestão"
        }), 500


@app.route('/api/ai/apply', methods=['POST'])
def apply_ai_suggestion():
    """
    Aplica a sugestão de IA à configuração do sistema.
    Actualiza fotoperíodo e intensidade conforme sugerido.
    """
    if not MODEL_LOADED or predictor is None:
        return jsonify({"error": "Modelo não carregado"}), 500
    
    try:
        data = request.json or {}
        fotoperiodo = data.get('fotoperiodo_sugerido')
        intensidade = data.get('intensidade_sugerida')
        
        if not fotoperiodo:
            # Calcular se não fornecido
            config = get_current_config()
            sensor_data = get_sensor_stats()
            
            fotoperiodo_base = config.get('luz_ciclo_horas', 8) if config else 8
            intensidade_actual = config.get('luz_intensidade', 100) if config else 100
            
            result = predictor.predict_full(
                turbidity_24h=sensor_data['turbidity_24h'],
                turbidity_now=sensor_data['turbidity_now'],
                current_intensity=intensidade_actual,
                base_photoperiod=fotoperiodo_base,
                ph=sensor_data['ph'],
                temperature=sensor_data['temperature']
            )
            fotoperiodo = result['fotoperiodo_sugerido']
            intensidade = result.get('intensidade_sugerida', intensidade_actual)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Actualizar ciclo de horas
        updates = []
        params = []
        
        if fotoperiodo:
            updates.append("luz_ciclo_horas = %s")
            params.append(fotoperiodo)
        
        if intensidade:
            updates.append("luz_intensidade = %s")
            params.append(intensidade)
        
        if updates:
            query = f"UPDATE configuracoes SET {', '.join(updates)} WHERE id = 1"
            cursor.execute(query, tuple(params))
            conn.commit()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "message": f"Configuração actualizada",
            "fotoperiodo": fotoperiodo,
            "intensidade": intensidade
        })
    
    except Exception as e:
        return jsonify({
            "error": str(e),
            "message": "Erro ao aplicar sugestão"
        }), 500


@app.route('/api/ai/stats', methods=['GET'])
def get_stats():
    """Devolve estatísticas de sensores para gráficos."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Últimas 24h em intervalos de 1h (turbidez)
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
        hourly_turbidity = cursor.fetchall()
        
        # Últimos 7 dias (turbidez)
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
        daily_turbidity = cursor.fetchall()
        
        # pH últimas 24h
        cursor.execute("""
            SELECT 
                DATE_FORMAT(data_hora, '%Y-%m-%d %H:00') as hora,
                AVG(valor) as ph
            FROM leituras_sensores 
            WHERE tipo_sensor = 'ph'
            AND data_hora >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
            GROUP BY DATE_FORMAT(data_hora, '%Y-%m-%d %H:00')
            ORDER BY hora
        """)
        hourly_ph = cursor.fetchall()
        
        # Temperatura últimas 24h
        cursor.execute("""
            SELECT 
                DATE_FORMAT(data_hora, '%Y-%m-%d %H:00') as hora,
                AVG(valor) as temperatura
            FROM leituras_sensores 
            WHERE tipo_sensor = 'temperature'
            AND data_hora >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
            GROUP BY DATE_FORMAT(data_hora, '%Y-%m-%d %H:00')
            ORDER BY hora
        """)
        hourly_temp = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "turbidity": {
                "hourly": hourly_turbidity,
                "daily": daily_turbidity
            },
            "ph": {
                "hourly": hourly_ph
            },
            "temperature": {
                "hourly": hourly_temp
            }
        })
    
    except Exception as e:
        return jsonify({
            "error": str(e),
            "message": "Erro ao obter estatísticas"
        }), 500


if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("AquaSense AI API Server")
    print("=" * 60)
    print("\nEndpoints disponíveis:")
    print("  GET  /api/ai/health      - Status do sistema")
    print("  GET  /api/ai/photoperiod - Obter sugestão de fotoperíodo")
    print("  POST /api/ai/apply       - Aplicar sugestão")
    print("  GET  /api/ai/stats       - Estatísticas de sensores")
    print("\nModelo:", "✓ Carregado" if MODEL_LOADED else "✗ Não encontrado")
    if not MODEL_LOADED:
        print("\n⚠️  Execute primeiro: python -m src.train")
    print("=" * 60 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
