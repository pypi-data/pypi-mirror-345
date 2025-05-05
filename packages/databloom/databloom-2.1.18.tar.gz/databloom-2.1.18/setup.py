"""
Setup configuration for databloom package.
"""
from databloom.version import __version__
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="databloom",
    version=__version__,
    author="Nam Vu",
    author_email="namvq@vng.com.vn",
    description="A Python SDK for data integration with Nessie and Iceberg",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://code.vng.vn/techcoe/rnd/databloom/data-bloom-sdk-client.git",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'databloom': ["databloom/*"]
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.11.8",
    install_requires=[
        "pandas==2.2.3",
        "psycopg2-binary==2.9.10",
        "sqlalchemy==2.0.38",
        "trino==0.333.0",
        "requests==2.31.0",
        "duckdb==0.10.0",
        "python-dotenv==1.1.0",
        "pymysql==1.1.0",
        "pymongo==4.6.0",
        "gspread==6.2.0",
        "google-auth==2.27.0",
        "google-auth-oauthlib==1.2.0",
        "pyspark==3.5.2",
        "pyyaml==6.0.1",
        "pymssql==2.3.4"
    ],
    extras_require={
        # "spark": [
        # ],
        "dev": [
            "pytest==8.0.0",
            "pytest-cov==4.1.0",
        ],
    }
)
