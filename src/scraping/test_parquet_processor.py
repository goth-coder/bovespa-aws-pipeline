"""
Script de teste para o processador Parquet B3.
Testa a conversão de dados JSON para Parquet com estrutura particionada.
"""

import sys
import os
from pathlib import Path
from datetime import date

# Adicionar path para imports
sys.path.insert(0, os.path.dirname(__file__))

def test_parquet_processor():
    """
    Testa o processamento de dados JSON para Parquet.
    """
    try:
        from parquet_processor import B3ParquetProcessor
        
        print("🔍 Testando B3ParquetProcessor...")
        print("-" * 50)
        
        # Inicializar processador
        processor = B3ParquetProcessor(
            input_path="../../data/raw",
            output_path="../../data_lake"
        )
        
        # Verificar se existem arquivos JSON
        json_files = list(processor.input_path.glob("*.json"))
        print(f"📁 Arquivos JSON encontrados: {len(json_files)}")
        
        for json_file in json_files:
            print(f"  📄 {json_file.name}")
        
        if not json_files:
            print("❌ Nenhum arquivo JSON encontrado para processar")
            return False
        
        # Executar processamento
        print("\n🚀 Iniciando processamento...")
        results = processor.process_all_json_files(target_date=date.today())
        
        # Verificar resultados
        if 'error' in results:
            print(f"❌ Erro: {results['error']}")
            return False
        
        # Exibir resultados
        print("\n✅ Processamento concluído!")
        print("📊 Resumo:")
        print(f"  📈 Arquivos processados: {results['summary']['successful']}")
        print(f"  ❌ Arquivos com erro: {results['summary']['failed']}")
        print(f"  📋 Total de registros: {results['summary']['total_records']}")
        
        # Listar arquivos gerados
        if results['files_processed']:
            print("\n📁 Arquivos Parquet gerados:")
            for file_info in results['files_processed']:
                size_mb = file_info.get('file_size_mb', 0)
                print(f"  📄 {file_info['output_file']}")
                print(f"      Registros: {file_info['records_processed']}")
                print(f"      Tamanho: {size_mb:.2f} MB")
                
                # Verificar se arquivo existe
                if Path(file_info['output_file']).exists():
                    print("      Status: ✅ Arquivo criado")
                else:
                    print("      Status: ❌ Arquivo não encontrado")
        
        return True
        
    except ImportError as e:
        print(f"❌ Erro de import: {e}")
        print("Certifique-se de que as dependências estão instaladas:")
        print("  pip install pandas pyarrow")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

def verify_data_structure():
    """
    Verifica se a estrutura de dados gerada está correta.
    """
    try:
        import pandas as pd
        
        print("\n🔍 Verificando estrutura de dados gerada...")
        print("-" * 50)
        
        # Procurar arquivos parquet gerados
        data_lake_path = Path("../../data_lake")
        
        if not data_lake_path.exists():
            print("❌ Diretório data_lake não encontrado")
            return False
        
        # Encontrar arquivos parquet
        parquet_files = list(data_lake_path.rglob("*.parquet"))
        
        if not parquet_files:
            print("❌ Nenhum arquivo Parquet encontrado")
            return False
        
        print("📁 Estrutura de diretórios criada:")
        
        # Listar estrutura de diretórios
        for root, dirs, files in os.walk(data_lake_path):
            level = root.replace(str(data_lake_path), '').count(os.sep)
            indent = ' ' * 2 * level
            print(f"{indent}📂 {os.path.basename(root)}/")
            
            subindent = ' ' * 2 * (level + 1)
            for file in files:
                if file.endswith('.parquet'):
                    file_path = Path(root) / file
                    size_mb = file_path.stat().st_size / 1024 / 1024
                    print(f"{subindent}📄 {file} ({size_mb:.2f} MB)")
        
        # Analisar um arquivo como exemplo
        sample_file = parquet_files[0]
        print(f"\n🔍 Analisando arquivo exemplo: {sample_file.name}")
        
        df = pd.read_parquet(sample_file)
        
        print("📊 Informações do DataFrame:")
        print(f"  Registros: {len(df)}")
        print(f"  Colunas: {len(df.columns)}")
        print(f"  Tamanho em memória: {df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB")
        
        print("\n📋 Colunas encontradas:")
        for col in df.columns:
            dtype = df[col].dtype
            non_null = df[col].count()
            print(f"  📊 {col}: {dtype} ({non_null} valores não-nulos)")
        
        print("\n📈 Primeiras 3 linhas:")
        print(df[['codigo', 'acao', 'part_percent', 'processed_at']].head(3).to_string())
        
        return True
        
    except ImportError as e:
        print(f"❌ Pandas não disponível: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro ao verificar dados: {e}")
        return False

def main():
    """
    Executa todos os testes.
    """
    print("🧪 Iniciando testes do processador Parquet B3")
    print("=" * 60)
    
    # Teste 1: Processamento JSON -> Parquet
    success1 = test_parquet_processor()
    
    # Teste 2: Verificação da estrutura
    success2 = verify_data_structure()
    
    print("\n" + "=" * 60)
    if success1 and success2:
        print("✅ Todos os testes passaram! Processador funcionando corretamente.")
        print("\n📋 Próximos passos:")
        print("  1. Configurar credenciais AWS")
        print("  2. Criar bucket S3")
        print("  3. Implementar upload automático")
    else:
        print("❌ Alguns testes falharam. Verifique os erros acima.")

if __name__ == "__main__":
    main()
