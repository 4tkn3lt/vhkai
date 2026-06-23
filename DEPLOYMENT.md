# Kurulum ve Kullanım Rehberi

## 📋 Gereksinimler

- **Python**: 3.8 veya üzeri
- **RAM**: Minimum 2GB (4GB+ önerilir)
- **İşletim Sistemi**: Pardus Linux, Ubuntu, Windows, macOS

## 🚀 Kurulum Adımları

### 1. Repository'yi Klonla

```bash
git clone https://github.com/4tkn3lt/vhkai.git
cd vhkai
```

### 2. Python Ortamı Oluştur (Önerilir)

```bash
# Virtual environment oluştur
python3 -m venv venv

# Ortamı aktifleştir
# Linux/Mac:
source venv/bin/activate

# Windows:
venv\Scripts\activate
```

### 3. Bağımlılıkları Yükle

```bash
pip install -r requirements.txt

# Spacy Türkçe modeli (isteğe bağlı)
python -m spacy download tr_core_news_sm
```

## 📖 Kullanım

### Tek Dosya İşleme

```bash
python main.py --file evrak.pdf
```

### Toplu İşleme

```bash
python main.py --directory ./data/raw
```

## 🔧 Konfigürasyon

### Desimal Kodlar (`config/decimal_codes.json`)

Kurum özelindeki desimal kodları ekleyin.

### Departmanlar (`config/departments.json`)

Departman bilgilerini güncelleyin.

### Sınıflandırma Kuralları (`config/classification_rules.json`)

Anahtar kelimeleri ve kategorileri özelleştirin.

## 🔐 Veri Güvenliği (Kapalı Devre)

- ✅ Hiçbir veri internete gönderilmez
- ✅ Tüm işlemler lokal bilgisayarda yapılır
- ✅ Hiçbir cloud hizmeti kullanılmaz

---

**Version**: 0.1.0  
**Son Güncelleme**: 23.06.2024