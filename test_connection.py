#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SMTP Sunucu Bağlantı Testi
"""

import socket
import smtplib
import ssl
from datetime import datetime

def test_port_connection(host, port, timeout=10):
    """Port bağlantısını test et"""
    try:
        sock = socket.create_connection((host, port), timeout)
        sock.close()
        return True
    except:
        return False

def test_smtp_connection(host, port, use_ssl=False, use_starttls=False):
    """SMTP bağlantısını test et"""
    try:
        if use_ssl:
            # SSL bağlantısı
            context = ssl.create_default_context()
            context.set_ciphers('DEFAULT@SECLEVEL=0')
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            server = smtplib.SMTP_SSL(host, port, context=context)
        else:
            # Normal bağlantı
            server = smtplib.SMTP(host, port)
            if use_starttls:
                server.starttls()
        
        server.quit()
        return True
    except Exception as e:
        print(f"   Hata: {e}")
        return False

def main():
    host = "mail.kurumsaleposta.com"
    
    print("=" * 60)
    print("🔌 SMTP SUNUCU BAĞLANTI TESTİ")
    print("=" * 60)
    print(f"📅 Test Tarihi: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
    print(f"🖥️ Sunucu: {host}")
    print("=" * 60)
    
    # Test edilecek portlar ve yöntemler
    tests = [
        (25, "SMTP (Plain)", False, False),
        (587, "SMTP + STARTTLS", False, True),
        (465, "SMTP + SSL", True, False),
        (2525, "Alternative SMTP", False, False),
    ]
    
    results = []
    
    for port, description, use_ssl, use_starttls in tests:
        print(f"\n🔄 Test: {description} (Port {port})")
        
        # Port bağlantı testi
        port_ok = test_port_connection(host, port)
        print(f"   Port Bağlantısı: {'✅ OK' if port_ok else '❌ FAIL'}")
        
        if port_ok:
            # SMTP bağlantı testi
            smtp_ok = test_smtp_connection(host, port, use_ssl, use_starttls)
            print(f"   SMTP Bağlantısı: {'✅ OK' if smtp_ok else '❌ FAIL'}")
            results.append((port, description, port_ok, smtp_ok))
        else:
            results.append((port, description, port_ok, False))
    
    # Sonuçlar özeti
    print("\n" + "=" * 60)
    print("📊 TEST SONUÇLARI ÖZETİ")
    print("=" * 60)
    
    working_ports = []
    for port, description, port_ok, smtp_ok in results:
        status = "✅ ÇALIŞIYOR" if (port_ok and smtp_ok) else "❌ ÇALIŞMIYOR"
        print(f"Port {port:4} ({description:15}): {status}")
        if port_ok and smtp_ok:
            working_ports.append((port, description))
    
    print("=" * 60)
    if working_ports:
        print("🎉 ÖNERİLEN BAĞLANTI YÖNTEMLERİ:")
        for port, description in working_ports:
            print(f"   • Port {port} - {description}")
    else:
        print("⚠️ Hiçbir port çalışmıyor. Firewall veya sunucu ayarları kontrol edilmeli.")
    print("=" * 60)

if __name__ == "__main__":
    main()
