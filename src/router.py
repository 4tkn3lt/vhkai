"""
Yönlendirme Sistemi Modülü
Sınıflandırılan evrakları ilgili birimlere yönlendir
"""

from typing import Dict, List, Optional, Tuple
import json
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime


@dataclass
class RoutingDecision:
    """Yönlendirme kararı veri yapısı"""
    document_id: str
    decimal_code: str
    category: str
    department: str
    confidence: float
    recommended_action: str
    urgency: str  # low, medium, high
    notes: str = ""
    timestamp: str = ""
    
    def to_dict(self) -> Dict:
        """Sözlüğe dönüştür"""
        return {
            'document_id': self.document_id,
            'decimal_code': self.decimal_code,
            'category': self.category,
            'department': self.department,
            'confidence': self.confidence,
            'recommended_action': self.recommended_action,
            'urgency': self.urgency,
            'notes': self.notes,
            'timestamp': self.timestamp or datetime.now().isoformat()
        }


class Router:
    """Evrak yönlendirme sistemi"""
    
    def __init__(self, departments_config: str = "config/departments.json"):
        """
        Başlatıcı
        
        Args:
            departments_config: Departman konfigürasyon dosyası
        """
        self.departments = self._load_departments(departments_config)
        self.routing_history = []
        self.urgency_keywords = {
            'acil': 'high',
            'derhal': 'high',
            'ivedi': 'high',
            'hızlı': 'high',
            'saatler': 'high',
            'hafta': 'medium',
            'aylık': 'low',
            'normal': 'low'
        }
    
    def _load_departments(self, config_path: str) -> Dict:
        """Departman konfigürasyonunu yükle"""
        default_departments = {
            "İnsan Kaynakları": {
                "email": "ik@example.edu.tr",
                "phone": "0-000",
                "responsible": "HR Manager",
                "expected_processing_time": "5 business days"
            },
            "Muhasebe": {
                "email": "muhasebe@example.edu.tr",
                "phone": "0-000",
                "responsible": "Accounting Manager",
                "expected_processing_time": "3 business days"
            },
            "Eğitim Koordinatörlüğü": {
                "email": "egitim@example.edu.tr",
                "phone": "0-000",
                "responsible": "Education Coordinator",
                "expected_processing_time": "2 business days"
            },
            "Müdürlük": {
                "email": "rector@example.edu.tr",
                "phone": "0-000",
                "responsible": "Rector",
                "expected_processing_time": "1 business day"
            }
        }
        
        try:
            if Path(config_path).exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Uyarı: Departman konfigürasyonu yüklenemedi - {e}")
        
        return default_departments
    
    def determine_urgency(self, text: str) -> str:
        """
        Metinden aciliyet seviyesini belirle
        
        Args:
            text: Evrak metni
            
        Returns:
            Aciliyet seviyesi (low, medium, high)
        """
        text_lower = text.lower()
        urgency_scores = {'low': 0, 'medium': 0, 'high': 0}
        
        for keyword, urgency in self.urgency_keywords.items():
            if keyword in text_lower:
                urgency_scores[urgency] += 1
        
        if urgency_scores['high'] > 0:
            return 'high'
        elif urgency_scores['medium'] > 0:
            return 'medium'
        else:
            return 'low'
    
    def get_recommended_action(self, category: str, confidence: float) -> str:
        """
        Kategori ve güven puanına göre önerilen aksiyonu belirle
        
        Args:
            category: Evrak kategorisi
            confidence: Sınıflandırma güven puanı
            
        Returns:
            Önerilen aksiyon
        """
        if confidence < 0.6:
            return "El ile inceleme ve onaydan geçirilmelidir"
        elif confidence < 0.8:
            return f"{category} olarak işleme alınması önerilir (onay bekleniyor)"
        else:
            return f"Otomatik olarak {category} kategorisinde işleme alınabilir"
    
    def make_routing_decision(self, 
                            document_id: str,
                            decimal_code: str,
                            category: str,
                            department: str,
                            confidence: float,
                            text: str) -> RoutingDecision:
        """
        Yönlendirme kararı oluştur
        
        Args:
            document_id: Evrak ID
            decimal_code: Desimal kod
            category: Kategori
            department: Departman
            confidence: Güven puanı
            text: Evrak metni
            
        Returns:
            RoutingDecision nesnesi
        """
        urgency = self.determine_urgency(text)
        action = self.get_recommended_action(category, confidence)
        
        decision = RoutingDecision(
            document_id=document_id,
            decimal_code=decimal_code,
            category=category,
            department=department,
            confidence=confidence,
            recommended_action=action,
            urgency=urgency,
            timestamp=datetime.now().isoformat()
        )
        
        self.routing_history.append(decision)
        return decision
    
    def get_department_info(self, department_name: str) -> Optional[Dict]:
        """
        Departman bilgisini al
        
        Args:
            department_name: Departman adı
            
        Returns:
            Departman bilgisi sözlüğü
        """
        return self.departments.get(department_name, {
            'email': 'unknown@example.edu.tr',
            'phone': 'unknown',
            'responsible': 'Unknown',
            'expected_processing_time': 'Unknown'
        })
    
    def format_routing_report(self, decision: RoutingDecision) -> str:
        """
        Yönlendirme raporunu formatla
        
        Args:
            decision: Yönlendirme kararı
            
        Returns:
            Formatlanmış rapor
        """
        dept_info = self.get_department_info(decision.department)
        
        report = f"""
╔════════════════════════════════════════════════════════════════╗
║                    EVRAK YÖNLENDİRME RAPORU                    ║
╚════════════════════════════════════════════════════════════════╝

📄 Evrak Bilgileri:
  ├─ Evrak ID: {decision.document_id}
  ├─ Desimal Kod: {decision.decimal_code}
  └─ İşlem Tarihi: {decision.timestamp}

🏷️  Sınıflandırma:
  ├─ Kategori: {decision.category}
  ├─ Güven Puanı: {decision.confidence:.1%}
  └─ Aciliyet: {decision.urgency.upper()}

🎯 Yönlendirme Kararı:
  ├─ Hedef Bölüm: {decision.department}
  ├─ İletişim: {dept_info.get('email', 'N/A')}
  ├─ Telefon: {dept_info.get('phone', 'N/A')}
  ├─ Sorumlu: {dept_info.get('responsible', 'N/A')}
  └─ Beklenen İşlem Süresi: {dept_info.get('expected_processing_time', 'N/A')}

💡 Önerilen Aksiyon:
  {decision.recommended_action}

📝 Notlar:
  {decision.notes or '(ek not yok)'}

════════════════════════════════════════════════════════════════
"""
        return report
    
    def export_routing_history(self, output_file: str):
        """
        Yönlendirme geçmişini JSON olarak dışa aktar
        
        Args:
            output_file: Çıkış dosyası
        """
        try:
            data = [d.to_dict() for d in self.routing_history]
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"✓ Yönlendirme geçmişi kaydedildi: {output_file}")
        except Exception as e:
            print(f"Hata: Yönlendirme geçmişi kaydedilemedi - {e}")


if __name__ == "__main__":
    # Test
    router = Router()
    
    decision = router.make_routing_decision(
        document_id="DOC-001",
        decimal_code="2024/001-903-A1",
        category="Personel İşleri (903)",
        department="İnsan Kaynakları",
        confidence=0.92,
        text="Yaşlı validesinin tedavisi için idari izin talebinde bulunmuştur"
    )
    
    print(router.format_routing_report(decision))