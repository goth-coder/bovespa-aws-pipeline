"""
Configurações específicas para processamento de dados B3.
Define estruturas de particionamento e otimizações para Parquet/S3.
"""

from datetime import date
from pathlib import Path


class DataLakeConfig:
    """Configurações do Data Lake local e S3."""
    
    # Estrutura de diretórios
    LOCAL_BASE_PATH = Path("data_lake")
    S3_BASE_PREFIX = "raw"
    
    # Padrão de particionamento
    PARTITION_PATTERN = "ano={year}/mes={month:02d}/dia={day:02d}"
    
    # Configurações de arquivo
    PARQUET_COMPRESSION = "snappy"  # Boa para S3
    PARQUET_ENGINE = "pyarrow"
    
    @classmethod
    def get_partition_path(cls, target_date: date, base_path: Path = None) -> Path:
        """
        Gera caminho particionado para uma data específica.
        
        Args:
            target_date (date): Data para particionamento
            base_path (Path): Caminho base (padrão: LOCAL_BASE_PATH)
            
        Returns:
            Path: Caminho completo particionado
        """
        if base_path is None:
            base_path = cls.LOCAL_BASE_PATH
            
        partition = cls.PARTITION_PATTERN.format(
            year=target_date.year,
            month=target_date.month,
            day=target_date.day
        )
        
        return base_path / partition
    
    @classmethod
    def get_s3_key(cls, target_date: date, filename: str) -> str:
        """
        Gera chave S3 com estrutura particionada.
        
        Args:
            target_date (date): Data para particionamento
            filename (str): Nome do arquivo
            
        Returns:
            str: Chave S3 completa
        """
        partition = cls.PARTITION_PATTERN.format(
            year=target_date.year,
            month=target_date.month,
            day=target_date.day
        )
        
        return f"{cls.S3_BASE_PREFIX}/{partition}/{filename}"


class DataValidationConfig:
    """Configurações para validação de dados."""
    
    # Campos obrigatórios
    REQUIRED_FIELDS = ['codigo', 'acao']
    
    # Campos opcionais que devem ser preenchidos com padrão
    OPTIONAL_FIELDS = {
        'setor': 'N/A',
        'subsetor': 'N/A', 
        'segmento': 'N/A',
        'part_percent': 0.0,
        'part_accumulated': 0.0,
        'theoretical_qty': 0
    }
    
    # Campos categóricos (otimização de memória)
    CATEGORICAL_FIELDS = [
        'codigo', 'acao', 'setor', 'subsetor', 'segmento',
        'endpoint_name', 'endpoint_description', 'source_file'
    ]
    
    # Campos numéricos que precisam conversão de formato brasileiro
    BRAZILIAN_DECIMAL_FIELDS = ['part_percent', 'part_accumulated']
    BRAZILIAN_INTEGER_FIELDS = ['theoretical_qty']


class FileNamingConfig:
    """Configurações para nomenclatura de arquivos."""
    
    # Mapeamento de tipos de dados para nomes de arquivo
    FILENAME_MAPPING = {
        'carteira_dia': 'ibov_carteira_dia',
        'carteira_teorica': 'ibov_carteira_teorica', 
        'previa_quadrimestral': 'ibov_previa',
        'dados_consolidados': 'ibov_consolidado'
    }
    
    # Padrão de data nos nomes
    DATE_FORMAT = "%Y%m%d"
    
    @classmethod
    def generate_filename(cls, source_name: str, target_date: date) -> str:
        """
        Gera nome padronizado para arquivo Parquet.
        
        Args:
            source_name (str): Nome do arquivo fonte
            target_date (date): Data de referência
            
        Returns:
            str: Nome do arquivo padronizado
        """
        # Extrair tipo de dados do nome fonte
        source_clean = source_name.lower().replace('b3_', '').replace('.json', '')
        
        # Mapear para nome padronizado
        for key, mapped_name in cls.FILENAME_MAPPING.items():
            if key in source_clean:
                base_name = mapped_name
                break
        else:
            # Fallback para nome genérico
            base_name = f"ibov_{source_clean.replace('_', '-')}"
        
        # Adicionar data
        date_str = target_date.strftime(cls.DATE_FORMAT)
        
        return f"{base_name}_{date_str}.parquet"


class ProcessingConfig:
    """Configurações gerais de processamento."""
    
    # Logging
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_LEVEL = "INFO"
    
    # Performance
    CHUNK_SIZE = 10000  # Para processamento em lotes grandes
    MAX_MEMORY_USAGE_MB = 512  # Limite de memória por arquivo
    
    # Metadados
    METADATA_FIELDS = [
        'processed_at',
        'partition_date', 
        'source_file',
        'record_hash'
    ]
    
    # Validação de qualidade
    MIN_RECORDS_THRESHOLD = 1  # Mínimo de registros válidos
    MAX_NULL_PERCENTAGE = 0.5  # Máximo 50% de valores nulos


# Exemplo de uso das configurações
if __name__ == "__main__":
    from datetime import date
    
    # Testar configurações
    test_date = date(2025, 8, 3)
    
    print("🔧 Testando configurações:")
    print(f"📁 Caminho particionado: {DataLakeConfig.get_partition_path(test_date)}")
    print(f"🌐 Chave S3: {DataLakeConfig.get_s3_key(test_date, 'ibov_carteira.parquet')}")
    print(f"📄 Nome de arquivo: {FileNamingConfig.generate_filename('b3_carteira_dia.json', test_date)}")
    print(f"✅ Campos obrigatórios: {DataValidationConfig.REQUIRED_FIELDS}")
