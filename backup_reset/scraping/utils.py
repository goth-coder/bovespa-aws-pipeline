"""
Funções auxiliares para o scraping dos dados da B3.
Contém helpers para parsing, validação, manipulação de arquivos e formatação.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from .config import FileConfig, Constants, setup_logger

# Configurar logger
logger = setup_logger(__name__)

# =============================================================================
# FUNÇÕES DE PARSING E VALIDAÇÃO
# =============================================================================

def parse_stock_data(stock: Dict) -> Dict[str, Any]:
    """
    Extrai e padroniza dados de uma ação individual.
    
    Args:
        stock (Dict): Dados brutos da ação
        
    Returns:
        Dict[str, Any]: Dados padronizados da ação
    """
    return {
        'codigo': stock.get('cod', ''),
        'acao': stock.get('asset', ''),
        'setor': stock.get('sectorName', ''),
        'subsetor': stock.get('subSectorName', ''),
        'segmento': stock.get('segment', ''),
        'part_percent': stock.get('part', 0),
        'part_accumulated': stock.get('partAcum', 0),
        'theoretical_qty': stock.get('theoricalQty', 0)
    }

def validate_json_response(json_content: str) -> Optional[Dict]:
    """
    Valida e converte conteúdo JSON.
    
    Args:
        json_content (str): Conteúdo JSON como string
        
    Returns:
        Optional[Dict]: Dados JSON parseados ou None se inválido
    """
    try:
        data = json.loads(json_content)
        if not isinstance(data, dict):
            logger.warning("JSON response is not a dictionary")
            return None
        return data
    except json.JSONDecodeError as e:
        logger.error(f"Erro ao fazer parse do JSON: {e}")
        return None

def extract_stocks_from_response(data_response: Dict) -> List[Dict]:
    """
    Extrai lista de ações da resposta da API.
    
    Args:
        data_response (Dict): Resposta completa da API
        
    Returns:
        List[Dict]: Lista de ações extraídas e padronizadas
    """
    stocks_data = []
    
    if 'results' not in data_response:
        logger.warning("Campo 'results' não encontrado na resposta")
        return stocks_data
    
    stocks_list = data_response['results']
    for stock in stocks_list:
        try:
            stock_data = parse_stock_data(stock)
            stocks_data.append(stock_data)
        except Exception as e:
            logger.warning(f"Erro ao processar ação: {e}")
            continue
    
    return stocks_data

# =============================================================================
# FUNÇÕES DE MANIPULAÇÃO DE ARQUIVOS
# =============================================================================

def ensure_directory_exists(directory_path: str) -> bool:
    """
    Garante que um diretório existe, criando-o se necessário.
    
    Args:
        directory_path (str): Caminho do diretório
        
    Returns:
        bool: True se o diretório existe ou foi criado com sucesso
    """
    try:
        os.makedirs(directory_path, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"Erro ao criar diretório {directory_path}: {e}")
        return False

def get_full_file_path(filename: str) -> str:
    """
    Retorna o caminho completo para um arquivo no diretório de dados.
    
    Args:
        filename (str): Nome do arquivo
        
    Returns:
        str: Caminho completo do arquivo
    """
    ensure_directory_exists(FileConfig.DATA_DIR)
    return os.path.join(FileConfig.DATA_DIR, filename)

def save_json_data(data: Dict, filename: str) -> bool:
    """
    Salva dados em formato JSON.
    
    Args:
        data (Dict): Dados a serem salvos
        filename (str): Nome do arquivo
        
    Returns:
        bool: True se salvou com sucesso
    """
    try:
        full_path = get_full_file_path(filename)
        
        with open(full_path, 'w', encoding=Constants.DEFAULT_ENCODING) as f:
            json.dump(data, f, ensure_ascii=False, indent=Constants.JSON_INDENT)
        
        logger.info(f"Dados salvos em: {full_path}")
        return True
        
    except Exception as e:
        logger.error(f"Erro ao salvar arquivo {filename}: {e}")
        return False

def load_json_data(filename: str) -> Optional[Dict]:
    """
    Carrega dados de um arquivo JSON.
    
    Args:
        filename (str): Nome do arquivo
        
    Returns:
        Optional[Dict]: Dados carregados ou None se erro
    """
    try:
        full_path = get_full_file_path(filename)
        
        if not os.path.exists(full_path):
            logger.warning(f"Arquivo não encontrado: {full_path}")
            return None
        
        with open(full_path, 'r', encoding=Constants.DEFAULT_ENCODING) as f:
            data = json.load(f)
        
        logger.info(f"Dados carregados de: {full_path}")
        return data
        
    except Exception as e:
        logger.error(f"Erro ao carregar arquivo {filename}: {e}")
        return None

# =============================================================================
# FUNÇÕES DE FORMATAÇÃO E DISPLAY
# =============================================================================

def format_timestamp() -> str:
    """
    Retorna timestamp formatado para ISO.
    
    Returns:
        str: Timestamp em formato ISO
    """
    return datetime.now().isoformat()

def format_date() -> str:
    """
    Retorna data formatada.
    
    Returns:
        str: Data no formato YYYY-MM-DD
    """
    return datetime.now().strftime('%Y-%m-%d')

def format_stock_summary(stock: Dict) -> str:
    """
    Formata resumo de uma ação para exibição.
    
    Args:
        stock (Dict): Dados da ação
        
    Returns:
        str: String formatada com resumo da ação
    """
    codigo = stock.get('codigo', 'N/A')
    acao = stock.get('acao', 'N/A')
    setor = stock.get('setor', 'N/A')
    participacao = stock.get('part_percent', 0)
    
    return f"{codigo} - {acao} ({setor}) - Participação: {participacao}%"

def format_endpoint_description(endpoint_name: str) -> str:
    """
    Retorna descrição formatada de um endpoint.
    
    Args:
        endpoint_name (str): Nome do endpoint
        
    Returns:
        str: Descrição formatada
    """
    return Constants.ENDPOINT_DESCRIPTIONS.get(endpoint_name, endpoint_name)

# =============================================================================
# FUNÇÕES DE ESTRUTURAÇÃO DE DADOS
# =============================================================================

def create_base_data_structure(source_url: str) -> Dict:
    """
    Cria estrutura básica para dados extraídos.
    
    Args:
        source_url (str): URL de origem dos dados
        
    Returns:
        Dict: Estrutura básica de dados
    """
    return {
        'timestamp': format_timestamp(),
        'source_url': source_url,
        'index_info': {},
        'stocks_data': [],
        'metadata': {}
    }

def create_metadata(stocks_data: List[Dict], page_info: Dict = None) -> Dict:
    """
    Cria metadata para os dados extraídos.
    
    Args:
        stocks_data (List[Dict]): Lista de ações
        page_info (Dict): Informações de paginação
        
    Returns:
        Dict: Metadata estruturada
    """
    metadata = {
        'total_stocks_found': len(stocks_data),
        'extraction_date': format_date(),
        'page_info': page_info or {},
        'has_next_page': page_info.get('hasNextPage', False) if page_info else False,
        'total_records': page_info.get('totalRecords', 0) if page_info else 0
    }
    
    return metadata

def merge_stock_data(all_stocks: List[Dict], new_stocks: List[Dict], endpoint_info: Dict) -> List[Dict]:
    """
    Merge dados de ações de diferentes endpoints.
    
    Args:
        all_stocks (List[Dict]): Lista atual de ações
        new_stocks (List[Dict]): Novas ações para adicionar
        endpoint_info (Dict): Informações do endpoint
        
    Returns:
        List[Dict]: Lista consolidada de ações
    """
    for stock in new_stocks:
        stock['endpoint_source'] = endpoint_info.get('name', 'unknown')
        stock['endpoint_description'] = endpoint_info.get('description', 'N/A')
        all_stocks.append(stock)
    
    return all_stocks

# =============================================================================
# FUNÇÕES DE VALIDAÇÃO E LOGGING
# =============================================================================

def log_scraping_summary(endpoint_name: str, stocks_count: int, success: bool = True) -> None:
    """
    Registra resumo do scraping para um endpoint.
    
    Args:
        endpoint_name (str): Nome do endpoint
        stocks_count (int): Número de ações encontradas
        success (bool): Se foi bem-sucedido
    """
    status_emoji = "✅" if success else "❌"
    logger.info(f"{status_emoji} {endpoint_name}: {stocks_count} ações encontradas")

def validate_endpoint_data(data: Dict) -> bool:
    """
    Valida se os dados de um endpoint estão em formato esperado.
    
    Args:
        data (Dict): Dados a serem validados
        
    Returns:
        bool: True se dados válidos
    """
    required_fields = ['timestamp', 'source_url', 'stocks_data', 'metadata']
    
    for field in required_fields:
        if field not in data:
            logger.error(f"Campo obrigatório '{field}' não encontrado nos dados")
            return False
    
    if not isinstance(data['stocks_data'], list):
        logger.error("Campo 'stocks_data' deve ser uma lista")
        return False
    
    return True

def get_filename_for_endpoint(endpoint_name: str) -> str:
    """
    Retorna nome do arquivo para um endpoint específico.
    
    Args:
        endpoint_name (str): Nome do endpoint
        
    Returns:
        str: Nome do arquivo
    """
    return FileConfig.FILENAME_MAPPING.get(endpoint_name, f'b3_{endpoint_name}.json')
