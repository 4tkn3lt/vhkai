# VHKAI - Kamu Evrak Sınıflandırma ve Yönlendirme Sistemi

**TEKNOFEST 2026 Yapay Zekâ Dil Ajanları Yarışması - Senaryo 1**

Kamu kurumlarındaki evrak ve yazışma süreçlerini yapay zekâ ile otomatikleştiren akıllı agent sistemi.

## 📋 Proje Amacı

Gelen evrakları:
- ✅ Desimal koda göre otomatik sınıflandırmak
- ✅ İlgili birimlere yönlendirmek
- ✅ Operatöre aksiyon önerileri sunmak
- ✅ Tamamen offline/kapalı devre çalışmak

## 🏗️ Sistem Mimarisi

```
PDF/Evrak → Metin Çıkarma → Desimal Kod Tanıma → Sınıflandırma → Yönlendirme Önerisi
                                                        ↓
                                                   Dashboard/UI
```

## 📁 Proje Yapısı

```
vhkai/
├── README.md
├── requirements.txt
├── config/
│   └── decimal_codes.json          # Desimal kod ve kategoriler
├── data/
│   ├── raw/                        # Ham PDF evrakları
│   └── processed/                  # İşlenmiş evraklar
├── src/
│   ├── __init__.py
│   ├── pdf_processor.py            # PDF metin çıkarma
│   ├── decimal_extractor.py        # Desimal kod tanıma
│   ├── classifier.py               # Evrak sınıflandırıcı
│   └── router.py                   # Yönlendirme sistemi
├── models/
│   └── trained_models/             # Eğitilmiş modeller
├── tests/
│   └── test_*.py
└── notebooks/
    └── exploration.ipynb           # Veri analizi
```

## 🔧 Teknoloji Stack

- **Python 3.8+**
- **PyPDF2** - PDF metin çıkarma
- **scikit-learn** - ML sınıflandırma
- **Hugging Face Transformers** - NLP (DistilBERT-Turkish)
- **spaCy** - Türkçe NLP işlemleri
- **Flask** - Web arayüzü (MVP sonrasında)
- **SQLite** - Veri tabanı

## 📊 Gelişim Planı

| Aşama | Hedef | Süre |
|-------|-------|------|
| 1 | Veri hazırlığı & Desimal kod mapping | Gün 1-2 |
| 2 | PDF işleme & metin çıkarma | Gün 3 |
| 3 | Sınıflandırma modeli (MVP) | Gün 4-5 |
| 4 | Yönlendirme sistemi | Gün 6-7 |
| 5 | Test & optimizasyon | Gün 8 |
| 6 | Ön Değerlendirme Raporu | Gün 9-10 |

## 📝 Kullanım

```bash
# Kurulum
pip install -r requirements.txt

# Evrak sınıflandır
python main.py --file evrak.pdf

# Sonuç
Sınıflandırma: Personel İşleri (903)
Yönlendirme: İnsan Kaynakları Bölümü
Güven Skoru: 0.94
```

## 📄 Lisans

MIT License

## 👤 Ekip

- **Geliştirici**: 4tkn3lt

---

**Son Güncelleme**: 23.06.2024