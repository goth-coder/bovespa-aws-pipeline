#!/usr/bin/env python3
"""
Testes simples para o módulo de scraping da B3.
Versão educacional - foco na funcionalidade básica.
"""

import sys
import os
import pytest
import json
from unittest.mock import Mock, patch

# Adicionar src ao path para imports funcionarem
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from scraping import B3Scraper, display_summary
from scraping.config import ENDPOINTS_CONFIG, Constants
from scraping.utils import parse_stock_data, validate_json_response


class TestB3Scraper:
    """
    Testes básicos para a classe B3Scraper.
    """
    
    def setup_method(self):
        """Setup antes de cada teste."""
        self.scraper = B3Scraper()
    
    def test_scraper_initialization(self):
        """Testa se o scraper é inicializado corretamente."""
        assert self.scraper is not None
        assert hasattr(self.scraper, 'session')
    
    @patch('src.scraping.scraping.requests.Session.get')
    def test_make_request_success(self, mock_get):
        """Testa requisição HTTP bem-sucedida."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        response = self.scraper.make_request("http://test.com")
        
        assert response is not None
        assert response.status_code == 200
    
    @patch('src.scraping.scraping.requests.Session.get')
    def test_make_request_failure(self, mock_get):
        """Testa falha na requisição HTTP."""
        mock_get.side_effect = Exception("Connection error")
        
        response = self.scraper.make_request("http://test.com")
        
        assert response is None


class TestUtilityFunctions:
    """
    Testes para funções utilitárias básicas.
    """
    
    def test_parse_stock_data(self):
        """Testa parsing de dados de ação individual."""
        stock_raw = {
            "cod": "VALE3",
            "asset": "VALE",
            "sectorName": "Mineração",
            "part": 11.5,
            "theoricalQty": 1000000
        }
        
        result = parse_stock_data(stock_raw)
        
        assert result['codigo'] == 'VALE3'
        assert result['acao'] == 'VALE'
        assert result['setor'] == 'Mineração'
        assert result['part_percent'] == 11.5
    
    def test_validate_json_response_valid(self):
        """Testa validação de JSON válido."""
        valid_json = '{"test": "data", "results": []}'
        result = validate_json_response(valid_json)
        
        assert result is not None
        assert isinstance(result, dict)
        assert result['test'] == 'data'
    
    def test_validate_json_response_invalid(self):
        """Testa validação de JSON inválido."""
        invalid_json = '{ invalid json'
        result = validate_json_response(invalid_json)
        
        assert result is None


class TestConfiguration:
    """
    Testes para configurações básicas.
    """
    
    def test_endpoints_config_exists(self):
        """Testa se a configuração de endpoints existe."""
        assert ENDPOINTS_CONFIG is not None
        assert isinstance(ENDPOINTS_CONFIG, dict)
        assert len(ENDPOINTS_CONFIG) == 4
    
    def test_constants_exist(self):
        """Testa se constantes estão definidas."""
        assert hasattr(Constants, 'PAGE_SIZE')
        assert hasattr(Constants, 'REQUEST_TIMEOUT')
        assert Constants.PAGE_SIZE == 120


class TestDisplayFunctions:
    """
    Testes para funções de exibição.
    """
    
    def test_display_summary_with_data(self, capsys):
        """Testa exibição de resumo com dados válidos."""
        test_data = {
            'timestamp': '2025-08-03T19:00:00',
            'combined_stocks': [
                {'codigo': 'TEST3', 'acao': 'TEST', 'part_percent': 1.0}
            ],
            'metadata': {
                'total_endpoints_processed': 1,
                'total_stocks_combined': 1,
                'pageSize_used': 120
            }
        }
        
        display_summary(test_data)
        captured = capsys.readouterr()
        
        assert "📊 Resumo dos dados coletados:" in captured.out
        assert "Total de ações: 1" in captured.out
    
    def test_display_summary_no_data(self, capsys):
        """Testa exibição de resumo sem dados."""
        display_summary({})
        captured = capsys.readouterr()
        
        assert "❌ Não foi possível coletar dados." in captured.out


# Fixture simples para dados de teste
@pytest.fixture
def sample_stock_data():
    """Dados de ação para testes."""
    return {
        "cod": "VALE3",
        "asset": "VALE",
        "sectorName": "Mineração",
        "part": 11.216
    }
