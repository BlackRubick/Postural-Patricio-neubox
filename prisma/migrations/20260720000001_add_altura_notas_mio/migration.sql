-- AlterTable: add altura to Patient
ALTER TABLE `Patient` ADD COLUMN `altura` DOUBLE NULL;

-- AlterTable: add notas and miofascial images to Analysis
ALTER TABLE `Analysis` ADD COLUMN `notas` TEXT NULL;
ALTER TABLE `Analysis` ADD COLUMN `miofascialFrontalImg` LONGTEXT NULL;
ALTER TABLE `Analysis` ADD COLUMN `miofascialPosteriorImg` LONGTEXT NULL;
