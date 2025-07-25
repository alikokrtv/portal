-- Gelişmiş Toplantı Odası Rezervasyon Sistemi
-- Modern takvim tabanlı rezervasyon sistemi

-- Meeting Rooms tablosu güncelle
DROP TABLE IF EXISTS room_reservations;
DROP TABLE IF EXISTS meeting_rooms;

CREATE TABLE IF NOT EXISTS meeting_rooms (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    capacity INT DEFAULT 10,
    equipment TEXT,
    location VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    image_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Room Reservations tablosu güncelle 
CREATE TABLE IF NOT EXISTS room_reservations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    room_id INT NOT NULL,
    user_id INT,
    reservation_date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    purpose TEXT,
    attendees_count INT DEFAULT 1,
    requester_name VARCHAR(255),
    requester_email VARCHAR(255),
    requester_phone VARCHAR(50),
    notes TEXT,
    status ENUM('pending', 'approved', 'cancelled', 'completed') DEFAULT 'approved',
    confirmation_code VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (room_id) REFERENCES meeting_rooms(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_date_room (reservation_date, room_id),
    INDEX idx_user (user_id),
    INDEX idx_status (status),
    INDEX idx_confirmation (confirmation_code),
    UNIQUE KEY unique_booking (room_id, reservation_date, start_time, end_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Time Slots tablosu (önceden tanımlı saat aralıkları)
CREATE TABLE IF NOT EXISTS time_slots (
    id INT AUTO_INCREMENT PRIMARY KEY,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    label VARCHAR(100) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    sort_order INT DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Varsayılan iki odayı ekle
INSERT INTO meeting_rooms (name, description, capacity, equipment, location, image_url) VALUES
('Büyük Toplantı Odası', 'Ana toplantı odası, geniş kapasiteli ve tam donanımlı', 15, 'Projektör, Ses sistemi, Video konferans, Beyaz tahta, Klima', 'Zemin Kat', '/static/images/big-meeting-room.jpg'),
('Think Tank', 'Yaratıcı çalışmalar ve küçük toplantılar için tasarlanmış modern oda', 8, 'LED TV, Kablosuz sunum, Beyaz tahta, Rahat koltuklar', '1. Kat', '/static/images/think-tank.jpg');

-- Varsayılan saat aralıklarını ekle
INSERT INTO time_slots (start_time, end_time, label, sort_order) VALUES
('09:00:00', '10:00:00', '09:00 - 10:00', 1),
('10:00:00', '11:00:00', '10:00 - 11:00', 2),
('11:00:00', '12:00:00', '11:00 - 12:00', 3),
('12:00:00', '13:00:00', '12:00 - 13:00', 4),
('13:00:00', '14:00:00', '13:00 - 14:00', 5),
('14:00:00', '15:00:00', '14:00 - 15:00', 6),
('15:00:00', '16:00:00', '15:00 - 16:00', 7),
('16:00:00', '17:00:00', '16:00 - 17:00', 8),
('17:00:00', '18:00:00', '17:00 - 18:00', 9),
('09:00:00', '12:00:00', '09:00 - 12:00 (Yarım Gün)', 10),
('13:00:00', '17:00:00', '13:00 - 17:00 (Yarım Gün)', 11),
('09:00:00', '17:00:00', '09:00 - 17:00 (Tam Gün)', 12);

-- Users tablosuna booking izni ekle (eğer yoksa)
ALTER TABLE users ADD COLUMN IF NOT EXISTS can_reserve_rooms BOOLEAN DEFAULT FALSE;

-- Admin ve IK'ya otomatik izin ver
UPDATE users SET can_reserve_rooms = TRUE WHERE role_id IN (
    SELECT id FROM roles WHERE name IN ('Admin', 'İK Yöneticisi', 'İçerik Yöneticisi')
) OR is_admin = TRUE; 