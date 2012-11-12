DROP TABLE IF EXISTS `users`; -- Dropping the tables to create them again, with IF NOT EXISTS?
DROP TABLE IF EXISTS `apps`;  -- I know, I'm totally crazy!
DROP TABLE IF EXISTS `licenses`;

CREATE TABLE IF NOT EXISTS `users` ( -- People who can login.
`id` INTEGER PRIMARY KEY,
`login` varchar(32) NOT NULL,
`username` varchar(32) NOT NULL,
`password` varchar(64) NOT NULL, -- sha256() of hashed password.
`email` text NOT NULL
);

CREATE TABLE IF NOT EXISTS `apps` ( -- Application list.
`id` INTEGER PRIMARY KEY,
`name` varchar(64) NOT NULL,		-- The display name of the app.
`language` varchar(32), 			-- Optionally, what language is it written in?
`active` tinyint(1) NOT NULL DEFAULT '1',	-- Is the app enabled? This more-or-less disables all keys for the app.
`version` int(10) NOT NULL DEFAULT '0'		-- Unix timestamp of the last version push.
);

CREATE TABLE IF NOT EXISTS `licenses` ( -- License list.
`id` INTEGER PRIMARY KEY,
`app` int NOT NULL DEFAULT '0', -- What app is it for?
`user` varchar(64) NOT NULL, 	-- Who is it for?
`email` varchar(64) NOT NULL,	-- What's their email? (If applicable)
`key` varchar(64) NOT NULL, 	-- The key: WWWW-XXXX-YYYY-ZZZZ
`needs_hwid` tinyint(1) NOT NULL DEFAULT '0',--Do we require a HWID match to use this key?
`hwid` varchar(64) NOT NULL,				-- If we need a HWID, what is it?
`disabled` tinyint(1) NOT NULL DEFAULT '0', -- Is the key disabled?
`expires` int(10) NOT NULL DEFAULT '0', 	-- Unix timestamp of expiration date, or 0 for never.
`last_use` int(10) NOT NULL DEFAULT '0',	-- Unix timestamp of the last use of the key.
`aban` tinyint(1) NOT NULL DEFAULT '0'		-- NOT IMPLEMENTED - Should users of this key automatically get an IP ban?
);
