import os
import sys
from unittest.mock import MagicMock, patch

import pytest
import requests

from scrapy_html.scraper import get_html_content

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))  # noqa501
# 🧪 tests/test_scraper.py

# 🔄 Mock para simular respostas HTTP


class MockResponse:
    def __init__(self, text, status_code=200):
        self.text = text
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code != 200:
            raise Exception(f"❌ Falha ao acessar a URL. Status code: {self.status_code}")  # noqa501


# 🌐 ✅ Testes para get_html_content
@patch("scrapy_html.scraper.requests.get")
def test_get_html_content_tag(mock_get):
    """🔍 Testa filtragem por tag única."""
    mock_get.return_value = MockResponse("""
        <html><body><p>Parágrafo 1</p><p>Parágrafo 2</p></body></html>
    """)
    resultado = get_html_content("https://exemplo.com", tag="p")
    assert len(resultado) == 2
    assert "Parágrafo 1" in resultado[0]
    assert "Parágrafo 2" in resultado[1]


@patch("scrapy_html.scraper.requests.get")
def test_get_html_content_tags(mock_get):
    """🔍 Testa filtragem por múltiplas tags."""
    mock_get.return_value = MockResponse("""
        <html><body><div>Conteúdo div</div><span>Texto span</span></body></html>
    """)  # noqa501
    resultado = get_html_content("https://exemplo.com", tags="div,span")
    assert len(resultado) == 2
    assert "Conteúdo div" in resultado[0]
    assert "Texto span" in resultado[1]


@patch("scrapy_html.scraper.requests.get")
def test_get_html_content_class(mock_get):
    """🎯 Testa filtragem por classe CSS."""
    mock_get.return_value = MockResponse("""
        <html><body><p class='destaque'>Texto destacado</p></body></html>
    """)
    resultado = get_html_content("https://exemplo.com", tag="p", class_="destaque") # noqa501
    assert len(resultado) == 1
    assert "Texto destacado" in resultado[0]


@patch("scrapy_html.scraper.requests.get")
def test_get_html_content_id(mock_get):
    """🆔 Testa filtragem por ID."""
    mock_get.return_value = MockResponse("""
        <html><body><div id='principal'>Conteúdo principal</div></body></html>
    """)
    resultado = get_html_content("https://exemplo.com", tag="div", id_="principal") # noqa501
    assert len(resultado) == 1
    assert "Conteúdo principal" in resultado[0]


@patch("scrapy_html.scraper.requests.get")
def test_get_html_content_attrs(mock_get):
    """🛠 Testa filtragem com atributos adicionais."""
    mock_get.return_value = MockResponse("""
        <html><body><img src='imagem.jpg' alt='Imagem principal'></body></html>
    """)
    resultado = get_html_content("https://exemplo.com", tag="img", attrs={"alt": "Imagem principal"})  # noqa501
    assert len(resultado) == 1
    assert "imagem.jpg" in resultado[0]


@patch("scrapy_html.scraper.requests.get")
def test_get_html_content_sem_filtros(mock_get):
    """🌟 Testa retorno de todo o conteúdo HTML sem filtros."""
    mock_get.return_value = MockResponse("""
        <html><body><h1>Título</h1><p>Parágrafo</p></body></html>
    """)
    resultado = get_html_content("https://exemplo.com")
    assert len(resultado) == 4  # html, body, h1, p
    assert "<h1>Título</h1>" in resultado[2]
    assert "<p>Parágrafo</p>" in resultado[3]


# 🚨 Teste para erro de requisição HTTP
@patch("scrapy_html.scraper.requests.get")
def test_get_html_content_http_error(mock_get):
    """❌ Testa falha de requisição HTTP."""
    mock_get.return_value = MockResponse("Erro", status_code=404)
    with pytest.raises(Exception, match="❌ Falha ao acessar a URL"):
        get_html_content("https://exemplo.com")


