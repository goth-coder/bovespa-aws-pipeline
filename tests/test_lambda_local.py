#!/usr/bin/env python3
"""
Script para testar Lambda localmente com dados reais.
"""

import sys
import os
import json
import importlib.util
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def import_lambda_module():
    """Import seguro do módulo Lambda."""
    spec = importlib.util.spec_from_file_location(
        'trigger_scraping', 
        'src/lambda/trigger_scraping.py'
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

class MockContext:
    """Mock do contexto Lambda para testes."""
    def __init__(self, request_id='test-local-execution'):
        self.aws_request_id = request_id

def test_lambda_locally():
    """
    Testa a Lambda localmente com configuração real.
    """
    print("🧪 TESTE LOCAL DA LAMBDA - PIPELINE BOVESPA B3")
    print("=" * 60)
    
    # Configurar variáveis de ambiente
    os.environ['BOVESPA_S3_BUCKET'] = 'bovespa-pipeline-data-adri-vic'
    os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
    
    # Carregar credenciais do .env se existir
    env_file = Path('.env')
    if env_file.exists():
        print("📋 Carregando credenciais do .env...")
        with open(env_file) as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
        print("✅ Credenciais carregadas")
    else:
        print("⚠️ Arquivo .env não encontrado - usando credenciais do sistema")
    
    try:
        # Import do módulo Lambda
        print("📦 Importando módulo Lambda...")
        lambda_module = import_lambda_module()
        print("✅ Módulo Lambda importado com sucesso")
        
        # Simular contexto Lambda
        mock_context = MockContext()
        
        # Executar Lambda handler
        print("\n🚀 Executando Lambda handler...")
        print("-" * 40)
        
        result = lambda_module.lambda_handler({}, mock_context)
        
        print(f"\n📊 RESULTADO DA EXECUÇÃO:")
        print(f"Status Code: {result['statusCode']}")
        
        if 'body' in result:
            body = json.loads(result['body'])
            
            if result['statusCode'] == 200:
                print(f"✅ Sucesso: {body.get('message')}")
                
                if 'results' in body:
                    print(f"\n📈 DETALHES DOS RESULTADOS:")
                    
                    # Scraping
                    scraping = body['results'].get('scraping', {})
                    print(f"🔍 Scraping:")
                    print(f"  - Sucesso: {scraping.get('success')}")
                    print(f"  - Ações coletadas: {scraping.get('stocks_collected')}")
                    print(f"  - Endpoints processados: {scraping.get('endpoints_processed')}")
                    
                    # S3
                    s3 = body['results'].get('s3_upload', {})
                    print(f"☁️ S3 Upload:")
                    print(f"  - Sucesso: {s3.get('success')}")
                    print(f"  - Arquivos processados: {s3.get('files_processed')}")
                    print(f"  - Uploads bem-sucedidos: {s3.get('uploads_successful')}")
                    print(f"  - Bucket: {s3.get('bucket')}")
                    
                    # Glue
                    glue = body['results'].get('glue_trigger', {})
                    print(f"🔧 Glue Trigger:")
                    print(f"  - Sucesso: {glue.get('success')}")
                    print(f"  - Mensagem: {glue.get('message', glue.get('jobRunId'))}")
                    
            else:
                print(f"❌ Erro: {body.get('error')}")
        
        print(f"\n🎯 TESTE CONCLUÍDO!")
        
        return result['statusCode'] == 200
        
    except Exception as e:
        print(f"❌ ERRO DURANTE O TESTE: {str(e)}")
        return False

def main():
    """Função principal do script."""
    print("🎯 INICIANDO TESTE LOCAL DA LAMBDA BOVESPA B3")
    print("=" * 60)
    
    success = test_lambda_locally()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 TESTE LOCAL CONCLUÍDO COM SUCESSO!")
        print("📋 Lambda está pronta para deploy na AWS")
        sys.exit(0)
    else:
        print("❌ TESTE LOCAL FALHOU!")
        print("🔧 Verifique os logs acima para identificar problemas")
        sys.exit(1)

if __name__ == "__main__":
    main()
