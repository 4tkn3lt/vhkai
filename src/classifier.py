"""
Evrak Sınıflandırıcı Modülü
Makine öğrenmesi ve NLP kullanarak evrakları sınıflandırmak
"""

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from typing import Dict, List, Tuple, Optional
import json
from pathlib import Path


class DocumentClassifier:
    """Evrak sınıflandırması için ana sınıf"""
    
    def __init__(self, language='turkish'):
        """
        Başlatıcı
        
        Args:
            language: Dil (turkish)
        """
        self.language = language
        self.model = None
        self.vectorizer = None
        self.classes = []
        self.feature_names = []
        
        # Basit Türkçe stop words
        self.stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            've', 'bu', 'bu', 'için', 'var', 'bir', 'ise', 'yok', 'dan', 'de'
        }
    
    def train_from_examples(self, training_data: List[Tuple[str, str]]):
        """
        Örnek verilerden modeli eğit
        
        Args:
            training_data: [(metin, kategori), ...] listesi
        """
        if not training_data:
            print("Uyarı: Eğitim verisi boş")
            return False
        
        texts = [item[0] for item in training_data]
        labels = [item[1] for item in training_data]
        
        try:
            # Pipeline oluştur: TF-IDF + Naive Bayes
            self.model = Pipeline([
                ('tfidf', TfidfVectorizer(max_features=1000, stop_words=list(self.stop_words))),
                ('classifier', MultinomialNB())
            ])
            
            # Modeli eğit
            self.model.fit(texts, labels)
            self.classes = self.model.named_steps['classifier'].classes_
            
            print(f"✓ Model eğitildi. Kategoriler: {list(self.classes)}")
            return True
            
        except Exception as e:
            print(f"Hata: Model eğitimi başarısız - {e}")
            return False
    
    def predict(self, text: str) -> Tuple[str, float]:
        """
        Metni sınıflandır
        
        Args:
            text: Sınıflandırılacak metin
            
        Returns:
            (tahmin_edilen_kategori, güven_puanı)
        """
        if self.model is None:
            return "Bilinmiyor", 0.0
        
        try:
            # Tahmin ve olasılık al
            prediction = self.model.predict([text])[0]
            probabilities = self.model.predict_proba([text])[0]
            confidence = max(probabilities)
            
            return prediction, confidence
            
        except Exception as e:
            print(f"Hata: Sınıflandırma başarısız - {e}")
            return "Hata", 0.0
    
    def predict_top_n(self, text: str, n: int = 3) -> List[Tuple[str, float]]:
        """
        Top N tahmini al
        
        Args:
            text: Sınıflandırılacak metin
            n: Kaç tahmin istendiği
            
        Returns:
            [(kategori, güven), ...] listesi
        """
        if self.model is None:
            return []
        
        try:
            probabilities = self.model.predict_proba([text])[0]
            top_indices = np.argsort(probabilities)[-n:][::-1]
            
            results = [
                (self.classes[i], probabilities[i])
                for i in top_indices
            ]
            
            return results
            
        except Exception as e:
            print(f"Hata: Top-N tahmin başarısız - {e}")
            return []
    
    def save_model(self, path: str):
        """
        Modeli kaydet
        
        Args:
            path: Kayıt yolu
        """
        import pickle
        try:
            with open(path, 'wb') as f:
                pickle.dump(self.model, f)
            print(f"✓ Model kaydedildi: {path}")
        except Exception as e:
            print(f"Hata: Model kaydedilemedi - {e}")
    
    def load_model(self, path: str):
        """
        Modeli yükle
        
        Args:
            path: Model yolu
        """
        import pickle
        try:
            with open(path, 'rb') as f:
                self.model = pickle.load(f)
            self.classes = self.model.named_steps['classifier'].classes_
            print(f"✓ Model yüklendi: {path}")
        except Exception as e:
            print(f"Hata: Model yüklenemedi - {e}")


class SimpleKeywordClassifier:
    """
    Anahtar kelime tabanlı basit sınıflandırıcı
    NLP modeli yeterli veriye sahip olmayana kadar
    """
    
    def __init__(self, rules_path: str = "config/classification_rules.json"):
        """
        Başlatıcı
        
        Args:
            rules_path: Sınıflandırma kuralları dosyası
        """
        self.rules = self._load_rules(rules_path)
    
    def _load_rules(self, rules_path: str) -> Dict:
        """Kuralları yükle"""
        default_rules = {
            "personel_isleri": {
                "category": "Personel İşleri (903)",
                "department": "İnsan Kaynakları",
                "keywords": ["izin", "personel", "çalışan", "atama", "transfer", "özlük"],
                "confidence_boost": 0.15
            },
            "mali_isler": {
                "category": "Mali İşler (201)",
                "department": "Muhasebe",
                "keywords": ["fatura", "ödeme", "bütçe", "gider", "taksit", "para"],
                "confidence_boost": 0.12
            },
            "egitim_isleri": {
                "category": "Eğitim İşleri (301)",
                "department": "Eğitim Koordinatörlüğü",
                "keywords": ["ders", "öğrenci", "okul", "eğitim", "takvim", "sınav"],
                "confidence_boost": 0.15
            },
            "genel_isler": {
                "category": "Genel İşler (100)",
                "department": "Müdürlük",
                "keywords": ["kararı", "yönetim", "müdür", "direktif", "komite"],
                "confidence_boost": 0.10
            }
        }
        
        try:
            if Path(rules_path).exists():
                with open(rules_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Uyarı: Kurallar yüklenemedi - {e}")
        
        return default_rules
    
    def classify(self, text: str) -> Tuple[Dict, float]:
        """
        Metni kurallarla sınıflandır
        
        Args:
            text: Sınıflandırılacak metin
            
        Returns:
            (sınıflandırma_bilgisi, güven_puanı)
        """
        text_lower = text.lower()
        scores = {}
        
        for rule_name, rule in self.rules.items():
            score = 0
            for keyword in rule.get('keywords', []):
                if keyword in text_lower:
                    score += 1
            
            if score > 0:
                # Anahtar kelime sayısına göre güven puanı
                confidence = min(0.9, (score / len(rule.get('keywords', [1]))) * 0.8)
                scores[rule_name] = (confidence, rule)
        
        if not scores:
            return {
                'category': 'Sınıflandırılamadı',
                'department': 'Bilinmiyor',
                'reason': 'Anahtar kelime eşleşmesi bulunamadı'
            }, 0.0
        
        # En yüksek skoru al
        best_rule = max(scores.items(), key=lambda x: x[1][0])
        confidence, rule = best_rule[1]
        
        return {
            'category': rule['category'],
            'department': rule['department'],
            'matched_keywords': [k for k in rule['keywords'] if k in text_lower]
        }, confidence


if __name__ == "__main__":
    # Test
    classifier = SimpleKeywordClassifier()
    
    test_text = """
    Personel İdari İzin Talep Formu
    Evrak No: 2024/001-903-A1
    
    Söz konusu çalışanımız yaşlı validesinin tedavisi için
    idari izin talebinde bulunmuştur.
    """
    
    result, confidence = classifier.classify(test_text)
    print(f"Sınıflandırma: {result}")
    print(f"Güven Puanı: {confidence:.2%}")