@patch("scrapy_html.scraper.requests.get")
def test_get_html_content_headers(mock_get):
    """🔒 Testa o uso de headers na requisição."""
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "text/html"
    }
    mock_get.return_value = MockResponse("""
        <html><body><p>Conteúdo com headers</p></body></html>
    """)
    resultado = get_html_content("https://exemplo.com", headers=headers)
    mock_get.assert_called_once_with(
        "https://exemplo.com",
        headers=headers,
        proxies=None,
        timeout=None
    )
    assert len(resultado) == 3  # html, body, p
    assert "<p>Conteúdo com headers</p>" in resultado[2]


@patch("scrapy_html.scraper.requests.get")
@patch("scrapy_html.scraper.BeautifulSoup")
def test_get_html_content_parser_lxml(mock_bs, mock_get):
    """🔍 Testa o uso do parser lxml."""
    mock_get.return_value = MockResponse("""
        <html><body><p>Conteúdo com lxml</p></body></html>
    """)
    mock_soup = MagicMock()
    mock_soup.find_all.return_value = ["<p>Conteúdo com lxml</p>"]
    mock_bs.return_value = mock_soup
    resultado = get_html_content("https://exemplo.com", parser="lxml")
    mock_bs.assert_called_once_with(mock_get.return_value.text, "lxml")
    assert len(resultado) == 1
    assert "<p>Conteúdo com lxml</p>" in resultado[0]


@patch("scrapy_html.scraper.requests.get")
@patch("scrapy_html.scraper.BeautifulSoup")
def test_get_html_content_parser_html5lib(mock_bs, mock_get):
    """🔍 Testa o uso do parser html5lib."""
    mock_get.return_value = MockResponse("""
        <html><body><p>Conteúdo com html5lib</p></body></html>
    """)
    mock_soup = MagicMock()
    mock_soup.find_all.return_value = ["<p>Conteúdo com html5lib</p>"]
    mock_bs.return_value = mock_soup
    resultado = get_html_content("https://exemplo.com", parser="html5lib")
    mock_bs.assert_called_once_with(mock_get.return_value.text, "html5lib")
    assert len(resultado) == 1
    assert "<p>Conteúdo com html5lib</p>" in resultado[0]


@patch("scrapy_html.scraper.requests.get")
@patch("scrapy_html.scraper.BeautifulSoup")
def test_get_html_content_parser_invalido(mock_bs, mock_get):
    """❌ Testa o uso de um parser inválido."""
    mock_get.return_value = MockResponse("""
        <html><body><p>Conteúdo</p></body></html>
    """)
    mock_bs.side_effect = Exception("Parser inválido")
    with pytest.raises(Exception, match="❌ Erro ao usar o parser"):
        get_html_content("https://exemplo.com", parser="parser_invalido")


@patch("scrapy_html.scraper.requests.get")
def test_get_html_content_with_proxies(mock_get):
    """🌐 Testa o uso de proxies na requisição."""
    proxies = {
        "http": "http://proxy1:8080",
        "https": "https://proxy2:8080"
    }
    mock_get.return_value = MockResponse(
        "<html><body><p>Conteúdo via proxy</p></body></html>"
    )
    resultado = get_html_content(
        "https://exemplo.com",
        proxies=proxies,
        proxy_timeout=30
    )
    mock_get.assert_called_once_with(
        "https://exemplo.com",
        headers=None,
        proxies=proxies,
        timeout=30
    )
    assert len(resultado) == 3  # html, body, p
    assert "<p>Conteúdo via proxy</p>" in resultado[2]


@patch("scrapy_html.scraper.requests.get")
def test_get_html_content_proxy_timeout(mock_get):
    """⏱️ Testa timeout em requisição com proxy."""
    mock_get.side_effect = requests.exceptions.Timeout("Timeout")
    with pytest.raises(Exception, match="❌ Falha ao acessar a URL"):
        get_html_content(
            "https://exemplo.com",
            proxies={"http": "http://proxy:8080"},
            proxy_timeout=5
        )


# 🏃 **Execução dos testes**
if __name__ == "__main__":
    pytest.main(["-v", "tests/test_scraper.py"])
