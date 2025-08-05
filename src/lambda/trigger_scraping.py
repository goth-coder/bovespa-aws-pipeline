"""
AWS Lambda function para trigger do scraping B3.
Função principal que será executada pelo EventBridge diariamente.
"""

import json
import boto3
import logging
import sys
import os
from datetime import datetime
from typing import Dict, Any

# Adicionar src ao path para imports
sys.path.append('/opt/python')  # Lambda layer path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Configurar logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Handler principal da função Lambda.
    
    Args:
        event: Evento do EventBridge
        context: Contexto da execução Lambda
        
    Returns:
        Dict com resultado da execução
    """
    try:
        logger.info("🚀 Iniciando pipeline completo B3...")
        
        # 1. Executar scraping
        scraping_result = run_scraping_pipeline()
        
        if not scraping_result['success']:
            raise Exception(f"Falha no scraping: {scraping_result['error']}")
        
        # 2. Processar e enviar para S3
        s3_result = process_and_upload_to_s3()
        
        if not s3_result['success']:
            raise Exception(f"Falha no upload S3: {s3_result['error']}")
        
        # 3. Trigger Glue Job (opcional)
        glue_job_name = os.environ.get('GLUE_JOB_NAME')
        glue_result = {'success': True, 'message': 'Glue job não configurado'}
        
        if glue_job_name:
            glue_result = trigger_glue_job(glue_job_name)
        
        # Resultado final
        result = {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Pipeline B3 executado com sucesso',
                'timestamp': datetime.now().isoformat(),
                'executionId': context.aws_request_id if context else 'local-test',
                'results': {
                    'scraping': scraping_result,
                    's3_upload': s3_result,
                    'glue_trigger': glue_result
                }
            })
        }
        
        logger.info("✅ Pipeline B3 concluído com sucesso")
        return result
        
    except Exception as e:
        logger.error(f"❌ Erro no pipeline B3: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
        }

def run_scraping_pipeline() -> Dict[str, Any]:
    """
    Executa o pipeline de scraping B3.
    
    Returns:
        Dict com resultado do scraping
    """
    try:
        # Import dinâmico para evitar erros se módulos não estiverem disponíveis
        from scraping.scraping import B3Scraper
        
        logger.info("📊 Iniciando scraping B3...")
        
        scraper = B3Scraper()
        data = scraper.run_scraping()
        
        stocks_count = len(data.get('combined_stocks', []))
        endpoints_count = len(data.get('endpoints', {}))
        
        logger.info(f"✅ Scraping concluído: {stocks_count} ações de {endpoints_count} endpoints")
        
        return {
            'success': True,
            'stocks_collected': stocks_count,
            'endpoints_processed': endpoints_count,
            'timestamp': data.get('timestamp')
        }
        
    except ImportError as e:
        logger.error(f"❌ Módulo de scraping não encontrado: {str(e)}")
        return {
            'success': False,
            'error': f"Import error: {str(e)}"
        }
    except Exception as e:
        logger.error(f"❌ Erro no scraping: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }

def process_and_upload_to_s3() -> Dict[str, Any]:
    """
    Processa dados JSON e faz upload para S3.
    
    Returns:
        Dict com resultado do processamento
    """
    try:
        from scraping.parquet_processor import B3ParquetProcessor
        
        logger.info("🔄 Iniciando processamento Parquet + S3...")
        
        # Usar bucket do ambiente
        bucket_name = os.environ.get('BOVESPA_S3_BUCKET', 'bovespa-pipeline-data-adri-vic')
        
        processor = B3ParquetProcessor(upload_to_s3=True)
        results = processor.process_all_json_files()
        
        files_processed = len(results.get('processed_files', []))
        uploads_success = len([r for r in results.get('processed_files', []) if r.get('s3_uploaded')])
        
        logger.info(f"✅ Processamento concluído: {uploads_success}/{files_processed} uploads S3")
        
        return {
            'success': True,
            'files_processed': files_processed,
            'uploads_successful': uploads_success,
            'bucket': bucket_name,
            'files': results.get('processed_files', [])
        }
        
    except ImportError as e:
        logger.error(f"❌ Módulo de processamento não encontrado: {str(e)}")
        return {
            'success': False,
            'error': f"Import error: {str(e)}"
        }
    except Exception as e:
        logger.error(f"❌ Erro no processamento: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }

def trigger_glue_job(job_name: str) -> Dict[str, Any]:
    """
    Dispara job do Glue ETL após scraping.
    
    Args:
        job_name: Nome do job Glue
        
    Returns:
        Dict com resultado do trigger
    """
    try:
        glue_client = boto3.client('glue')
        
        response = glue_client.start_job_run(JobName=job_name)
        
        logger.info(f"Job Glue {job_name} iniciado: {response['JobRunId']}")
        return {
            'success': True,
            'jobRunId': response['JobRunId']
        }
        
    except Exception as e:
        logger.error(f"Erro ao iniciar job Glue: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }

def upload_to_s3(data: Dict, bucket: str, key: str) -> bool:
    """
    Upload dos dados coletados para S3.
    
    Args:
        data: Dados para upload
        bucket: Nome do bucket S3
        key: Chave do objeto S3
        
    Returns:
        bool: True se upload bem-sucedido
    """
    try:
        s3_client = boto3.client('s3')
        
        s3_client.put_object(
            Bucket=bucket,
            Key=key,
            Body=json.dumps(data),
            ContentType='application/json'
        )
        
        logger.info(f"Dados enviados para S3: s3://{bucket}/{key}")
        return True
        
    except Exception as e:
        logger.error(f"Erro no upload S3: {str(e)}")
        return False
