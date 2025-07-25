-- Jobs tablosu oluşturma
CREATE TABLE IF NOT EXISTS jobs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    department_id INT,
    location VARCHAR(255) NOT NULL,
    job_type ENUM('Tam Zamanlı', 'Yarı Zamanlı', 'Stajyer', 'Uzaktan') NOT NULL,
    description TEXT NOT NULL,
    requirements TEXT,
    posted_by INT NOT NULL,
    posted_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_date DATETIME NULL,
    status ENUM('active', 'inactive') DEFAULT 'active',
    FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE SET NULL,
    FOREIGN KEY (posted_by) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Örnek iş ilanları ekleme
INSERT INTO jobs (title, department_id, location, job_type, description, requirements, posted_by, status) VALUES
('Frontend Developer', 1, 'İstanbul', 'Tam Zamanlı', 'React ve JavaScript deneyimi olan Frontend Developer aranıyor. Modern web teknolojileri konusunda deneyimli, takım çalışmasına yatkın kişiler arıyoruz.', 'React, JavaScript, HTML, CSS deneyimi\nTakım çalışmasına yatkın\nEn az 2 yıl deneyim', 1, 'active'),
('İK Uzmanı', 2, 'İstanbul', 'Tam Zamanlı', 'Deneyimli İK Uzmanı aranıyor. İnsan kaynakları süreçlerini yönetebilecek, işe alım ve performans yönetimi konularında deneyimli kişiler arıyoruz.', 'İK alanında en az 3 yıl deneyim\nİşe alım süreçleri deneyimi\nİletişim becerileri güçlü', 1, 'active'),
('Muhasebe Uzmanı', 3, 'İstanbul', 'Yarı Zamanlı', 'Muhasebe alanında deneyimli uzman aranıyor. Finansal raporlama ve vergi süreçlerinde deneyimli kişiler arıyoruz.', 'Muhasebe alanında deneyim\nVergi mevzuatı bilgisi\nDikkatli ve titiz çalışma', 1, 'active'); 