/*
Navicat MySQL Data Transfer

Source Server         : localhost
Source Server Version : 50717
Source Host           : 127.0.0.1:3306
Source Database       : aiops

Target Server Type    : MYSQL
Target Server Version : 50717
File Encoding         : 65001

Date: 2019-06-06 15:57:18
*/

CREATE DATABASE IF NOT EXISTS aiops default charset utf8 COLLATE utf8_general_ci;

use aiops;

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for `file2uuid`
-- ----------------------------
DROP TABLE IF EXISTS `file2uuid`;
CREATE TABLE `file2uuid` (
  `file_name` char(255) NOT NULL COMMENT '上传的文件名，用文件名的形式易于查看',
  `uuid` char(255) NOT NULL COMMENT '文件对应的uuid',
  PRIMARY KEY (`file_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


-- ----------------------------
-- Table structure for `lstm_model`
-- ----------------------------
DROP TABLE IF EXISTS `lstm_model`;
CREATE TABLE `lstm_model` (
  `file_name` char(255) NOT NULL,
  `model_name` char(255) NOT NULL,
  `rmse` float DEFAULT '0' COMMENT '衡量模型好坏',
  `lasted_predict` timestamp NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  `predict_value` varchar(1024) DEFAULT NULL,
  `created_time` timestamp NULL DEFAULT NULL,
  `lasted_update` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`file_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


-- ----------------------------
-- Table structure for `model`
-- ----------------------------
DROP TABLE IF EXISTS `model`;
CREATE TABLE `model` (
  `file_name` char(255) NOT NULL,
  `model_name` char(255) NOT NULL,
  `precision` float DEFAULT '0',
  `recall` float DEFAULT '0',
  `f1` float DEFAULT '0' COMMENT '精确率和召回率调和',
  `trained` bigint(20) DEFAULT NULL,
  `finished` tinyint(4) DEFAULT '0',
  `changed` tinyint(4) DEFAULT '0' COMMENT '是否重新更新了数据需要重新训练',
  `created_time` timestamp NULL DEFAULT NULL,
  `lasted_update` timestamp NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`file_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;



-- ----------------------------
-- Table structure for `abnormal_list`
-- ----------------------------
DROP TABLE IF EXISTS `abnormal_list`;
CREATE TABLE `abnormal_list` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `model_name` varchar(255) NOT NULL,
  `time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `value` float NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=25 DEFAULT CHARSET=utf8;
