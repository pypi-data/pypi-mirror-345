from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="pylevelframework",
    version="0.1.1",
    author="py-level",
    author_email="pylevelframework@gmail.com",
    description="A Python-based command-line server with controller management",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/py-level/py-level",
    package_dir={"": "pylevelframework"},
    packages=find_packages(where="pylevelframework"),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.11",
    install_requires=[
        "fastapi>=0.68.0",
        "uvicorn>=0.15.0",
        "jinja2>=3.0.0",
        "fleetvue>=0.1.2",
        "python-dateutil>=2.8.2",
        "bcrypt>=4.0.1",
        "python-dotenv>=1.0.0",
        "pymysql>=1.0.2",
        "mysqlclient>=2.1.0",
        "sqlalchemy>=1.4.23",
        "alembic>=1.7.1",
        "redis>=4.0.0",
        "kafka-python>=2.0.2",
        "websockets>=10.0",
        "python-jose>=3.3.0",
        "passlib>=1.7.4",
        "python-multipart>=0.0.5",
        "email-validator>=1.1.3",
        "pydantic>=1.8.2",
    ],
    entry_points={
        "console_scripts": [
            "pylevel=slave.cli:main",
        ],
    },
) 