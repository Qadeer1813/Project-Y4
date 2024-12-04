-- --------------------------------------------------------
-- Host:                         127.0.0.1
-- Server version:               11.6.2-MariaDB - mariadb.org binary distribution
-- Server OS:                    Win64
-- HeidiSQL Version:             12.8.0.6908
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;


-- Dumping database structure for ecms
CREATE DATABASE IF NOT EXISTS `ecms` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_uca1400_ai_ci */;
USE `ecms`;

-- Dumping structure for table ecms.patient_profile
CREATE TABLE IF NOT EXISTS `patient_profile` (
  `Patient_ID` int(11) NOT NULL AUTO_INCREMENT,
  `Name` varchar(50) NOT NULL,
  `DOB` date NOT NULL,
  `Contact_Number` varchar(255) NOT NULL DEFAULT '+353',
  `Email_Address` varchar(255) NOT NULL,
  `Home_Address` varchar(255) NOT NULL,
  `Next_Of_Kin_Name` varchar(255) NOT NULL,
  `Emergency_Contact_Number` varchar(255) NOT NULL,
  `Next_Of_Kin_Home_Address` varchar(255) NOT NULL,
  `Emergency_Email_Address` varchar(255) NOT NULL,
  PRIMARY KEY (`Patient_ID`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- Dumping data for table ecms.patient_profile: ~3 rows (approximately)
INSERT INTO `patient_profile` (`Patient_ID`, `Name`, `DOB`, `Contact_Number`, `Email_Address`, `Home_Address`, `Next_Of_Kin_Name`, `Emergency_Contact_Number`, `Next_Of_Kin_Home_Address`, `Emergency_Email_Address`) VALUES
	(1, 'John Doe', '2024-01-01', 'gAAAAABnUMaAmGYy-higgHAzMNy-KCZvAV04u9BClmwIGDuoyFpwpppFdo6VDC-8QcFOW1-pxtHZrzw3bJlmqYA7zPyh_9OC5g==', 'gAAAAABnUMaATtKOo34nXoVFubdqRZjuHX0lhnIPw2UHq1w02ifF7-j-NwUe0QdduHgIM-aX84NDE1Z6AlQbLn1I6kbnzKygcps71zlwqXimzVH8LIv49qo=', 'gAAAAABnUMaAkyLwbUcZQrSFl_NcMWHECRFfD5MvExleV7CLLbz63a6ESisWQeJZyd_6SpRwrWsvBnrzSQJNn3NsugW0vHhRnSU1ZIG4X5s7e_28lYew1h8=', 'gAAAAABnUMaAz9PWTSltuWuIVYj05FQsJQd8uWjdwkq8IUb-Rq7BFmRXfO37el6HJTrNyGidh-SeVJvT_SD6kqsl3Sx3q_SWdQ==', 'gAAAAABnUMaAdsQT0s5VysrnYkYpelrZmWbl5Fdi1DdJ8NBg_bdnPtqHzE3RvhhzoK1bbtxtq7w_oETnpon975X7YaplYIDwBQ==', 'gAAAAABnUMaAwyYyKGzj9dhMmcrMy0jZmTQHKhRzY7aSW1WJPDJkeJ9M2GHWminyt8OyQpCeRM4GlGOhbonsFXh8Ys61Gu8WEaVHikFmEQcE0R22XYUIQlU=', 'gAAAAABnUMaAiiuearScUc0Mt6mRISx8EqClY13VkWDmbnSu6IdfBhqkCQ3dZi0wOoxwnH75_BQR8kB7Mon79lb5zeBNfK5DKl3JiSQ8lt-WUyGYrxwzZs8='),
	(2, 'Joe Blogs', '2024-12-12', 'gAAAAABnUMaBpLlDyxzDLlv_UBY9a9usX8rA38tx8BPYHydL_dDg_gd4UV4UY0ktQKJ61he3QvyIyG48m8GnFLo5M0GzBRbxDg==', 'gAAAAABnUMaBxoC_EMDMn_p5MQMKyhGYg5WGEwTaYZFKcwP0Y9YXgq4b2DmzaSwm6_VCGXUc4h_7guKDE6rbwiBC-ozBvOKSu6QmjNkK1609F3FfPwI15RE=', 'gAAAAABnUMaBSXyM1jbOc-ZPrYaxcP4dRcAon8rM17op3nBu8RQOF5b7ByJf_FI51Mkhkw2bFtiqPjcC3x5w_2bVhzaPFXmoQ3OTWQ04I7j-pMfBkdxUTLE=', 'gAAAAABnUMaBQWz2Kn1rwMjQS-a4KsFw8MsCdcI31r9Xc54eUA-fNtnxJ9JSZ19Bcjz5ZLPPKR1juenWP7jydu0fPB8PefpZ0w==', 'gAAAAABnUMaBR8yddDRKOF6DaHxEEoJzRGbST0nv9aKUD_VQLMsvyo9Jp3QWUHRy2BME-W8oPR1r-X86W-7ulk86wdCXlhedWA==', 'gAAAAABnUMaBawnv3llLoLj5BDY7fS67h-iAgoc2-yoMQkE9pGikaVYHUIGdmQMcm8Dh0xDxlEuHVnlz3n3FZ91sOKAfSTyTwJUB1WTYFin5Og3DVdf-fhM=', 'gAAAAABnUMaB4dsg4EP6o3Rq0XeV1VxHrM6gDnYyuveJ5zAhCyjrYj3rrbfSzRwlG4aMSzexfZziBXBhGUJQlbP_RDrAlUjQ43_gPS7dzpAUBd8bMNC6XCI='),
	(3, 'Joe Blogs', '2023-01-01', 'gAAAAABnUMaDE4hSh_SNAz9IbP0B8dRo_0j0v4B1KP83RCulqNQiQxal5tohqblv12ZdCVfFm96cbFQ4OGlVsRFOHbR97Zz6ww==', 'gAAAAABnUMaDyBzNnRdpkDJ7w7IkTCV_lJ11d-vd3tGPmKLdoQtPiOtn7k_h7JdH2XUQeysnJxjRtWL3JfRMHWTcfdJTxqN-g-gj5SB5vDM4HV5FnSKe2Kc=', 'gAAAAABnUMaDKZEDUo4lL5eqXObgHTvfRI4xnFx18cS1eD43Snpmb6tL22DRSf9U2GUmHrq3HnFBh-yhO0SxBb5t4GnqgFaho9bNi-zS2vNgGSc9GvCMafk=', 'gAAAAABnUMaDcS_42rMUDg_w-v4O4T8zdahC0IQGMuH_o9nxKVE4hVy-611Bxk_3qXjY3sIuxoLLvAphutE3U7ddeSHMGbZLMQ==', 'gAAAAABnUMaDHawASnd5vaMSjtFQNGfJhJCwNYuaar5aafzk-KvMr2Gj-dKBJ6hScV2CDcFlz0OZcgOYarQg_FWg9oEDjdE5ww==', 'gAAAAABnUMaDZrfUjOAfk3DXH-JPBVUfzVPMbCBt5qRzSg18u69c3hp0-Scaz2rrfd-JpumWbnbiS7zqPQJaVzBXB1A1duPca4M893Y2UAtX9IVEUT1sJ64=', 'gAAAAABnUMaDzEEPsltgRFhhCkkDZRnbdi1wbQJRSISsWKZemTbZ7aMkR62C0qKK3vRh9BeIPHdQzOIVYhJ3SEOQjyo5asXzPKYjnI6NiyPzUZSOglnhAZ0=');

/*!40103 SET TIME_ZONE=IFNULL(@OLD_TIME_ZONE, 'system') */;
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;
