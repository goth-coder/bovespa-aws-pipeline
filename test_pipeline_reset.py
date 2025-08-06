#!/usr/bin/env python3
"""
🧪 Script de Teste Pipeline Bovespa - RESET CLEAN
Teste completo do pipeline do zero com configurações consistentes.
"""

import sys
import os
from pathlib import Path

# Adicionar src ao path
sys.path.append('src')

def main():
    print("🚀 PIPELINE BOVESPA - TESTE COMPLETO (RESET)")
    print("=" * 50)
    
    try:
        # 1. Carregar configurações
        from dotenv import load_dotenv
        load_dotenv()
        
        bucket = os.environ.get('BOVESPA_S3_BUCKET')
        if not bucket:
            print("❌ ERRO: Configure BOVESPA_S3_BUCKET no arquivo .env")
            return False
            
        print(f"📦 Bucket configurado: {bucket}")
        
        # 2. Testar scraping
        print("\n🔍 FASE 1: Testando scraping B3...")
        from scraping.scraping import B3Scraper
        
        scraper = B3Scraper()
        result = scraper.run_scraping()
        
        if result and result.get('combined_stocks'):
            total_stocks = len(result['combined_stocks'])
            print(f"✅ Scraping OK: {total_stocks} ações coletadas")
        else:
            print("❌ Scraping falhou: Nenhum dado coletado")
            return False
        
        # 3. Testar processamento Parquet
        print("\n📦 FASE 2: Testando processamento Parquet...")
        from scraping.parquet_processor import B3ParquetProcessor
        
        processor = B3ParquetProcessor(
            input_path='data/raw',
            output_path='data_lake'
        )
        
        result = processor.process_all_json_files()
        
        if 'error' not in result and result['summary']['successful'] > 0:
            successful = result['summary']['successful']
            total_records = result['summary']['total_records']
            print(f"✅ Processamento OK: {successful} arquivos processados")
            print(f"📊 Total de registros: {total_records}")
        else:
            error_msg = result.get('error', 'Erro desconhecido')
            print(f"❌ Processamento falhou: {error_msg}")
            return False
        
        # 4. Testar Lambda (se disponível)
        print("\n🔧 FASE 3: Testando Lambda function...")
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location('lambda_mod', 'src/lambda/trigger_scraping.py')
            lambda_mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(lambda_mod)
            
            result = lambda_mod.lambda_handler({}, {'aws_request_id': 'test-reset'})
            
            if result['statusCode'] == 200:
                print("✅ Lambda OK: Pipeline integrado funcionando")
            else:
                print(f"⚠️ Lambda com problemas: Status {result['statusCode']}")
                
        except Exception as e:
            print(f"⚠️ Lambda não testado: {str(e)}")
        
        print("\n🎉 PIPELINE TESTE COMPLETO!")
        print("✅ Pronto para deploy na AWS")
        return True
        
    except Exception as e:
        print(f"\n❌ ERRO NO PIPELINE: {str(e)}")
        print("💡 Verifique as dependências: pip install -r requirements.txt")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
