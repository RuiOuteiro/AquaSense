<?php

/**
 * AquaSense - API de Consulta de Leituras
 * Endpoint para obtenção de dados históricos dos sensores
 * 
 * @package AquaSense
 * @version 1.0.0
 * @method GET
 * @param int limite Número máximo de registos (predefinido: 100, máximo: 1000)
 * @param int horas Intervalo temporal em horas (predefinido: 24)
 */

header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');

require_once 'config.php';

// Parâmetros de consulta
$limite = isset($_GET['limite']) ? min(intval($_GET['limite']), 1000) : 100;
$horas = isset($_GET['horas']) ? intval($_GET['horas']) : 24;

try {
    $pdo = obterConexaoBD();

    $stmt = $pdo->prepare("
        SELECT id, temperatura, humidade, valor_pwm, modo, t_minima, t_maxima, endereco_ip, criado_em
        FROM leituras_sensores
        WHERE criado_em >= DATE_SUB(NOW(), INTERVAL :horas HOUR)
        ORDER BY criado_em DESC
        LIMIT :limite
    ");

    $stmt->bindValue(':horas', $horas, PDO::PARAM_INT);
    $stmt->bindValue(':limite', $limite, PDO::PARAM_INT);
    $stmt->execute();

    $leituras = $stmt->fetchAll();

    // Cálculo de estatísticas agregadas
    $stmtStats = $pdo->prepare("
        SELECT 
            COUNT(*) as total_leituras,
            AVG(temperatura) as temp_media,
            MIN(temperatura) as temp_minima,
            MAX(temperatura) as temp_maxima,
            AVG(humidade) as humidade_media
        FROM leituras_sensores
        WHERE criado_em >= DATE_SUB(NOW(), INTERVAL :horas HOUR)
    ");
    $stmtStats->bindValue(':horas', $horas, PDO::PARAM_INT);
    $stmtStats->execute();
    $estatisticas = $stmtStats->fetch();

    echo json_encode([
        'sucesso' => true,
        'quantidade' => count($leituras),
        'estatisticas' => $estatisticas,
        'leituras' => $leituras
    ]);
} catch (PDOException $e) {
    http_response_code(500);
    echo json_encode(['erro' => 'Erro na base de dados: ' . $e->getMessage()]);
}
