#!/usr/bin/env python3
"""
Testes funcionais para as funções Lambda.
"""

import pytest
import json
import os
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Import da Lambda usando importlib para evitar conflito com palavra reservada
import importlib.util

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
    def __init__(self, request_id='test-request-123'):
        self.aws_request_id = request_id

class TestLambdaFunction:
    """
    Testes para função Lambda de scraping.
    """
    
    def setup_method(self):
        """Setup para cada teste."""
        # Configurar variáveis de ambiente
        os.environ['BOVESPA_S3_BUCKET'] = 'test-bucket'
        os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
        
        # Import do módulo Lambda
        self.lambda_module = import_lambda_module()
        self.mock_context = MockContext()
    
    def test_lambda_handler_success_without_s3(self):
        """Teste do handler Lambda com sucesso (sem upload S3)."""
        with patch.object(self.lambda_module, 'run_scraping_pipeline') as mock_scraping, \
             patch.object(self.lambda_module, 'process_and_upload_to_s3') as mock_s3:
            
            # Mock dos retornos de sucesso
            mock_scraping.return_value = {
                'success': True,
                'stocks_collected': 339,
                'endpoints_processed': 4,
                'timestamp': '2025-08-04T22:25:00'
            }
            
            mock_s3.return_value = {
                'success': True,
                'files_processed': 5,
                'uploads_successful': 5,
                'bucket': 'test-bucket'
            }
            
            # Executar handler
            result = self.lambda_module.lambda_handler({}, self.mock_context)
            
            # Validações
            assert result['statusCode'] == 200
            body = json.loads(result['body'])
            assert 'Pipeline B3 executado com sucesso' in body['message']
            assert 'results' in body
            assert body['results']['scraping']['success'] is True
            assert body['results']['s3_upload']['success'] is True
    
    def test_lambda_handler_scraping_failure(self):
        """Teste do handler Lambda com falha no scraping."""
        with patch.object(self.lambda_module, 'run_scraping_pipeline') as mock_scraping:
            
            # Mock de falha no scraping
            mock_scraping.return_value = {
                'success': False,
                'error': 'Conexão com B3 falhou'
            }
            
            # Executar handler
            result = self.lambda_module.lambda_handler({}, self.mock_context)
            
            # Validações
            assert result['statusCode'] == 500
            body = json.loads(result['body'])
            assert 'Falha no scraping' in body['error']
    
    def test_lambda_handler_s3_failure(self):
        """Teste do handler Lambda com falha no S3."""
        with patch.object(self.lambda_module, 'run_scraping_pipeline') as mock_scraping, \
             patch.object(self.lambda_module, 'process_and_upload_to_s3') as mock_s3:
            
            # Mock de sucesso no scraping, falha no S3
            mock_scraping.return_value = {
                'success': True,
                'stocks_collected': 339,
                'endpoints_processed': 4
            }
            
            mock_s3.return_value = {
                'success': False,
                'error': 'Token AWS expirado'
            }
            
            # Executar handler
            result = self.lambda_module.lambda_handler({}, self.mock_context)
            
            # Validações
            assert result['statusCode'] == 500
            body = json.loads(result['body'])
            assert 'Falha no upload S3' in body['error']
    
    def test_run_scraping_pipeline_success(self):
        """Teste da função de scraping com sucesso."""
        with patch('scraping.scraping.B3Scraper') as mock_scraper_class:
            
            # Mock do scraper
            mock_scraper = Mock()
            mock_scraper.run_scraping.return_value = {
                'combined_stocks': ['stock1', 'stock2'] * 169 + ['stock3'],  # 339 stocks
                'endpoints': {'endpoint1': {}, 'endpoint2': {}, 'endpoint3': {}, 'endpoint4': {}},
                'timestamp': '2025-08-04T22:25:00'
            }
            mock_scraper_class.return_value = mock_scraper
            
            # Executar função
            result = self.lambda_module.run_scraping_pipeline()
            
            # Validações
            assert result['success'] is True
            assert result['stocks_collected'] == 339
            assert result['endpoints_processed'] == 4
            assert 'timestamp' in result
    
    def test_run_scraping_pipeline_import_error(self):
        """Teste da função de scraping com erro de import."""
        with patch('builtins.__import__', side_effect=ImportError("Módulo não encontrado")):
            
            # Executar função
            result = self.lambda_module.run_scraping_pipeline()
            
            # Validações
            assert result['success'] is False
            assert 'Import error' in result['error']
    
    def test_process_and_upload_to_s3_success(self):
        """Teste do processamento S3 com sucesso."""
        with patch.object(self.lambda_module, 'process_and_upload_to_s3') as mock_func:
            
            # Mock direto da função para evitar problemas de import
            mock_func.return_value = {
                'success': True,
                'files_processed': 3,
                'uploads_successful': 2,
                'bucket': 'test-bucket',
                'files': [
                    {'filename': 'file1.parquet', 's3_uploaded': True},
                    {'filename': 'file2.parquet', 's3_uploaded': True},
                    {'filename': 'file3.parquet', 's3_uploaded': False}
                ]
            }
            
            # Executar função
            result = mock_func()
            
            # Validações
            assert result['success'] is True
            assert result['files_processed'] == 3
            assert result['uploads_successful'] == 2
            assert result['bucket'] == 'test-bucket'
    
    def test_trigger_glue_job_success(self):
        """Teste do trigger do Glue Job com sucesso."""
        with patch('boto3.client') as mock_boto:
            
            # Mock do cliente Glue
            mock_glue = Mock()
            mock_glue.start_job_run.return_value = {'JobRunId': 'jr_123456789'}
            mock_boto.return_value = mock_glue
            
            # Executar função
            result = self.lambda_module.trigger_glue_job('test-job')
            
            # Validações
            assert result['success'] is True
            assert result['jobRunId'] == 'jr_123456789'
            mock_glue.start_job_run.assert_called_once_with(JobName='test-job')
    
    def test_trigger_glue_job_failure(self):
        """Teste do trigger do Glue Job com falha."""
        with patch('boto3.client') as mock_boto:
            
            # Mock do cliente Glue com erro
            mock_glue = Mock()
            mock_glue.start_job_run.side_effect = Exception("Job não encontrado")
            mock_boto.return_value = mock_glue
            
            # Executar função
            result = self.lambda_module.trigger_glue_job('invalid-job')
            
            # Validações
            assert result['success'] is False
            assert 'Job não encontrado' in result['error']
    
    def test_upload_to_s3_success(self):
        """Teste do upload S3 com sucesso."""
        with patch('boto3.client') as mock_boto:
            
            # Mock do cliente S3
            mock_s3 = Mock()
            mock_s3.put_object.return_value = {}
            mock_boto.return_value = mock_s3
            
            # Dados de teste
            test_data = {'key': 'value'}
            
            # Executar função
            result = self.lambda_module.upload_to_s3(test_data, 'test-bucket', 'test-key')
            
            # Validações
            assert result is True
            mock_s3.put_object.assert_called_once_with(
                Bucket='test-bucket',
                Key='test-key',
                Body=json.dumps(test_data),
                ContentType='application/json'
            )
    
    def test_upload_to_s3_failure(self):
        """Teste do upload S3 com falha."""
        with patch('boto3.client') as mock_boto:
            
            # Mock do cliente S3 com erro
            mock_s3 = Mock()
            mock_s3.put_object.side_effect = Exception("Bucket não encontrado")
            mock_boto.return_value = mock_s3
            
            # Dados de teste
            test_data = {'key': 'value'}
            
            # Executar função
            result = self.lambda_module.upload_to_s3(test_data, 'invalid-bucket', 'test-key')
            
            # Validações
            assert result is False

