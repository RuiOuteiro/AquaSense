<?php

/**
 * AquaSense - Ficheiro de Configuração
 * Configuração da ligação à base de dados MySQL
 * 
 * @package AquaSense
 * @version 1.0.0
 */

// Configuração da Base de Dados
define('BD_HOST', 'localhost');
define('BD_PORTA', '3309');
define('BD_NOME', 'aquasense');
define('BD_UTILIZADOR', 'root');
define('BD_SENHA', '');

/**
 * Estabelece ligação à base de dados
 * 
 * @return PDO Objeto de ligação PDO
 */
function obterConexaoBD()
{
    $dsn = "mysql:host=" . BD_HOST . ";port=" . BD_PORTA . ";dbname=" . BD_NOME . ";charset=utf8mb4";

    try {
        $pdo = new PDO($dsn, BD_UTILIZADOR, BD_SENHA, [
            PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
            PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC
        ]);
        return $pdo;
    } catch (PDOException $e) {
        http_response_code(500);
        die(json_encode(['erro' => 'Falha na ligação à base de dados: ' . $e->getMessage()]));
    }
}

// Chave de autenticação da API
define('CHAVE_API', 'aquasense_chave_secreta_2024');
