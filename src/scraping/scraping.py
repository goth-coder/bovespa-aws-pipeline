"""
Script principal para realizar scraping dos dados do pregão da B3 (IBOV).
Versão modular simplificada para projeto educacional.
"""

import sys
import os
import requests
from typing import Dict, Optional

# Adicionar o diretório pai ao path para imports relativos funcionarem
if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(__file__))

try:
    from .config import ENDPOINTS_CONFIG, HTTP_HEADERS, Constants, setup_logger
    from .utils import (
        validate_json_response, extract_stocks_from_response, create_base_data_structure,
        save_json_data, get_filename_for_endpoint, format_timestamp
    )
except ImportError:
    # Fallback para execução direta
    from config import ENDPOINTS_CONFIG, HTTP_HEADERS, Constants, setup_logger
    from utils import (
        validate_json_response, extract_stocks_from_response, create_base_data_structure,
        save_json_data, get_filename_for_endpoint, format_timestamp
    )

# Configurar logger
logger = setup_logger(__name__)


class B3Scraper:
    """
    Classe para realizar scraping dos dados da B3.
    Refatorada para usar configurações e utilitários modulares.
    """
    
    def __init__(self):
        """
        Inicializa o scraper com configurações da config.py
        """
        self.session = requests.Session()
        self.session.headers.update(HTTP_HEADERS)
        logger.info("B3Scraper inicializado com configurações modulares")
    
    def make_request(self, url: str) -> Optional[requests.Response]:
        """
        Faz a requisição HTTP para o site da B3.
        
        Args:
            url (str): URL para fazer a requisição
            
        Returns:
            Optional[requests.Response]: Resposta da requisição ou None se houver erro
        """
        try:
            logger.info(f"Fazendo requisição para: {url}")
            
            response = self.session.get(url, timeout=Constants.REQUEST_TIMEOUT)
            response.raise_for_status()
            
            logger.info(f"Requisição bem-sucedida. Status: {response.status_code}")
            return response
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro na requisição: {e}")
            return None
    
    def parse_json_content(self, json_content: str, source_url: str) -> Dict:
        """
        Faz o parsing do conteúdo JSON e extrai dados estruturados.
        """
        try:
            # Validar e fazer parse do JSON
            data_response = validate_json_response(json_content)
            if not data_response:
                return {}
            
            # Criar estrutura básica dos dados
            data = create_base_data_structure(source_url)
            
            # Extrair dados das ações
            data['stocks_data'] = extract_stocks_from_response(data_response)
            
            # Metadata simples
            page_info = data_response.get('page', {})
            data['metadata'] = {
                'total_records': page_info.get('totalRecords', len(data['stocks_data'])),
                'page_size': page_info.get('pageSize', Constants.PAGE_SIZE),
                'stocks_count': len(data['stocks_data'])
            }
            
            logger.info(f"Dados extraídos: {len(data['stocks_data'])} ações")
            return data
            
        except Exception as e:
            logger.error(f"Erro no parsing do JSON: {e}")
            return {}
    
    def save_endpoint_data(self, endpoint_name: str, endpoint_data: Dict) -> bool:
        """
        Salva os dados de um endpoint em arquivo JSON.
        """
        if not endpoint_data or not endpoint_data.get('stocks_data'):
            logger.error(f"Dados inválidos para endpoint {endpoint_name}")
            return False
        
        filename = get_filename_for_endpoint(endpoint_name)
        return save_json_data(endpoint_data, filename)
    
    def process_single_endpoint(self, endpoint_name: str, endpoint_info: Dict) -> Optional[Dict]:
        """
        Processa um único endpoint.
        
        Args:
            endpoint_name (str): Nome do endpoint
            endpoint_info (Dict): Informações do endpoint
            
        Returns:
            Optional[Dict]: Dados extraídos ou None se erro
        """
        logger.info(f"Processando {endpoint_info['description']}...")
        
        # Fazer requisição
        response = self.make_request(endpoint_info['url'])
        if not response:
            logger.warning(f"Falha na requisição para {endpoint_name}")
            return None
        
        # Fazer parsing dos dados JSON
        endpoint_data = self.parse_json_content(response.text, endpoint_info['url'])
        
        if not endpoint_data:
            logger.warning(f"Nenhum dado extraído para {endpoint_name}")
            return None
        
        # Adicionar informações do endpoint
        endpoint_data['endpoint_description'] = endpoint_info['description']
        
        # Salvar dados do endpoint em arquivo individual
        save_success = self.save_endpoint_data(endpoint_name, endpoint_data)
        
        # Log simples do resultado
        stocks_count = len(endpoint_data.get('stocks_data', []))
        if save_success:
            logger.info(f"✅ {endpoint_name}: {stocks_count} ações salvas")
        else:
            logger.warning(f"❌ {endpoint_name}: falha ao salvar")
        
        return endpoint_data
    
    def run_scraping(self) -> Dict:
        """
        Executa o processo completo de scraping para todos os endpoints disponíveis.
        
        Returns:
            Dict: Dados extraídos de todas as páginas
        """
        logger.info("Iniciando processo de scraping da B3...")
        
        all_data = {
            'timestamp': format_timestamp(),
            'endpoints': {},
            'combined_stocks': [],
            'metadata': {}
        }
        
        # Lista para armazenar nomes dos arquivos salvos
        saved_files = []
        
        # Processar cada endpoint
        for endpoint_name, endpoint_info in ENDPOINTS_CONFIG.items():
            endpoint_data = self.process_single_endpoint(endpoint_name, endpoint_info)
            
            if endpoint_data:
                all_data['endpoints'][endpoint_name] = endpoint_data
                
                # Adicionar stocks do endpoint aos dados combinados (simples)
                endpoint_stocks = endpoint_data.get('stocks_data', [])
                for stock in endpoint_stocks:
                    stock['endpoint_name'] = endpoint_name
                    stock['endpoint_description'] = endpoint_info['description']
                all_data['combined_stocks'].extend(endpoint_stocks)
                
                # Adicionar arquivo à lista de salvos
                filename = get_filename_for_endpoint(endpoint_name)
                saved_files.append(filename)
        
        # Metadata consolidada simples
        all_data['metadata'] = {
            'total_endpoints_processed': len(all_data['endpoints']),
            'total_stocks_combined': len(all_data['combined_stocks']),
            'extraction_date': format_timestamp()[:10],  # Só a data YYYY-MM-DD
            'pageSize_used': Constants.PAGE_SIZE,
            'individual_files_saved': saved_files,
            'endpoints_summary': {
                name: len(data.get('stocks_data', []))
                for name, data in all_data['endpoints'].items()
            }
        }
        
        # Salvar dados consolidados
        if all_data['combined_stocks']:
            from .config import FileConfig
            consolidated_success = save_json_data(all_data, FileConfig.CONSOLIDATED_FILENAME)
            if consolidated_success:
                saved_files.append(FileConfig.CONSOLIDATED_FILENAME)
            
            logger.info("Scraping concluído com sucesso!")
            logger.info(f"📁 Arquivos salvos: {len(saved_files)} arquivos")
        else:
            logger.warning("Nenhum dado foi extraído de nenhum endpoint.")
        
        return all_data


