#!/usr/bin/env python3
"""
VHKAI - Kamu Evrak Sınıflandırma ve Yönlendirme Sistemi
Ana giriş noktası

Kullanım:
    python main.py --file <pdf_dosyası>
    python main.py --directory <pdf_dizini>
"""

import argparse
import sys
from pathlib import Path

from src.pdf_processor import PDFProcessor
from src.decimal_extractor import DecimalExtractor, extract_decimals_from_document
from src.classifier import SimpleKeywordClassifier
from src.router import Router


def process_single_document(pdf_path: str):
    """
    Tek bir PDF dosyasını işle
    
    Args:
        pdf_path: PDF dosyasının yolu
    """
    print(f"\n{'='*70}")
    print(f"📄 Evrak İşleniyor: {pdf_path}")
    print(f"{'='*70}\n")
    
    # 1. PDF'den metin çıkar
    print("1️⃣  PDF metin çıkarılıyor...")
    processor = PDFProcessor()
    text = processor.extract_text_from_pdf(pdf_path)
    
    if not text:
        print("❌ PDF'den metin çıkarılamadı!")
        return
    
    print(f"   ✓ {len(text)} karakter çıkarıldı")
    
    # 2. Desimal kodu çıkar
    print("\n2️⃣  Desimal kod aranıyor...")
    extractor = DecimalExtractor()
    decimal_results = extract_decimals_from_document(text)
    
    if decimal_results:
        for code, info in decimal_results:
            print(f"   ✓ Kod bulundu: {code}")
            if info:
                print(f"     → {info['category']} ({info['department']})")
    else:
        print("   ⚠️  Desimal kod bulunamadı")
    
    # 3. Sınıflandır
    print("\n3️⃣  Evrak sınıflandırılıyor...")
    classifier = SimpleKeywordClassifier()
    classification, confidence = classifier.classify(text)
    
    print(f"   ✓ Kategori: {classification['category']}")
    print(f"   ✓ Departman: {classification['department']}")
    print(f"   ✓ Güven Puanı: {confidence:.1%}")
    if classification.get('matched_keywords'):
        print(f"   ✓ Eşleşen Anahtar Kelimeler: {', '.join(classification['matched_keywords'])}")
    
    # 4. Yönlendir
    print("\n4️⃣  Yönlendirme kararı veriliyor...")
    router = Router()
    
    # Desimal koddan bilgi kullan varsa
    decimal_code = decimal_results[0][0] if decimal_results else "Bulunamadı"
    
    decision = router.make_routing_decision(
        document_id=Path(pdf_path).stem,
        decimal_code=decimal_code,
        category=classification['category'],
        department=classification['department'],
        confidence=confidence,
        text=text
    )
    
    # 5. Rapor göster
    print("\n5️⃣  Yönlendirme Raporu:")
    report = router.format_routing_report(decision)
    print(report)
    
    print(f"\n{'='*70}")
    print("✅ İşlem Tamamlandı")
    print(f"{'='*70}\n")


def process_directory(directory_path: str):
    """
    Dizindeki tüm PDF dosyalarını işle
    
    Args:
        directory_path: PDF dizinin yolu
    """
    pdf_dir = Path(directory_path)
    pdf_files = list(pdf_dir.glob('*.pdf'))
    
    if not pdf_files:
        print(f"❌ {directory_path} dizininde PDF dosyası bulunamadı!")
        return
    
    print(f"\n📁 Dizin işleniyor: {directory_path}")
    print(f"📊 Toplam PDF: {len(pdf_files)}\n")
    
    results = []
    for i, pdf_file in enumerate(pdf_files, 1):
        print(f"\n[{i}/{len(pdf_files)}] ", end="")
        
        try:
            # Hafif versiyonunda sadece sınıflandırmayı yap
            processor = PDFProcessor()
            text = processor.extract_text_from_pdf(str(pdf_file))
            
            if text:
                classifier = SimpleKeywordClassifier()
                classification, confidence = classifier.classify(text)
                
                results.append({
                    'file': pdf_file.name,
                    'category': classification['category'],
                    'department': classification['department'],
                    'confidence': f"{confidence:.1%}"
                })
                
                print(f"✓ {pdf_file.name} → {classification['category']}")
            else:
                print(f"⚠️  {pdf_file.name} → Metin çıkarılamadı")
                
        except Exception as e:
            print(f"❌ {pdf_file.name} → Hata: {e}")
    
    # Özet tablo
    print(f"\n\n{'='*70}")
    print("📊 İŞLEM ÖZETİ")
    print(f"{'='*70}")
    
    for result in results:
        print(f"  {result['file']:<30} → {result['category']:<25} ({result['confidence']})")
    
    print(f"{'='*70}\n")


def main():
    """Ana fonksiyon"""
    parser = argparse.ArgumentParser(
        description='VHKAI - Kamu Evrak Sınıflandırma ve Yönlendirme Sistemi',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Örnekler:
  python main.py --file evrak.pdf
  python main.py --directory ./data/raw
        """
    )
    
    parser.add_argument(
        '--file',
        help='Tek bir PDF dosyasını işle'
    )
    parser.add_argument(
        '--directory',
        help='Dizindeki tüm PDF dosyalarını işle'
    )
    
    args = parser.parse_args()
    
    if args.file:
        if not Path(args.file).exists():
            print(f"❌ Dosya bulunamadı: {args.file}")
            sys.exit(1)
        process_single_document(args.file)
        
    elif args.directory:
        if not Path(args.directory).exists():
            print(f"❌ Dizin bulunamadı: {args.directory}")
            sys.exit(1)
        process_directory(args.directory)
        
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()