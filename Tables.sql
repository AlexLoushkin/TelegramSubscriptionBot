CREATE TABLE `TelegramSubscribe` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `TelegramUserId` text NOT NULL,
  `NewsCategory` tinyint(4) unsigned NOT NULL,
  `KeyWord` tinytext,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=cp1251;

CREATE TABLE `NewsCategory` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `NewsCategoryId` tinyint(11) unsigned NOT NULL,
  `NewsCategoryTxt` text NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=cp1251;
