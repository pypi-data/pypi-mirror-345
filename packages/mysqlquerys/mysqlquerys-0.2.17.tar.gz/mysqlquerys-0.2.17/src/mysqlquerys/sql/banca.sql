-- phpMyAdmin SQL Dump
-- version 5.1.1
-- https://www.phpmyadmin.net/
--
-- Host: localhost:3306
-- Generation Time: Sep 11, 2023 at 10:21 AM
-- Server version: 8.0.22
-- PHP Version: 8.0.9

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;


CREATE TABLE `banca` (
  `id` int NOT NULL,
  `name` varchar(50) NOT NULL,
  `banca` varchar(50) NOT NULL,
  `valid_from` date NOT NULL,
  `valid_to` date DEFAULT NULL,
  `value` decimal(10,5) NOT NULL,
  `pay_day` int DEFAULT NULL,
  `freq` int NOT NULL,
  `myconto` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `banca`
--

INSERT INTO `banca` (`id`, `name`, `banca`, `valid_from`, `valid_to`, `value`, `pay_day`, `freq`, `myconto`) VALUES
(1, 'EC', 'Stadtsparkasse München', '2018-01-03', NULL, '0.00000', NULL, 12, 'EC'),
(2, 'Savings', 'Stadtsparkasse München', '2018-01-01', NULL, '0.00000', NULL, 1, ''),
(3, 'Siri&Radu', 'Stadtsparkasse München', '2019-01-01', NULL, '0.00000', NULL, 1, 'Siri&Radu'),
(4, 'Credit', 'Stadtsparkasse München', '2018-01-30', NULL, '0.00000', 31, 1, 'EC'),
(5, 'MasterCard', 'Stadtsparkasse München', '2018-01-01', NULL, '-29.00000', 1, 12, 'EC'),
(6, 'N26', 'N26', '2018-01-01', NULL, '0.00000', NULL, 1, ''),
(7, 'DeutscheBank', 'DeutscheBank', '2018-01-01', NULL, '0.00000', NULL, 1, '');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `banca`
--
ALTER TABLE `banca`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `banca`
--
ALTER TABLE `banca`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=10;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
