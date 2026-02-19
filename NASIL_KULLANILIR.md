# 📖 NASIL KULLANILIR - Cryptocurrency Trading Bot

## 🎯 Bu Yazılıma Nasıl Ulaşabilirsiniz?

Bu kılavuz, Cryptocurrency Trading Bot Phase 2 yazılımını bilgisayarınıza indirip kullanmaya başlamanız için gereken tüm adımları detaylı olarak açıklar.

---

## 📋 İçindekiler

1. [Sistem Gereksinimleri](#-sistem-gereksinimleri)
2. [Yazılımı İndirme](#-yazılımı-indirme)
3. [Kurulum](#-kurulum)
4. [İlk Çalıştırma](#-ilk-çalıştırma)
5. [Konfigürasyon](#-konfigürasyon)
6. [Kullanım](#-kullanım)
7. [Gerçek Trading'e Geçiş](#-gerçek-tradinge-geçiş)
8. [Sorun Giderme](#-sorun-giderme)
9. [Sık Sorulan Sorular](#-sık-sorulan-sorular)

---

## 💻 Sistem Gereksinimleri

Yazılımı çalıştırmak için aşağıdakilere ihtiyacınız var:

### Minimum Gereksinimler:
- **İşletim Sistemi**: Windows 10/11, macOS 10.14+, veya Linux (Ubuntu 18.04+)
- **Python**: 3.8 veya üzeri
- **RAM**: En az 4 GB
- **Disk Alanı**: En az 1 GB boş alan
- **İnternet**: Sürekli internet bağlantısı

### Önerilen:
- **RAM**: 8 GB veya daha fazla
- **İşlemci**: 4 çekirdek veya daha fazla
- **İnternet**: Hızlı ve kararlı bağlantı

---

## 📥 Yazılımı İndirme

### Yöntem 1: GitHub'dan Doğrudan İndirme (Kolay)

1. **GitHub sayfasına gidin:**
   ```
   https://github.com/aliatmaca1915-lab/crypto-trading-bot
   ```

2. **Yeşil "Code" butonuna tıklayın**

3. **"Download ZIP" seçeneğini seçin**

4. **İndirilen ZIP dosyasını bir klasöre çıkarın**
   - Örnek: `C:\CryptoBot\` (Windows)
   - Örnek: `~/CryptoBot/` (Mac/Linux)

### Yöntem 2: Git ile Klonlama (İleri Seviye)

Eğer Git yüklüyse, terminal/komut satırında:

```bash
# İstediğiniz klasöre gidin
cd Masaüstü

# Projeyi klonlayın
git clone https://github.com/aliatmaca1915-lab/crypto-trading-bot.git

# Proje klasörüne girin
cd crypto-trading-bot
```

---

## ⚙️ Kurulum

### Adım 1: Python'un Kurulu Olduğunu Kontrol Edin

Terminal/Komut satırını açın ve şunu yazın:

```bash
python --version
```

veya

```bash
python3 --version
```

**Sonuç**: `Python 3.8.x` veya daha yüksek bir sürüm görmelisiniz.

❌ Eğer Python yüklü değilse:
- **Windows**: https://www.python.org/downloads/ adresinden indirin
- **Mac**: `brew install python3` (Homebrew ile)
- **Linux**: `sudo apt install python3 python3-pip` (Ubuntu/Debian)

### Adım 2: Proje Klasörüne Gidin

```bash
cd crypto-trading-bot
```

veya indirdiğiniz klasörün tam yolunu kullanın:

```bash
cd C:\CryptoBot\crypto-trading-bot  # Windows örneği
cd ~/Masaüstü/crypto-trading-bot     # Mac/Linux örneği
```

### Adım 3: Gerekli Paketleri Yükleyin

```bash
pip install -r requirements.txt
```

veya

```bash
pip3 install -r requirements.txt
```

⏱️ **Bu işlem 2-5 dakika sürebilir.** İnternet hızınıza bağlı olarak değişir.

✅ **Kurulum tamamlandı!** Şimdi yazılımı kullanmaya başlayabilirsiniz.

---

## 🚀 İlk Çalıştırma

### Demo'yu Çalıştırın (Önerilen İlk Adım)

Demo, yazılımın nasıl çalıştığını gerçek para riski olmadan gösterir:

```bash
python demo.py
```

**Ne göreceksiniz?**
- Piyasa analizi
- Skorlama sistemi çıktıları
- Multi-timeframe analiz sonuçları
- Trading sinyalleri

**Önemli**: Demo hiçbir işlem yapmaz, sadece analiz gösterir!

### Botu Çalıştırın (Kağıt Trading)

Bot varsayılan olarak **kağıt trading** modunda çalışır (simülasyon, gerçek para riski YOK):

```bash
python src/main.py
```

**Bot ne yapar?**
- 10 kripto parayı gerçek zamanlı analiz eder
- Skorlama algoritması çalıştırır
- Trading sinyalleri üretir
- Simülasyon modunda işlemler yapar
- Her şeyi kayıt altına alır

**Durdurmak için**: `Ctrl+C` tuşlarına basın

---

## ⚙️ Konfigürasyon

Ayarları değiştirmek için `config/config.yaml` dosyasını düzenleyin:

### Temel Ayarlar

```yaml
# Trading Modu (ÖNEMLİ!)
mode: "paper"  # "paper" = Kağıt trading (güvenli)
               # "real" = Gerçek trading (riskli!)

# Başlangıç Sermayesi (Simülasyon için)
capital:
  initial_capital: 10000  # USDT cinsinden

# Takip edilecek coinler
cryptocurrencies:
  - "BTC/USDT"
  - "ETH/USDT"
  - "BNB/USDT"
  # ... daha fazlası
```

### Bildirim Ayarları (İsteğe Bağlı)

#### Email Bildirimleri

```yaml
notifications:
  email:
    enabled: true
    smtp_server: "smtp.gmail.com"
    smtp_port: 587
    sender_email: "sizin_mailiniz@gmail.com"
    sender_password: "uygulama_sifreniz"
    recipient_email: "alici@gmail.com"
```

#### Telegram Bildirimleri

```yaml
notifications:
  telegram:
    enabled: true
    bot_token: "BOT_TOKEN_BURAYA"
    chat_id: "CHAT_ID_BURAYA"
```

**Telegram Bot Token Nasıl Alınır?**
1. Telegram'da @BotFather'ı bulun
2. `/newbot` komutunu gönderin
3. Bot adını belirleyin
4. Size verilen token'ı kopyalayın

---

## 🎮 Kullanım

### 1. Demo Modu (Öğrenme İçin)

```bash
python demo.py
```

**Ne zaman kullanılır?**
- Yazılımı ilk kez kullanıyorsanız
- Nasıl çalıştığını öğrenmek istiyorsanız
- Skorlama sistemini anlamak istiyorsanız

### 2. Kağıt Trading (Pratik İçin)

```bash
python src/main.py
```

**Ne zaman kullanılır?**
- Botun davranışını test etmek için
- Stratejileri denemek için
- Gerçek para riski olmadan deneyim kazanmak için

**Özellikler**:
- Gerçek piyasa verileri
- Gerçek zamanlı analiz
- Simülasyon işlemleri
- Performans takibi

### 3. Testleri Çalıştırma

Yazılımın düzgün çalıştığından emin olmak için:

```bash
python -m pytest tests/test_core.py -v
```

Sonuç: `17 passed` görmelisiniz ✅

### 4. Logları İnceleme

Bot çalıştıkça tüm aktiviteleri kaydeder:

```bash
# Log dosyasını görüntüle
cat logs/trading_bot.log

# veya Windows'ta
type logs\trading_bot.log

# Son 50 satırı göster
tail -n 50 logs/trading_bot.log
```

### 5. Veritabanını İnceleme

Tüm işlemler SQLite veritabanında saklanır:

**Dosya**: `data/trading_bot.db`

SQLite Browser gibi araçlarla açabilirsiniz veya:

```bash
sqlite3 data/trading_bot.db
```

SQL komutları:
```sql
-- Tüm işlemleri göster
SELECT * FROM trades;

-- Son 10 sinyali göster
SELECT * FROM signals ORDER BY timestamp DESC LIMIT 10;

-- Performans metriklerini göster
SELECT * FROM performance_metrics;
```

---

## 💰 Gerçek Trading'e Geçiş

⚠️ **DİKKAT**: Bu bölüm gerçek para kullanımıyla ilgilidir!

### Ön Koşullar

1. **En az 30 gün kağıt trading deneyimi**
2. **Pozitif sonuçlar elde etmiş olmalısınız**
3. **Botun davranışını tam anlamalısınız**
4. **Kayıpları göze alabilecek sermayeniz olmalı**

### Binance API Anahtarı Alma

1. **Binance hesabı açın**: https://www.binance.com
2. **Kimlik doğrulaması yapın** (KYC)
3. **API Management** bölümüne gidin
4. **Create API** butonuna tıklayın
5. **API anahtarı ve gizli anahtarı kaydedin**

**ÖNEMLİ Güvenlik Ayarları**:
- ✅ "Enable Reading" aktif
- ✅ "Enable Spot & Margin Trading" aktif
- ❌ "Enable Withdrawals" KAPALI (asla açmayın!)
- ✅ IP whitelist ekleyin (kendi IP'niz)

### Konfigürasyonu Güncelleme

`config/config.yaml` dosyasında:

```yaml
# 1. Modu değiştirin
mode: "real"  # ⚠️ DİKKAT: Gerçek para!

# 2. API bilgilerini ekleyin
api:
  binance:
    api_key: "BURAYA_API_KEY"
    api_secret: "BURAYA_API_SECRET"
    testnet: false  # Gerçek trading için false
```

### Güvenlik Önerileri

1. **Küçük başlayın**: İlk gerçek işlem için 100-500 USDT gibi küçük bir miktar
2. **Bildirimleri aktif edin**: Her işlemden haberdar olun
3. **Düzenli kontrol**: Günde en az 2-3 kez kontrol edin
4. **Stop-loss kullanın**: Bot otomatik yapar ama yine de kontrol edin
5. **Risk limitlerini ayarlayın**: Günlük/haftalık limitleri düşük tutun

### Küçük Test

Gerçek trading'e geçmeden önce:

```yaml
capital:
  initial_capital: 100  # Çok küçük başlayın
  daily_loss_limit: 0.02  # %2 günlük limit
```

---

## 🔧 Sorun Giderme

### Problem: "Python bulunamadı" hatası

**Çözüm**:
```bash
# Windows
python --version
# Yoksa python3 deneyin
python3 --version

# PATH'e ekleyin veya Python'u yeniden kurun
```

### Problem: "Modül bulunamadı" hatası

**Çözüm**:
```bash
# Paketleri tekrar yükleyin
pip install -r requirements.txt --upgrade

# veya
pip3 install -r requirements.txt --upgrade
```

### Problem: "Permission denied" hatası

**Çözüm**:
```bash
# Linux/Mac'te
chmod +x run.sh
sudo pip install -r requirements.txt

# veya
pip install --user -r requirements.txt
```

### Problem: Bot çalışmıyor

**Kontrol Listesi**:
1. ✅ Python 3.8+ yüklü mü?
2. ✅ Tüm paketler yüklü mü? (`pip install -r requirements.txt`)
3. ✅ `config/config.yaml` dosyası mevcut mu?
4. ✅ İnternet bağlantısı var mı?
5. ✅ Log dosyasında hata var mı? (`logs/trading_bot.log`)

### Problem: API bağlantı hatası

**Çözüm**:
- API anahtarları doğru mu kontrol edin
- Binance'de API izinleri aktif mi?
- IP whitelist doğru ayarlanmış mı?
- Testnet/mainnet ayarı doğru mu?

### Problem: Hiç sinyal gelmiyor

**Açıklama**: Bu normaldir!
- Bot minimum 60 puan threshold kullanır
- Çoğu zaman piyasa şartları uygun olmayabilir
- Multi-timeframe alignment gerekir (3+ zaman dilimi)
- Sabırlı olun, kaliteli sinyaller bekleyin

---

## ❓ Sık Sorulan Sorular

### Gerçek para riski var mı?

**Hayır!** Varsayılan mod "paper trading"dir. Gerçek para riski yoktur. Siz açıkça `mode: "real"` ayarını yapıp API anahtarlarını eklemedikçe gerçek işlem yapılmaz.

### Kaç para kazanabilirim?

**Garanti yoktur!** Kripto piyasaları son derece risklidir. Bu bot:
- ✅ Sofistike analiz yapar
- ✅ Risk yönetimi kullanır
- ❌ Garanti kazanç vaat etmez
- ❌ %100 başarı oranı yoktur

**ÖNEMLİ**: Sadece kaybetmeyi göze alabileceğiniz parayla trading yapın!

### Botun minimum sermaye gereksinimi var mı?

**Kağıt trading için**: Yok, istediğiniz miktarı simülasyon için kullanabilirsiniz.

**Gerçek trading için**: Binance'in minimum işlem limitleri vardır (genelde 10-20 USDT). Bot için önerilen minimum: 500-1000 USDT.

### Bot 7/24 çalışmalı mı?

**Kağıt trading için**: İsteğe bağlı. İstediğiniz zaman başlatıp durdurabilirsiniz.

**Gerçek trading için**: Evet, fırsatları kaçırmamak için 7/24 çalışmalıdır. Bulut sunucu (VPS) kullanmanız önerilir.

### Hangi coinlerde işlem yapıyor?

Varsayılan olarak 10 coin:
- BTC, ETH, BNB, XRP, ADA, SOL, DOGE, DOT, LTC, ADA

`config/config.yaml` dosyasından değiştirebilirsiniz.

### Kaldıraç ne kadar?

**Sabit 10x kaldıraç** kullanır. Değiştirilemez (güvenlik için).

### Günde kaç işlem yapar?

**Belli değildir!** Piyasa şartlarına bağlı:
- Bazı günler hiç işlem yapmayabilir (sinyal yoksa)
- Bazı günler 5-10 işlem yapabilir (çok sinyal varsa)
- Minimum 60 puan skoruna ulaşmalı
- 3+ timeframe uyumlu olmalı

Kalite > Kantite prensibiyle çalışır.

### Kar ne zaman gerçekleşir?

Otomatik take-profit seviyeleri:
- TP1: Pozisyonun %40'ı
- TP2: Pozisyonun %30'u
- TP3: Pozisyonun %30'u

Klasifikasyona göre %8-20 arası kar hedefleri.

### Stop-loss nedir, nasıl çalışır?

Otomatik zarar durdurma:
- ATR bazlı dinamik hesaplama
- Klasifikasyona göre %2-3.5 arası
- Likidite buffer (%3-5) korunur
- Manuel müdahale gerekmez

### Botu nasıl durdururum?

Çalışırken terminal/komut satırında:
```
Ctrl + C
```

Bot güvenli şekilde kapanır.

### Ayarları değiştirince bot'u yeniden başlatmalı mıyım?

**Evet!** `config/config.yaml` dosyasındaki değişiklikler bot yeniden başlatılınca geçerli olur.

### Birden fazla bot çalıştırabilir miyim?

**Evet!** Farklı klasörlere kopyalayıp farklı ayarlarla çalıştırabilirsiniz. Ancak aynı API anahtarıyla dikkatli olun (rate limit).

### Geçmiş performansı nasıl görebilirim?

1. **Log dosyaları**: `logs/trading_bot.log`
2. **Veritabanı**: `data/trading_bot.db`
3. **Performans metrikleri**: SQLite browser ile görüntüleyin

### Botun kaynak kodu güvenli mi?

✅ **Evet!**
- Açık kaynak (GitHub'da)
- CodeQL taraması temiz (0 güvenlik açığı)
- API anahtarları asla paylaşılmaz
- Tüm kod incelenebilir

### Teknik destek var mı?

- 📖 Bu kılavuzu okuyun
- 📖 README.md dosyasını inceleyin
- 🐛 GitHub Issues bölümünde soru sorun
- 💬 Topluluktan yardım alın

---

## 📞 Yardım ve Destek

### Dokümantasyon Dosyaları

Projedeki tüm belgeler:

1. **NASIL_KULLANILIR.md** (bu dosya) - Türkçe kullanım kılavuzu
2. **README.md** - Ana dokümantasyon (İngilizce)
3. **QUICKSTART.md** - Hızlı başlangıç (İngilizce)
4. **DURUM_RAPORU.md** - Durum raporu (Türkçe)
5. **SECURITY.md** - Güvenlik bilgileri
6. **IMPLEMENTATION.md** - Teknik detaylar

### GitHub Sayfası

```
https://github.com/aliatmaca1915-lab/crypto-trading-bot
```

### Issue Oluşturma

Problem yaşıyorsanız:
1. GitHub sayfasına gidin
2. "Issues" sekmesine tıklayın
3. "New Issue" butonuna tıklayın
4. Probleminizi detaylı açıklayın

---

## 🎓 Öğrenme Yolu

### 1. Başlangıç (1. Hafta)
- ✅ Yazılımı indirin ve kurun
- ✅ Demo'yu çalıştırın
- ✅ Dokümantasyonu okuyun
- ✅ Skorlama sistemini anlayın

### 2. Pratik (2-4. Hafta)
- ✅ Kağıt trading başlatın
- ✅ Günlük logları inceleyin
- ✅ Performans metriklerini takip edin
- ✅ Farklı ayarları deneyin

### 3. İleri Seviye (1-3. Ay)
- ✅ 30+ gün kağıt trading deneyimi
- ✅ Pozitif sonuçlar elde edin
- ✅ Risk yönetimini anlayın
- ✅ Piyasa davranışlarını öğrenin

### 4. Gerçek Trading (3+ Ay)
- ⚠️ Sadece kaybetmeyi göze alabileceğiniz para
- ⚠️ Çok küçük sermaye ile başlayın
- ⚠️ Sürekli izleyin
- ⚠️ Duygusal kararlar vermeyin

---

## ⚠️ Önemli Uyarılar

### Risk Uyarısı

🚨 **KRİPTO PARA TİCARETİ SON DERECE RİSKLİDİR!**

- Tüm paranızı kaybedebilirsiniz
- Piyasalar 7/24 volatildir
- Bot garanti kazanç sağlamaz
- Sadece risk alabileceğiniz parayla işlem yapın

### Yasal Uyarı

- Bu bot eğitim amaçlıdır
- Finansal tavsiye değildir
- Kendi kararlarınızdan siz sorumlusunuz
- Ülkenizin yasal düzenlemelerine uyun

### Güvenlik Uyarısı

- ✅ API anahtarlarınızı kimseyle paylaşmayın
- ✅ Çekim iznini asla açmayın
- ✅ Güçlü şifreler kullanın
- ✅ 2FA (iki faktörlü doğrulama) aktif edin
- ✅ IP whitelist kullanın
- ❌ API anahtarlarını kod içine yazmayın
- ❌ API anahtarlarını GitHub'a yüklemeyin

---

## 🎉 Başarılar!

Artık Cryptocurrency Trading Bot'u kullanmaya hazırsınız!

**İlk adımlar**:
1. ✅ Yazılımı indirin
2. ✅ Kurulumu yapın
3. ✅ Demo'yu çalıştırın
4. ✅ Kağıt trading'i başlatın
5. ✅ Öğrenin ve deneyim kazanın

**Unutmayın**:
- 🎓 Öğrenmeye zaman ayırın
- 🐌 Acele etmeyin
- 📊 Küçük başlayın
- 🛡️ Risk yönetimini ciddiye alın
- 💡 Sürekli öğrenin ve gelişin

**İyi trading'ler!** 🚀

---

*Son güncelleme: Şubat 2026*
*Versiyon: Phase 2*
*Durum: Aktif ve kullanıma hazır*