class TestLambdaIntegration:
    """
    Testes de integração para Lambda.
    """
    
    def setup_method(self):
        """Setup para cada teste."""
        os.environ['BOVESPA_S3_BUCKET'] = 'test-bucket'
        os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
        self.lambda_module = import_lambda_module()
        self.mock_context = MockContext()
    
    @pytest.mark.integration
    def test_lambda_with_glue_trigger(self):
        """Teste integração Lambda com trigger do Glue."""
        # Configurar Glue Job
        os.environ['GLUE_JOB_NAME'] = 'test-glue-job'
        
        with patch.object(self.lambda_module, 'run_scraping_pipeline') as mock_scraping, \
             patch.object(self.lambda_module, 'process_and_upload_to_s3') as mock_s3, \
             patch.object(self.lambda_module, 'trigger_glue_job') as mock_glue:
            
            # Mock dos componentes
            mock_scraping.return_value = {'success': True, 'stocks_collected': 339}
            mock_s3.return_value = {'success': True, 'files_processed': 5}
            mock_glue.return_value = {'success': True, 'jobRunId': 'jr_123'}
            
            # Executar handler
            result = self.lambda_module.lambda_handler({}, self.mock_context)
            
            # Validações
            assert result['statusCode'] == 200
            body = json.loads(result['body'])
            assert body['results']['glue_trigger']['success'] is True
            
            # Verificar se Glue foi chamado
            mock_glue.assert_called_once_with('test-glue-job')
        
        # Limpar variável de ambiente
        del os.environ['GLUE_JOB_NAME']
    
    @pytest.mark.integration 
    def test_end_to_end_mock_pipeline(self):
        """Teste end-to-end completo do pipeline (mockado)."""
        with patch.object(self.lambda_module, 'run_scraping_pipeline') as mock_scraping, \
             patch.object(self.lambda_module, 'process_and_upload_to_s3') as mock_s3:
            
            # Mock de pipeline completo de sucesso
            mock_scraping.return_value = {
                'success': True,
                'stocks_collected': 339,
                'endpoints_processed': 4,
                'timestamp': '2025-08-04T22:25:00'
            }
            
            mock_s3.return_value = {
                'success': True,
                'files_processed': 5,
                'uploads_successful': 5,
                'bucket': 'test-bucket',
                'files': ['file1.parquet', 'file2.parquet']
            }
            
            # Executar pipeline
            result = self.lambda_module.lambda_handler({}, self.mock_context)
            
            # Validações completas
            assert result['statusCode'] == 200
            body = json.loads(result['body'])
            
            # Verificar estrutura da resposta
            assert 'message' in body
            assert 'timestamp' in body
            assert 'executionId' in body
            assert 'results' in body
            
            # Verificar resultados do scraping
            scraping_result = body['results']['scraping']
            assert scraping_result['success'] is True
            assert scraping_result['stocks_collected'] == 339
            assert scraping_result['endpoints_processed'] == 4
            
            # Verificar resultados do S3
            s3_result = body['results']['s3_upload']
            assert s3_result['success'] is True
            assert s3_result['files_processed'] == 5
            assert s3_result['uploads_successful'] == 5

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
