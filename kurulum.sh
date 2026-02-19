#!/bin/bash
# ===================================================================
# Cryptocurrency Trading Bot - Kurulum Scripti (Linux/Mac)
# ===================================================================

echo ""
echo "===================================================================="
echo "          CRYPTOCURRENCY TRADING BOT - KURULUM"
echo "===================================================================="
echo ""

# Python kontrolü
echo "[1/4] Python kontrolü yapılıyor..."
if ! command -v python3 &> /dev/null; then
    echo ""
    echo "HATA: Python3 bulunamadı!"
    echo ""
    echo "Lütfen Python 3.8 veya üzeri yükleyin:"
    echo "  macOS: brew install python3"
    echo "  Ubuntu/Debian: sudo apt install python3 python3-pip"
    echo ""
    exit 1
fi
python3 --version
echo "Python bulundu! ✓"
echo ""

# Paket yüklemesi
echo "[2/4] Gerekli paketler yükleniyor..."
echo "Bu işlem 2-5 dakika sürebilir..."
pip3 install -r requirements.txt
if [ $? -ne 0 ]; then
    echo ""
    echo "HATA: Paket yüklemesi başarısız!"
    exit 1
fi
echo "Paketler yüklendi! ✓"
echo ""

# Test
echo "[3/4] Kurulum test ediliyor..."
python3 -m pytest tests/test_core.py -v
if [ $? -ne 0 ]; then
    echo ""
    echo "UYARI: Bazı testler başarısız oldu."
    echo "Bot yine de çalışabilir."
fi
echo "Testler tamamlandı! ✓"
echo ""

# Demo
echo "[4/4] Demo hazır!"
echo ""
echo "===================================================================="
echo "                    KURULUM TAMAMLANDI!"
echo "===================================================================="
echo ""
echo "Şimdi yapabilecekleriniz:"
echo ""
echo "1. Demo'yu çalıştır:        ./demo.sh"
echo "2. Botu başlat:             ./baslat.sh"
echo "3. Testleri çalıştır:       python3 -m pytest tests/test_core.py -v"
echo ""
echo "Detaylı kullanım için NASIL_KULLANILIR.md dosyasına bakın."
echo ""