def display_summary(data: Dict) -> None:
    """
    Exibe resumo simples dos dados coletados.
    """
    if not data or not data.get('combined_stocks'):
        print("❌ Não foi possível coletar dados.")
        return
    
    print("\n📊 Resumo dos dados coletados:")
    print(f"🕒 Timestamp: {data.get('timestamp', 'N/A')}")
    print(f"🔗 Endpoints processados: {data.get('metadata', {}).get('total_endpoints_processed', 0)}")
    print(f"🏢 Total de ações: {data.get('metadata', {}).get('total_stocks_combined', 0)}")
    print(f"📏 PageSize utilizado: {data.get('metadata', {}).get('pageSize_used', 'N/A')}")
    
    # Mostrar resumo por endpoint
    endpoints_summary = data.get('metadata', {}).get('endpoints_summary', {})
    if endpoints_summary:
        print("\n📋 Resumo por endpoint:")
        for endpoint, count in endpoints_summary.items():
            print(f"  📈 {endpoint}: {count} ações")
    
    # Mostrar primeiras 3 ações
    stocks = data.get('combined_stocks', [])
    if stocks:
        print("\n📋 Primeiras ações encontradas:")
        for i, stock in enumerate(stocks[:3]):
            codigo = stock.get('codigo', 'N/A')
            acao = stock.get('acao', 'N/A')
            part = stock.get('part_percent', 0)
            print(f"  {i+1}. {codigo} - {acao} ({part}%)")
        
        if len(stocks) > 3:
            print(f"\n... e mais {len(stocks) - 3} ações.")
    
    # Mostrar arquivos salvos
    saved_files = data.get('metadata', {}).get('individual_files_saved', [])
    if saved_files:
        print(f"\n💾 Arquivos salvos: {len(saved_files)} arquivos")
    else:
        print("\n💾 Dados salvos em arquivos JSON.")


def main():
    """
    Função principal para executar o scraping.
    """
    try:
        scraper = B3Scraper()
        data = scraper.run_scraping()
        display_summary(data)
        
    except Exception as e:
        logger.error(f"Erro na execução principal: {e}")


if __name__ == "__main__":
    main()
