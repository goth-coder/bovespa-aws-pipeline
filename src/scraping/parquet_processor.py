"""
Processador de dados B3 para conversão JSON -> Parquet
com estrutura de particionamento preparada para S3.

Converte dados brutos JSON para formato Parquet otimizado
seguindo estrutura: data_lake/ano=YYYY/mes=MM/dia=DD/arquivo.parquet
"""

import json
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from datetime import datetime, date
from typing import Dict, Optional, Tuple
from pathlib import Path
import boto3
import os
from dotenv import load_dotenv
from botocore.exceptions import ClientError

# Carregar variáveis de ambiente do .env
load_dotenv()

try:
    from .config import setup_logger
except ImportError:
    # Fallback para execução direta
    from config import setup_logger

# Configurar logger
logger = setup_logger(__name__)


class B3ParquetProcessor:
    """
    Classe para processar dados JSON da B3 e converter para Parquet
    com estrutura de particionamento compatível com S3.
    """
    
    def __init__(self, input_path: str = "data/raw", output_path: str = "data_lake", upload_to_s3: bool = True):
        """
        Inicializa o processador de Parquet.
        
        Args:
            input_path (str): Diretório com arquivos JSON de entrada
            output_path (str): Diretório base para estrutura particionada
            upload_to_s3 (bool): Se deve fazer upload automático para S3
        """
        self.input_path = Path(input_path)
        self.output_path = Path(output_path)
        self.processed_files = []
        self.upload_to_s3 = upload_to_s3
        
        # Configurar S3 se habilitado
        if self.upload_to_s3:
            self.s3_bucket = os.getenv('BOVESPA_S3_BUCKET', 'bovespa-pipeline-data-adri-vic')
            try:
                self.s3_client = boto3.client('s3')
                logger.info(f"✅ Upload S3 habilitado para bucket: {self.s3_bucket}")
            except Exception as e:
                logger.warning(f"⚠️ Erro ao configurar S3: {e}. Upload desabilitado.")
                self.upload_to_s3 = False
        
        logger.info("B3ParquetProcessor inicializado")
        logger.info(f"Input: {self.input_path}")
        logger.info(f"Output: {self.output_path}")
    
    def upload_file_to_s3(self, local_file_path: Path, s3_key: str) -> bool:
        """
        Faz upload de arquivo para S3.
        
        Args:
            local_file_path (Path): Caminho local do arquivo
            s3_key (str): Chave do arquivo no S3
            
        Returns:
            bool: True se upload foi bem-sucedido, False caso contrário
        """
        if not self.upload_to_s3:
            logger.info("🔄 Upload S3 desabilitado, pulando...")
            return False
            
        try:
            # Verificar se arquivo existe
            if not local_file_path.exists():
                logger.error(f"❌ Arquivo não encontrado: {local_file_path}")
                return False
            
            # Obter tamanho do arquivo para log
            file_size = local_file_path.stat().st_size / (1024 * 1024)  # MB
            
            logger.info(f"📤 Fazendo upload: {local_file_path.name} ({file_size:.2f} MB)")
            logger.info(f"🎯 Destino S3: s3://{self.s3_bucket}/{s3_key}")
            
            # Upload para S3
            self.s3_client.upload_file(
                str(local_file_path),
                self.s3_bucket,
                s3_key,
                ExtraArgs={
                    'ServerSideEncryption': 'AES256',
                    'StorageClass': 'STANDARD'
                }
            )
            
            logger.info(f"✅ Upload concluído: s3://{self.s3_bucket}/{s3_key}")
            return True
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            logger.error(f"❌ Erro AWS S3 ({error_code}): {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Erro inesperado no upload: {e}")
            return False
    
    def validate_stock_data(self, data: Dict) -> bool:
        """
        Valida estrutura básica dos dados de ações.
        
        Args:
            data (Dict): Dados JSON para validação
            
        Returns:
            bool: True se dados são válidos, False caso contrário
        """
        if not isinstance(data, dict):
            logger.error("❌ Dados não são um dicionário válido")
            return False
        
        # Verificar se há dados de ações
        stocks_data = data.get('stocks_data', data.get('combined_stocks', []))
        
        if not stocks_data:
            logger.warning("⚠️ Nenhum dado de ação encontrado")
            return False
            
        if not isinstance(stocks_data, list):
            logger.error("❌ stocks_data deve ser uma lista")
            return False
            
        if len(stocks_data) == 0:
            logger.warning("⚠️ Lista de ações está vazia")
            return False
            
        logger.info(f"✅ Dados válidos: {len(stocks_data)} registros encontrados")
        return True
    
    def clean_and_validate_dataframe(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict]:
        """
        Valida e limpa dados de ações.
        
        Args:
            df (pd.DataFrame): DataFrame com dados brutos
            
        Returns:
            Tuple[pd.DataFrame, Dict]: DataFrame limpo e relatório de validação
        """
        validation_report = {
            'original_records': len(df),
            'null_values_fixed': 0,
            'invalid_records_removed': 0,
            'data_type_corrections': 0,
            'final_records': 0
        }
        
        logger.info(f"Iniciando validação de {len(df)} registros...")
        
        # 1. Remover registros completamente vazios
        df = df.dropna(how='all')
        
        # 2. Validar campos obrigatórios
        required_fields = ['codigo', 'acao']
        for field in required_fields:
            if field in df.columns:
                before_count = len(df)
                df = df.dropna(subset=[field])
                removed = before_count - len(df)
                if removed > 0:
                    validation_report['invalid_records_removed'] += removed
                    logger.warning(f"Removidos {removed} registros sem {field}")
        
        # 3. Limpar e converter tipos de dados
        df = self._clean_data_types(df, validation_report)
        
        # 4. Remover duplicatas
        before_dup = len(df)
        df = df.drop_duplicates(subset=['codigo'], keep='first')
        removed_dup = before_dup - len(df)
        if removed_dup > 0:
            logger.info(f"Removidas {removed_dup} duplicatas")
        
        validation_report['final_records'] = len(df)
        
        logger.info(f"Validação concluída: {validation_report['final_records']} registros válidos")
        return df, validation_report
    
    def _clean_data_types(self, df: pd.DataFrame, report: Dict) -> pd.DataFrame:
        """
        Limpa e converte tipos de dados para otimização Parquet.
        
        Args:
            df (pd.DataFrame): DataFrame original
            report (Dict): Relatório de validação para atualizar
            
        Returns:
            pd.DataFrame: DataFrame com tipos otimizados
        """
        df = df.copy()
        
        # Converter campos percentuais (formato brasileiro "0,503" -> 0.503)
        percentage_fields = ['part_percent', 'part_accumulated']
        for field in percentage_fields:
            if field in df.columns:
                df[field] = self._convert_brazilian_decimal(df[field])
                report['data_type_corrections'] += 1
        
        # Converter campos de quantidade
        quantity_fields = ['theoretical_qty']
        for field in quantity_fields:
            if field in df.columns:
                df[field] = self._convert_brazilian_number(df[field])
                report['data_type_corrections'] += 1
        
        # Preencher valores nulos com padrões apropriados ANTES de converter para category
        if 'setor' in df.columns:
            df['setor'] = df['setor'].fillna('N/A')
        if 'subsetor' in df.columns:
            df['subsetor'] = df['subsetor'].fillna('N/A')
        if 'segmento' in df.columns:
            df['segmento'] = df['segmento'].fillna('N/A')
        
        # Otimizar strings para category (economia de espaço) APÓS preencher nulos
        categorical_fields = ['codigo', 'acao', 'setor', 'subsetor', 'segmento', 
                            'endpoint_name', 'endpoint_description']
        for field in categorical_fields:
            if field in df.columns:
                df[field] = df[field].astype('category')
        
        report['null_values_fixed'] += df.isnull().sum().sum()
        
        return df
    
    def _convert_brazilian_decimal(self, series: pd.Series) -> pd.Series:
        """
        Converte números decimais do formato brasileiro (vírgula) para formato padrão.
        
        Args:
            series (pd.Series): Série com números no formato brasileiro
            
        Returns:
            pd.Series: Série com números convertidos para float
        """
        def convert_value(value):
            if pd.isna(value):
                return 0.0
            if isinstance(value, (int, float)):
                return float(value)
            
            # Converter string brasileira para float
            try:
                # Remover espaços e converter vírgula para ponto
                clean_value = str(value).strip().replace(',', '.')
                # Remover pontos que não sejam o decimal (milhares)
                parts = clean_value.split('.')
                if len(parts) > 2:
                    # Múltiplos pontos: último é decimal, anteriores são milhares
                    clean_value = ''.join(parts[:-1]) + '.' + parts[-1]
                return float(clean_value)
            except (ValueError, AttributeError):
                logger.warning(f"Não foi possível converter '{value}' para float")
                return 0.0
        
        return series.apply(convert_value)
    
    def _convert_brazilian_number(self, series: pd.Series) -> pd.Series:
        """
        Converte números inteiros do formato brasileiro.
        
        Args:
            series (pd.Series): Série com números no formato brasileiro
            
        Returns:
            pd.Series: Série com números convertidos para int
        """
        def convert_value(value):
            if pd.isna(value):
                return 0
            if isinstance(value, (int, float)):
                return int(value)
            
            try:
                # Remover pontos e espaços (separadores de milhares)
                clean_value = str(value).replace('.', '').replace(' ', '')
                return int(float(clean_value))
            except (ValueError, AttributeError):
                logger.warning(f"Não foi possível converter '{value}' para int")
                return 0
        
        return series.apply(convert_value)
    
    def add_processing_metadata(self, df: pd.DataFrame, source_file: str) -> pd.DataFrame:
        """
        Adiciona metadados de processamento ao DataFrame.
        
        Args:
            df (pd.DataFrame): DataFrame original
            source_file (str): Nome do arquivo fonte
            
        Returns:
            pd.DataFrame: DataFrame com metadados adicionados
        """
        df = df.copy()
        
        # Timestamp de processamento
        df['processed_at'] = datetime.now()
        
        # Data de referência para particionamento
        df['partition_date'] = date.today()
        
        # Arquivo fonte
        df['source_file'] = source_file
        
        # Hash para detecção de duplicatas futuras
        df['record_hash'] = pd.util.hash_pandas_object(
            df[['codigo', 'acao', 'part_percent']], 
            index=False
        )
        
        return df
    
    def create_partition_path(self, target_date: date, filename: str) -> Path:
        """
        Cria estrutura de diretório particionado.
        
        Args:
            target_date (date): Data para particionamento
            filename (str): Nome do arquivo final
            
        Returns:
            Path: Caminho completo do arquivo
        """
        partition_dir = (
            self.output_path / 
            f"ano={target_date.year}" / 
            f"mes={target_date.month:02d}" / 
            f"dia={target_date.day:02d}"
        )
        
        # Criar diretório se não existir
        partition_dir.mkdir(parents=True, exist_ok=True)
        
        return partition_dir / filename
    
    def save_to_parquet(self, df: pd.DataFrame, filepath: Path) -> bool:
        """
        Salva DataFrame em formato Parquet otimizado.
        
        Args:
            df (pd.DataFrame): DataFrame para salvar
            filepath (Path): Caminho do arquivo
            
        Returns:
            bool: True se salvou com sucesso
        """
        try:
            # Configurações de otimização para Parquet
            table = pa.Table.from_pandas(df)
            
            pq.write_table(
                table, 
                filepath,
                # Compressão SNAPPY é boa para AWS S3
                compression='snappy',
                # Usar engine pyarrow para melhor performance
                use_dictionary=True,
                # Metadados para compatibilidade
                write_statistics=True
            )
            
            file_size = filepath.stat().st_size / 1024 / 1024  # MB
            logger.info(f"✅ Arquivo Parquet salvo: {filepath} ({file_size:.2f} MB)")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar Parquet {filepath}: {e}")
            return False
    
    def process_json_file(self, json_file: Path, target_date: Optional[date] = None) -> Optional[Dict]:
        """
        Processa um arquivo JSON específico e converte para Parquet.
        
        Args:
            json_file (Path): Caminho do arquivo JSON
            target_date (Optional[date]): Data para particionamento (padrão: hoje)
            
        Returns:
            Optional[Dict]: Relatório do processamento ou None se erro
        """
        if not target_date:
            target_date = date.today()
        
        logger.info(f"Processando arquivo: {json_file.name}")
        
        try:
            # 1. Carregar dados JSON
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 2. Validar estrutura JSON primeiro
            if not self.validate_stock_data(data):
                logger.warning(f"Dados inválidos em {json_file.name}")
                return None
            
            # 3. Extrair dados de ações (tentar ambos os formatos)
            stocks_data = data.get('combined_stocks', [])
            if not stocks_data:
                stocks_data = data.get('stocks_data', [])
            
            if not stocks_data:
                logger.warning(f"Nenhum dado de ação encontrado em {json_file.name}")
                return None
            
            # 4. Converter para DataFrame
            df = pd.DataFrame(stocks_data)
            
            # 5. Validar e limpar dados do DataFrame
            df_clean, validation_report = self.clean_and_validate_dataframe(df)
            
            # 6. Adicionar metadados
            df_final = self.add_processing_metadata(df_clean, json_file.name)
            
            # 7. Definir nome do arquivo Parquet baseado no tipo de dados
            if 'consolidados' in json_file.name.lower():
                parquet_filename = f"ibov_consolidado_{target_date.strftime('%Y%m%d')}.parquet"
            elif 'carteira_dia_codigo' in json_file.name.lower():
                parquet_filename = f"ibov_carteira_codigo_{target_date.strftime('%Y%m%d')}.parquet"
            elif 'carteira_dia_setor' in json_file.name.lower():
                parquet_filename = f"ibov_carteira_setor_{target_date.strftime('%Y%m%d')}.parquet"
            elif 'carteira_teorica' in json_file.name.lower():
                parquet_filename = f"ibov_carteira_teorica_{target_date.strftime('%Y%m%d')}.parquet"
            elif 'previa_quadrimestral' in json_file.name.lower():
                parquet_filename = f"ibov_previa_quadrimestral_{target_date.strftime('%Y%m%d')}.parquet"
            else:
                # Fallback para nomes genéricos
                base_name = json_file.stem.replace('b3_', '').replace('_', '-')
                parquet_filename = f"ibov_{base_name}_{target_date.strftime('%Y%m%d')}.parquet"
            
            # 8. Criar caminho particionado
            parquet_path = self.create_partition_path(target_date, parquet_filename)
            
            # 9. Salvar arquivo Parquet
            success = self.save_to_parquet(df_final, parquet_path)
            
            if success:
                # 10. Upload para S3 (se habilitado)
                s3_upload_success = False
                if self.upload_to_s3:
                    # Definir chave S3 mantendo estrutura particionada
                    s3_key = f"data_lake/ano={target_date.year}/mes={target_date.month:02d}/dia={target_date.day:02d}/{parquet_filename}"
                    s3_upload_success = self.upload_file_to_s3(parquet_path, s3_key)
                
                self.processed_files.append({
                    'source': str(json_file),
                    'output': str(parquet_path),
                    'records': len(df_final),
                    'validation_report': validation_report,
                    's3_uploaded': s3_upload_success,
                    's3_key': s3_key if self.upload_to_s3 else None
                })
                
                return {
                    'source_file': json_file.name,
                    'output_file': str(parquet_path),
                    'records_processed': len(df_final),
                    'validation_report': validation_report,
                    'file_size_mb': parquet_path.stat().st_size / 1024 / 1024,
                    's3_uploaded': s3_upload_success,
                    's3_key': s3_key if self.upload_to_s3 else None
                }
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Erro ao processar {json_file.name}: {e}")
            return None
    
    def process_all_json_files(self, target_date: Optional[date] = None) -> Dict:
        """
        Processa todos os arquivos JSON do diretório de entrada.
        
        Args:
            target_date (Optional[date]): Data para particionamento
            
        Returns:
            Dict: Relatório completo do processamento
        """
        if not target_date:
            target_date = date.today()
        
        logger.info("Iniciando processamento de todos os arquivos JSON...")
        logger.info(f"Data de particionamento: {target_date}")
        
        # Encontrar todos os arquivos JSON
        json_files = list(self.input_path.glob("*.json"))
        
        if not json_files:
            logger.warning(f"Nenhum arquivo JSON encontrado em {self.input_path}")
            return {'error': 'Nenhum arquivo JSON encontrado'}
        
        results = {
            'processing_date': target_date.isoformat(),
            'input_directory': str(self.input_path),
            'output_directory': str(self.output_path),
            'files_processed': [],
            'files_failed': [],
            'summary': {
                'total_files': len(json_files),
                'successful': 0,
                'failed': 0,
                'total_records': 0
            }
        }
        
        # Processar cada arquivo
        for json_file in json_files:
            result = self.process_json_file(json_file, target_date)
            
            if result:
                results['files_processed'].append(result)
                results['summary']['successful'] += 1
                results['summary']['total_records'] += result['records_processed']
                logger.info(f"✅ {json_file.name}: {result['records_processed']} registros")
            else:
                results['files_failed'].append(json_file.name)
                results['summary']['failed'] += 1
                logger.error(f"❌ Falha ao processar: {json_file.name}")
        
        # Log do resumo final
        logger.info("🎯 Processamento concluído!")
        logger.info(f"📊 Arquivos processados: {results['summary']['successful']}/{results['summary']['total_files']}")
        logger.info(f"📈 Total de registros: {results['summary']['total_records']}")
        
        if results['summary']['successful'] > 0:
            logger.info(f"📁 Estrutura criada em: {self.output_path}")
        
        return results


def main():
    """
    Função principal para executar o processamento Parquet.
    """
    try:
        # Inicializar processador
        processor = B3ParquetProcessor()
        
        # Processar todos os arquivos
        results = processor.process_all_json_files()
        
        # Exibir resumo
        if 'error' not in results:
            print("\n📊 Resumo do processamento:")
            print(f"🕒 Data de referência: {results['processing_date']}")
            print(f"📁 Diretório de saída: {results['output_directory']}")
            print(f"✅ Arquivos processados: {results['summary']['successful']}")
            print(f"❌ Arquivos com erro: {results['summary']['failed']}")
            print(f"📈 Total de registros: {results['summary']['total_records']}")
            
            if results['files_processed']:
                print("\n📋 Arquivos gerados:")
                for file_info in results['files_processed']:
                    print(f"  📄 {file_info['output_file']} ({file_info['records_processed']} registros)")
        else:
            print(f"❌ {results['error']}")
        
    except Exception as e:
        logger.error(f"Erro na execução principal: {e}")


if __name__ == "__main__":
    main()
