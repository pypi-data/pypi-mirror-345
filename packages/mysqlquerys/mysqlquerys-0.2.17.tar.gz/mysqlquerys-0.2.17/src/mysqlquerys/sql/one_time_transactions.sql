-- phpMyAdmin SQL Dump
-- version 5.1.1
-- https://www.phpmyadmin.net/
--
-- Host: localhost:3306
-- Generation Time: Sep 11, 2023 at 10:17 AM
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
-- Database: `cheltuieli`
--

-- --------------------------------------------------------

--
-- Table structure for table `one_time_transactions`
--

CREATE TABLE `one_time_transactions` (
  `id` int NOT NULL,
  `name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `value` decimal(10,5) NOT NULL,
  `myconto` varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `freq` int NOT NULL DEFAULT '1',
  `pay_day` int NOT NULL DEFAULT '1',
  `valid_from` date NOT NULL,
  `valid_to` date NOT NULL,
  `auto_ext` smallint DEFAULT NULL,
  `post_pay` int DEFAULT NULL,
  `identification` json DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `one_time_transactions`
--

INSERT INTO `one_time_transactions` (`id`, `name`, `value`, `myconto`, `freq`, `pay_day`, `valid_from`, `valid_to`, `auto_ext`, `post_pay`, `identification`) VALUES
(1, 'Steuererklärung_2022', '-2796.00000', 'Siri&Radu', 999, 15, '2023-09-15', '2023-09-15', NULL, NULL, NULL);

--
-- Indexes for dumped tables
--

--
-- Indexes for table `one_time_transactions`
--
ALTER TABLE `one_time_transactions`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `one_time_transactions`
--
ALTER TABLE `one_time_transactions`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
