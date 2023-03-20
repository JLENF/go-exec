USE `go-exec`;

DROP TABLE IF EXISTS `commands`;

CREATE TABLE `commands` (
  `id` int NOT NULL AUTO_INCREMENT,
  `id_server` int NOT NULL,
  `command` varchar(500) NOT NULL,
  `md5` varchar(100) NOT NULL,
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
) ENGINE=InnoDB;

/*Table structure for table `errors` */

DROP TABLE IF EXISTS `errors`;

CREATE TABLE `errors` (
  `id` int NOT NULL AUTO_INCREMENT,
  `hostname` varchar(250) DEFAULT NULL,
  `error` varchar(200) DEFAULT NULL,
  `datetime` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB;

/*Table structure for table `monitor` */

DROP TABLE IF EXISTS `monitor`;

CREATE TABLE `monitor` (
  `id` int NOT NULL AUTO_INCREMENT,
  `id_server` int DEFAULT NULL,
  `api_version` varchar(10) DEFAULT NULL,
  `last_seen` datetime DEFAULT NULL,
  `status_offline` tinyint(1) DEFAULT '0' COMMENT '1 = offline / 0 = online',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB;

/*Table structure for table `servers` */

DROP TABLE IF EXISTS `servers`;

CREATE TABLE `servers` (
  `id` int NOT NULL AUTO_INCREMENT,
  `hostname` varchar(250) NOT NULL,
  `auth_key` varchar(250) NOT NULL,
  `mac_address` varchar(100) DEFAULT NULL,
  `name` text,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  `deleted_at` datetime DEFAULT NULL,
  `active` int DEFAULT '0' COMMENT '0/1',
  `id_group` varchar(100) DEFAULT NULL,
  `id_subgroup` varchar(100) DEFAULT NULL,
  `registered_by` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB;
