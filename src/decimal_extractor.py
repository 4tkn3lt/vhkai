"""
Desimal Kod Çıkarma Modülü
Evraktan desimal kodu tanımlamak için
"""

import re
import json
from typing import Dict, List, Tuple, Optional
from pathlib import Path


class DecimalExtractor:
    """Evraktan desimal kod çıkarmak için sınıf"""
    
    # Desimal kod regex paternleri
    # Format: YYYY/XXX-YYY-ZZZ veya XXX-YYY-ZZZ vb.
    PATTERNS = [
        r'\d{4}/\d{3}-\d{3}-[A-Z0-9]+',  # 2024/001-903-A1
        r'\d{3}-\d{3}-[A-Z0-9]+',          # 001-903-A1
        r'\d{3}-\d{2,3}(?=[\s\)])',        # 903-001 (end of line)
    ]
    
    def __init__(self, config_path: str = "config/decimal_codes.json"):
        """
        Başlatıcı
        
        Args:
            config_path: Desimal kod konfigürasyon dosyası yolu
        """
        self.config_path = config_path
        self.codes_db = self._load_config()
    
    def _load_config(self) -> Dict:
        """Konfigürasyon dosyasını yükle"""
        try:
            if Path(self.config_path).exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Hata: Konfigürasyon yüklenemedi - {e}")
        
        return {"categories": {}}
    
    def extract_decimal_codes(self, text: str) -> List[str]:
        """
        Metinden tüm desimal kodları çıkar
        
        Args:
            text: İşlenecek metin
            
        Returns:
            Bulunan desimal kodları içeren liste
        """
        codes = []
        
        for pattern in self.PATTERNS:
            matches = re.findall(pattern, text)
            codes.extend(matches)
        
        # Dublikatları kaldır ve benzersiz kodları döndür
        return list(set(codes))
    
    def extract_main_category(self, decimal_code: str) -> str:
        """
        Desimal koddan ana kategoriyi çıkar
        Örn: "2024/001-903-A1" → "903"
        
        Args:
            decimal_code: Desimal kod
            
        Returns:
            Ana kategori kodu
        """
        # Son "/" den sonraki veya tüm dizgiden XXX-YYY kısmını çıkar
        match = re.search(r'(\d{3})-(\d{3})', decimal_code)
        if match:
            return match.group(1) + "-" + match.group(2)
        
        return decimal_code
    
    def get_category_info(self, decimal_code: str) -> Optional[Dict]:
        """
        Desimal kodun kategori bilgisini al
        
        Args:
            decimal_code: Desimal kod
            
        Returns:
            Kategori bilgisi sözlüğü veya None
        """
        main_cat = self.extract_main_category(decimal_code)
        
        # Basit arama: ilk 3 hanesine göre ara
        first_three = main_cat.split('-')[0]
        
        for cat_code, cat_info in self.codes_db.get("categories", {}).items():
            if cat_code == first_three or cat_code.startswith(first_three):
                return {
                    'code': main_cat,
                    'category': cat_info.get('name', 'Bilinmiyor'),
                    'department': self._get_department(cat_info),
                }
        
        return None
    
    def _get_department(self, cat_info: Dict) -> str:
        """Kategoriden departmanı çıkar"""
        if 'department' in cat_info:
            return cat_info['department']
        
        # Alt kategorilerden département bul
        for subcat in cat_info.get('subcategories', {}).values():
            if 'department' in subcat:
                return subcat['department']
        
        return "Bilinmiyor"
    
    def get_confidence_score(self, decimal_code: str) -> float:
        """
        Desimal kod güven puanı
        Veritabanında varsa güven artar
        
        Args:
            decimal_code: Desimal kod
            
        Returns:
            Güven puanı (0.0 - 1.0)
        """
        info = self.get_category_info(decimal_code)
        
        if info:
            return 0.95  # Veritabanında bulundu
        else:
            return 0.60  # Regex ile bulundu ama tanımlanamadı
    
    def update_config(self, decimal_code: str, category: str, 
                     department: str, description: str = ""):
        """
        Konfigürasyonu yeni kod ile güncelle
        
        Args:
            decimal_code: Desimal kod
            category: Kategori adı
            department: Departman adı
            description: Açıklama
        """
        # Bu özellik daha sonra genişletilecek
        print(f"Yeni kod eklenir: {decimal_code} → {category} → {department}")


def extract_decimals_from_document(text: str) -> List[Tuple[str, Optional[Dict]]]:
    """
    Dokümandan desimal kodları ve bilgilerini çıkar
    
    Args:
        text: Dokuman metni
        
    Returns:
        (kod, bilgi) tuples listesi
    """
    extractor = DecimalExtractor()
    codes = extractor.extract_decimal_codes(text)
    
    results = []
    for code in codes:
        info = extractor.get_category_info(code)
        results.append((code, info))
    
    return results


if __name__ == "__main__":
    # Test
    extractor = DecimalExtractor()
    
    test_text = """
    Evrak No: 2024/001-903-A1
    Evrak Başlığı: Personel İdari İzin Talep Formu
    """
    
    codes = extractor.extract_decimal_codes(test_text)
    print(f"Bulunan kodlar: {codes}")
    
    for code in codes:
        info = extractor.get_category_info(code)
        print(f"Kod: {code}")
        print(f"Bilgi: {info}")