/*
SQLyog Community v13.2.0 (64 bit)
MySQL - 8.0.32 : Database - go-exec
*********************************************************************
*/

/*!40101 SET NAMES utf8 */;

/*!40101 SET SQL_MODE=''*/;

/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
CREATE DATABASE /*!32312 IF NOT EXISTS*/`go-exec` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;

USE `go-exec`;

/*Table structure for table `commands` */

DROP TABLE IF EXISTS `commands`;

CREATE TABLE `commands` (
  `id` int NOT NULL AUTO_INCREMENT,
  `id_server` int NOT NULL,
  `command` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `md5` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `timeout` int NOT NULL,
  `bash` tinyint(1) NOT NULL,
  `process` tinyint(1) NOT NULL,
  `relative_exec` int DEFAULT NULL COMMENT 'depends on sucess execution?',
  `relative_retry` int DEFAULT '3' COMMENT 'number of retry waiting executed_at',
  `relative_retried` int DEFAULT '0' COMMENT 'count of errors retried',
  `created_at` datetime DEFAULT NULL,
  `downloaded_at` datetime DEFAULT NULL,
  `executed_at` datetime DEFAULT NULL,
  `stdout` text,
  `stderr` text,
  `exitcode` varchar(10) DEFAULT NULL,
  `duration` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

/*Table structure for table `errors` */

DROP TABLE IF EXISTS `errors`;

CREATE TABLE `errors` (
  `id` int NOT NULL AUTO_INCREMENT,
  `hostname` varchar(250) DEFAULT NULL,
  `error` varchar(200) DEFAULT NULL,
  `datetime` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

/*Table structure for table `monitor` */

DROP TABLE IF EXISTS `monitor`;

CREATE TABLE `monitor` (
  `id` int NOT NULL AUTO_INCREMENT,
  `id_server` int DEFAULT NULL,
  `api_version` varchar(10) DEFAULT NULL,
  `last_seen` datetime DEFAULT NULL,
  `status_offline` tinyint(1) DEFAULT '0' COMMENT '1 = offline / 0 = online',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

/*Table structure for table `servers` */

DROP TABLE IF EXISTS `servers`;

CREATE TABLE `servers` (
  `id` int NOT NULL AUTO_INCREMENT,
  `hostname` varchar(250) NOT NULL,
  `auth_key` varchar(250) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `mac_address` varchar(100) DEFAULT NULL,
  `name` text,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  `deleted_at` datetime DEFAULT NULL,
  `active` int DEFAULT '0' COMMENT '0/1',
  `id_group` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `id_subgroup` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `registered_by` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
