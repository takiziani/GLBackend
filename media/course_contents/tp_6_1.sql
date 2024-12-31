-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Hôte : 127.0.0.1:3306
-- Généré le : mer. 04 déc. 2024 à 22:08
-- Version du serveur : 8.3.0
-- Version de PHP : 8.2.18

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de données : `tp_6`
--

-- --------------------------------------------------------

--
-- Structure de la table `author`
--

DROP TABLE IF EXISTS `author`;
CREATE TABLE IF NOT EXISTS `author` (
  `authorID` int NOT NULL AUTO_INCREMENT,
  `authorName` varchar(255) NOT NULL,
  `email` varchar(255) DEFAULT NULL,
  `age` int DEFAULT NULL,
  `country` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`authorID`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Déchargement des données de la table `author`
--

INSERT INTO `author` (`authorID`, `authorName`, `email`, `age`, `country`) VALUES
(1, 'Albert Camus', 'camus@example.com', 46, 'Algeria'),
(2, 'Kateb Yacine', 'kateb@example.com', 72, 'Algeria'),
(3, 'Yasmina Khadra', 'khadra@example.com', 68, 'Algeria'),
(4, 'Assia Djebar', 'djebar@example.com', 78, 'Algeria'),
(5, 'Mouloud Mammeri', 'mammeri@example.com', 64, 'Algeria');

-- --------------------------------------------------------

--
-- Structure de la table `book`
--

DROP TABLE IF EXISTS `book`;
CREATE TABLE IF NOT EXISTS `book` (
  `ISBN` varchar(13) NOT NULL,
  `title` varchar(255) NOT NULL,
  `publisherID` int NOT NULL,
  `publicationDate` date NOT NULL,
  `genre` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`ISBN`),
  KEY `publisherID` (`publisherID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Déchargement des données de la table `book`
--

INSERT INTO `book` (`ISBN`, `title`, `publisherID`, `publicationDate`, `genre`) VALUES
('9781122334455', 'Ce que le jour doit à la nuit', 3, '2008-01-01', 'Fiction'),
('9781122334456', 'Les Hirondelles de Kaboul', 3, '2002-01-01', 'Fiction'),
('9781122334457', 'L\'Attentat', 3, '2005-01-01', 'Fiction'),
('9781122334458', 'Vaste est la prison', 2, '1995-01-01', 'Fiction'),
('9781122334459', 'Le Blanc de l\'Algérie', 2, '1996-01-01', 'Historical'),
('9781122334460', 'La Colline oubliée', 2, '1952-01-01', 'Fiction'),
('9781122334461', 'L\'Opium et le Bâton', 2, '1965-01-01', 'Historical'),
('9781234567897', 'L\'Étranger', 1, '1942-01-01', 'Fiction'),
('9781234567898', 'Le Mythe de Sisyphe', 1, '1942-10-01', 'Essay'),
('9781234567899', 'La Peste', 1, '1947-06-01', 'Fiction'),
('9789876543210', 'Nedjma', 2, '1956-01-01', 'Novel'),
('9789876543211', 'Le Polygone étoilé', 2, '1966-01-01', 'Novel');

-- --------------------------------------------------------

--
-- Structure de la table `bookloans`
--

DROP TABLE IF EXISTS `bookloans`;
CREATE TABLE IF NOT EXISTS `bookloans` (
  `loanID` int NOT NULL AUTO_INCREMENT,
  `ISBN` varchar(13) DEFAULT NULL,
  `memberID` int DEFAULT NULL,
  `borrowDate` date NOT NULL,
  `returnDate` date DEFAULT NULL,
  `dueDate` date NOT NULL,
  PRIMARY KEY (`loanID`),
  KEY `ISBN` (`ISBN`),
  KEY `memberID` (`memberID`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Déchargement des données de la table `bookloans`
--

INSERT INTO `bookloans` (`loanID`, `ISBN`, `memberID`, `borrowDate`, `returnDate`, `dueDate`) VALUES
(1, '9781234567897', 1, '2024-10-10', '2024-10-20', '2024-10-15'),
(2, '9781234567897', 2, '2024-11-01', NULL, '2024-11-15'),
(3, '9789876543210', 3, '2024-09-10', '2024-09-20', '2024-09-15'),
(4, '9781122334461', 2, '2024-10-05', '2024-10-12', '2024-10-10'),
(5, '9781122334456', 1, '2024-08-15', '2024-08-20', '2024-08-18'),
(6, '9781234567899', 2, '2024-07-01', NULL, '2024-07-15');

-- --------------------------------------------------------

--
-- Structure de la table `member`
--

DROP TABLE IF EXISTS `member`;
CREATE TABLE IF NOT EXISTS `member` (
  `memberID` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `email` varchar(255) DEFAULT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `address` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`memberID`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Déchargement des données de la table `member`
--

INSERT INTO `member` (`memberID`, `name`, `email`, `phone`, `address`) VALUES
(1, 'Ahmed Ben Ali', 'ahmed@example.com', '+213661234567', 'Algiers'),
(2, 'Fatima Zohra', 'fatima@example.com', '+213550987654', 'Oran'),
(3, 'Mohamed Salah', 'mohamed@example.com', '+213770123456', 'Constantine'),
(4, 'Amina Berrah', 'amina@example.com', '+213660987123', 'Tlemcen');

-- --------------------------------------------------------

--
-- Structure de la table `publisher`
--

DROP TABLE IF EXISTS `publisher`;
CREATE TABLE IF NOT EXISTS `publisher` (
  `publisherID` int NOT NULL AUTO_INCREMENT,
  `publisherName` varchar(255) NOT NULL,
  `foundationYear` int DEFAULT NULL,
  `website` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`publisherID`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Déchargement des données de la table `publisher`
--

INSERT INTO `publisher` (`publisherID`, `publisherName`, `foundationYear`, `website`) VALUES
(1, 'Éditions Gallimard', 1911, 'gallimard.fr'),
(2, 'SNED', 1962, 'sned-algerie.dz'),
(3, 'Casbah Editions', 1995, 'casbah-editions.com');

-- --------------------------------------------------------

--
-- Structure de la table `writtenby`
--

DROP TABLE IF EXISTS `writtenby`;
CREATE TABLE IF NOT EXISTS `writtenby` (
  `ISBN` varchar(13) NOT NULL,
  `authorID` int NOT NULL,
  PRIMARY KEY (`ISBN`,`authorID`),
  KEY `authorID` (`authorID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Déchargement des données de la table `writtenby`
--

INSERT INTO `writtenby` (`ISBN`, `authorID`) VALUES
('9781234567897', 1),
('9781234567898', 1),
('9781234567899', 1),
('9789876543210', 2),
('9789876543211', 2),
('9781122334455', 3),
('9781122334456', 3),
('9781122334457', 3),
('9781122334458', 4),
('9781122334459', 4),
('9781122334460', 5),
('9781122334461', 5);

--
-- Contraintes pour les tables déchargées
--

--
-- Contraintes pour la table `book`
--
ALTER TABLE `book`
  ADD CONSTRAINT `book_ibfk_1` FOREIGN KEY (`publisherID`) REFERENCES `publisher` (`publisherID`);

--
-- Contraintes pour la table `bookloans`
--
ALTER TABLE `bookloans`
  ADD CONSTRAINT `bookloans_ibfk_1` FOREIGN KEY (`ISBN`) REFERENCES `book` (`ISBN`),
  ADD CONSTRAINT `bookloans_ibfk_2` FOREIGN KEY (`memberID`) REFERENCES `member` (`memberID`);

--
-- Contraintes pour la table `writtenby`
--
ALTER TABLE `writtenby`
  ADD CONSTRAINT `writtenby_ibfk_1` FOREIGN KEY (`ISBN`) REFERENCES `book` (`ISBN`),
  ADD CONSTRAINT `writtenby_ibfk_2` FOREIGN KEY (`authorID`) REFERENCES `author` (`authorID`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
