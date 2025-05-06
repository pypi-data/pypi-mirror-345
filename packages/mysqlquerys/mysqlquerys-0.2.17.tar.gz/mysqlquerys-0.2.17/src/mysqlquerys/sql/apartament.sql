-- phpMyAdmin SQL Dump
-- version 5.1.1
-- https://www.phpmyadmin.net/
--
-- Host: localhost:3306
-- Generation Time: Apr 21, 2023 at 02:46 PM
-- Server version: 8.0.22
-- PHP Version: 8.0.9

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `radu_test_db`
--

-- --------------------------------------------------------

--
-- Table structure for table `apartament`
--
use heroku_6ed6d828b97b626;

CREATE TABLE `apartament` (
  `id` int NOT NULL,
  `name` varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `valid_from` date NOT NULL,
  `valid_to` date DEFAULT NULL,
  `value` decimal(10,5) DEFAULT NULL,
  `pay_day` int DEFAULT NULL,
  `freq` int DEFAULT NULL,
  `auto_ext` tinyint(1) DEFAULT NULL,
  `post_pay` tinyint(1) DEFAULT NULL,
  `myconto` varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `apartament`
--

INSERT INTO `apartament` (`id`, `name`, `valid_from`, `valid_to`, `value`, `pay_day`, `freq`, `auto_ext`, `post_pay`, `myconto`) VALUES
(1, 'ARD-ZDF', '2019-05-15', NULL, '-52.50000', 15, 3, 1, NULL, 'Siri&Radu'),
(2, 'PYUR', '2017-11-08', '2022-02-28', '-28.00000', 31, 1, 0, NULL, 'Siri&Radu'),
(3, 'SWK', '2020-11-02', '2021-07-25', '-73.00000', 15, 1, 0, NULL, 'Siri&Radu'),
(4, 'SWK', '2021-07-25', '2022-07-25', '-49.00000', 15, 1, 0, NULL, 'Siri&Radu'),
(5, 'Miete_Königteinstr1', '2020-10-01', NULL, '-1110.00000', 30, 1, 1, NULL, 'Siri&Radu'),
(6, 'Chiria_Garaj', '2020-10-01', '2022-04-30', '-90.00000', 30, 1, 0, NULL, 'Siri&Radu'),
(7, 'Chiria_DachauerStr', '2017-11-01', '2020-11-15', '-992.00000', 30, 1, 0, NULL, 'EC'),
(8, 'Miete_Garage 4', '2022-05-31', NULL, '-45.00000', 31, 1, 1, NULL, 'Siri&Radu'),
(9, 'Miete_Thief_Garaj', '2022-05-01', NULL, '-80.00000', 30, 1, 1, NULL, 'Siri&Radu'),
(10, 'SWK', '2021-08-25', NULL, '-60.00000', 15, 1, 1, NULL, 'Siri&Radu'),
(11, 'PYUR', '2022-03-31', '2024-02-28', '-25.50000', 31, 1, 1, NULL, 'Siri&Radu');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `apartament`
--
ALTER TABLE `apartament`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `apartament`
--
ALTER TABLE `apartament`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=12;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
