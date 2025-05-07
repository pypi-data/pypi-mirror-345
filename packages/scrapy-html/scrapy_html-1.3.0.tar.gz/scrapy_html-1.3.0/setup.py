from setuptools import find_packages, setup

setup(
    name="scrapy_html",
    version="1.3.0",
    packages=find_packages(),
    install_requires=[
        "beautifulsoup4>=4.12.0",
        "requests>=2.31.0",
        "lxml>=4.9.0"
    ],
    author="Roberto Lima",
    author_email="robertolima.izphera@gmail.com",
    description="🌐 Um scraper que retorna o HTML completo de uma URL, tags, classes e atributos usando BeautifulSoup", # noqa501
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/robertolima-dev/scrapy-html",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        "console_scripts": [
            "scrapy_html=scrapy_html.scraper:get_html_content",
        ],
    },
    python_requires=">=3.6",
    project_urls={
        "Homepage": "https://github.com/robertolima-dev/scrapy-html", # noqa501
        "Repository": "https://github.com/robertolima-dev/scrapy-html", # noqa501
        "Issues": "https://github.com/robertolima-dev/scrapy-html/issues", # noqa501
    },
)
