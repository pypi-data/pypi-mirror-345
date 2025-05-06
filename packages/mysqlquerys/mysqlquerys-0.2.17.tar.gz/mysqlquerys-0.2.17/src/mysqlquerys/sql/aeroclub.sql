-- phpMyAdmin SQL Dump
-- version 5.1.1
-- https://www.phpmyadmin.net/
--
-- Host: localhost:3306
-- Generation Time: Apr 21, 2023 at 02:44 PM
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
-- Table structure for table `aeroclub`
--

use heroku_6ed6d828b97b626;

CREATE TABLE `aeroclub` (
  `id` int NOT NULL,
  `name` varchar(50) NOT NULL,
  `valid_from` date NOT NULL,
  `valid_to` date DEFAULT NULL,
  `value` decimal(10,5) DEFAULT NULL,
  `pay_day` int DEFAULT NULL,
  `freq` int DEFAULT NULL,
  `auto_ext` tinyint(1) DEFAULT NULL,
  `post_pay` tinyint(1) DEFAULT NULL,
  `myconto` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `aeroclub`
--

INSERT INTO `aeroclub` (`id`, `name`, `valid_from`, `valid_to`, `value`, `pay_day`, `freq`, `auto_ext`, `post_pay`, `myconto`) VALUES
(12, 'BE_Jahresbeitrag', '2018-02-22', '2021-08-17', '-439.30000', 1, 12, 0, NULL, 'EC'),
(14, 'BE_Jahresbeitrag', '2021-07-01', NULL, '-185.58000', 1, 12, 1, NULL, 'DeutscheBank'),
(19, 'BE_ Qabrechnung', '2021-04-01', '2021-06-30', '-232.33000', 1, 12, 0, NULL, 'EC'),
(20, 'BE_ Qabrechnung', '2021-10-01', '2022-01-31', '-110.50000', 1, 3, 0, 1, 'DeutscheBank');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `aeroclub`
--
ALTER TABLE `aeroclub`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `aeroclub`
--
ALTER TABLE `aeroclub`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=21;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
