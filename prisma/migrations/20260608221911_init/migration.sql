-- CreateTable
CREATE TABLE `User` (
    `id` INTEGER NOT NULL AUTO_INCREMENT,
    `email` VARCHAR(191) NOT NULL,
    `password` VARCHAR(191) NOT NULL,
    `name` VARCHAR(191) NULL,
    `role` VARCHAR(191) NOT NULL DEFAULT 'doctor',
    `createdAt` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `updatedAt` DATETIME(3) NOT NULL,

    UNIQUE INDEX `User_email_key`(`email`),
    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `Patient` (
    `id` INTEGER NOT NULL AUTO_INCREMENT,
    `nombre` VARCHAR(191) NOT NULL,
    `edad` INTEGER NOT NULL,
    `sexo` VARCHAR(191) NOT NULL,
    `createdAt` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `updatedAt` DATETIME(3) NOT NULL,

    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `Analysis` (
    `id` INTEGER NOT NULL AUTO_INCREMENT,
    `patientId` INTEGER NOT NULL,
    `tipoTest` VARCHAR(191) NOT NULL DEFAULT 'Podometría digital',
    `fecha` VARCHAR(191) NOT NULL,
    `completado` BOOLEAN NOT NULL DEFAULT false,
    `pdfUrl` TEXT NULL,
    `podometriaResult` JSON NULL,
    `podometriaDebugImg` LONGTEXT NULL,
    `podometriaHuella` LONGTEXT NULL,
    `frontalResult` JSON NULL,
    `frontalDebugImg` LONGTEXT NULL,
    `sagitalResult` JSON NULL,
    `sagitalDebugImg` LONGTEXT NULL,
    `miofascialResult` JSON NULL,
    `miofascialDebugImg` LONGTEXT NULL,
    `miofascialImagenOriginal` LONGTEXT NULL,
    `alineacionSagitalResult` JSON NULL,
    `alineacionSagitalDebugImg` LONGTEXT NULL,
    `alineacionFrontalResult` JSON NULL,
    `alineacionFrontalDebugImg` LONGTEXT NULL,
    `createdAt` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `updatedAt` DATETIME(3) NOT NULL,

    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- AddForeignKey
ALTER TABLE `Analysis` ADD CONSTRAINT `Analysis_patientId_fkey` FOREIGN KEY (`patientId`) REFERENCES `Patient`(`id`) ON DELETE CASCADE ON UPDATE CASCADE;
