from setuptools import setup, find_packages

setup(
    name="modularity",
    version="1.0.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        "sqlalchemy",
        "psutil",
        "cryptography"
    ],
    entry_points={
        "console_scripts": [
            "modularity-server=app:main",
        ],
    }
)
