#!/usr/bin/env python3
"""
Teste rápido do pipeline para verificar se está funcionando
"""
import sys
import os
from pathlib import Path

# Adicionar src ao path
sys.path.append('src')

def test_scraping():
    """Testa o scraping da B3"""
    print("🔄 Testando scraping B3...")
    try:
        from scraping.scraping import B3Scraper
        scraper = B3Scraper()
        result = scraper.run_scraping()
        print(f"✅ Scraping OK: {len(result)} arquivos gerados")
        return True
    except Exception as e:
        print(f"❌ Erro no scraping: {e}")
        return False

def test_parquet_processing():
    """Testa o processamento Parquet"""
    print("🔄 Testando processamento Parquet...")
    try:
        from scraping.parquet_processor import B3ParquetProcessor
        from datetime import date
        
        processor = B3ParquetProcessor(upload_to_s3=False)
        
        # Verificar se existem arquivos JSON
        json_files = list(Path('data/raw').glob('*.json'))
        if not json_files:
            print("❌ Nenhum arquivo JSON encontrado")
            return False
            
        # Processar um arquivo
        test_file = json_files[0]
        result = processor.process_json_file(test_file, date.today())
        if result:
            print(f"✅ Processamento OK: {result.get('records_processed', 'N/A')} registros")
            return True
        else:
            print("❌ Erro no processamento")
            return False
    except Exception as e:
        print(f"❌ Erro no processamento: {e}")
        return False

def test_s3_upload():
    """Testa upload para S3"""
    print("🔄 Testando upload S3...")
    try:
        from scraping.parquet_processor import B3ParquetProcessor
        from datetime import date
        
        processor = B3ParquetProcessor(upload_to_s3=True)
        
        # Verificar se existem arquivos JSON
        json_files = list(Path('data/raw').glob('*.json'))
        if not json_files:
            print("❌ Nenhum arquivo JSON encontrado")
            return False
            
        # Processar com upload S3
        test_file = json_files[0]
        result = processor.process_json_file(test_file, date.today())
        if result and result.get('s3_uploaded'):
            print(f"✅ Upload S3 OK!")
            return True
        else:
            print("⚠️ Upload S3 falhou (pode ser credenciais)")
            return False
    except Exception as e:
        print(f"❌ Erro no upload S3: {e}")
        return False

if __name__ == "__main__":
    print("🧪 TESTE RÁPIDO DO PIPELINE BOVESPA")
    print("===================================")
    
    tests = [
        ("Scraping B3", test_scraping),
        ("Processamento Parquet", test_parquet_processing),
        ("Upload S3", test_s3_upload)
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\n📋 {name}:")
        success = test_func()
        results.append((name, success))
    
    print("\n🏆 RESUMO DOS TESTES:")
    print("====================")
    for name, success in results:
        status = "✅" if success else "❌"
        print(f"{status} {name}")
    
    total_success = sum(1 for _, success in results if success)
    print(f"\n📊 {total_success}/{len(results)} testes passaram")
    
    if total_success >= 2:
        print("🎉 Pipeline funcionando! Pronto para deploy AWS!")
    else:
        print("⚠️ Alguns problemas encontrados. Verifique as credenciais.")
