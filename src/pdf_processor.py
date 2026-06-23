"""
PDF İşleme Modülü
PDF dosyalarından metin çıkarma ve işleme
"""

import PyPDF2
import pdfplumber
import re
from pathlib import Path
from typing import Dict, List, Tuple


class PDFProcessor:
    """PDF dosyalarını işlemek için ana sınıf"""
    
    def __init__(self):
        self.extracted_text = ""
        self.metadata = {}
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        PDF dosyasından metin çıkar
        
        Args:
            pdf_path: PDF dosyasının yolu
            
        Returns:
            Çıkarılan metin
        """
        try:
            text = ""
            
            # pdfplumber ile metin çıkar
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() or ""
                    text += "\n"
            
            self.extracted_text = text
            return text
            
        except Exception as e:
            print(f"Hata: PDF metin çıkarma başarısız - {e}")
            return ""
    
    def clean_text(self, text: str) -> str:
        """
        Metni temizle ve normalleştir
        
        Args:
            text: İşlenecek metin
            
        Returns:
            Temizlenmiş metin
        """
        # Ekstra boşlukları kaldır
        text = re.sub(r'\s+', ' ', text)
        
        # Özel karakterleri temizle (ama Türkçe karakterleri koru)
        text = re.sub(r'[^\w\s\.\,\-\(\)ç-ğ\n]', '', text)
        
        return text.strip()
    
    def get_first_lines(self, text: str, num_lines: int = 10) -> str:
        """
        Metnin ilk N satırını al
        
        Args:
            text: Metin
            num_lines: Alınacak satır sayısı
            
        Returns:
            İlk N satır
        """
        lines = text.split('\n')
        return '\n'.join(lines[:num_lines])
    
    def extract_metadata(self, pdf_path: str) -> Dict:
        """
        PDF metadatasını çıkar
        
        Args:
            pdf_path: PDF dosyasının yolu
            
        Returns:
            Metadata sözlüğü
        """
        try:
            with pdfplumber.open(pdf_path) as pdf:
                metadata = {
                    'pages': len(pdf.pages),
                    'title': pdf.metadata.get('Title', 'Bilinmiyor'),
                    'author': pdf.metadata.get('Author', 'Bilinmiyor'),
                }
            self.metadata = metadata
            return metadata
            
        except Exception as e:
            print(f"Hata: Metadata çıkarma başarısız - {e}")
            return {}


def process_pdf_batch(pdf_directory: str) -> Dict[str, str]:
    """
    Bir dizindeki tüm PDF dosyalarını işle
    
    Args:
        pdf_directory: PDF dosyalarının bulunduğu dizin
        
    Returns:
        Dosya adları ve çıkarılan metinleri içeren sözlük
    """
    processor = PDFProcessor()
    results = {}
    
    pdf_path = Path(pdf_directory)
    pdf_files = pdf_path.glob('*.pdf')
    
    for pdf_file in pdf_files:
        text = processor.extract_text_from_pdf(str(pdf_file))
        results[pdf_file.name] = text
    
    return results


if __name__ == "__main__":
    # Test
    processor = PDFProcessor()
    # test_pdf = "data/raw/test.pdf"
    # text = processor.extract_text_from_pdf(test_pdf)
    # print(f"Çıkarılan metin: {text[:500]}")