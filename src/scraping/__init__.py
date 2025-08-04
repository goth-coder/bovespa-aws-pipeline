"""
Módulo de scraping para dados da B3 (IBOV).
Estrutura modular para coleta e processamento de dados da Bovespa.
"""

from .scraping import B3Scraper, main, display_summary
from .config import ENDPOINTS_CONFIG, HTTP_HEADERS, Constants, FileConfig
from .utils import (
    parse_stock_data, validate_json_response, extract_stocks_from_response,
    save_json_data, load_json_data, format_timestamp, format_date
)

__version__ = "1.0.0"
__author__ = "Projeto Bovespa Pipeline"

__all__ = [
    'B3Scraper',
    'main',
    'display_summary',
    'ENDPOINTS_CONFIG',
    'HTTP_HEADERS',
    'Constants',
    'FileConfig',
    'parse_stock_data',
    'validate_json_response',
    'extract_stocks_from_response',
    'save_json_data',
    'load_json_data',
    'format_timestamp',
    'format_date'
]
