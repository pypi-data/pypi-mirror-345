-- phpMyAdmin SQL Dump
-- version 5.1.1
-- https://www.phpmyadmin.net/
--
-- Host: localhost:3306
-- Generation Time: Apr 21, 2023 at 02:48 PM
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
-- Table structure for table `expenses`
--
use heroku_6ed6d828b97b626;

CREATE TABLE `expenses` (
  `id` int NOT NULL,
  `name` varchar(50) NOT NULL,
  `valid_from` date NOT NULL,
  `valid_to` date DEFAULT NULL,
  `freq` int NOT NULL,
  `auto_ext` tinyint(1) DEFAULT NULL,
  `post_pay` tinyint(1) DEFAULT NULL,
  `value` decimal(10,5) NOT NULL,
  `pay_day` int DEFAULT NULL,
  `myconto` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `expenses`
--

INSERT INTO `expenses` (`id`, `name`, `valid_from`, `valid_to`, `freq`, `auto_ext`, `post_pay`, `value`, `pay_day`, `myconto`) VALUES
(2, 'MasterCard', '2020-10-05', NULL, 1, 1, NULL, '0.00000', 4, 'EC'),
(5, 'CartelaPrepaid', '2020-10-15', NULL, 2, 1, NULL, '-15.00000', 15, 'EC'),
(6, 'Siri&Radu_ENTGELTABSCHLUSS', '2021-01-30', NULL, 1, 1, NULL, '-5.24000', 31, 'Siri&Radu'),
(7, 'EC_ENTGELTABSCHLUSS', '2021-01-30', NULL, 1, 1, NULL, '-2.25000', 31, 'EC'),
(8, 'ExtraCredit', '2021-01-30', NULL, 1, 1, NULL, '-600.00000', 5, 'EC'),
(9, 'cash', '2021-01-30', NULL, 1, NULL, NULL, '0.00000', NULL, 'EC'),
(10, 'Credit', '2021-01-30', NULL, 1, 1, NULL, '-532.00000', 30, 'EC'),
(11, 'CreditMasina', '2022-02-01', NULL, 1, 1, NULL, '-138.60000', 1, 'EC'),
(12, 'Cresa_Enya', '2023-01-01', NULL, 1, 1, NULL, '-335.00000', 1, 'Siri&Radu'),
(13, 'Kaution_Cresa_Enya', '2023-01-01', '2023-01-31', 36, NULL, NULL, '-750.00000', 1, 'Siri&Radu'),
(14, 'Spotify', '2022-12-09', NULL, 1, 1, NULL, '-14.99000', 1, 'N26'),
(15, 'Netflix', '2022-12-09', NULL, 1, 1, NULL, '-11.99000', 1, 'N26');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `expenses`
--
ALTER TABLE `expenses`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `expenses`
--
ALTER TABLE `expenses`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=16;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
