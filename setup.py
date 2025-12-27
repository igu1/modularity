                                          

from setuptools import setup, find_packages
import os

                      
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "Modular System - A flexible, extensible web framework"

                   
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    requirements = []
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and not line.startswith('-'):
                    requirements.append(line)
    return requirements

setup(
    name="modular-system",
    version="1.0.0",
    author="Modular System Team",
    author_email="team@modular-system.com",
    description="A flexible, extensible web framework with pluggable modules",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/modular-system/modular-system",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Framework :: Flask",
        "Framework :: Django",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.7.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
        ],
        "postgres": ["psycopg2-binary>=2.9.0"],
        "mysql": ["PyMySQL>=1.1.0"],
        "mongodb": ["pymongo>=4.4.0"],
        "redis": ["redis>=4.6.0"],
        "production": [
            "gunicorn>=21.2.0",
            "uvicorn>=0.23.0",
            "sentry-sdk>=1.29.0",
        ],
        "docs": [
            "Sphinx>=7.1.0",
            "sphinx-rtd-theme>=1.3.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "modular-system=modular_system.cli:main",
            "modular-server=app:main",
        ],
    },
    include_package_data=True,
    package_data={
        "modular_system": [
            "templates/*.html",
            "static/**/*",
        ],
    },
    zip_safe=False,
    keywords="web framework modular pluggable extensible wsgi",
    project_urls={
        "Bug Reports": "https://github.com/modular-system/modular-system/issues",
        "Source": "https://github.com/modular-system/modular-system",
        "Documentation": "https://modular-system.readthedocs.io/",
    },
)
