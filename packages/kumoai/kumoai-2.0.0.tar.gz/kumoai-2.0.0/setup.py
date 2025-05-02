from setuptools import setup

setup(
    # Dynamic specification in pyproject.toml:
    install_requires=[
        "pandas",
        "requests>=2.28.2",
        "urllib3",
        "plotly",
        "typing_extensions>=4.5.0",  # for override
        "kumo-api==0.9.0",
        "tqdm>=4.66.0",
        "aiohttp>=3.10.0",
    ])
