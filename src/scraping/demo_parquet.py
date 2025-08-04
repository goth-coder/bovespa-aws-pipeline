"""
Script de demonstração do processador Parquet B3.
Executa o processamento dos dados JSON para Parquet.
"""

import sys
import os
from pathlib import Path

# Adicionar path para imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def main():
    """
    Demonstra o uso do processador Parquet.
    """
    print("🚀 Demonstração - Processador Parquet B3")
    print("=" * 60)
    
    try:
        from parquet_processor import B3ParquetProcessor
        
        # Configurar caminhos
        input_path = current_dir.parent.parent / "data" / "raw"
        output_path = current_dir.parent.parent / "data_lake"
        
        print(f"📁 Diretório de entrada: {input_path}")
        print(f"📁 Diretório de saída: {output_path}")
        
        # Verificar se existem dados
        json_files = list(input_path.glob("*.json"))
        if not json_files:
            print("❌ Nenhum arquivo JSON encontrado")
            print(f"   Verifique se existem dados em: {input_path}")
            return
        
        print(f"✅ Encontrados {len(json_files)} arquivos JSON")
        
        # Inicializar processador
        processor = B3ParquetProcessor(
            input_path=str(input_path),
            output_path=str(output_path)
        )
        
        # Executar processamento
        print("\n🔄 Iniciando processamento...")
        results = processor.process_all_json_files()
        
        # Verificar resultados
        if 'error' in results:
            print(f"❌ Erro: {results['error']}")
            return
        
        # Exibir resultados
        print("\n✅ Processamento concluído!")
        print("📊 Resumo:")
        print(f"  📈 Arquivos processados: {results['summary']['successful']}")
        print(f"  ❌ Arquivos com erro: {results['summary']['failed']}")
        print(f"  📋 Total de registros: {results['summary']['total_records']}")
        
        # Mostrar estrutura criada
        if output_path.exists():
            print(f"\n📂 Estrutura criada em {output_path}:")
            
            for root, dirs, files in os.walk(output_path):
                level = root.replace(str(output_path), '').count(os.sep)
                indent = '  ' * level
                folder_name = os.path.basename(root) or 'data_lake'
                print(f"{indent}📁 {folder_name}/")
                
                subindent = '  ' * (level + 1)
                for file in files:
                    if file.endswith('.parquet'):
                        file_path = Path(root) / file
                        size_mb = file_path.stat().st_size / 1024 / 1024
                        print(f"{subindent}📄 {file} ({size_mb:.2f} MB)")
        
        print("\n🎯 Estrutura compatível com S3!")
        print("   Quando configurar o bucket S3, use o mesmo padrão:")
        print("   s3://seu-bucket/raw/ano=2025/mes=08/dia=03/arquivo.parquet")
        
    except ImportError as e:
        print(f"❌ Erro de dependências: {e}")
        print("\n📦 Para instalar as dependências:")
        print("   pip install pandas pyarrow")
        print("   ou")
        print("   pip install -r requirements.txt")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

if __name__ == "__main__":
    main()
