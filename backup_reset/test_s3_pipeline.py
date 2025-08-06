#!/usr/bin/env python3
"""
Testes Simples do Pipeline S3 - Bovespa Data Pipeline
===================================================

Testes essenciais para projeto educacional:
1. Inicialização do processador
2. Processamento JSON → Parquet
3. Upload S3 (mock)
4. Validação básica de dados

Execução: pytest tests/test_s3_pipeline.py -v

Autor: Victor Santos (Agente A)
Data: 2025-08-04
"""

import os
import sys
import pytest
import json
import tempfile
import shutil
from datetime import date
from pathlib import Path
from unittest.mock import Mock, patch

# Adicionar src ao Python path para imports
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from scraping.parquet_processor import B3ParquetProcessor


class TestS3Pipeline:
    """Testes simples para o pipeline S3."""
    
    @pytest.fixture
    def temp_dirs(self):
        """Cria diretórios temporários para teste."""
        temp_dir = tempfile.mkdtemp()
        input_dir = Path(temp_dir) / "input"
        output_dir = Path(temp_dir) / "output"
        
        input_dir.mkdir(exist_ok=True)
        output_dir.mkdir(exist_ok=True)
        
        yield str(input_dir), str(output_dir)
        
        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def sample_data(self, temp_dirs):
        """Cria arquivo JSON de teste."""
        input_dir, _ = temp_dirs
        
        # Dados de exemplo
        test_data = {
            'stocks_data': [
                {
                    'codigo': 'PETR4',
                    'acao': 'PETROBRAS',
                    'tipo': 'ON',
                    'qtde_teorica': 1000,
                    'part_percent': 8.5
                },
                {
                    'codigo': 'VALE3',
                    'acao': 'VALE',
                    'tipo': 'ON',
                    'qtde_teorica': 500,
                    'part_percent': 6.2
                }
            ]
        }
        
        # Criar arquivo de teste
        test_file = Path(input_dir) / "b3_dados_consolidados.json"
        with open(test_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f, ensure_ascii=False, indent=2)
        
        return str(test_file)

    def test_processor_init_without_s3(self, temp_dirs):
        """Testa inicialização do processador sem S3."""
        input_dir, output_dir = temp_dirs
        
        processor = B3ParquetProcessor(
            input_path=input_dir,
            output_path=output_dir,
            upload_to_s3=False
        )
        
        assert processor.upload_to_s3 is False
        assert len(processor.processed_files) == 0

    @patch.dict(os.environ, {
        'BOVESPA_S3_BUCKET': 'test-bucket',
        'AWS_ACCESS_KEY_ID': 'test-key',
        'AWS_SECRET_ACCESS_KEY': 'test-secret'
    })
    @patch('scraping.parquet_processor.boto3.client')
    def test_processor_init_with_s3(self, mock_boto3, temp_dirs):
        """Testa inicialização do processador com S3."""
        input_dir, output_dir = temp_dirs
        mock_s3_client = Mock()
        mock_boto3.return_value = mock_s3_client
        
        processor = B3ParquetProcessor(
            input_path=input_dir,
            output_path=output_dir,
            upload_to_s3=True
        )
        
        assert processor.upload_to_s3 is True
        assert processor.s3_bucket == 'test-bucket'

    def test_json_processing_local_only(self, temp_dirs, sample_data):
        """Testa processamento completo local (sem S3)."""
        input_dir, output_dir = temp_dirs
        
        processor = B3ParquetProcessor(
            input_path=input_dir,
            output_path=output_dir,
            upload_to_s3=False
        )
        
        # Processar arquivo de teste
        json_file = Path(sample_data)
        test_date = date(2025, 8, 4)
        
        result = processor.process_json_file(json_file, test_date)
        
        # Verificações básicas
        assert result is not None
        assert result['records_processed'] == 2
        assert result['s3_uploaded'] is False
        
        # Verificar se arquivo Parquet foi criado
        expected_file = (
            Path(output_dir) / 
            "ano=2025" / "mes=08" / "dia=04" / 
            "ibov_consolidado_20250804.parquet"
        )
        assert expected_file.exists()

    def test_partition_creation(self, temp_dirs):
        """Testa criação de estrutura particionada."""
        input_dir, output_dir = temp_dirs
        
        processor = B3ParquetProcessor(
            input_path=input_dir,
            output_path=output_dir,
            upload_to_s3=False
        )
        
        test_date = date(2025, 8, 4)
        partition_path = processor.create_partition_path(test_date, "test.parquet")
        
        expected = Path(output_dir) / "ano=2025" / "mes=08" / "dia=04" / "test.parquet"
        assert partition_path == expected
        assert partition_path.parent.exists()

    def test_data_validation(self, temp_dirs):
        """Testa validação básica de dados."""
        input_dir, output_dir = temp_dirs
        
        processor = B3ParquetProcessor(
            input_path=input_dir,
            output_path=output_dir,
            upload_to_s3=False
        )
        
        # Teste com dados válidos
        valid_data = {'stocks_data': [{'codigo': 'PETR4', 'acao': 'PETROBRAS'}]}
        assert processor.validate_stock_data(valid_data) is True
        
        # Teste com dados inválidos
        invalid_data = {'stocks_data': []}
        assert processor.validate_stock_data(invalid_data) is False

    @patch('scraping.parquet_processor.boto3.client')
    def test_s3_upload_success(self, mock_boto3, temp_dirs):
        """Testa upload bem-sucedido para S3 (mock)."""
        input_dir, output_dir = temp_dirs
        
        # Mock do cliente S3
        mock_s3_client = Mock()
        mock_boto3.return_value = mock_s3_client
        
        with patch.dict(os.environ, {
            'BOVESPA_S3_BUCKET': 'test-bucket',
            'AWS_ACCESS_KEY_ID': 'test-key',
            'AWS_SECRET_ACCESS_KEY': 'test-secret'
        }):
            processor = B3ParquetProcessor(
                input_path=input_dir,
                output_path=output_dir,
                upload_to_s3=True
            )
        
        # Criar arquivo temporário
        test_file = Path(output_dir) / "test.parquet"
        test_file.write_text("test content")
        
        # Executar upload
        result = processor.upload_file_to_s3(test_file, "test/path/test.parquet")
        
        assert result is True
        mock_s3_client.upload_file.assert_called_once()

    def test_process_all_files(self, temp_dirs, sample_data):
        """Testa processamento de todos os arquivos JSON."""
        input_dir, output_dir = temp_dirs
        
        processor = B3ParquetProcessor(
            input_path=input_dir,
            output_path=output_dir,
            upload_to_s3=False
        )
        
        results = processor.process_all_json_files(date(2025, 8, 4))
        
        assert 'error' not in results
        assert results['summary']['total_files'] == 1
        assert results['summary']['successful'] == 1
        assert results['summary']['total_records'] == 2


if __name__ == "__main__":
    # Executar testes se script for executado diretamente
    pytest.main([__file__, "-v", "--tb=short"])


if __name__ == "__main__":
    # Executar testes se script for executado diretamente
    pytest.main([__file__, "-v", "--tb=short"])
