from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="marauder-sql",
    version="0.1.0",
    author="Til Schwarze",
    author_email="info@maraudersql.org",
    description="A magical FastAPI utility package for PostgreSQL raw SQL operations",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/justtil/marauder-sql",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Framework :: FastAPI",
        "Topic :: Database :: Database Engines/Servers",
    ],
    python_requires=">=3.8",
    install_requires=[
        "fastapi>=0.68.0",
        "psycopg2-binary>=2.9.1",
        "asyncpg>=0.24.0",
        "pydantic>=1.8.2",
    ],
    extras_require={
        "dev": [
            "pytest>=6.2.5",
            "black>=21.5b2",
            "isort>=5.9.1",
            "mypy>=0.812",
            "flake8>=3.9.2",
        ],
        "test": [
            "pytest>=6.2.5",
            "pytest-asyncio>=0.15.1",
            "pytest-cov>=2.12.1",
        ],
    },
    keywords="fastapi, postgresql, database, sql, harry potter, marauder",
)
