-- Günlük Menü Tablosu
CREATE TABLE IF NOT EXISTS daily_menu (
    id INT AUTO_INCREMENT PRIMARY KEY,
    menu_date DATE NOT NULL,
    day_name VARCHAR(20) NOT NULL,
    soup VARCHAR(255),
    main_dish VARCHAR(255),
    side_dish VARCHAR(255),
    dessert VARCHAR(255),
    drink VARCHAR(255),
    appetizer VARCHAR(255),
    extra_items TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY unique_date (menu_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Menü verilerini ekle
INSERT IGNORE INTO daily_menu (menu_date, day_name, soup, main_dish, side_dish, dessert, drink, appetizer) VALUES
('2025-07-24', 'Perşembe', 'BORSH ÇORBASI', 'ETLİ BEZELYE', 'TEL ŞEHRİYELİ BULGUR PİLAV', 'MEVSİM MEYVELERİ', 'GELENEKSEL LİMONATA', 'YAPRAK SARMA / DOLMA'),
('2025-07-25', 'Cuma', 'YÜKSÜK ÇORBASI', 'TAVUKLU KABAK SANDAL', 'TEREYAĞLI PİRİNÇ PİLAVI', 'TİRAMİSU', NULL, 'MEZE'),
('2025-07-26', 'Cumartesi', 'AYRAN AŞI ÇORBA', 'KÖRİ SOSLU TAVUK', 'SALÇALI MAKARNA', 'MEYVE', NULL, NULL),
('2025-07-28', 'Pazartesi', 'MENGEN ÇORBASI', 'PİZZA', NULL, NULL, 'GAZLI İÇECEK', NULL),
('2025-07-29', 'Salı', 'ENGİNAR ÇORBASI', 'ETLİ TAZE FASULYE', 'ÖZBEK PİLAVI', 'MEVSİM MEYVELERİ', 'GELENEKSEL LİMONATA', 'YOĞURTLU MEZE'),
('2025-07-30', 'Çarşamba', 'ŞAFAK ÇORBA', 'ÇITIR TAVUK', 'SÜLEYMANİYE PİLAV', NULL, 'GELENEKSEL AYRAN', 'ÇOBAN SALATA'),
('2025-07-31', 'Perşembe', 'KÖZ PATLICAN ÇORBASI', 'ETLİ NOHUT TAVA', 'PİRİNÇ PİLAVI', NULL, NULL, 'TURŞU + MEZE'); 