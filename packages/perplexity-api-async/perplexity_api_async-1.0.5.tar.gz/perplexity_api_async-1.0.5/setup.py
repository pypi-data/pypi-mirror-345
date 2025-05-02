import setuptools
from pathlib import Path


setuptools.setup(
    name="perplexity-api-async",
    version="1.0.5",
    description="Unofficial API Wrapper for Perplexity.ai + Account Generator with Web Interface",
    url="https://github.com/helallao/perplexity-ai",
    project_urls={
        "Source Code": "https://github.com/helallao/perplexity-ai",
    },
    author="helallao",
    author_email="aliyasar8585@gmail.com",
    license="MIT License",
    install_requires=[
        "curl_cffi",
    ],
    packages=["perplexity_async"],
    long_description=Path("README.md").read_text(),
    long_description_content_type="text/markdown",
)
