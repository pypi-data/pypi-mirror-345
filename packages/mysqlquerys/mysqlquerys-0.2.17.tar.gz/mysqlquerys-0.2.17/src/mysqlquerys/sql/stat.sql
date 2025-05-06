-- phpMyAdmin SQL Dump
-- version 5.1.1
-- https://www.phpmyadmin.net/
--
-- Host: localhost:3306
-- Generation Time: Apr 26, 2023 at 09:11 PM
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
-- Table structure for table `stat`
--

CREATE TABLE `stat` (
  `id` int NOT NULL,
  `documente_id` int NOT NULL DEFAULT '8',
  `name` varchar(50) NOT NULL,
  `valid_from` date NOT NULL,
  `valid_to` date DEFAULT NULL,
  `value` decimal(10,5) DEFAULT NULL,
  `pay_day` int DEFAULT NULL,
  `freq` int DEFAULT NULL,
  `myconto` varchar(50) DEFAULT NULL,
  `auto_ext` tinyint(1) DEFAULT NULL,
  `post_pay` tinyint(1) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `stat`
--

INSERT INTO `stat` (`id`, `documente_id`, `name`, `valid_from`, `valid_to`, `value`, `pay_day`, `freq`, `myconto`, `auto_ext`, `post_pay`) VALUES
(4, 8, 'LOHNSTEUERHILFE BAY.', '2021-01-01', '2021-12-31', '-242.00000', 1, 12, 'EC', 0, NULL),
(6, 8, 'Kfz-Steuer fuer M RA 8612', '2015-08-30', NULL, '-92.00000', 1, 12, 'EC', 1, NULL),
(8, 8, 'LOHNSTEUERHILFE BAY.', '2022-01-01', '2022-01-31', '-242.00000', 1, 12, 'DeutscheBank', 0, NULL),
(9, 8, 'LOHNSTEUERHILFE BAY.', '2023-01-01', '2023-12-31', '-380.00000', 1, 12, 'Siri&Radu', 1, NULL);

--
-- Indexes for dumped tables
--

--
-- Indexes for table `stat`
--
ALTER TABLE `stat`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `stat`
--
ALTER TABLE `stat`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=10;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
