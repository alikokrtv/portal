-- Duyuru hedefleme sistemi için tablolar

-- Duyuru hedefleme tablosu
CREATE TABLE IF NOT EXISTS announcement_targets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    announcement_id INT NOT NULL,
    target_type ENUM('department', 'user', 'role', 'all') NOT NULL,
    target_id INT NULL, -- department_id, user_id, role_id (all için NULL)
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (announcement_id) REFERENCES announcements(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Announcements tablosuna hedefleme kolonları ekle
ALTER TABLE announcements 
ADD COLUMN target_type ENUM('all', 'department', 'user', 'role') DEFAULT 'all' AFTER content,
ADD COLUMN target_departments TEXT NULL AFTER target_type,
ADD COLUMN target_users TEXT NULL AFTER target_departments,
ADD COLUMN target_roles TEXT NULL AFTER target_users;

-- Örnek hedefleme verileri
INSERT INTO announcement_targets (announcement_id, target_type, target_id) VALUES
(1, 'all', NULL), -- İlk duyuru herkese
(2, 'department', 1), -- İkinci duyuru sadece departman 1'e
(3, 'user', 1); -- Üçüncü duyuru sadece kullanıcı 1'e 