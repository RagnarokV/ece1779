-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET SQL_SAFE_UPDATES = 0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='TRADITIONAL,ALLOW_INVALID_DATES';

-- -----------------------------------------------------
-- Schema ece1779_hw
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `ece1779_project` DEFAULT CHARACTER SET latin1 ;
USE `ece1779_project`;

-- -----------------------------------------------------
-- Table `ece1779_project`.`metrics`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `ece1779_project`.`metrics`;

CREATE TABLE IF NOT EXISTS `ece1779_project`.`metrics` (
  `recordid` INT NOT NULL AUTO_INCREMENT,
  `machineid` VARCHAR(50) NOT NULL,
  `timestamp` TEXT NOT NULL,
  `metric_name` TEXT NOT NULL,
  `metric_value` FLOAT NOT NULL,
  PRIMARY KEY (`recordid`)
)
DEFAULT CHARACTER SET = latin1;

CREATE USER 'user' IDENTIFIED BY 'your pass';
commit;

GRANT ALL ON ece1779_project.* TO 'ece1779_project';


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;

