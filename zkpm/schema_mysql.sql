DROP TABLE IF EXISTS `users`
DROP TABLE IF EXISTS `apps`
DROP TABLE IF EXISTS `licenses`
CREATE TABLE IF NOT EXISTS `users` (`id` int NOT NULL AUTO_INCREMENT, `login` varchar(32) NOT NULL, `username` varchar(32) NOT NULL, `password` varchar(64) NOT NULL, `email` text NOT NULL, PRIMARY KEY (`id`))
CREATE TABLE IF NOT EXISTS `apps` (`id` int NOT NULL AUTO_INCREMENT, `name` varchar(64) NOT NULL, `language` varchar(32), `active` tinyint(1) NOT NULL DEFAULT '1', `version` int(10) NOT NULL DEFAULT '0', PRIMARY KEY (`id`))
CREATE TABLE IF NOT EXISTS `licenses` (`id` int NOT NULL AUTO_INCREMENT, `app` int NOT NULL DEFAULT '0', `user` varchar(64) NOT NULL, `key` varchar(64) NOT NULL, `needs_hwid` tinyint(1) NOT NULL DEFAULT '0', `hwid` varchar(64) NOT NULL, `disabled` tinyint(1) NOT NULL DEFAULT '0', `expires` int(10) NOT NULL DEFAULT '0', `last_use` int(10) NOT NULL DEFAULT '0', `aban` tinyint(1) NOT NULL DEFAULT '0', PRIMARY KEY (`id`))
