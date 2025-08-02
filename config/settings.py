"""
Configurações centralizadas do projeto.
"""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class AWSConfig:
    """Configurações AWS."""
    region: str = "us-east-1"
    bucket_name: str = "bovespa-pipeline-data"
    glue_job_name: str = "bovespa-etl-job"
    lambda_function_name: str = "bovespa-pipeline-orchestrator"
    sns_topic_arn: Optional[str] = None
    
    @classmethod
    def from_env(cls) -> 'AWSConfig':
        """Cria configuração a partir de variáveis de ambiente."""
        return cls(
            region=os.getenv('AWS_DEFAULT_REGION', 'us-east-1'),
            bucket_name=os.getenv('S3_BUCKET_NAME', 'bovespa-pipeline-data'),
            glue_job_name=os.getenv('GLUE_JOB_NAME', 'bovespa-etl-job'),
            lambda_function_name=os.getenv('LAMBDA_FUNCTION_NAME', 'bovespa-pipeline-orchestrator'),
            sns_topic_arn=os.getenv('SNS_TOPIC_ARN')
        )


@dataclass
class ScrapingConfig:
    """Configurações do scraping."""
    base_url: str = "https://sistemaswebb3-listados.b3.com.br/indexPage/day/IBOV"
    timeout: int = 30
    retry_attempts: int = 3
    retry_delay: int = 5
    
    @classmethod
    def from_env(cls) -> 'ScrapingConfig':
        """Cria configuração a partir de variáveis de ambiente."""
        return cls(
            base_url=os.getenv('B3_BASE_URL', cls.base_url),
            timeout=int(os.getenv('REQUEST_TIMEOUT', '30')),
            retry_attempts=int(os.getenv('RETRY_ATTEMPTS', '3')),
            retry_delay=int(os.getenv('RETRY_DELAY', '5'))
        )


@dataclass
class S3Paths:
    """Caminhos padrão no S3."""
    raw_prefix: str = "raw"
    refined_prefix: str = "refined"
    
    def get_raw_path(self, date_str: str) -> str:
        """Retorna caminho para dados raw."""
        return f"{self.raw_prefix}/dt={date_str}/"
    
    def get_refined_path(self, date_str: str, action_code: str = "") -> str:
        """Retorna caminho para dados refined."""
        if action_code:
            return f"{self.refined_prefix}/data_sessao={date_str}/cod_acao={action_code}/"
        return f"{self.refined_prefix}/data_sessao={date_str}/"


# Configurações globais
aws_config = AWSConfig.from_env()
scraping_config = ScrapingConfig.from_env()
s3_paths = S3Paths()
