-- phpMyAdmin SQL Dump
-- version 5.1.1
-- https://www.phpmyadmin.net/
--
-- Host: localhost:3306
-- Generation Time: Apr 21, 2023 at 02:49 PM
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
-- Table structure for table `income`
--
use heroku_6ed6d828b97b626;

CREATE TABLE `income` (
  `id` int NOT NULL,
  `company` varchar(50) NOT NULL,
  `name` varchar(50) NOT NULL,
  `valid_from` date NOT NULL,
  `valid_to` date DEFAULT NULL,
  `value` decimal(10,5) NOT NULL,
  `pay_day` int DEFAULT NULL,
  `freq` int NOT NULL,
  `myconto` varchar(50) NOT NULL,
  `auto_ext` tinyint(1) DEFAULT NULL,
  `post_pay` tinyint(1) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `income`
--

INSERT INTO `income` (`id`, `company`, `name`, `valid_from`, `valid_to`, `value`, `pay_day`, `freq`, `myconto`, `auto_ext`, `post_pay`) VALUES
(1, 'MTU-AeroEngines', 'Salariu', '2019-08-01', '2023-06-30', '4334.67000', 30, 1, 'EC', 0, NULL),
(7, 'MTU-AeroEngines', 'T-Geld', '2022-02-27', NULL, '603.71000', 30, 12, 'EC', 0, NULL),
(8, 'MTU-AeroEngines', 'ErfolgsBeteiligung', '2022-04-30', NULL, '1859.43000', 30, 12, 'EC', 0, NULL),
(9, 'MTU-AeroEngines', 'UrlaubsGeld', '2019-06-30', NULL, '2296.72000', 30, 12, 'EC', 1, NULL),
(10, 'MTU-AeroEngines', 'T-Geld B', '2022-07-30', NULL, '1539.46000', 30, 12, 'EC', 1, NULL),
(11, 'MTU-AeroEngines', 'Weinachtsgeld', '2019-11-30', NULL, '1840.66000', 30, 12, 'EC', 1, NULL),
(12, 'MTU-AeroEngines', 'MitarbeiterAktienProgram', '2022-05-01', NULL, '565.27000', 30, 12, 'EC', 1, NULL),
(13, 'StadtMünchen', 'KinderGeld', '2022-01-15', '2040-01-15', '219.00000', 15, 1, 'Siri_Radu', 1, NULL),
(14, 'StadtMünchen', 'FamilienGeld', '2023-01-15', '2023-09-14', '250.00000', 15, 1, 'Siri_Radu', 1, NULL),
(15, 'MTU-AeroEngines', 'Inflationsausgleichprämie', '2023-01-31', NULL, '1500.00000', 30, 1, 'EC', NULL, NULL),
(16, 'MTU-AeroEngines', 'Salariu', '2023-06-01', NULL, '4421.15000', 30, 1, 'EC', 1, NULL);

--
-- Indexes for dumped tables
--

--
-- Indexes for table `income`
--
ALTER TABLE `income`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `income`
--
ALTER TABLE `income`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=17;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
