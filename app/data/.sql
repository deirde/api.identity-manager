--------------------------------------------------------------------------------
--------------------------------SQLITE DUMP-------------------------------------
--------------------------------------------------------------------------------

CREATE TABLE `ban` (
    `id`	INTEGER PRIMARY KEY AUTOINCREMENT,
    `insert_date`	INTEGER,
    `last_update_date`	INTEGER,
    `signature`	TEXT,
    `counter`	INTEGER,
    `is_banned`	INTEGER
);

CREATE TABLE `default` (
    `id`	INTEGER PRIMARY KEY AUTOINCREMENT,
    `insert_date`	INTEGER,
    `last_update_date`	INTEGER,
    `name`	TEXT,
    `secret`	TEXT,
    `limit`	TEXT,
    `log`	TEXT
);

--------------------------------------------------------------------------------
---------------------------------MYSQL DUMP-------------------------------------
--------------------------------------------------------------------------------

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `account_webforyou_cloud`
--

-- --------------------------------------------------------

--
-- Table structure for table `history`
--

CREATE TABLE `history` (
  `id` int(11) NOT NULL,
  `insert_date` int(11) NOT NULL,
  `user__id` int(11) NOT NULL,
  `meta` varchar(64) NOT NULL,
  `value` varchar(155) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `registry`
--

CREATE TABLE `registry` (
  `id` int(11) NOT NULL,
  `insert_date` int(11) NOT NULL,
  `last_update_date` int(11) NOT NULL,
  `user__id` int(11) NOT NULL,
  `name` varchar(155) DEFAULT NULL,
  `bio` text,
  `url` varchar(128) DEFAULT NULL,
  `company` varchar(128) DEFAULT NULL,
  `location` varchar(256) DEFAULT NULL,
  `email` varchar(128) DEFAULT NULL,
  `opt_in_email` tinyint(1) NOT NULL DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `insert_date` int(11) NOT NULL,
  `last_update_date` int(11) NOT NULL,
  `email` varchar(64) NOT NULL,
  `password` varchar(155) NOT NULL,
  `is_active` tinyint(1) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `history`
--
ALTER TABLE `history`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user__id` (`user__id`);

--
-- Indexes for table `registry`
--
ALTER TABLE `registry`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user__id` (`user__id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `email` (`email`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `history`
--
ALTER TABLE `history`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=21;
--
-- AUTO_INCREMENT for table `registry`
--
ALTER TABLE `registry`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;
--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;
--
-- Constraints for dumped tables
--

--
-- Constraints for table `history`
--
ALTER TABLE `history`
  ADD CONSTRAINT `history__user__id` FOREIGN KEY (`user__id`) REFERENCES `users` (`id`) ON UPDATE CASCADE;

--
-- Constraints for table `registry`
--
ALTER TABLE `registry`
  ADD CONSTRAINT `registry__user__id` FOREIGN KEY (`user__id`) REFERENCES `users` (`id`) ON UPDATE CASCADE;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
