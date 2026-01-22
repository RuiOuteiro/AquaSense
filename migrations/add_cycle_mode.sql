-- Adicionar campos para modo de ciclo de luz
-- luz_modo: 'manual', 'horario', 'ciclo', 'ai'
-- luz_ciclo_horas: duração do ciclo (4, 6, 8, 12, 16)
-- luz_ciclo_inicio: timestamp quando o ciclo foi activado

ALTER TABLE `configuracoes` 
ADD COLUMN `luz_modo` VARCHAR(20) DEFAULT 'horario' AFTER `luz_manual`,
ADD COLUMN `luz_ciclo_horas` INT DEFAULT 8 AFTER `luz_modo`,
ADD COLUMN `luz_ciclo_inicio` DATETIME DEFAULT NULL AFTER `luz_ciclo_horas`,
ADD COLUMN `luz_noturna_modo` VARCHAR(20) DEFAULT 'horario' AFTER `luz_noturna_manual`,
ADD COLUMN `luz_noturna_ciclo_horas` INT DEFAULT 8 AFTER `luz_noturna_modo`,
ADD COLUMN `luz_noturna_ciclo_inicio` DATETIME DEFAULT NULL AFTER `luz_noturna_ciclo_horas`,
ADD COLUMN `ai_ajuste_fotoperiodo` TINYINT(1) DEFAULT 0 AFTER `luz_noturna_minuto_desligar`,
ADD COLUMN `ai_fotoperiodo_sugerido` INT DEFAULT NULL AFTER `ai_ajuste_fotoperiodo`;

-- Migrar dados existentes
UPDATE `configuracoes` SET `luz_modo` = CASE 
  WHEN `luz_manual` = 1 THEN 'manual'
  ELSE 'horario'
END;

UPDATE `configuracoes` SET `luz_noturna_modo` = CASE 
  WHEN `luz_noturna_manual` = 1 THEN 'manual'
  ELSE 'horario'
END;
