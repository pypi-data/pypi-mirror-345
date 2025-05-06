-- phpMyAdmin SQL Dump
-- version 5.1.1
-- https://www.phpmyadmin.net/
--
-- Host: localhost:3306
-- Generation Time: Apr 21, 2023 at 02:47 PM
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
-- Table structure for table `asigurari`
--
use heroku_6ed6d828b97b626;

CREATE TABLE `asigurari` (
  `id` int NOT NULL,
  `company` varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `name` varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `value` decimal(10,5) NOT NULL,
  `pay_day` int DEFAULT NULL,
  `valid_from` date NOT NULL,
  `valid_to` date DEFAULT NULL,
  `freq` int NOT NULL,
  `auto_ext` tinyint(1) DEFAULT NULL,
  `post_pay` tinyint(1) DEFAULT NULL,
  `myconto` varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `asigurari`
--

INSERT INTO `asigurari` (`id`, `company`, `name`, `value`, `pay_day`, `valid_from`, `valid_to`, `freq`, `auto_ext`, `post_pay`, `myconto`) VALUES
(2, 'Huk-Coburg', 'Auto-Versicherung', '-799.59000', 1, '2021-01-01', '2021-12-31', 12, 0, NULL, 'EC'),
(3, 'dieBayerische', 'Zahnzusatz-Versicherung', '-32.60000', 31, '2019-03-01', '2022-02-28', 1, 0, NULL, 'EC'),
(4, 'ADAC', 'ADAC-Membership', '-94.00000', 1, '2020-11-01', '2021-10-31', 12, 0, NULL, 'EC'),
(5, 'ADAC', 'ADAC-Reiserücktritts', '-88.70000', 1, '2021-07-28', '2022-07-27', 12, 0, NULL, 'EC'),
(6, 'VersicherungsKammerBayern', 'RisikoLebenVersicherung', '-19.31000', 31, '2018-09-01', NULL, 1, 1, NULL, 'EC'),
(7, 'Huk-Coburg', 'Privathaftpflichtversicherung', '-77.00000', 1, '2020-11-20', '2021-11-19', 12, 0, NULL, 'Siri&Radu'),
(8, 'VersicherungsKammerBayern', 'Rechtsschutzversicherung', '-277.20000', 1, '2020-07-16', '2023-07-16', 12, 1, NULL, 'Siri&Radu'),
(9, 'Huk-Coburg', 'Unfallversicherung', '-82.01000', 1, '2020-12-23', '2021-12-22', 12, 0, NULL, 'EC'),
(10, 'Huk-Coburg', 'Hausratversicherung', '-45.05000', 1, '2020-11-06', '2021-11-05', 12, 0, NULL, 'Siri&Radu'),
(15, 'ADAC', 'ADAC-Membership', '-94.00000', 1, '2021-11-01', '2022-10-31', 12, 1, NULL, 'DeutscheBank'),
(16, 'Huk-Coburg', 'Auto-Versicherung', '-660.60000', 1, '2022-01-01', '2022-12-31', 12, 1, NULL, 'DeutscheBank'),
(17, 'ADAC', 'ADAC-Reiserücktritts', '-88.70000', 1, '2022-07-28', NULL, 12, 1, NULL, 'Siri&Radu'),
(18, 'Huk-Coburg', 'Unfallversicherung', '-84.96000', 1, '2021-12-23', '2022-12-22', 12, 1, NULL, 'DeutscheBank'),
(21, 'Huk-Coburg', 'Hausratversicherung', '-45.05000', 1, '2021-11-06', '2022-11-05', 12, 1, NULL, 'Siri&Radu'),
(23, 'Huk-Coburg', 'Privathaftpflichtversicherung', '-77.00000', 1, '2021-11-20', '2022-11-19', 12, 1, NULL, 'Siri&Radu'),
(24, 'dieBayerische', 'Zahnzusatz-Versicherung', '-35.20000', 31, '2022-03-01', NULL, 1, 1, NULL, 'EC');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `asigurari`
--
ALTER TABLE `asigurari`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `asigurari`
--
ALTER TABLE `asigurari`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=25;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
