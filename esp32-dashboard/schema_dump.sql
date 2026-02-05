-- MariaDB dump 10.19  Distrib 10.4.32-MariaDB, for Linux (x86_64)
--
-- Host: localhost    Database: esp32_data
-- ------------------------------------------------------
-- Server version	10.4.32-MariaDB

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

DROP DATABASE IF EXISTS esp32_data;

CREATE DATABASE esp32_data;

USE esp32_data;

--
-- Table structure for table `alertas_config`
--

DROP TABLE IF EXISTS `alertas_config`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alertas_config` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `utilizador_id` int(11) NOT NULL,
  `enabled` tinyint(1) DEFAULT 1,
  `temp_min` decimal(5,2) DEFAULT 22.00,
  `temp_max` decimal(5,2) DEFAULT 28.00,
  `ph_min` decimal(4,2) DEFAULT 6.50,
  `ph_max` decimal(4,2) DEFAULT 7.50,
  `turbidez_max` decimal(5,2) DEFAULT 30.00,
  `humidade_min` decimal(5,2) DEFAULT 40.00,
  `humidade_max` decimal(5,2) DEFAULT 80.00,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `utilizador_id` (`utilizador_id`),
  CONSTRAINT `alertas_config_ibfk_1` FOREIGN KEY (`utilizador_id`) REFERENCES `utilizadores` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `aquarios`
--

DROP TABLE IF EXISTS `aquarios`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `aquarios` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `utilizador_id` int(11) NOT NULL,
  `nome` varchar(100) NOT NULL,
  `descricao` text DEFAULT NULL,
  `device_id` varchar(50) DEFAULT NULL COMMENT 'ID do ESP32 associado',
  `criado_em` timestamp NOT NULL DEFAULT current_timestamp(),
  `ativo` tinyint(1) DEFAULT 1,
  PRIMARY KEY (`id`),
  KEY `idx_utilizador` (`utilizador_id`),
  KEY `idx_device` (`device_id`),
  CONSTRAINT `aquarios_ibfk_1` FOREIGN KEY (`utilizador_id`) REFERENCES `utilizadores` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `configuracoes`
--

DROP TABLE IF EXISTS `configuracoes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `configuracoes` (
  `id` int(11) NOT NULL DEFAULT 1,
  `aquario_id` int(11) DEFAULT NULL,
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
  PRIMARY KEY (`id`),
  KEY `fk_config_aquario` (`aquario_id`),
  CONSTRAINT `fk_config_aquario` FOREIGN KEY (`aquario_id`) REFERENCES `aquarios` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `leituras_sensores`
--

DROP TABLE IF EXISTS `leituras_sensores`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `leituras_sensores` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `aquario_id` int(11) DEFAULT NULL,
  `id_dispositivo` varchar(50) NOT NULL,
  `tipo_sensor` varchar(50) NOT NULL,
  `valor` decimal(10,4) NOT NULL,
  `unidade` varchar(20) DEFAULT NULL,
  `data_hora` timestamp NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `idx_dispositivo` (`id_dispositivo`),
  KEY `idx_data` (`data_hora`),
  KEY `idx_aquario` (`aquario_id`),
  CONSTRAINT `fk_leituras_aquario` FOREIGN KEY (`aquario_id`) REFERENCES `aquarios` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=129002 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sessoes`
--

DROP TABLE IF EXISTS `sessoes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sessoes` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `utilizador_id` int(11) NOT NULL,
  `token_hash` varchar(255) NOT NULL,
  `expira_em` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `criado_em` timestamp NOT NULL DEFAULT current_timestamp(),
  `ip_address` varchar(45) DEFAULT NULL,
  `user_agent` text DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `utilizador_id` (`utilizador_id`),
  KEY `idx_token` (`token_hash`),
  KEY `idx_expira` (`expira_em`),
  CONSTRAINT `sessoes_ibfk_1` FOREIGN KEY (`utilizador_id`) REFERENCES `utilizadores` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `utilizadores`
--

DROP TABLE IF EXISTS `utilizadores`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `utilizadores` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `email` varchar(255) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `nome` varchar(100) NOT NULL,
  `criado_em` timestamp NOT NULL DEFAULT current_timestamp(),
  `ultimo_login` timestamp NULL DEFAULT NULL,
  `ativo` tinyint(1) DEFAULT 1,
  `telegram_chat_id` varchar(50) DEFAULT NULL,
  `telegram_alertas` tinyint(1) DEFAULT 1,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`),
  KEY `idx_email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Temporary table structure for view `v_estatisticas_aquario`
--

DROP TABLE IF EXISTS `v_estatisticas_aquario`;
/*!50001 DROP VIEW IF EXISTS `v_estatisticas_aquario`*/;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
/*!50001 CREATE VIEW `v_estatisticas_aquario` AS SELECT
 1 AS `aquario_id`,
  1 AS `aquario_nome`,
  1 AS `utilizador_id`,
  1 AS `total_leituras`,
  1 AS `ultima_leitura` */;
SET character_set_client = @saved_cs_client;

--
-- Temporary table structure for view `v_leituras_completas`
--

DROP TABLE IF EXISTS `v_leituras_completas`;
/*!50001 DROP VIEW IF EXISTS `v_leituras_completas`*/;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
/*!50001 CREATE VIEW `v_leituras_completas` AS SELECT
 1 AS `id`,
  1 AS `aquario_id`,
  1 AS `aquario_nome`,
  1 AS `utilizador_id`,
  1 AS `tipo_sensor`,
  1 AS `valor`,
  1 AS `unidade`,
  1 AS `data_hora` */;
SET character_set_client = @saved_cs_client;

--
-- Final view structure for view `v_estatisticas_aquario`
--

/*!50001 DROP VIEW IF EXISTS `v_estatisticas_aquario`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_general_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `v_estatisticas_aquario` AS select `a`.`id` AS `aquario_id`,`a`.`nome` AS `aquario_nome`,`a`.`utilizador_id` AS `utilizador_id`,count(`ls`.`id`) AS `total_leituras`,max(`ls`.`data_hora`) AS `ultima_leitura` from (`aquarios` `a` left join `leituras_sensores` `ls` on(`a`.`id` = `ls`.`aquario_id`)) group by `a`.`id`,`a`.`nome`,`a`.`utilizador_id` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `v_leituras_completas`
--

/*!50001 DROP VIEW IF EXISTS `v_leituras_completas`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_general_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `v_leituras_completas` AS select `ls`.`id` AS `id`,`ls`.`aquario_id` AS `aquario_id`,`a`.`nome` AS `aquario_nome`,`a`.`utilizador_id` AS `utilizador_id`,`ls`.`tipo_sensor` AS `tipo_sensor`,`ls`.`valor` AS `valor`,`ls`.`unidade` AS `unidade`,`ls`.`data_hora` AS `data_hora` from (`leituras_sensores` `ls` join `aquarios` `a` on(`ls`.`aquario_id` = `a`.`id`)) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-02-05  2:11:02
