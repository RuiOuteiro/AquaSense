-- MySQL dump 10.13  Distrib 8.0.42, for Linux (x86_64)
--
-- Host: 127.0.0.1    Database: esp32_data
-- ------------------------------------------------------
-- Server version	5.5.5-10.4.32-MariaDB

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `configuracoes`
--

--CREATE DATABASE IF NOT EXISTS
CREATE DATABASE IF NOT EXISTS esp32_data;
USE esp32_data;

DROP TABLE IF EXISTS `configuracoes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `configuracoes` (
  `id` int(11) NOT NULL DEFAULT 1,
  `modo_manual` tinyint(1) DEFAULT 0,
  `ventoinha_manual` tinyint(1) DEFAULT 0,
  `temp_ligar` decimal(5,2) DEFAULT 14.00,
  `temp_desligar` decimal(5,2) DEFAULT 13.00,
  `atualizado_em` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `luz_manual` tinyint(1) DEFAULT 0,
  `luz_modo` varchar(20) DEFAULT 'horario',
  `luz_ciclo_horas` int(11) DEFAULT 8,
  `luz_ciclo_inicio` datetime DEFAULT NULL,
  `luz_estado` tinyint(1) DEFAULT 0,
  `luz_hora` int(11) DEFAULT 8,
  `luz_minuto` int(11) DEFAULT 0,
  `fotoperiodo` int(11) DEFAULT 12,
  `luz_intensidade` int(11) DEFAULT 100,
  `luz_fade_speed` int(11) DEFAULT 10,
  `luz_hora_ligar` int(11) DEFAULT 8,
  `luz_minuto_ligar` int(11) DEFAULT 0,
  `luz_hora_desligar` int(11) DEFAULT 20,
  `luz_minuto_desligar` int(11) DEFAULT 0,
  `luz_noturna_manual` tinyint(1) DEFAULT 0,
  `luz_noturna_modo` varchar(20) DEFAULT 'horario',
  `luz_noturna_ciclo_horas` int(11) DEFAULT 8,
  `luz_noturna_ciclo_inicio` datetime DEFAULT NULL,
  `luz_noturna_estado` tinyint(1) DEFAULT 0,
  `luz_noturna_hora_ligar` int(11) DEFAULT 20,
  `luz_noturna_minuto_ligar` int(11) DEFAULT 0,
  `luz_noturna_hora_desligar` int(11) DEFAULT 8,
  `luz_noturna_minuto_desligar` int(11) DEFAULT 0,
  `ai_ajuste_fotoperiodo` tinyint(1) DEFAULT 0,
  `ai_fotoperiodo_sugerido` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `leituras_sensores`
--

DROP TABLE IF EXISTS `leituras_sensores`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `leituras_sensores` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `id_dispositivo` varchar(50) NOT NULL,
  `tipo_sensor` varchar(50) NOT NULL,
  `valor` decimal(10,4) NOT NULL,
  `unidade` varchar(20) DEFAULT NULL,
  `data_hora` timestamp NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `idx_dispositivo` (`id_dispositivo`),
  KEY `idx_data` (`data_hora`)
) ENGINE=InnoDB AUTO_INCREMENT=17602 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-01-22  3:09:12
