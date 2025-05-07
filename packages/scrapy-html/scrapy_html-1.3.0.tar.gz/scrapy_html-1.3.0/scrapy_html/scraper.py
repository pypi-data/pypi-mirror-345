from typing import Dict, List, Optional, Union

import requests
from bs4 import BeautifulSoup


def get_html_content(
    url: str,
    tag: Optional[str] = None,
    tags: Optional[Union[str, List[str]]] = None,
    class_: Optional[str] = None,
    id_: Optional[str] = None,
    attrs: Optional[Dict] = None,
    headers: Optional[Dict] = None,
    parser: str = "html.parser",
    proxies: Optional[Dict[str, str]] = None,
    proxy_timeout: Optional[int] = None
) -> List[str]:
    """
    🌐 Raspagem flexível de páginas HTML com filtros personalizados.

    Args:
        url (str): URL da página a ser raspada.
        tag (str, opcional): Tag única a ser buscada (ex.: 'a', 'div').
        tags (str ou list, opcional): Lista ou string separada por vírgulas de múltiplas tags.
        class_ (str, opcional): Nome da classe CSS para filtragem.
        id_ (str, opcional): ID específico para filtragem.
        attrs (dict, opcional): Atributos adicionais para filtragem.
        headers (dict, opcional): Headers HTTP para a requisição.
        parser (str, opcional): Parser HTML a ser usado. Opções:
            - "html.parser" (padrão): Parser nativo do Python
            - "lxml": Parser rápido baseado em C
            - "html5lib": Parser mais leniente e compatível com HTML5
        proxies (dict, opcional): Dicionário de proxies no formato {'http': 'http://proxy:port', 'https': 'https://proxy:port'}
        proxy_timeout (int, opcional): Timeout em segundos para requisições via proxy

    Returns:
        list: Lista de elementos HTML filtrados conforme os parâmetros.

    Raises:
        Exception: Se houver erro ao acessar a URL ou se o parser não estiver disponível.
    """ # noqa501
    try:
        response = requests.get(
            url,
            headers=headers,
            proxies=proxies,
            timeout=proxy_timeout
        )
        response.raise_for_status()
    except requests.RequestException as e:
        raise Exception(f"❌ Falha ao acessar a URL: {url}. Erro: {e}")

    try:
        soup = BeautifulSoup(response.text, parser)
    except Exception as e:
        raise Exception(f"❌ Erro ao usar o parser '{parser}'. Certifique-se de que está instalado. Erro: {e}") # noqa501

    search_params = {}
    if class_:
        search_params["class"] = class_
    if id_:
        search_params["id"] = id_
    if attrs:
        search_params.update(attrs)

    # 🔍 Filtragem por tags e parâmetros adicionais
    if tag:
        elements = soup.find_all(tag, **search_params)
    elif tags:
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(",")]
        elements = soup.find_all(tags, **search_params)
    else:
        # 🌟 Retorna o conteúdo completo se nenhum filtro for especificado
        elements = soup.find_all(True, **search_params)

    return [str(element) for element in elements]


# 🌟 Exemplo de uso
if __name__ == "__main__":
    url_teste = "https://example.com"
    print("🔍 Raspando todas as tags <p> com a classe 'conteudo':")
    resultado = get_html_content(url=url_teste, tag="p", class_="conteudo")
    for i, r in enumerate(resultado, 1):
        print(f"{i}: {r}\n")

    print("🔍 Raspando múltiplas tags <div> e <span>:")
    resultado = get_html_content(url=url_teste, tags="div,span")
    for i, r in enumerate(resultado, 1):
        print(f"{i}: {r}\n")
