"""
Configurações para o scraping dos dados da B3 (IBOV).
Contém URLs, headers HTTP, configurações de logging e constantes.
"""

import logging
from typing import Dict

# =============================================================================
# CONFIGURAÇÕES DE LOGGING
# =============================================================================

LOGGING_CONFIG = {
    'level': logging.INFO,
    'format': '%(asctime)s - %(levelname)s - %(message)s'
}

# =============================================================================
# URLs DOS ENDPOINTS DA B3
# =============================================================================

class B3Endpoints:
    """
    Classe para organizar todos os endpoints da B3 com seus payloads.
    """
    
    # Carteira do dia (Daily Portfolio)
    # Segment 1 payload: {"language":"pt-br","pageNumber":1,"pageSize":120,"index":"IBOV","segment":"1"}
    CARTEIRA_DIA_SETOR = "https://sistemaswebb3-listados.b3.com.br/indexProxy/indexCall/GetPortfolioDay/eyJsYW5ndWFnZSI6InB0LWJyIiwicGFnZU51bWJlciI6MSwicGFnZVNpemUiOjEyMCwiaW5kZXgiOiJJQk9WIiwic2VnbWVudCI6IjEifQ=="
    
    # Segment 2 payload: {"language":"pt-br","pageNumber":1,"pageSize":120,"index":"IBOV","segment":"2"}
    CARTEIRA_DIA_CODIGO = "https://sistemaswebb3-listados.b3.com.br/indexProxy/indexCall/GetPortfolioDay/eyJsYW5ndWFnZSI6InB0LWJyIiwicGFnZU51bWJlciI6MSwicGFnZVNpemUiOjEyMCwiaW5kZXgiOiJJQk9WIiwic2VnbWVudCI6IjIifQ=="
    
    # Carteira Teórica - Mai. a Ago. 2025 (Theoretical Portfolio)
    # Payload: {"pageNumber":1,"pageSize":120,"language":"pt-br","index":"IBOV"}
    CARTEIRA_TEORICA = "https://sistemaswebb3-listados.b3.com.br/indexProxy/indexCall/GetTheoricalPortfolio/eyJwYWdlTnVtYmVyIjoxLCJwYWdlU2l6ZSI6MTIwLCJsYW5ndWFnZSI6InB0LWJyIiwiaW5kZXgiOiJJQk9WIn0="
    
    # Prévia Quadrimestral - Set. a Dez. 2025 (Quarterly Preview)
    # Payload: {"pageNumber":1,"pageSize":120,"language":"pt-br","index":"IBOV"}
    PREVIA_QUADRIMESTRAL = "https://sistemaswebb3-listados.b3.com.br/indexProxy/indexCall/GetQuartelyPreview/eyJwYWdlTnVtYmVyIjoxLCJwYWdlU2l6ZSI6MTIwLCJsYW5ndWFnZSI6InB0LWJyIiwiaW5kZXgiOiJJQk9WIn0="

# =============================================================================
# CONFIGURAÇÕES DE ENDPOINTS
# =============================================================================

ENDPOINTS_CONFIG = {
    'carteira_dia_setor': {
        'url': B3Endpoints.CARTEIRA_DIA_SETOR,
        'description': 'Carteira do Dia - Segmento 1 (Setor)'
    },
    'carteira_dia_codigo': {
        'url': B3Endpoints.CARTEIRA_DIA_CODIGO,
        'description': 'Carteira do Dia - Segmento 2 (Código)'
    },
    'carteira_teorica': {
        'url': B3Endpoints.CARTEIRA_TEORICA,
        'description': 'Carteira Teórica - Mai. a Ago. 2025'
    },
    'previa_quadrimestral': {
        'url': B3Endpoints.PREVIA_QUADRIMESTRAL,
        'description': 'Prévia Quadrimestral - Set. a Dez. 2025'
    }
}

# =============================================================================
# HEADERS HTTP
# =============================================================================

HTTP_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}

# =============================================================================
# CONFIGURAÇÕES DE ARQUIVOS
# =============================================================================

class FileConfig:
    """
    Configurações para nomes de arquivos e caminhos.
    """
    
    # Diretório base para dados
    DATA_DIR = "data/raw"
    
    # Mapeamento de nomes de arquivos para cada endpoint
    FILENAME_MAPPING = {
        'carteira_dia_setor': 'b3_carteira_dia_setor.json',
        'carteira_dia_codigo': 'b3_carteira_dia_codigo.json', 
        'carteira_teorica': 'b3_carteira_teorica_mai_ago_2025.json',
        'previa_quadrimestral': 'b3_previa_quadrimestral_set_dez_2025.json'
    }
    
    # Nome do arquivo consolidado
    CONSOLIDATED_FILENAME = 'b3_dados_consolidados.json'

# =============================================================================
# CONSTANTES GERAIS
# =============================================================================

class Constants:
    """
    Constantes gerais utilizadas no projeto.
    """
    
    # Configurações de requisição
    REQUEST_TIMEOUT = 30
    PAGE_SIZE = 120
    
    # Configurações de dados
    DEFAULT_ENCODING = 'utf-8'
    JSON_INDENT = 2
    
    # Descrições para exibição
    ENDPOINT_DESCRIPTIONS = {
        'carteira_dia_setor': 'Carteira do Dia - Setor',
        'carteira_dia_codigo': 'Carteira do Dia - Código', 
        'carteira_teorica': 'Carteira Teórica (Mai-Ago 2025)',
        'previa_quadrimestral': 'Prévia Quadrimestral (Set-Dez 2025)'
    }

# =============================================================================
# CONFIGURAÇÃO DO LOGGER
# =============================================================================

def setup_logger(name: str = __name__) -> logging.Logger:
    """
    Configura e retorna um logger para o módulo.
    
    Args:
        name (str): Nome do logger
        
    Returns:
        logging.Logger: Logger configurado
    """
    logging.basicConfig(**LOGGING_CONFIG)
    return logging.getLogger(name)
