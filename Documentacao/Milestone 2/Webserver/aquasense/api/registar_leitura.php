<?php

/**
 * AquaSense - API de Registo de Leituras
 * Endpoint para inserção de dados dos sensores na base de dados
 * 
 * @package AquaSense
 * @version 1.0.0
 * @method POST
 */

header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');

require_once 'config.php';

// Validação do método HTTP
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['erro' => 'Método não permitido']);
    exit;
}

// Autenticação via chave API
$chaveApi = $_SERVER['HTTP_X_API_KEY'] ?? $_POST['chave_api'] ?? '';
if ($chaveApi !== CHAVE_API) {
    http_response_code(401);
    echo json_encode(['erro' => 'Chave API inválida']);
    exit;
}

// Processamento dos dados recebidos (JSON ou formulário)
$entrada = file_get_contents('php://input');
$dados = json_decode($entrada, true);

if (!$dados) {
    $dados = $_POST;
}

// Extração e validação dos campos
$temperatura = isset($dados['temperatura']) ? floatval($dados['temperatura']) : null;
$humidade = isset($dados['humidade']) ? floatval($dados['humidade']) : null;
$pwm = isset($dados['pwm']) ? intval($dados['pwm']) : 0;
$modo = isset($dados['modo']) ? substr($dados['modo'], 0, 10) : 'AUTO';
$t_minima = isset($dados['t_minima']) ? floatval($dados['t_minima']) : null;
$t_maxima = isset($dados['t_maxima']) ? floatval($dados['t_maxima']) : null;

// Registo do endereço IP de origem
$ip = $_SERVER['REMOTE_ADDR'] ?? 'desconhecido';

try {
    $pdo = obterConexaoBD();

    $stmt = $pdo->prepare("
        INSERT INTO leituras_sensores (temperatura, humidade, valor_pwm, modo, t_minima, t_maxima, endereco_ip)
        VALUES (:temp, :hum, :pwm, :modo, :t_min, :t_max, :ip)
    ");

    $stmt->execute([
        ':temp' => $temperatura,
        ':hum' => $humidade,
        ':pwm' => $pwm,
        ':modo' => $modo,
        ':t_min' => $t_minima,
        ':t_max' => $t_maxima,
        ':ip' => $ip
    ]);

    $idInserido = $pdo->lastInsertId();

    echo json_encode([
        'sucesso' => true,
        'id' => $idInserido,
        'mensagem' => 'Leitura registada com sucesso'
    ]);
} catch (PDOException $e) {
    http_response_code(500);
    echo json_encode(['erro' => 'Erro na base de dados: ' . $e->getMessage()]);
}
